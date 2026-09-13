// KV-13 Browser Playground - mirrors model/inference/engine.py logic
const examples = {
  buggy: `def process_payment(user, amount):
    query = "SELECT * FROM users WHERE id = " + user
    result = eval(user)
    return amount / 0

# TODO: add validation`,
  clean: `from typing import Optional

def calculate_total(items: list[float], discount: Optional[float] = None) -> float:
    """Calculate total with optional discount."""
    if not items:
        return 0.0
    total = sum(items)
    if discount is not None:
        if not 0 <= discount <= 1:
            raise ValueError("discount must be 0-1")
        total *= (1 - discount)
    return round(total, 2)`,
  security: `import hashlib
import random

def auth(password):
    # Weak hash + weak random
    h = hashlib.md5(password.encode()).hexdigest()
    token = str(random.random())
    query = "SELECT * FROM users WHERE pw = '" + password + "'"
    return h, token`,
  legacy: `IDENTIFICATION DIVISION.
PROGRAM-ID. CALC-PAY.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 AMOUNT PIC 9(5).
PROCEDURE DIVISION.
    COMPUTE AMOUNT = AMOUNT / 0
    DISPLAY AMOUNT
    STOP RUN.`
};

const patterns = [
  {re: /\/\s*0/, type:"DivisionByZero", sev:"critical", conf:0.98, expl:"Unconditional division by zero."},
  {re: /eval\s*\(/, type:"CodeInjection", sev:"critical", conf:0.96, expl:"Use of eval() allows code injection."},
  {re: /SELECT.*\+/, type:"SQLInjection", sev:"high", conf:0.91, expl:"String concat in SQL — use parameterized queries."},
  {re: /password\s*=\s*['"]|pw\s*=\s*['"]/, type:"HardcodedSecret", sev:"high", conf:0.94, expl:"Hardcoded credential."},
  {re: /TODO|FIXME/, type:"TechDebt", sev:"low", conf:0.60, expl:"Tech debt marker."},
  {re: /md5|sha1\s*\(/, type:"WeakHash", sev:"high", conf:0.88, expl:"Broken hash — use SHA-256."},
  {re: /random\.random|Math\.random/, type:"WeakRandom", sev:"medium", conf:0.75, expl:"Weak PRNG for security context."},
];

function analyze(code, lang){
  const lines = code.split("\n");
  const loc = lines.filter(l=>l.trim()).length;
  let bugs=[], risk=10;
  lines.forEach((line,i)=>{
    patterns.forEach(p=>{
      if(p.re.test(line)){
        bugs.push({line:i+1, type:p.type, severity:p.sev, confidence:p.conf, explanation:p.expl});
        risk += p.sev==="critical"?55: p.sev==="high"?25: p.sev==="medium"?12:7;
      }
    });
  });
  risk = Math.min(100, risk + bugs.length*8);
  let review = Math.max(0, 100 - risk + (code.includes('"""')?5:0) + (code.includes('assert')?10:0));
  let suggestions=[];
  if(bugs.length) suggestions.push(`Fix ${bugs.length} bug(s) before merging`);
  if(!code.includes('"""') && !code.includes("'''")) suggestions.push("Add docstring for public functions");
  if(!code.includes("try:")) suggestions.push("Add error handling for external inputs");
  if(!suggestions.length) suggestions.push("Code looks clean — add property-based tests.");
  let diff = bugs.length ? `--- before.py\n+++ after.py\n@@\n+# KV-13 Auto-Fix: guarded ${bugs.length} issue(s)\n ` + code.split("\n").slice(0,4).join("\n ") : "# No diff needed - code is clean";
  return {risk, review, bugs, suggestions, diff, loc, lang};
}

function render(result){
  document.getElementById("riskVal").textContent = result.risk + "/100";
  document.getElementById("riskVal").style.color = result.risk>70?"#FF3B30": result.risk>40?"#FFD21E":"#00FF88";
  document.getElementById("riskBar").style.width = result.risk+"%";
  document.getElementById("reviewVal").textContent = result.review + "/100";
  document.getElementById("langVal").textContent = result.lang;
  const bugsPanel = document.getElementById("bugsPanel");
  bugsPanel.innerHTML = result.bugs.length ? result.bugs.map(b=>`
    <div class="bug ${b.severity}">
      <b>${b.type}</b> <span style="float:right;font-size:11px;opacity:.8">${b.severity} • ${b.confidence.toFixed(2)}</span>
      <div style="font-size:12px;margin-top:4px">Line ${b.line}: ${b.explanation}</div>
    </div>
  `).join("") : `<div style="padding:10px;border:1px solid var(--border);border-radius:12px;background:rgba(0,255,136,.08);margin:8px 0;color:var(--green)">No bugs detected — code is clean!</div>`;
  document.getElementById("suggestionsPanel").innerHTML = `<div style="font-weight:700;font-size:12px;margin-bottom:6px">Suggestions</div>` + result.suggestions.map(s=>`<div style="font-size:12px;padding:6px 8px;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:8px;margin:4px 0">• ${s}</div>`).join("");
  document.getElementById("diffPanel").textContent = result.diff;
}

document.getElementById("analyzeBtn").addEventListener("click", ()=>{
  const code = document.getElementById("codeInput").value;
  const lang = document.querySelector(".tab.active")?.dataset.lang || "python";
  const r = analyze(code, lang);
  render(r);
});
document.querySelectorAll(".tab").forEach(t=>{
  t.addEventListener("click", ()=>{
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    document.getElementById("langVal").textContent = t.dataset.lang;
  });
});
document.getElementById("exampleSelect").addEventListener("change", (e)=>{
  document.getElementById("codeInput").value = examples[e.target.value];
});
// auto-run on load
window.addEventListener("load", ()=> document.getElementById("analyzeBtn").click());
