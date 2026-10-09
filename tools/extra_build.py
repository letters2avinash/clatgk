#!/usr/bin/env python3
"""Merge extra-quiz writer output (extra/out/xNN.json) into dashboard/data/<mid>.json. Idempotent (replaces earlier extras).
usage: extra_build.py <mid>"""
import json, sys, glob, os, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matchfix import fix_match
mid = sys.argv[1]; p = f"dashboard/data/{mid}.json"
d = json.load(open(p, encoding="utf8"))
d["quizzes"] = [q for q in d["quizzes"] if "-x" not in q["id"]]
sub = {}
for c in d["chapters"]:
    for t in c["topics"]:
        for s in t["subtopics"]: sub[s["id"]] = (c["id"], t["id"])
rnd = random.Random(31); issues = []; nq = 0
for f in sorted(glob.glob(f"data/booklets/{mid}/extra/out/x*.json")):
    key = os.path.basename(f)[:-5]
    try: w = json.load(open(f, encoding="utf8"))
    except Exception as e: issues.append(f"{key}: bad json {e}"); continue
    cnt = {"MCQ": 0, "TITA": 0}
    for z in w.get("quizzes", []):
        typ = z.get("type"); sid = z.get("subtopic")
        if typ not in cnt or sid not in sub: issues.append(f"{key}: bad quiz type/subtopic {typ} {sid}"); continue
        qs = z.get("questions", [])
        okq = []
        for x in qs:
            if typ == "MCQ":
                if not (isinstance(x.get("options"), list) and len(x["options"]) == 4 and len(set(x["options"])) == 4 and x.get("answer") in (0, 1, 2, 3) and x.get("q")): issues.append(f"{key}: bad MCQ"); continue
                if x["q"].startswith("Match") and not fix_match(x, rnd): issues.append(f"{key}: match not normalisable, dropped"); continue
            elif not (x.get("q") and str(x.get("answer", "")).strip()): issues.append(f"{key}: bad TITA"); continue
            okq.append(x)
        if len(okq) < 6 or len(str(z.get("passage", "")).split()) < 120: issues.append(f"{key}: quiz too small {sid} {typ}"); continue
        for _ in range(5000):
            a = [x["answer"] for x in okq] if typ == "MCQ" else [0]
            run = any(a[i] == a[i+1] == a[i+2] for i in range(len(a)-2))
            cyc = any(all((a[i+j+1]-a[i+j]) % 4 == 1 for j in range(3)) or all((a[i+j]-a[i+j+1]) % 4 == 1 for j in range(3)) for i in range(len(a)-3))
            if not run and not cyc: break
            rnd.shuffle(okq)
        cnt[typ] += 1
        ch, tp = sub[sid]
        d["quizzes"].append({"id": f"{'q' if typ=='MCQ' else 't'}-{key}-{len(d['quizzes'])}", "type": typ, "ref": sid, "chapter": ch, "topic": tp,
                             "subtopic": sid, "title": z.get("title", ""), "passage": z["passage"], "questions": okq}); nq += len(okq)
json.dump(d, open(p, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print(mid, "extra quizzes:", sum(1 for q in d["quizzes"] if "-x" in q["id"]), "questions", nq); print("\n".join(issues) or "no issues")
