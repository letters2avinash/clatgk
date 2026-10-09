#!/usr/bin/env python3
"""Apply blind-verification verdicts (verdict/xNN.json) to the extra quizzes in dashboard/data/<mid>.json.
Drops disagreeing/flagged questions, drops flagged passage sentences, removes quizzes that fall below 6 questions.
usage: extra_apply.py <mid>"""
import json, glob, re, sys, os, collections
sys.argv_saved = sys.argv; mid = sys.argv[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apply_verdict.py"), encoding="utf8").read()
# reuse helper functions (norm, tita_match, match_pairs, ROW, BAD) from apply_verdict without running its main body
head = src[:src.index("report = collections.defaultdict")]
head = head.replace('path = f"dashboard/data/{mid}.json"', 'path = f"dashboard/data/{mid}.json"')
exec(head)
W = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))
report = collections.defaultdict(list)
done_p = f"data/booklets/{mid}/verdict/applied_x.json"
done = set(json.load(open(done_p))) if os.path.exists(done_p) else set()
new_done = set()
for f in sorted(glob.glob(f"data/booklets/{mid}/verdict/x[0-9]*.json")):
    if os.path.basename(f) in done: continue
    new_done.add(os.path.basename(f))
    v = json.load(open(f, encoding="utf8")); bl = json.load(open(f.replace("/verdict/", "/blind/"), encoding="utf8"))
    BQ = {b["id"]: {x["n"]: x["q"] for x in b["questions"]} for b in bl["quizzes"]}
    BO = {b["id"]: {x["n"]: x.get("options") for x in b["questions"]} for b in bl["quizzes"]}
    for vq in v["quizzes"]:
        q = Q.get(vq["id"])
        if not q: report["unknown quiz"].append(vq["id"]); continue
        pos = {x["q"]: k for k, x in enumerate(q["questions"])}; drop = {}
        for r in vq["questions"]:
            txt = BQ.get(vq["id"], {}).get(r["n"])
            if txt not in pos and txt and txt.startswith("Match"):
                sig = lambda t: frozenset(g for l in t.split("\n") if (mm := ROW.match(l.strip())) for g in (mm.group(2), mm.group(4)))
                cand = [k for k, y in enumerate(q["questions"]) if y["q"].startswith("Match") and sig(y["q"]) == sig(txt)]
                if len(cand) == 1: pos[txt] = cand[0]
            if txt not in pos: report["not found"].append((vq["id"], r["n"])); continue
            i = pos[txt]; x = q["questions"][i]; why = []
            if not r.get("supported", True): why.append("unsupported")
            why += [s for s in r.get("issues", []) if s.startswith(BAD) or s.startswith("other")]
            if q["type"] == "MCQ":
                ok = r["my_answer"] == x["answer"]; bopts = BO.get(vq["id"], {}).get(r["n"])
                if x["q"].startswith("Match") and isinstance(r["my_answer"], int) and bopts:
                    vp = match_pairs(txt, bopts[r["my_answer"]]); sp = match_pairs(x["q"], x["options"][x["answer"]]); ok = vp is not None and vp == sp
                if not ok: why.append("answer mismatch")
            elif not tita_match(x["answer"], x.get("accept"), r["my_answer"]): why.append("answer mismatch")
            if why: drop[i] = why
        for i, w in drop.items(): report["dropped"].append((q["id"], i + 1, w))
        q["questions"] = [x for i, x in enumerate(q["questions"]) if i not in drop]
        for pf in vq.get("passage_flags", []):
            sents = re.split(r"(?<=[.!?])\s+", q["passage"]); cw = W(pf["claim"])
            if not cw: continue
            best = max(range(len(sents)), key=lambda i: len(W(sents[i]) & cw) / max(1, len(cw)))
            score = len(W(sents[best]) & cw) / len(cw); left = sum(len(s.split()) for i, s in enumerate(sents) if i != best)
            if score >= 0.5 and left >= 100: del sents[best]; q["passage"] = " ".join(sents); report["passage sentence dropped"].append(q["id"])
            else: report["passage flag KEPT"].append((q["id"], round(score, 2), left)); q["_flagged"] = q.get("_flagged", 0) + 1
before = len([q for q in d["quizzes"] if "-x" in q["id"]])
keep = []
for q in d["quizzes"]:
    if "-x" in q["id"]:
        if len(q["questions"]) < 6: report["quiz removed (<6 questions)"].append(q["id"]); continue
        if q.pop("_flagged", 0) >= 2: report["quiz removed (unfixable passage flags)"].append(q["id"]); continue
        q.pop("_flagged", None)
    keep.append(q)
d["quizzes"] = keep
json.dump(d, open(path, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(sorted(done | new_done), open(done_p, "w"))
for k, vv in report.items(): print(f"== {k}: {len(vv)}")
print("extra quizzes", before, "->", len([q for q in d["quizzes"] if "-x" in q["id"]]), "| extra questions", sum(len(q["questions"]) for q in d["quizzes"] if "-x" in q["id"]))
