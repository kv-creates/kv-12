"""
KV-13 Python SDK
pip install kv13 then:
  from kv13 import KV13Client
  client = KV13Client()
  result = client.analyze_file("src/app.py")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class AnalysisResult:
    risk_score: int
    review_score: int
    bugs: list
    security: list
    suggestions: list
    auto_fix_diff: str
    language: str
    loc: int


class KV13Client:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        if HAS_HTTPX:
            self._client = httpx.Client(timeout=timeout, headers={"Authorization": f"Bearer {api_key}"} if api_key else {})
        else:
            self._client = None

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        if self._client:
            resp = self._client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        # fallback: use local engine without HTTP
        print(f"[KV-13 SDK] httpx not installed, using local engine for {path}")
        from model.inference.engine import analyze_code, detect_language, generate_review, modernize_code
        if path == "/v1/analyze":
            lang = payload.get("language") or detect_language(payload["code"], payload.get("filename"))
            r = analyze_code(payload["code"], lang)
            return {
                "risk_score": r.risk_score,
                "review_score": r.review_score,
                "bugs": [b.__dict__ for b in r.bugs],
                "security": [s.__dict__ for s in r.security],
                "suggestions": r.suggestions,
                "auto_fix_diff": r.auto_fix_diff,
                "language": r.language,
                "loc": r.loc,
            }
        raise RuntimeError("HTTP client required for this endpoint. pip install httpx")

    def analyze(self, code: str, language: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        return self._post("/v1/analyze", {"code": code, "language": language, "filename": filename})

    def analyze_file(self, path: str | Path) -> Dict[str, Any]:
        p = Path(path)
        return self.analyze(p.read_text(encoding="utf-8"), filename=str(p))

    def fix(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        return self._post("/v1/fix", {"code": code, "language": language})

    def review(self, diff: str, repo: Optional[str] = None) -> Dict[str, Any]:
        return self._post("/v1/review", {"diff": diff, "repo": repo})

    def review_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        # In production fetches PR diff from GitHub API
        mock_diff = f"diff --git a/src/app.py b/src/app.py\n+ # PR #{pr_number} in {repo}\n+ def new_feature(): pass\n"
        return self.review(mock_diff, repo=repo)

    def modernize(self, code: str, source: str, target: str) -> Dict[str, Any]:
        return self._post("/v1/modernize", {"code": code, "source": source, "target": target})

    def test_gen(self, code: str, language: Optional[str] = None, framework: str = "pytest") -> Dict[str, Any]:
        return self._post("/v1/test-gen", {"code": code, "language": language, "framework": framework})


# Convenience alias
Client = KV13Client

if __name__ == "__main__":
    # Demo without server: local engine
    c = KV13Client()
    result = c.analyze("def foo(x): return x/0", language="python")
    print(json.dumps(result, indent=2))
