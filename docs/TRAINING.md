# Training Guide

## Quick Debug (no GPU)

```bash
pip install -r requirements.txt
python model/training/train.py --config model/training/config.yaml --debug
python model/training/dataset.py --output_dir data/processed
python -m model.inference.engine --code "def foo(): return 1/0" --json
```

## Full Dataset Preparation

Requires HuggingFace datasets + 500GB disk.

```bash
python model/training/prepare_full.py --config model/training/config.yaml
# Writes to data/processed/train.jsonl (packed 32K sequences)
```

## Training (8x A100 80GB)

```bash
torchrun --nproc_per_node=8 model/training/train.py --config model/training/config.yaml
# Or with DeepSpeed
deepspeed --num_gpus=8 model/training/train.py --config model/training/config.yaml --deepspeed configs/deepspeed_zero3.json
```

Monitor at `wandb` project `kv13`.

## RLHF (DPO)

After SFT:

```bash
python model/training/dpo.py --config model/training/config.yaml --checkpoint checkpoints/kv13-sft
```

## Evaluation

```bash
python model/training/eval.py --checkpoint checkpoints/kv13-final --benchmarks humanevalfix,defects4j,cvefixes
```

## Quantization

```bash
python model/quantize.py --checkpoint checkpoints/kv13-final --bits 4 --method awq
python model/quantize.py --checkpoint checkpoints/kv13-final --bits 4 --method gguf
```

## Hardware

- Training: 8x A100 80GB, ~4 days, ~$2k on cloud
- Inference FP16: 26GB VRAM (A100, 4090 24GB with offload)
- Inference Q4: 7GB VRAM (RTX 3060, laptop)

## Config

Edit `model/training/config.yaml`. Key fields: `training.learning_rate`, `data.datasets`, `model.max_position_embeddings`.
