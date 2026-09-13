# Contributing to KV-13

Thank you for contributing to open-source code intelligence.

## Setup

```bash
git clone https://github.com/kv-creates/KV-13.git
cd KV-13
pip install -e ".[dev]"
pytest -v
```

## Workflow

1. Fork and create branch: `git checkout -b feat/your-feature`
2. Make changes with tests
3. Run checks: `pytest && python -m model.inference.engine --code "def foo(): return 1/0"`
4. Submit PR with description and benchmark if model-related

## Areas

- Model: `model/kv13.py`, `model/training/`
- API: `api/app.py`
- Website: `website/assets/`
- Docs: `docs/`

## Code Style

- Python: ruff + black, line length 100
- Commit: conventional commits (`feat:`, `fix:`, `docs:`)

## Reporting Issues

Open GitHub issue with repro code and language.

## License

By contributing, you agree MIT.
