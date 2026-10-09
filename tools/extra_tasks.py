#!/usr/bin/env python3
"""List subtopics without a quiz and write per-topic task files for the extra-quiz writers.
usage: extra_tasks.py <mid>   -> data/booklets/<mid>/extra/tasks/xNN.json"""
import json, sys, os, re, glob
mid = sys.argv[1]
d = json.load(open(f"dashboard/data/{mid}.json", encoding="utf8"))
have = {q["subtopic"] for q in d["quizzes"] if "-x" not in q["id"]}
texts = {os.path.basename(f).split("_")[0]: os.path.basename(f) for f in glob.glob(f"data/booklets/{mid}/t[0-9][0-9]_*.txt")}
os.makedirs(f"data/booklets/{mid}/extra/tasks", exist_ok=True); os.makedirs(f"data/booklets/{mid}/extra/out", exist_ok=True)
tn = {}
for q in d["quizzes"]:
    if "-x" in q["id"]: continue
    tn.setdefault(q["topic"], q["id"].split("-")[1])          # tNN
n = 0
for c in d["chapters"]:
    for t in c["topics"]:
        unc = [s for s in t["subtopics"] if s["id"] not in have]
        if not unc: continue
        key = tn[t["id"]]; x = "x" + key[1:]
        asked = [qq["q"].split("\n")[0] for q in d["quizzes"] if q["topic"] == t["id"] and "-x" not in q["id"] for qq in q["questions"]]
        json.dump({"key": x, "topic": t["title"], "chapter": c["title"], "text_file": f"data/booklets/{mid}/{texts[key]}",
                   "subtopics": [{"id": s["id"], "title": s["title"], "summary": s["summary"], "facts": s["facts"]} for s in unc],
                   "already_asked": asked}, open(f"data/booklets/{mid}/extra/tasks/{x}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        n += 1
print(mid, "tasks:", n, "uncovered subtopics:", sum(1 for c in d["chapters"] for t in c["topics"] for s in t["subtopics"] if s["id"] not in have))
