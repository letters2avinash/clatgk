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


import re, random
ROM = ["I", "II", "III", "IV"]; LET = "ABCD"
def parse_match(stem):
    lines = [re.sub(r"\s*\|\s*", "   ->   ", l.strip()) for l in stem.split("\n") if l.strip()]
    lines = [l for l in lines if not re.match(r"^List I\s*(->\s*List II)?$", l)]
    l1, l2 = {}, {}
    for l in lines[1:]:
        m = re.match(r"^(IV|III|II|I)\.\s+(.*?)(?:\s+->\s+([A-D])\.\s+(.*))?$", l)
        if m and not l.startswith("List"):
            l1[m.group(1)] = m.group(2).strip()
            if m.group(3): l2[m.group(3)] = m.group(4).strip()
            continue
        l = re.sub(r"^List II:?\s*", "", l)
        for mm in re.finditer(r"([A-D])\.\s+(.*?)(?=\s{2,}[A-D]\.|$)", l):
            l2[mm.group(1)] = mm.group(2).strip()
    return l1, l2
def fix_match(x, rnd):
    l1, l2 = parse_match(x["q"])
    if len(l1) != 4 or len(l2) != 4: return False
    om = re.findall(r"(IV|III|II|I)-([A-D])", x["options"][x["answer"]])
    if len(om) != 4: return False
    corr = dict(om)                       # roman -> letter (old letters)
    items = [l2[corr[r]] for r in ROM]    # item correctly paired with I..IV
    for _ in range(200):
        perm = list(range(4)); rnd.shuffle(perm)       # new letter j shows items[perm[j]]
        if sum(1 for j in range(4) if perm[j] == j) == 0: break
    shown = [items[perm[j]] for j in range(4)]
    newcorr = {ROM[perm[j]]: LET[j] for j in range(4)}  # roman perm[j] correct letter j
    def fmt(m): return ", ".join(f"{r}-{m[r]}" for r in ROM)
    correct = fmt(newcorr)
    opts = {correct}
    while len(opts) < 4:
        pl = list(LET); rnd.shuffle(pl); c = fmt(dict(zip(ROM, pl)))
        if c != correct and all(dict(zip(ROM, pl))[r] != LET[ROM.index(r)] for r in ROM[:0]): opts.add(c)
    others = sorted(o for o in opts if o != correct); rnd.shuffle(others)
    new = others[:]; new.insert(x["answer"], correct)
    rows = "\n".join(f"{r}. {l1[r]}   ->   {LET[j]}. {shown[j]}" for j, r in enumerate(ROM))
    x["q"] = "Match List I with List II:\n" + rows; x["options"] = new
    return True
rnd = random.Random(2026)
nfix = 0
for q in qz:
    if q["type"] != "MCQ": continue
    for x in q["questions"]:
        if x["q"].startswith("Match"):
            nfix += fix_match(x, rnd)
    for _ in range(5000):
        a = [x["answer"] for x in q["questions"]]
        run = any(a[i] == a[i+1] == a[i+2] for i in range(len(a)-2))
        cyc = any(((a[i+1]-a[i]) % 4 == 1 and (a[i+2]-a[i+1]) % 4 == 1 and (a[i+3]-a[i+2]) % 4 == 1) or
                  ((a[i]-a[i+1]) % 4 == 1 and (a[i+1]-a[i+2]) % 4 == 1 and (a[i+2]-a[i+3]) % 4 == 1) for i in range(len(a)-3))
        if not run and not cyc: break
        rnd.shuffle(q["questions"])
print("match questions normalised:", nfix)

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
