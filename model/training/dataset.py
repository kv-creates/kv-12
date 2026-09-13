"""
KV-13 Dataset Preparation
Handles: The Stack v2, PR reviews, CVEFixes, Defects4J
Creates packed 32K sequences with repo-level context.

Usage:
  python model/training/dataset.py --config model/training/config.yaml
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List, Dict

# Lightweight tokenizer mock - real tokenizer is at model/tokenizer/
# This file demonstrates packing logic without heavy deps.


PROMPT_TEMPLATES = {
    "analyze": "### Code ({language}):\n{code}\n\n### Task: Analyze for bugs, security issues, and code quality. Provide risk score 0-100.",
    "fix": "### Buggy Code ({language}):\n{code}\n\n### Bug: {bug_type}\n### Task: Generate minimal fix as unified diff.",
    "review": "### Pull Request Diff:\n{diff}\n\n### Task: Review as senior engineer. Provide summary, issues, suggestions, and score.",
    "modernize": "### Legacy Code ({source_lang}):\n{code}\n\n### Task: Modernize to {target_lang} preserving behavior. Output refactored code.",
}


def pack_repo_context(files: List[Dict[str, str]], max_tokens: int = 32768) -> str:
    """
    Packs multiple files with symbol graph into a single context.
    Uses file path as delimiter for repo-level attention.
    """
    packed = []
    total = 0
    for f in files:
        chunk = f"<file path=\"{f['path']}\">\n{f['content']}\n</file>\n"
        tokens_est = len(chunk) // 4  # rough
        if total + tokens_est > max_tokens:
            break
        packed.append(chunk)
        total += tokens_est
    return "\n".join(packed)


def create_instruction_sample(code: str, language: str, task: str, **kwargs) -> Dict[str, str]:
    template = PROMPT_TEMPLATES.get(task, PROMPT_TEMPLATES["analyze"])
    prompt = template.format(code=code, language=language, **kwargs)
    return {"prompt": prompt, "language": language, "task": task}


def load_mock_dataset(n: int = 10) -> List[Dict]:
    """Generates mock samples for testing without downloading 1.2T tokens."""
    samples = []
    bug_types = ["NullDereference", "RaceCondition", "SQLInjection", "DivisionByZero", "BufferOverflow"]
    langs = ["python", "javascript", "java", "go", "rust"]
    for i in range(n):
        lang = random.choice(langs)
        bug = random.choice(bug_types)
        code = f"# Sample {i}\ndef func_{i}(x):\n    return x * 2  # {bug} risk"
        samples.append(create_instruction_sample(code, lang, "analyze", bug_type=bug))
        samples.append(create_instruction_sample(code, lang, "fix", bug_type=bug))
    return samples


def prepare(output_dir: str = "data/processed", config_path: str = "model/training/config.yaml"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    samples = load_mock_dataset(100)
    with open(out / "train.jsonl", "w") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
    print(f"[KV-13 Dataset] Wrote {len(samples)} mock samples to {out / 'train.jsonl'}")
    print("[KV-13 Dataset] For full dataset, run: python model/training/prepare_full.py (requires HF datasets)")

    # Also demonstrate repo packing
    mock_repo = [
        {"path": "src/app.py", "content": "def add(a,b): return a+b"},
        {"path": "src/utils.py", "content": "def validate(x): return x is not None"},
        {"path": "tests/test_app.py", "content": "def test_add(): assert add(1,2)==3"},
    ]
    packed = pack_repo_context(mock_repo, max_tokens=4096)
    print("\n[KV-13 Dataset] Repo packing example:")
    print(packed[:500] + "...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="model/training/config.yaml")
    parser.add_argument("--output_dir", default="data/processed")
    args = parser.parse_args()
    prepare(args.output_dir, args.config)
