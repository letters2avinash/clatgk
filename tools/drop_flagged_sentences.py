#!/usr/bin/env python3
"""Remove passage sentences flagged by a verdict file (closest sentence by word overlap). usage: drop_flagged_sentences.py <mid> <verdict.json>"""
import json, re, sys
mid, vf = sys.argv[1], sys.argv[2]
d = json.load(open(f"dashboard/data/{mid}.json", encoding="utf8")); v = json.load(open(vf, encoding="utf8"))
Q = {q["id"]: q for q in d["quizzes"]}
W = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))
done = 0
for f in v.get("passage_flags", []):
    q = Q.get(f["quiz"]);
    if not q: print("no quiz", f["quiz"]); continue
    sents = re.split(r"(?<=[.!?])\s+", q["passage"]); cw = W(f["claim"])
    if not cw: continue
    best = max(range(len(sents)), key=lambda i: len(W(sents[i]) & cw) / max(1, len(cw)))
    score = len(W(sents[best]) & cw) / len(cw)
    left = sum(len(s.split()) for i, s in enumerate(sents) if i != best)
    if score >= 0.5 and left >= 120:
        print(f"[{f['quiz']}] drop ({score:.2f}): {sents[best][:110]}"); del sents[best]; q["passage"] = " ".join(sents); done += 1
    else: print(f"[{f['quiz']}] KEPT (score {score:.2f}, words left {left}): {f['claim'][:90]}")
json.dump(d, open(f"dashboard/data/{mid}.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("dropped", done, "of", len(v.get("passage_flags", [])))
