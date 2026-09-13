"""
KV-13 Training Pipeline
Supports: pretraining, instruction tuning, DPO/RLHF

Usage:
  torchrun --nproc_per_node=8 model/training/train.py --config model/training/config.yaml
  python model/training/train.py --config model/training/config.yaml --debug
"""

from __future__ import annotations

import argparse
import yaml
from pathlib import Path
from dataclasses import dataclass

import torch
from torch.utils.data import DataLoader

try:
    from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

from model.kv13 import KV13Config, KV13ForCausalLM


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_model(config_dict: dict) -> KV13ForCausalLM:
    m = config_dict["model"]
    cfg = KV13Config(
        vocab_size=m["vocab_size"],
        hidden_size=m["hidden_size"],
        intermediate_size=m["intermediate_size"],
        num_hidden_layers=m["num_hidden_layers"],
        num_attention_heads=m["num_attention_heads"],
        num_key_value_heads=m["num_key_value_heads"],
        max_position_embeddings=m["max_position_embeddings"],
    )
    model = KV13ForCausalLM(cfg)
    print(f"[KV-13] Initialized {model.count_parameters() / 1e9:.2f}B parameters")
    return model


def train(config_path: str, debug: bool = False):
    cfg = load_config(config_path)
    print(f"[KV-13] Loaded config from {config_path}")
    print(f"[KV-13] Datasets: {[d['name'] for d in cfg['data']['datasets']]}")
    print(f"[KV-13] Training for {cfg['training']['max_steps']} steps, LR={cfg['training']['learning_rate']}")

    model = build_model(cfg)

    if debug:
        # Quick forward pass sanity check
        input_ids = torch.randint(0, cfg["model"]["vocab_size"], (2, 512))
        out = model(input_ids)
        print(f"[KV-13 DEBUG] logits shape: {out['logits'].shape}")
        print(f"[KV-13 DEBUG] risk_score: {out['risk_score'].flatten().tolist()}")
        print("[KV-13 DEBUG] Forward pass OK")
        return

    if not HF_AVAILABLE:
        print("[KV-13] transformers/datasets not installed. Install with pip install -r requirements.txt")
        return

    # Real training would use HF Trainer + DeepSpeed
    # Simplified placeholder for open-source reproducibility
    print("[KV-13] Starting training loop (mock - replace with Trainer for full run)")
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["training"]["learning_rate"], weight_decay=cfg["training"]["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg["training"]["max_steps"])

    # Mock loop
    model.train()
    for step in range(3):
        dummy_ids = torch.randint(0, cfg["model"]["vocab_size"], (cfg["training"]["per_device_train_batch_size"], 512))
        dummy_labels = dummy_ids.clone()
        out = model(dummy_ids, labels=dummy_labels)
        loss = out["loss"]
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
        print(f"  step {step+1}/3 - loss: {loss.item():.4f}")

    print("[KV-13] Mock training complete. Use deepspeed + real data for full training.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KV-13 Training")
    parser.add_argument("--config", type=str, default="model/training/config.yaml")
    parser.add_argument("--debug", action="store_true", help="Run single forward pass only")
    args = parser.parse_args()
    train(args.config, debug=args.debug)
