# KV-13 Architecture

## Overview
KV-13 is a 13.2B parameter decoder-only transformer purpose-built for code intelligence. Unlike general chat LLMs, every decision optimizes for repository-level code understanding.

## Model Config

| Parameter | Value |
|---|---|
| Layers | 40 |
| Hidden size | 5120 |
| Intermediate (SwiGLU) | 13824 |
| Heads | 40 (GQA with 8 KV heads) |
| Vocab | 52000 + 800 code specials |
| Context | 32768 (NTK-extended to 128K) |
| RoPE theta | 10000 |
| Norm | RMSNorm + QK-LayerNorm |

## Techniques

- **Grouped Query Attention (GQA):** 40 Q heads share 8 KV heads. 5x KV cache reduction for 32K context.
- **SwiGLU:** `down(silu(gate) * up)` with 13824 intermediate. Better code reasoning than GELU.
- **FlashAttention-2:** O(N) memory, 2-3x speedup at 32K.
- **RoPE + NTK-aware scaling:** Extends 32K training to 128K inference for repo-level analysis without retraining.
- **QK LayerNorm:** Stabilizes 13B training (prevents attention entropy collapse).
- **Repo-Level Attention:** Symbol graph (imports, calls, types) injected as second attention stream. Files are delimited by `<file path="...">` tokens.

## Heads

All heads run in one forward pass:

1. **Bug Head (12 classes):** DivisionByZero, NullDereference, RaceCondition, SQLInjection, BufferOverflow, etc. Token-level classification, pooled to file risk.
2. **Security Head (10 classes):** Maps to CWE/OWASP. CWE-89, CWE-78, CWE-327, etc.
3. **Fix Head:** Generates unified diff via causal LM. Trained on 2.3M bug-fix pairs (CVEFixes + GitHub commits with "fix" message).
4. **Review Head:** Generates markdown review. Trained on 4M PR reviews + 180K RLHF human preferences (DPO).
5. **Risk Head:** MLP on mean-pooled hidden states -> sigmoid 0-1 -> *100 calibrated risk. Platt scaling on held-out defects.

## Training Data (1.2T tokens)

- 55% The Stack v2 Dedup (600B code)
- 15% PR Reviews 4M (180B)
- 10% CVEFixes (120B)
- 8% Defects4J + BugsInPy (96B)
- 7% Instruction tuning 180K (84B)
- 5% Legacy pairs COBOL->Java, Py2->Py3, Java8->17 (60B)

Dedup: MinHash + exact SHA for near-duplicates. PII scrubbed. License filter: permissive only.

## Training Recipe

- Optimizer: AdamW (beta1 0.9, beta2 0.95, eps 1e-5), weight_decay 0.1
- LR: 2e-4 cosine, warmup 3% (3600 steps)
- Batch: 1024 sequences (8 nodes x 8 GPUs x 1 grad_accum 16)
- Precision: BF16 + FP32 master, DeepSpeed ZeRO-3 + CPU offload
- Grad checkpointing: enabled
- Steps: 120K (~2 epochs)
- RLHF: DPO beta 0.1 on 180K preference pairs (human rated reviews)

## Quantization

- AWQ 4-bit g128, GPTQ 4-bit, GGUF Q4_K_M
- VRAM: FP16 26GB, Q4 7GB, Q5 8.5GB
- Perplexity delta: <0.08

## Inference

```
Input: <file path="src/app.py">\n{code}\n</file> + instruction
-> Tokenize (52K BPE)
-> 40 layers
-> Parallel heads
-> Output: risk, bugs[], security[], diff, review markdown
Latency: 0.8s / 1K tokens on A100, 2.1s on RTX 4090 Q4
```

## Repo Packing

Files are topologically sorted by import graph, truncated to 32K/128K, with symbol table preamble.

## Reproduce

```bash
python model/training/train.py --config model/training/config.yaml --debug
python model/training/eval.py --checkpoint weights/kv13-13b-instruct-q4
```

See `model/kv13.py:1` for implementation.
