#!/usr/bin/env python3
"""Apply blind-verification verdicts (Haiku) to dashboard/data/<month>.json. usage: apply_verdict.py 2026-01"""
import json, glob, re, sys, collections
mid = sys.argv[1]
path = f"dashboard/data/{mid}.json"
d = json.load(open(path, encoding="utf8"))
Q = {q["id"]: q for q in d["quizzes"]}
def norm(s):
    s = str(s).lower().replace(",", "")
    s = re.sub(r"\b(per ?cent|percent|percentage|billion|bn|usd|us|the|a|an|of)\b", " ", s)
    return re.sub(r"[^a-z0-9. ]+", " ", s).split()
def tita_match(stored, accept, mine):
    m = " ".join(norm(mine))
    for a in [stored] + list(accept or []):
        n = " ".join(norm(a))
        if n and (n == m or n in m or m in n and m): return True
    return False

ROW = re.compile(r"^(IV|III|II|I)\.\s+(.*?)\s+->\s+([A-D])\.\s+(.*)$")
def match_pairs(stem, opt):
    r1, r2 = {}, {}
    for l in stem.split("\n"):
        m = ROW.match(l.strip())
        if m: r1[m.group(1)] = m.group(2).strip(); r2[m.group(3)] = m.group(4).strip()
    try: return {(r1[a], r2[b]) for a, b in re.findall(r"(IV|III|II|I)-([A-D])", opt)}
    except KeyError: return None
BAD = ("ambiguous", "multiple_correct", "no_correct_option", "answer_stated_in_passage", "garbled_basis")
report = collections.defaultdict(list); passage_flags = []; fact_flags = []; keeplist = []
for f in sorted(glob.glob(f"data/booklets/{mid}/verdict/t*.json")):
    v = json.load(open(f, encoding="utf8"))
    bl = json.load(open(f.replace("/verdict/", "/blind/"), encoding="utf8"))
    BQ = {b["id"]: {x["n"]: x["q"] for x in b["questions"]} for b in bl["quizzes"]}
    BO = {b["id"]: {x["n"]: x.get("options") for x in b["questions"]} for b in bl["quizzes"]}   # question text exactly as the verifier saw it
    for vq in v["quizzes"]:
        q = Q.get(vq["id"])
        if not q: report["unknown quiz"].append(vq["id"]); continue
        drop = {}
        pos = {x["q"]: k for k, x in enumerate(q["questions"])}
        for r in vq["questions"]:
            txt = BQ.get(vq["id"], {}).get(r["n"])
            if txt not in pos: report["question text not found (skipped)"].append((vq["id"], r["n"])); continue
            i = pos[txt]
            x = q["questions"][i]; why = []
            if not r.get("supported", True): why.append("unsupported")
            iss = [s for s in r.get("issues", []) if s.startswith(BAD) or s.startswith("other")]
            why += iss
            if q["type"] == "MCQ":
                ok = r["my_answer"] == x["answer"]
                bopts = BO.get(vq["id"], {}).get(r["n"])
                if x["q"].startswith("Match") and isinstance(r["my_answer"], int) and bopts:
                    vp = match_pairs(txt, bopts[r["my_answer"]]); sp = match_pairs(x["q"], x["options"][x["answer"]])
                    ok = vp is not None and vp == sp
                if not ok: why.append(f"answer mismatch (verifier {r['my_answer']} vs stored {x['answer']})")
            elif not tita_match(x["answer"], x.get("accept"), r["my_answer"]):
                why.append(f"answer mismatch (verifier '{r['my_answer']}' vs stored '{x['answer']}')")
            if why: drop[i] = why
        # keep >= 6: if too many drops, keep the least-flagged ones
        n = len(q["questions"])
        if n - len(drop) < 6:
            keep = sorted(drop, key=lambda k: (any("mismatch" in w or "unsupported" in w for w in drop[k]), len(drop[k])))[: 6 - (n - len(drop))]
            for k in keep:
                report["kept despite flags (quiz would fall below 6)"].append((q["id"], k + 1, drop[k])); keeplist.append({"quiz": q["id"], "q": q["questions"][k]["q"], "issues": drop.pop(k)})
        for i, w in drop.items(): report["dropped"].append((q["id"], i + 1, q["questions"][i]["q"][:70].replace("\n", " "), w))
        q["questions"] = [x for i, x in enumerate(q["questions"]) if i not in drop]
        for pf in vq.get("passage_flags", []): passage_flags.append({"quiz": q["id"], **pf})
    for ff in v.get("fact_flags", []): fact_flags.append({"file": f.split("/")[-1], **ff})
# answer-position / pattern re-check after drops
import random
rnd = random.Random(7)
for q in d["quizzes"]:
    if q["type"] != "MCQ": continue
    for _ in range(5000):
        a = [x["answer"] for x in q["questions"]]
        run = any(a[i] == a[i+1] == a[i+2] for i in range(len(a)-2))
        cyc = any(all((a[i+j+1]-a[i+j]) % 4 == 1 for j in range(3)) or all((a[i+j]-a[i+j+1]) % 4 == 1 for j in range(3)) for i in range(len(a)-3))
        if not run and not cyc: break
        rnd.shuffle(q["questions"])
json.dump(d, open(path, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(keeplist, open(f"data/booklets/{mid}/keep_list.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump({"passage_flags": passage_flags, "fact_flags": fact_flags}, open(f"data/booklets/{mid}/repair_list.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for k, v in report.items():
    print(f"== {k}: {len(v)}")
    for row in v: print("  ", row)
print("passage flags", len(passage_flags), "fact flags", len(fact_flags))
print("questions now:", sum(len(q["questions"]) for q in d["quizzes"]))
