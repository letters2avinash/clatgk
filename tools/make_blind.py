#!/usr/bin/env python3
"""Write answer-free blind verification inputs from dashboard/data/<mid>.json. usage: make_blind.py <mid>"""
import json, sys, os, collections
mid = sys.argv[1]; d = json.load(open(f"dashboard/data/{mid}.json", encoding="utf8"))
subs = {s["id"]: s for c in d["chapters"] for t in c["topics"] for s in t["subtopics"]}
os.makedirs(f"data/booklets/{mid}/blind", exist_ok=True); os.makedirs(f"data/booklets/{mid}/verdict", exist_ok=True)
groups = collections.OrderedDict()
for q in d["quizzes"]: groups.setdefault(q["id"].split("-")[1], []).append(q)   # q-tNN-j -> tNN
tops = {}
for c in d["chapters"]:
    for t in c["topics"]: tops.setdefault(t["id"], t)
for k, qs in groups.items():
    tid = qs[0]["topic"]; t = tops[tid]
    blind = {"topic": t["title"], "subtopics": [{"i": i, "title": s["title"], "summary": s["summary"], "facts": s["facts"]} for i, s in enumerate(t["subtopics"])],
             "quizzes": [{"id": q["id"], "type": q["type"], "passage": q["passage"],
                          "questions": [({"n": i+1, "q": x["q"], "options": x["options"]} if q["type"] == "MCQ" else {"n": i+1, "q": x["q"]}) for i, x in enumerate(q["questions"])]} for q in qs]}
    json.dump(blind, open(f"data/booklets/{mid}/blind/{k}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(mid, "blind files:", len(groups), "questions:", sum(len(q["questions"]) for q in d["quizzes"]))
