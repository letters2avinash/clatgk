#!/usr/bin/env python3
"""Build the CLAT CURRENT AFFAIR MEGA SHEET PDF from the dashboard data.
Every MCQ passage with its questions, then the answer key at the end.
All navigation is internal PDF links (contents, previous/next passage, question <-> answer key).
usage: python3 -I tools/build_mega_sheet.py <out.pdf>      (needs playwright + chromium)
"""
import json, html, sys, os
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
BASE = "dashboard/data"
idx = json.load(open(f"{BASE}/index.json", encoding="utf8"))
passages = []   # (num, month_label, month_id, chapter, topic, quiz)
for m in idx["months"]:
    d = json.load(open(f"{BASE}/{m['file']}", encoding="utf8"))
    ch = {c["id"]: c["title"] for c in d["chapters"]}
    tp = {t["id"]: t for c in d["chapters"] for t in c["topics"]}
    for z in d["quizzes"]:
        if z["type"] != "MCQ":
            continue
        t = tp.get(z["topic"], {})
        for k, q in enumerate(z["questions"]):
            assert len(q["options"]) == 4 and 0 <= q["answer"] <= 3, (z["id"], k)
        passages.append(dict(month=d["month"]["label"], chapter=ch.get(z["chapter"], ""), topic=t.get("title", z["title"]),
                             title=z["title"], passage=z["passage"], questions=z["questions"], n=len(passages) + 1, mid=m["id"], zid=z["id"]))

esc = lambda s: html.escape(str(s), quote=True).replace("\n", "<br>")
def pid(p): return f"p{p['n']}"
def qid(p, k): return f"q{p['n']}-{k+1}"
def aid(p, k): return f"a{p['n']}-{k+1}"
L = "ABCD"
total_q = sum(len(p["questions"]) for p in passages)

css = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
body { font-family: 'Lato', 'Helvetica Neue', Arial, sans-serif; color:#1d1d24; font-size:10.5pt; line-height:1.5; }
h1 { font-family: Georgia, serif; font-size:30pt; margin:0 0 6pt; }
h2 { font-size:15pt; margin:0 0 8pt; }
a { color:#2a4f9e; text-decoration:none; }
.cover { height: 250mm; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; }
.cover .kicker { letter-spacing:.2em; color:#777; font-size:11pt; text-transform:uppercase; }
.cover .sub { color:#555; font-style:italic; margin-top:10pt; }
.pb { page-break-before: always; }
.bar { display:flex; align-items:center; gap:12px; background:#f5f5f7; border-radius:4px; padding:6px 10px; margin-bottom:10px; }
.num { background:#2a7f73; color:#fff; font-weight:bold; font-size:15pt; padding:4px 12px; border-radius:3px; }
.bar .t { font-family:Georgia, serif; font-size:13pt; font-weight:bold; }
.meta { color:#6b6b75; font-size:9pt; margin-bottom:8px; }
.nav { font-size:9pt; display:flex; justify-content:space-between; margin:4px 0 10px; }
.passage { border-left:3px solid #2a7f73; padding:4px 0 4px 12px; margin:6px 0 12px; white-space:normal; }
.qblock { break-inside: avoid; margin:0 0 14px; }
.qhead { font-size:9pt; letter-spacing:.08em; color:#2a7f73; font-weight:bold; text-transform:uppercase; margin-bottom:3px; }
.qtext { font-weight:bold; margin-bottom:6px; }
table.opts { width:100%; border-collapse:collapse; }
table.opts td { border:1px solid #d9d9e0; padding:5px 8px; vertical-align:top; }
table.opts td.l { width:26px; text-align:center; font-weight:bold; color:#2a7f73; background:#f7fbfa; }
.key h3 { margin:0; font-size:11pt; }
.kb { break-inside: avoid; border:1px solid #d9d9e0; border-radius:4px; padding:6px 10px; margin:0 0 8px; }
.kb .ans { font-weight:bold; color:#1f6b5f; }
.kb .exp { margin-top:3px; font-size:9.5pt; color:#333; }
.toc a { display:block; padding:1px 0; font-size:9.5pt; }
.toc .m { font-weight:bold; margin-top:10px; font-size:11pt; color:#2a4f9e; }
"""

parts = []
parts.append(f"""<div class="cover" id="top">
  <div class="kicker">Current affairs · MCQ practice</div>
  <h1>CLAT Current Affair Mega Sheet</h1>
  <div class="sub">{len(passages)} passages · {total_q} questions · answers at the end</div>
</div>""")

# contents
parts.append('<div class="pb"></div><h2 id="contents">Contents</h2><p class="meta">Click a passage to open it. Answers are in the Answer key at the end.</p><div class="toc">')
last_m = None
for p in passages:
    if p["month"] != last_m:
        parts.append(f'<div class="m">{esc(p["month"])}</div>'); last_m = p["month"]
    parts.append(f'<a href="#{pid(p)}">{p["n"]:03d} · {esc(p["title"])}</a>')
parts.append('</div>')
parts.append(f'<p class="meta"><a href="#answers">Go to the Answer key →</a></p>')

for p in passages:
    i = p["n"] - 1
    prev = f'<a href="#{pid(passages[i-1])}">← Previous passage</a>' if i > 0 else '<span></span>'
    nxt = f'<a href="#{pid(passages[i+1])}">Next passage →</a>' if i < len(passages) - 1 else '<span></span>'
    nav = f'<div class="nav">{prev}<a href="#contents">Contents</a>{nxt}</div>'
    body = [f'<div class="pb"></div><div id="{pid(p)}"></div>', nav,
            f'<div class="bar"><span class="num">{p["n"]:03d}</span><span class="t">{esc(p["title"])}</span></div>',
            f'<div class="meta">{esc(p["month"])} · {esc(p["chapter"])} · {esc(p["topic"])}</div>',
            f'<div class="passage">{esc(p["passage"])}</div>']
    for k, q in enumerate(p["questions"]):
        opts = "".join(f'<tr><td class="l">{L[j]}</td><td>{esc(o)}</td></tr>' for j, o in enumerate(q["options"]))
        body.append(f'''<div class="qblock" id="{qid(p,k)}">
  <div class="qhead">Question {k+1} of {len(p["questions"])} · <a href="#{aid(p,k)}">Answer ↓</a></div>
  <div class="qtext">{esc(q["q"])}</div>
  <table class="opts">{opts}</table></div>''')
    body.append(f'<div class="nav" style="margin-top:6px">{prev}<a href="#answers">Answer key</a>{nxt}</div>')
    parts.append("".join(body))

# answer key
parts.append('<div class="pb"></div><h2 id="answers">Answer key</h2><p class="meta">Each answer links back to its question.</p>')
for p in passages:
    parts.append(f'<div class="key"><h3><a href="#{pid(p)}">{p["n"]:03d} · {esc(p["title"])}</a></h3>')
    for k, q in enumerate(p["questions"]):
        parts.append(f'''<div class="kb" id="{aid(p,k)}">
  <div><a href="#{qid(p,k)}">↑ Question {k+1}</a> &nbsp;·&nbsp; <span class="ans">Answer: {L[q["answer"]]}. {esc(q["options"][q["answer"]])}</span></div>
  </div>''')
    parts.append('</div>')
parts.append(f'<p class="meta"><a href="#top">Back to the top</a></p>')

doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>CLAT Current Affair Mega Sheet</title>
<style>{css}</style></head><body>{''.join(parts)}</body></html>"""
tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mega_sheet.html")
open(tmp, "w", encoding="utf8").write(doc)

footer = ('<div style="font-size:8pt;width:100%;padding:0 16mm;color:#777;display:flex;justify-content:space-between;">'
          '<span>CLAT Current Affair Mega Sheet</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page()
    pg.goto("file://" + tmp, wait_until="load")
    pg.pdf(path=OUT, format="A4", print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=footer,
           margin=dict(top="18mm", bottom="20mm", left="16mm", right="16mm"))
    b.close()
print("passages", len(passages), "questions", total_q, "->", OUT)
