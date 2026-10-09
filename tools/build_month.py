#!/usr/bin/env python3
"""Merge per-topic Haiku outputs into one dashboard month file and validate.
usage: python3 tools/build_month.py 2026-01 "January 2026" CLAT_Express__January_2026.pdf 100
"""
import json, sys, glob, os, collections
mid, label, src, pages = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
base = f"data/booklets/{mid}/out"
files = sorted(glob.glob(base + "/t*.json"))
chapters, mm, mn, qz, issues, checks = [], [], [], [], [], []
chap_idx = {}
pos = collections.Counter()

def err(f, m): issues.append(f"{os.path.basename(f)}: {m}")

for f in files:
    try: d = json.load(open(f, encoding="utf8"))
    except Exception as e: err(f, f"bad JSON {e}"); continue
    t = d["topic"]; ct = t.get("chapter_title", "General")
    if ct not in chap_idx:
        chap_idx[ct] = len(chapters)
        chapters.append({"id": f"{mid}-c{len(chapters)+1}", "title": ct, "topics": []})
    ch = chapters[chap_idx[ct]]
    tid = f"{ch['id']}-t{len(ch['topics'])+1}"
    subs = []
    for i, s in enumerate(t["subtopics"]):
        subs.append({"id": f"{tid}-s{i+1}", "title": s["title"], "summary": s.get("summary", ""),
                     "facts": s.get("facts", []), "keywords": s.get("keywords", [])})
    ch["topics"].append({"id": tid, "title": t["title"], "subtopics": subs})
    def ref(x):
        if x.get("scope") == "subtopic" or "subtopic_index" in x:
            i = x.get("subtopic_index", 0)
            return (subs[i]["id"] if i < len(subs) else subs[0]["id"]), "subtopic"
        return tid, "topic"
    k = os.path.basename(f)[:3]
    for j, m in enumerate(d.get("mindmaps", [])):
        r, sc = ref(m); mm.append({"id": f"mm-{k}-{j}", "scope": sc, "ref": r, "title": m["title"], "root": m["root"]})
    for j, m in enumerate(d.get("mnemonics", [])):
        r, sc = ref(m); mn.append({"id": f"mn-{k}-{j}", "scope": sc, "ref": r, "title": m["title"], "mnemonic": m["mnemonic"], "decode": m.get("decode", [])})
    for j, q in enumerate(d.get("quizzes", [])):
        sidx = min(q.get("subtopic_index", 0), len(subs) - 1)
        typ = q["type"]
        if len(q["questions"]) < 6: err(f, f"{typ} quiz has {len(q['questions'])} questions")
        for n, qq in enumerate(q["questions"]):
            if typ == "MCQ":
                o = qq["options"]
                if len(o) != 4 or len(set(o)) != 4: err(f, f"MCQ q{n+1} options not 4 distinct")
                if qq["answer"] not in (0, 1, 2, 3): err(f, f"MCQ q{n+1} bad answer idx")
                else: pos[qq["answer"]] += 1
            elif not str(qq.get("answer", "")).strip(): err(f, f"TITA q{n+1} empty answer")
        qz.append({"id": f"{'q' if typ=='MCQ' else 't'}-{k}-{j}", "type": typ, "ref": subs[sidx]["id"], "chapter": ch["id"],
                   "topic": tid, "subtopic": subs[sidx]["id"], "title": q["title"], "passage": q["passage"], "questions": q["questions"]})
    for c in d.get("needs_check", []): checks.append({"topic": t["title"], **c})

root = {"label": label, "children": [{"label": c["title"], "children": [{"label": t["title"]} for t in c["topics"]]} for c in chapters]}
mm.insert(0, {"id": f"mm-month", "scope": "month", "ref": mid, "title": f"{label} at a glance", "root": root})
for c in chapters:
    mm.insert(1, {"id": f"mm-{c['id']}", "scope": "chapter", "ref": c["id"], "title": c["title"],
                  "root": {"label": c["title"], "children": [{"label": t["title"], "children": [{"label": s["title"]} for s in t["subtopics"]]} for t in c["topics"]]}})
out = {"month": {"id": mid, "label": label, "source": src, "pages": pages}, "chapters": chapters,
       "mindmaps": mm, "mnemonics": mn, "quizzes": qz}
json.dump(out, open(f"dashboard/data/{mid}.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(checks, open(f"data/booklets/{mid}/needs_check.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("topics", sum(len(c['topics']) for c in chapters), "mindmaps", len(mm), "mnemonics", len(mn), "quizzes", len(qz),
      "MCQ answer positions", dict(sorted(pos.items())), "needs_check", len(checks))
print("\n".join(issues) or "no validation issues")
