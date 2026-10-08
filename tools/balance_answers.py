"""Balance answer positions in a CLAT GK test and reject cyclic patterns.
Usage: balance_answers.py test.json [--check]
Shuffles options only where that cannot change meaning (direct, match, statement_multi without
'above'/'both'/'all of'/'none of' options, and no option letter quoted in the explanation).
Assertion-reason, statement_two and statement_count have fixed option frames: their positions are
set by content, so the shufflable questions are placed to even out the totals.
Rules enforced on the final 1..N answer sequence:
  - each of A-D is 20-30% of answers (when N >= 20); falls back to 15-35% and says so
  - no 3 identical answers in a row
  - no 3 consecutive answers stepping by +1 or -1 around A-B-C-D (ABC, BCD, CDA, DAB, DCB, CBA, BAD, ADC)
  - (strict tier, tried first) no 4 consecutive answers that are all different, e.g. ABCD, DBCA
  - no window of 4 immediately repeated (e.g. ABAB..., ABCDABCD)
"""
import json, random, re, sys, hashlib

BAD_OPT = re.compile(r"\b(above|both|all of|none of|neither)\b", re.I)
PIN = re.compile(r"\b(all|none) of the above\b", re.I)


def pinned_idx(q):
    return [i for i, o in enumerate(q["options"]) if PIN.search(o)]
LETTER_REF = re.compile(r"\(([A-D])\)|\boption ([A-D])\b", re.I)

def shufflable(q):
    t = q["type"]
    if t not in ("direct", "match", "statement_multi"):
        return False
    if any(BAD_OPT.search(o) and not PIN.search(o) for o in q["options"]):
        return False
    if q["answer"] in pinned_idx(q):
        return False
    if LETTER_REF.search(q.get("explanation", "")):
        return False
    return True

def violations(seq, band=(0.2, 0.3), strict=False):
    n = len(seq); out = []
    for i in range(n - 2):
        a, b, c = seq[i:i + 3]
        if a == b == c: out.append(f"3 identical at Q{i+1}")
        if (b - a) % 4 == 1 and (c - b) % 4 == 1: out.append(f"ascending cycle at Q{i+1}")
        if (b - a) % 4 == 3 and (c - b) % 4 == 3: out.append(f"descending cycle at Q{i+1}")
    if strict:
        for i in range(n - 3):
            if len(set(seq[i:i + 4])) == 4:
                out.append(f"four different answers in a row at Q{i+1}")
    for i in range(n - 7):
        if seq[i:i + 4] == seq[i + 4:i + 8]: out.append(f"repeated 4-block at Q{i+1}")
    if n >= 20:
        for k in range(4):
            share = seq.count(k) / n
            if not band[0] <= share <= band[1]: out.append(f"{'ABCD'[k]} is {share:.0%}")
    return out

def flat(data):
    return [q for p in data["passages"] for q in p["questions"]]

def balance(data, tries=200000):
    """Try option shuffling first; if the fixed-frame answers force a violation, also
    permute question order inside passages (then passage order) and retry."""
    import copy
    seq = [q["answer"] for q in flat(data)]
    for strict in (True, False):
        for band in ((0.2, 0.3), (0.15, 0.35)):
            ok, seq = _balance(data, tries, band, strict)
            if ok:
                return True, seq, (band, "strict" if strict else "loose")
    rng = random.Random(99)
    orig = copy.deepcopy(data["passages"])
    for attempt in range(400):
        data["passages"] = copy.deepcopy(orig)
        for p in data["passages"]:
            rng.shuffle(p["questions"])
        if attempt % 2:
            rng.shuffle(data["passages"])
        for strict in (True, False):
            for band in ((0.2, 0.3), (0.15, 0.35)):
                ok, seq = _balance(data, 3000, band, strict)
                if ok:
                    return True, seq, (band, ("strict" if strict else "loose") + "+reordered")
    data["passages"] = orig
    return False, seq, None


def _balance(data, tries, band, strict):
    qs = flat(data)
    seed = int(hashlib.sha256(data["title"].encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    free = [i for i, q in enumerate(qs) if shufflable(q)]
    base = [q["answer"] for q in qs]
    best = None
    for _ in range(tries):
        seq = base[:]
        for i in free:
            seq[i] = rng.randrange(4 - len(pinned_idx(qs[i])))
        v = violations(seq, band, strict)
        if not v:
            best = seq; break
    if best is None:
        return False, base
    for i in free:
        q = qs[i]; target = best[i]
        opts = q["options"]; right = opts[q["answer"]]
        pins = [opts[j] for j in pinned_idx(q)]
        order = list(range(4)); rng.shuffle(order)
        others = [opts[j] for j in order if opts[j] != right and opts[j] not in pins]
        new = others[:target] + [right] + others[target:] + pins
        q["options"] = new; q["answer"] = target
    return True, best

if __name__ == "__main__":
    path = sys.argv[1]
    data = json.load(open(path))
    if "--check" in sys.argv:
        seq = [q["answer"] for q in flat(data)]
        v = violations(seq)
        print("".join("ABCD"[x] for x in seq)); print("OK" if not v else v); sys.exit(1 if v else 0)
    ok, seq, band = balance(data)
    print("".join("ABCD"[x] for x in seq))
    if not ok:
        print("FAILED: could not satisfy rules; fixed-frame questions force a violation", file=sys.stderr); sys.exit(1)
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    print("balanced:", {c: seq.count(i) for i, c in enumerate("ABCD")}, "band", band)
