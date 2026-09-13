from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_analyze():
    r = client.post("/v1/analyze", json={"code":"def foo(x): return x/0","language":"python"})
    assert r.status_code == 200
    assert r.json()["risk_score"] >= 70

def test_fix():
    r = client.post("/v1/fix", json={"code":"x/0","language":"python"})
    assert r.status_code == 200
    assert "diff" in r.json()

def test_modernize():
    r = client.post("/v1/modernize", json={"code":"old","source":"cobol","target":"java17"})
    assert r.status_code == 200

def test_empty_code():
    r = client.post("/v1/analyze", json={"code":"   ","language":"python"})
    assert r.status_code == 400
