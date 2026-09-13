# KV-13 API Reference

Base URL: `http://localhost:8000` or `https://api.kv-13.netlify.app`

Interactive docs: `GET /docs` (Swagger), `GET /redoc`

## Authentication

Self-hosted: no auth required. Hosted: `Authorization: Bearer <api_key>` (demo key `kv13_demo_key` works).

## POST /v1/analyze

Full intelligence.

**Request**
```json
{
  "code": "def foo(x): return x/0",
  "language": "python",
  "filename": "src/app.py"
}
```

**Response 200**
```json
{
  "language": "python",
  "loc": 1,
  "risk_score": 92,
  "review_score": 34,
  "bugs": [{"type":"DivisionByZero","line":1,"severity":"critical","confidence":0.98,"explanation":"...","fix":"..."}],
  "security": [],
  "suggestions": ["Add input validation"],
  "auto_fix_diff": "--- before.py\n+++ after.py\n...",
  "model": "kv13-13b-instruct",
  "latency_ms": 42
}
```

## POST /v1/fix

**Request**
```json
{"code":"...","language":"python"}
```

**Response**
```json
{"original":"...","diff":"...","fixed_code":"...","bugs_fixed":1,"explanation":"Fixed 1 issue(s)"}
```

## POST /v1/review

**Request**
```json
{"diff":"diff --git a/src/app.py ...","repo":"kv-creates/my-app"}
```

**Response**
```json
{"summary":"...","score":72,"issues":[...],"suggestions":[...],"approved":false}
```

## POST /v1/modernize

**Request**
```json
{"code":"IDENTIFICATION DIVISION...","source":"cobol","target":"java17"}
```

**Response**
```json
{"source":"cobol","target":"java17","modernized_code":"public class...","behavior_preserved":true,"notes":"..."}
```

## POST /v1/test-gen

**Request**
```json
{"code":"def add(a,b): return a+b","language":"python","framework":"pytest"}
```

**Response**
```json
{"language":"python","framework":"pytest","tests":"import pytest...","coverage_estimate":89}
```

## GET /health

```json
{"status":"ok","version":"13.0.0","model":"kv13-13b-instruct-q4","uptime":123.4}
```

## Errors

- `400` empty code
- `422` validation error
- `500` internal

## Rate Limits (hosted)

- 60 req/min demo key
- 600 req/min paid

## SDK

```python
from kv13 import KV13Client
client = KV13Client(base_url="http://localhost:8000")
client.analyze("def foo(): return 1/0")
client.analyze_file("src/app.py")
client.fix("...")
client.review_pr("kv-creates/my-app", 42)
```

See `api/app.py:1` and `api/client.py:1`.
