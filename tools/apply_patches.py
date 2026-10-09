#!/usr/bin/env python3
"""Apply repair patches for a month and write blind/_patched.json for the Haiku re-check. usage: apply_patches.py <mid>"""
import json, sys
mid = sys.argv[1]; b = f"data/booklets/{mid}"
d = json.load(open(f"dashboard/data/{mid}.json", encoding="utf8")); p = json.load(open(f"{b}/patches.json", encoding="utf8"))
keep = {(k["quiz"], k["q"]) for k in json.load(open(f"{b}/keep_list.json"))} if True else set()
Q = {q["id"]: q for q in d["quizzes"]}
subs = [s for c in d["chapters"] for t in c["topics"] for s in t["subtopics"]]
changed_quiz, bad = set(), []
for f in p.get("passage_fixes", []):
    q = Q.get(f["quiz"])
    if not q or q["passage"].count(f["old"]) != 1: bad.append(("passage", f["quiz"], f["old"][:50])); continue
    q["passage"] = q["passage"].replace(f["old"], f["new"]).replace("  ", " "); changed_quiz.add(f["quiz"])
fact_changed = set()
for f in p.get("fact_fixes", []):
    hit = 0
    for s in subs:
        if f["old"] in s["summary"]: s["summary"] = s["summary"].replace(f["old"], f["new"]).replace("  ", " ").strip(); hit += 1; fact_changed.add(s["id"])
        for i, x in enumerate(s["facts"]):
            if f["old"] in x: s["facts"][i] = x.replace(f["old"], f["new"]).replace("  ", " ").strip(); hit += 1; fact_changed.add(s["id"])
    if not hit: bad.append(("fact", f["old"][:50]))
    for s in subs: s["facts"] = [x for x in s["facts"] if x]
rep_q = []
for r in p.get("replacements", []):
    q = Q.get(r["quiz"]); n = r["n"] - 1
    if not q or not (0 <= n < len(q["questions"])) or (r["quiz"], q["questions"][n]["q"]) not in keep: bad.append(("replacement", r["quiz"], r["n"])); continue
    new = r["question"]
    ans = str(new["options"][new["answer"]] if q["type"] == "MCQ" else new["answer"]).lower()
    if len(ans) > 2 and ans in q["passage"].lower(): bad.append(("answer in passage", r["quiz"], r["n"]))
    q["questions"][n] = new; rep_q.append({"id": r["quiz"], "n": r["n"], "q": new["q"], **({"options": new["options"]} if q["type"] == "MCQ" else {})}); changed_quiz.add(r["quiz"])
json.dump(d, open(f"dashboard/data/{mid}.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump({"passage_changes": [{"quiz": i, "passage": Q[i]["passage"]} for i in sorted(changed_quiz)],
           "facts": [{"title": s["title"], "summary": s["summary"], "facts": s["facts"]} for s in subs if s["id"] in fact_changed],
           "questions": rep_q}, open(f"{b}/blind/_patched.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(mid, "passages changed", len(changed_quiz), "facts subtopics", len(fact_changed), "replacements", len(rep_q), "PROBLEMS:", bad or "none")
