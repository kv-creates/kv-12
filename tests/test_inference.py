import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from model.inference.engine import analyze_code, detect_language, modernize_code, generate_review

def test_division_by_zero():
    r = analyze_code("def foo(x): return x/0", "python")
    assert r.risk_score >= 70
    assert any(b.type == "DivisionByZero" for b in r.bugs)

def test_clean_code():
    code = '''def add(a:int,b:int)->int:\n    """Add two numbers."""\n    return a+b'''
    r = analyze_code(code, "python")
    assert r.risk_score < 50

def test_security():
    r = analyze_code("query = \"SELECT * FROM users WHERE id = \" + user", "python")
    assert any(b.type == "SQLInjection" for b in r.bugs)

def test_lang_detect():
    assert detect_language("def foo(): pass", "app.py") == "python"
    assert detect_language("function foo(){return 1}", "app.js") == "javascript"

def test_modernize():
    out = modernize_code("IDENTIFICATION DIVISION.", "cobol", "java17")
    assert "java" in out.lower() or "Modernized" in out

def test_review():
    r = generate_review("diff --git a/app.py")
    assert "summary" in r
