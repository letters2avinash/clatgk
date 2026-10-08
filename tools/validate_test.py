"""Validate a CLAT GK test JSON (docs/clat_gk_schema.md). Usage: validate_test.py test.json"""
import json, re, sys
TYPES = {"direct", "assertion_reason", "match", "statement_two", "statement_multi", "statement_count"}

def check(data):
    errs, warns = [], []
    nq = 0
    for pi, p in enumerate(data["passages"], 1):
        words = len(p["text"].split())
        if words < 120:
            warns.append(f"P{pi}: passage is {words} words (very short)")
        if not p.get("sources"):
            errs.append(f"P{pi}: no passage sources")
        qs = p["questions"]
        if len(qs) not in (5, 6):
            errs.append(f"P{pi}: {len(qs)} questions, expected 5-6")
        elif len(qs) == 5:
            warns.append(f"P{pi}: only 5 questions (one slot dropped in verification)")
        types = [q["type"] for q in qs]
        if len(set(types)) < 4:
            warns.append(f"P{pi}: only {len(set(types))} distinct question types")
        for qi, q in enumerate(qs, 1):
            nq += 1
            tag = f"P{pi}Q{qi}"
            t = q.get("type")
            if t not in TYPES:
                errs.append(f"{tag}: bad type {t}"); continue
            if not q.get("explanation"): errs.append(f"{tag}: no explanation")
            if not str(q.get("source", "")).startswith("http"): errs.append(f"{tag}: no source URL")
            a = q.get("answer")
            if t in ("direct", "match", "statement_multi"):
                if len(q.get("options", [])) != 4: errs.append(f"{tag}: needs 4 options")
                if len(set(q.get("options", []))) != len(q.get("options", [])): errs.append(f"{tag}: duplicate options")
            if t == "match" and (len(q["list1"]) != 4 or len(q["list2"]) != 4): errs.append(f"{tag}: match lists must have 4 rows")
            if t == "statement_two" and len(q["statements"]) != 2: errs.append(f"{tag}: needs exactly 2 statements")
            if t in ("statement_multi", "statement_count") and not 2 <= len(q["statements"]) <= 4: errs.append(f"{tag}: 2-4 statements")
            if t == "statement_count" and q.get("mode") not in ("correct", "incorrect"): errs.append(f"{tag}: mode must be correct/incorrect")
            if not isinstance(a, int) or not 0 <= a <= 3: errs.append(f"{tag}: answer must be 0-3")
            # RC-leak heuristic: correct option text copied from the passage
            if t == "direct" and isinstance(a, int) and 0 <= a < len(q["options"]):
                opt = q["options"][a].lower().strip()
                if len(opt) > 12 and opt in p["text"].lower():
                    warns.append(f"{tag}: correct option appears verbatim in passage (RC-style leak?)")
    import collections
    dist = collections.Counter(q["answer"] for p in data["passages"] for q in p["questions"])
    if nq >= 20:
        for i in range(4):
            share = dist.get(i, 0) / nq
            if share > 0.4 or share < 0.1:
                warns.append(f"answer position {'ABCD'[i]} is {share:.0%} of answers (aim for 15-35% each)")
    return nq, errs, warns

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    n, e, w = check(d)
    print(f"{n} questions, {len(e)} errors, {len(w)} warnings")
    for x in e: print("ERROR", x)
    for x in w: print("WARN ", x)
    sys.exit(1 if e else 0)
