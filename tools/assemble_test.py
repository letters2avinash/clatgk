"""Assemble, balance, validate and render a test from verified passages.
Usage: assemble_test.py N [--title-extra TEXT]
Reads data/final/tNN_p1..p5.json, writes data/test_NN.json and out/CLAT_GK_Test_NN(.pdf|_Key.pdf)."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import balance_answers as b
import validate_test as v
import clat_gk_generator as g

n = int(sys.argv[1]); nn = f"{n:02d}"
root = os.path.join(os.path.dirname(__file__), "..")
ps, residual, miss = [], [], []
for k in range(1, 6):
    path = os.path.join(root, "data", "final", f"t{nn}_p{k}.json")
    if not os.path.exists(path):
        miss.append(k); continue
    p = json.load(open(path)); ps.append(p)
    for r in p.get("residual", []):
        residual.append(f"Passage {len(ps)}: {r}")
residual.append("Static-GK explanations cite Wikipedia or exam-prep pages in places where a primary text was not reachable.")
test = {"title": f"CLAT GK - Test {nn}", "date": "2026-10-08", "duration_minutes": 50, "marks_correct": 1, "marks_wrong": -0.25,
        "notes": "Generated with Haiku 5.5, then independently verified question by question by separate Sonnet agents using fresh searches (two-source rule; claims that could not be confirmed were removed or reworded; ambiguous, unchecked or overlapping questions were dropped). Several primary sources were unreachable, so residual risk is listed below. Not reviewed by a human.",
        "residual": residual, "passages": ps}
ok, seq, band = b.balance(test)
nq = sum(len(p["questions"]) for p in ps)
print(f"Test {nn}: {len(ps)} passages, {nq} questions, missing slots {miss}")
for i, p in enumerate(ps, 1):
    print(f"  P{i} {p.get('title','')[:60]} - {len(p['text'].split())} words, {len(p['questions'])} q")
if not ok:
    print("BALANCE FAILED", file=sys.stderr); sys.exit(1)
print("answers:", "".join("ABCD"[x] for x in seq), {c: seq.count(i) for i, c in enumerate("ABCD")}, band)
json.dump(test, open(os.path.join(root, "data", f"test_{nn}.json"), "w"), indent=1, ensure_ascii=False)
_, errs, warns = v.check(test)
for e in errs: print("ERROR", e)
for w in warns: print("WARN", w)
q = os.path.join(root, "out", f"CLAT_GK_Test_{nn}.pdf"); k = os.path.join(root, "out", f"CLAT_GK_Test_{nn}_Key.pdf")
g.build_pdf(test, q, mode="paper"); g.build_key_pdf(test, k)
print("rendered", q, k)
