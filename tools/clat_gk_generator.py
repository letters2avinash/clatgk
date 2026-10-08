"""
Reusable CLAT GK test PDF generator.
Reads a test JSON (schema: clat_gk_schema.md) and renders all 6 question types.
Usage: python3 clat_gk_generator.py input.json questions.pdf [key.pdf]
With key.pdf: questions.pdf has no answers; key.pdf has answers, explanations and sources.
"""
import json
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib import colors

AR_OPTIONS = [
    "Both (A) and (R) are true and (R) is the correct explanation of (A)",
    "Both (A) and (R) are true but (R) is NOT the correct explanation of (A)",
    "(A) is true but (R) is false",
    "(A) is false but (R) is true",
]
S2_OPTIONS = ["I only", "II only", "Both I and II", "Neither I nor II"]
COUNT_OPTIONS = ["Only one", "Only two", "Only three", "All four"]
LETTERS = ["A", "B", "C", "D"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleX", parent=styles["Title"], fontSize=16, spaceAfter=4),
        "meta": ParagraphStyle("Meta", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER,
                                textColor=colors.HexColor("#444444")),
        "section": ParagraphStyle("Section", parent=styles["Heading3"], fontSize=11, spaceBefore=14,
                                   spaceAfter=6, textColor=colors.HexColor("#1a3c6e")),
        "passage": ParagraphStyle("PassageText", parent=styles["Normal"], fontSize=10.5, leading=15,
                                   alignment=TA_LEFT, spaceAfter=10),
        "q": ParagraphStyle("Q", parent=styles["Normal"], fontSize=10.5, leading=14, spaceBefore=9,
                             spaceAfter=3, fontName="Helvetica-Bold"),
        "sub": ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10.5, leading=14, spaceBefore=2,
                               spaceAfter=2),
        "opt": ParagraphStyle("Opt", parent=styles["Normal"], fontSize=10.5, leading=13.5, leftIndent=14),
        "ans": ParagraphStyle("Ans", parent=styles["Normal"], fontSize=9.5, leading=13, leftIndent=14,
                               textColor=colors.HexColor("#1a5c1a"), spaceBefore=3),
        "exp": ParagraphStyle("Exp", parent=styles["Normal"], fontSize=9, leading=12.5, leftIndent=14,
                               textColor=colors.HexColor("#444444"), spaceAfter=2),
        "src": ParagraphStyle("Src", parent=styles["Normal"], fontSize=7.5, leading=10, leftIndent=14,
                               textColor=colors.HexColor("#888888"), spaceAfter=10),
        "notes": ParagraphStyle("Notes", parent=styles["Normal"], fontSize=9, leading=12.5,
                                 textColor=colors.HexColor("#555555"), spaceBefore=10, spaceAfter=10),
        "listhdr": ParagraphStyle("ListHdr", parent=styles["Normal"], fontSize=9.5, leading=12,
                                   fontName="Helvetica-Bold"),
        "srchdr": ParagraphStyle("SrcHdr", parent=styles["Normal"], fontSize=8.5,
                                  textColor=colors.HexColor("#666666"), spaceAfter=2),
    }


def render_options(story, st, options, answer_idx, mode="inline"):
    for i, opt in enumerate(options):
        letter = LETTERS[i]
        story.append(Paragraph(f"({letter}) {esc(opt)}", st["opt"]))
    if mode == "inline":
        story.append(Paragraph(f"Answer: ({LETTERS[answer_idx]}) {esc(options[answer_idx])}", st["ans"]))


def render_question(story, st, qnum, q, mode="inline"):
    outer, story = story, []
    qtype = q["type"]

    if qtype == "direct":
        story.append(Paragraph(f'Q{qnum}. {esc(q["q"])}', st["q"]))
        render_options(story, st, q["options"], q["answer"], mode)

    elif qtype == "assertion_reason":
        story.append(Paragraph(f'Q{qnum}. Assertion (A): {esc(q["assertion"])}', st["q"]))
        story.append(Paragraph(f'Reason (R): {esc(q["reason"])}', st["sub"]))
        render_options(story, st, AR_OPTIONS, q["answer"], mode)

    elif qtype == "match":
        story.append(Paragraph(f'Q{qnum}. Match List I with List II:', st["q"]))
        rows = [[Paragraph("List I", st["listhdr"]), Paragraph("List II", st["listhdr"])]]
        n = max(len(q["list1"]), len(q["list2"]))
        for i in range(n):
            left = esc(q["list1"][i]) if i < len(q["list1"]) else ""
            right = esc(q["list2"][i]) if i < len(q["list2"]) else ""
            rows.append([Paragraph(left, st["opt"]), Paragraph(right, st["opt"])])
        tbl = Table(rows, colWidths=[85 * mm, 85 * mm])
        tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 4))
        story.append(Paragraph("Choose the correct matching:", st["sub"]))
        render_options(story, st, q["options"], q["answer"], mode)

    elif qtype == "statement_two":
        story.append(Paragraph(f'Q{qnum}. Statement {esc(q["statements"][0])}', st["q"]))
        story.append(Paragraph(f'Statement {esc(q["statements"][1])}', st["sub"]))
        story.append(Paragraph("Which of the above statement(s) is/are correct?", st["sub"]))
        render_options(story, st, S2_OPTIONS, q["answer"], mode)

    elif qtype == "statement_multi":
        story.append(Paragraph(f'Q{qnum}. Statement {esc(q["statements"][0])}', st["q"]))
        for s in q["statements"][1:]:
            story.append(Paragraph(f'Statement {esc(s)}', st["sub"]))
        story.append(Paragraph("Which of the above statements is/are correct?", st["sub"]))
        render_options(story, st, q["options"], q["answer"], mode)

    elif qtype == "statement_count":
        story.append(Paragraph(f'Q{qnum}. Statement {esc(q["statements"][0])}', st["q"]))
        for s in q["statements"][1:]:
            story.append(Paragraph(f'Statement {esc(s)}', st["sub"]))
        verb = "correct" if q.get("mode", "correct") == "correct" else "incorrect"
        story.append(Paragraph(f'How many of the above statements are {verb}?', st["sub"]))
        render_options(story, st, COUNT_OPTIONS, q["answer"], mode)

    else:
        raise ValueError(f"Unknown question type: {qtype}")

    if mode == "inline":
        story.append(Paragraph(f'Explanation: {esc(q["explanation"])}', st["exp"]))
        if q.get("source"):
            story.append(Paragraph(f'Source: {esc(q["source"])}', st["src"]))
    outer.append(KeepTogether(story))


def build_pdf(data, out_path, mode="inline"):
    st = build_styles()
    doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                             leftMargin=18 * mm, rightMargin=18 * mm, title=data["title"])
    story = [Paragraph(esc(data["title"]), st["title"])]
    meta_line = (f'Date: {data["date"]}  |  Duration: {data["duration_minutes"]} min  |  '
                 f'Marking: +{data["marks_correct"]} / {data["marks_wrong"]}')
    story.append(Paragraph(esc(meta_line), st["meta"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#999999")))
    story.append(Spacer(1, 6))

    if data.get("notes") and mode == "inline":
        story.append(Paragraph("<b>Note:</b> " + esc(data["notes"]), st["notes"]))

    qnum = 1
    for p in data["passages"]:
        if p.get("title"):
            story.append(Paragraph(esc(p["title"]), st["section"]))
        for para in p["text"].split("\n\n"):
            story.append(Paragraph(esc(para), st["passage"]))
        story.append(Spacer(1, 2))

        for q in p["questions"]:
            render_question(story, st, qnum, q, mode)
            qnum += 1

        if p.get("sources") and mode == "inline":
            story.append(Spacer(1, 6))
            story.append(Paragraph("Passage sources:", st["srchdr"]))
            for s in p["sources"]:
                story.append(Paragraph(esc(s), st["src"]))

    doc.build(story)


def answer_text(q):
    t = q["type"]
    if t == "assertion_reason":
        opts = AR_OPTIONS
    elif t == "statement_two":
        opts = S2_OPTIONS
    elif t == "statement_count":
        opts = COUNT_OPTIONS
    else:
        opts = q["options"]
    return f"({LETTERS[q['answer']]}) {opts[q['answer']]}"


def build_key_pdf(data, out_path):
    st = build_styles()
    doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                             leftMargin=18 * mm, rightMargin=18 * mm, title=data["title"] + " - Answer Key")
    story = [Paragraph(esc(data["title"]) + " - Answer Key", st["title"])]
    story.append(Paragraph(esc(f'Date: {data["date"]}'), st["meta"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#999999")))
    if data.get("notes"):
        story.append(Paragraph("<b>Note:</b> " + esc(data["notes"]), st["notes"]))
    allq = [q for p in data["passages"] for q in p["questions"]]
    row, rows = [], []
    for i, q in enumerate(allq, 1):
        row.append(Paragraph(f"<b>{i}.</b> {LETTERS[q['answer']]}", st["opt"]))
        if len(row) == 6:
            rows.append(row); row = []
    if row:
        rows.append(row + [""] * (6 - len(row)))
    tbl = Table(rows, colWidths=[28 * mm] * 6)
    tbl.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story += [Spacer(1, 8), tbl, Spacer(1, 10)]
    qnum = 1
    for pi, p in enumerate(data["passages"], 1):
        story.append(Paragraph(esc(f'Passage {pi}: {p.get("title", "")}'), st["section"]))
        for q in p["questions"]:
            story.append(Paragraph(f"Q{qnum}. Answer: {esc(answer_text(q))}", st["ans"]))
            story.append(Paragraph(f'Explanation: {esc(q["explanation"])}', st["exp"]))
            if q.get("source"):
                story.append(Paragraph(f'Source: {esc(q["source"])}', st["src"]))
            qnum += 1
        if p.get("sources"):
            story.append(Paragraph("Passage sources:", st["srchdr"]))
            for src in p["sources"]:
                story.append(Paragraph(esc(src), st["src"]))
    doc.build(story)


if __name__ == "__main__":
    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path) as f:
        data = json.load(f)
    if len(sys.argv) > 3:
        build_pdf(data, out_path, mode="paper")
        build_key_pdf(data, sys.argv[3])
        print("done:", out_path, sys.argv[3])
    else:
        build_pdf(data, out_path)
        print("done:", out_path)
