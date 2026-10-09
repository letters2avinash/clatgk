#!/usr/bin/env python3
"""Build PDFs from dashboard/data/<month>.json -> pdfs/<month>/ : Study Notes, Quiz Paper, Answer Key.
usage: python3 tools/build_month_pdfs.py 2026-01"""
import json, sys, os
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether

mid = sys.argv[1]
D = json.load(open(f"dashboard/data/{mid}.json", encoding="utf8"))
label = D["month"]["label"]
for n, f in [("DJ", "DejaVuSans.ttf"), ("DJB", "DejaVuSans-Bold.ttf"), ("DJS", "DejaVuSerif.ttf"), ("DJSB", "DejaVuSerif-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(n, "/usr/share/fonts/truetype/dejavu/" + f))
INK = colors.HexColor("#2b3990")
H1 = ParagraphStyle("h1", fontName="DJB", fontSize=17, leading=21, textColor=INK, spaceAfter=6)
H2 = ParagraphStyle("h2", fontName="DJB", fontSize=12, leading=15, textColor=INK, spaceBefore=8, spaceAfter=3)
H3 = ParagraphStyle("h3", fontName="DJB", fontSize=10, leading=13, spaceBefore=5, spaceAfter=2)
BODY = ParagraphStyle("b", fontName="DJS", fontSize=9.5, leading=14, spaceAfter=3)
SM = ParagraphStyle("s", fontName="DJ", fontSize=8.5, leading=12)
Q = ParagraphStyle("q", fontName="DJS", fontSize=9.5, leading=13.5, spaceBefore=4, spaceAfter=2)
OPT = ParagraphStyle("o", fontName="DJ", fontSize=9, leading=12.5, leftIndent=12)
ST = ParagraphStyle("st", fontName="DJS", fontSize=9.5, leading=13.5, leftIndent=14, firstLineIndent=-14)
def P(t, s=BODY): return Paragraph(escape(str(t)).replace("\n", "<br/>"), s)
def footer(c, d):
    c.saveState(); c.setFont("DJ", 7.5); c.setFillColor(colors.grey)
    c.drawString(18*mm, 10*mm, f"CLAT Express - {label} - practice material (built from the booklet text; verify key facts against the original)")
    c.drawRightString(A4[0]-18*mm, 10*mm, f"Page {d.page}"); c.restoreState()
def doc(path): return SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title=os.path.basename(path))
def stem(q):
    L = [l.strip() for l in q.split("\n") if l.strip()]; out = []; rows = []
    def flush():
        nonlocal rows
        if rows:
            t = Table([[P("List I", H3), P("List II", H3)]] + [[P(a, SM), P(b, SM)] for a, b in rows], colWidths=[85*mm, 85*mm])
            t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .4, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8eaf6")), ("VALIGN", (0,0), (-1,-1), "TOP")]))
            out.append(t); out.append(Spacer(1, 3)); rows = []
    for l in L:
        m = l.split("   ->   ")
        if len(m) == 2: rows.append(m); continue
        flush(); out.append(P(l, ST if l[:2] in ("I.","II") or l[:2].rstrip(".").isdigit() or l.startswith("Assertion") or l.startswith("Reason") else Q))
    flush(); return out

# ---------- Study notes
def notes(path):
    s = [P(f"CLAT Express - {label}: Study Notes", H1), P("Chapters, topics and sub-topics with key facts, memory aids and mind-map outlines.", SM), Spacer(1, 6)]
    mm = {m["ref"]: m for m in D["mindmaps"]}; mn = {}
    for m in D["mnemonics"]: mn.setdefault(m["ref"], []).append(m)
    def outline(n, d=0):
        r = [("&nbsp;" * 4 * d) + ("• " if d else "<b>") + escape(n["label"]) + ("" if d else "</b>")]
        for c in n.get("children", []): r += outline(c, d + 1)
        return r
    for c in D["chapters"]:
        s.append(P(c["title"], H2))
        for t in c["topics"]:
            s.append(P(t["title"], ParagraphStyle("t", parent=H2, fontSize=11, textColor=colors.black)))
            for sub in t["subtopics"]:
                blk = [P(sub["title"], H3), P(sub["summary"])]
                for f in sub["facts"]: blk.append(Paragraph("• " + escape(f), ParagraphStyle("f", parent=BODY, leftIndent=10, firstLineIndent=-8, fontSize=9, leading=12.5, spaceAfter=1)))
                for m in mn.get(sub["id"], []):
                    dec = "; ".join(f"<b>{escape(str(x['key']))}</b> = {escape(str(x['meaning']))}" for x in m["decode"])
                    blk.append(Paragraph(f"<b>Mnemonic - {escape(m['title'])}:</b> {escape(m['mnemonic'])}<br/>{dec}", ParagraphStyle("m", parent=BODY, backColor=colors.HexColor("#fff3d6"), borderPadding=3, fontSize=9, leading=12.5, spaceBefore=3)))
                if sub["id"] in mm:
                    blk.append(Paragraph("<b>Mind-map outline</b><br/>" + "<br/>".join(outline(mm[sub["id"]]["root"])), ParagraphStyle("mo", parent=SM, leftIndent=6, spaceBefore=3)))
                s.append(KeepTogether(blk[:3])); s += blk[3:]
    doc(path).build(s, onFirstPage=footer, onLaterPages=footer)

# ---------- Quiz paper + key
def quiz_paper(path, key=False):
    s = [P(f"CLAT Express - {label}: " + ("Answer Key" if key else "Practice Quizzes"), H1)]
    if not key: s.append(P("MCQ: +1 for a correct answer, -0.25 for a wrong answer. TITA (type-in-the-answer): +1, no negative marking.", SM))
    for typ, name in (("MCQ", "Multiple-choice passages"), ("TITA", "Type-in-the-answer passages")):
        s.append(P(name, H2))
        for q in [x for x in D["quizzes"] if x["type"] == typ]:
            if key:
                s.append(P(q["title"], H3))
                rows = []
                for i, x in enumerate(q["questions"], 1):
                    a = "ABCD"[x["answer"]] + ". " + x["options"][x["answer"]] if typ == "MCQ" else x["answer"]
                    rows.append([P(str(i), SM), P(a, SM), P(x.get("explanation", ""), SM)])
                t = Table(rows, colWidths=[8*mm, 55*mm, 107*mm]); t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .3, colors.lightgrey), ("VALIGN", (0,0), (-1,-1), "TOP")])); s.append(t)
            else:
                s.append(PageBreak()) if s and len(s) > 3 and isinstance(s[-1], Spacer) is False and False else None
                s.append(P(q["title"], H3)); s.append(P(q["passage"]))
                for i, x in enumerate(q["questions"], 1):
                    blk = [P(f"Q{i}.", ParagraphStyle("qn", parent=Q, fontName="DJB", spaceBefore=6))] + stem(x["q"])
                    if typ == "MCQ": blk += [P("(" + "ABCD"[k] + ")  " + o, OPT) for k, o in enumerate(x["options"])]
                    else: blk.append(P("Answer: ______________________", OPT))
                    s.append(KeepTogether(blk))
                s.append(Spacer(1, 10))
    doc(path).build(s, onFirstPage=footer, onLaterPages=footer)

os.makedirs(f"pdfs/{mid}", exist_ok=True)
base = f"pdfs/{mid}/CLAT_Express_{label.replace(' ', '_')}"
notes(base + "_Study_Notes.pdf"); quiz_paper(base + "_Quizzes.pdf"); quiz_paper(base + "_Quiz_Answer_Key.pdf", key=True)
for f in sorted(os.listdir(f"pdfs/{mid}")): print(f, os.path.getsize(f"pdfs/{mid}/{f}")//1024, "KB")
