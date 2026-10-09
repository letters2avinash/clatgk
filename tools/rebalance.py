"""Rebalance MCQ answer positions for a month by swapping options of plain direct questions.
Usage: python3 -I tools/rebalance.py <mid>   (do NOT run on 2026-01)"""
import json, re, sys, collections
mid = sys.argv[1]
assert mid != '2026-01'
p = f'dashboard/data/{mid}.json'
d = json.load(open(p))
REF = re.compile(r'\b(both|neither|only|all of|none of|above|I and|II and|III|statement|correct|either|any of|other)\b|^\s*[IVX]+[\.,]|^\s*\(?[A-D]\)?[\.\)] ', re.I)
def swappable(q):
    t = q['q']
    if re.search(r'assertion|match|consider|statement|following|how many|which of', t, re.I) and not re.search(r'^(Which|What|Who|Where|When|How)\b', t.strip()):
        pass
    if re.search(r'Assertion|Match|Consider the following|statements?|\n', t): return False
    if any(REF.search(o) for o in q['options']): return False
    return True
qs = [q for z in d['quizzes'] if z['type'] == 'MCQ' for q in z['questions']]
n = len(qs); target = n / 4
cnt = collections.Counter(q['answer'] for q in qs)
def bad(seq, i, v):
    s = seq[:i] + [v] + seq[i+1:]
    for k in range(max(0, i-3), min(len(s), i+4)):
        w = s[k:k+3]
        if len(w) == 3 and w[0] == w[1] == w[2]: return True
        w = s[k:k+5]
        if len(w) == 5 and all((w[j+1]-w[j]) % 4 == 1 for j in range(4)): return True
        if len(w) == 5 and all((w[j]-w[j+1]) % 4 == 1 for j in range(4)): return True
    return False
seq = [q['answer'] for q in qs]
moved = 0
for i, q in enumerate(qs):
    if not swappable(q): continue
    cur = q['answer']
    cands = sorted(range(4), key=lambda k: cnt[k])
    for k in cands:
        if cnt[k] >= cnt[cur] - 1 and k != cur: break
        if k == cur: break
        if bad(seq, i, k): continue
        o = q['options']; o[cur], o[k] = o[k], o[cur]
        q['answer'] = k; cnt[cur] -= 1; cnt[k] += 1; seq[i] = k; moved += 1
        break
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=1)
print(mid, 'moved', moved, dict(sorted(collections.Counter(q['answer'] for q in qs).items())))
