#!/usr/bin/env python3
"""Split data/booklets/<mid>/full.txt into per-topic files using topics.json. usage: split_topics.py <mid>"""
import json, re, sys, os
mid = sys.argv[1]; b = f"data/booklets/{mid}"
t = open(f"{b}/full.txt", encoding="utf8").read()
parts = re.split(r"=== PAGE (\d+) ===", t); P = {int(parts[i]): parts[i+1] for i in range(1, len(parts), 2)}
topics = json.load(open(f"{b}/topics.json")); os.makedirs(f"{b}/out", exist_ok=True)
for x in topics:
    s = "".join(f"=== PAGE {p} ===\n{P.get(p, '')}\n" for p in range(x["start"], x["end"] + 1))
    open(f"{b}/{x['key']}.txt", "w", encoding="utf8").write(s)
print(mid, len(topics), "topics;", " ".join(f"{x['key'].split('_')[0]}:{len(open(f'{b}/{x[chr(107)+chr(101)+chr(121)]}.txt').read())//1000}k" for x in topics))
