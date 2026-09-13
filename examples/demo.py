"""KV-13 Demo - 4 tasks"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.inference.engine import analyze_code

# 1. Bug detection
print("=== 1. Bug Detection ===")
print(analyze_code("def foo(x): return x/0", "python").bugs[0].__dict__)

# 2. Security
print("\n=== 2. Security ===")
r = analyze_code('query = "SELECT * FROM t WHERE id = " + user', "python")
print(r.bugs)

# 3. Client SDK
print("\n=== 3. SDK (offline) ===")
from api.client import KV13Client
c = KV13Client()
print(c.analyze("import hashlib; h=hashlib.md5(pw.encode())", language="python"))

# 4. Legacy modernize
print("\n=== 4. Modernize ===")
from model.inference.engine import modernize_code
print(modernize_code("IDENTIFICATION DIVISION.", "cobol", "java17")[:200])
