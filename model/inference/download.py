"""
KV-13 Weight Downloader
Downloads from HuggingFace Hub with resume and quantization options.
"""

import argparse
from pathlib import Path

VARIANTS = {
    "kv13-13b": {"files": ["config.json", "model.safetensors"], "size": "26GB"},
    "kv13-13b-instruct": {"files": ["config.json", "model.safetensors"], "size": "26GB"},
    "kv13-13b-instruct-q4": {"files": ["model-q4.gguf"], "size": "7GB"},
    "kv13-13b-instruct-awq": {"files": ["model-awq.safetensors"], "size": "7GB"},
}

def download(variant: str = "kv13-13b-instruct-q4", dest: str = "weights"):
    dest_path = Path(dest) / variant
    dest_path.mkdir(parents=True, exist_ok=True)
    print(f"[KV-13] Downloading {variant} ({VARIANTS[variant]['size']}) to {dest_path}")
    print("[KV-13] Source: https://huggingface.co/kv-creates/KV-13")
    # Mock download - real uses huggingface_hub.snapshot_download
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=f"kv-creates/{variant}", local_dir=str(dest_path))
    except ImportError:
        print("[KV-13] huggingface_hub not installed. Mocking download...")
        for f in VARIANTS[variant]["files"]:
            (dest_path / f).write_text(f"# Mock {f} for {variant}\n# Replace with real weights from HF Hub")
            print(f"  created mock {f}")
    print(f"[KV-13] Done. Load with: python -m model.inference.engine --variant {variant}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="kv13-13b-instruct-q4", choices=list(VARIANTS.keys()))
    parser.add_argument("--dest", default="weights")
    args = parser.parse_args()
    download(args.variant, args.dest)
