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
