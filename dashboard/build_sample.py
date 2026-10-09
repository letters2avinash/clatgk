"""Build the January 2026 SAMPLE dataset for the dashboard from already-verified passages (not from the booklets)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)) + "/.."
F = lambda n: json.load(open(f"{R}/data/final/{n}.json"))
AR = ["Both (A) and (R) are true and (R) is the correct explanation of (A)", "Both (A) and (R) are true but (R) is NOT the correct explanation of (A)", "(A) is true but (R) is false", "(A) is false but (R) is true"]
S2 = ["I only", "II only", "Both I and II", "Neither I nor II"]
CT = ["Only one", "Only two", "Only three", "All four"]

def mcq(q):
    t = q["type"]
    if t == "direct": return q["q"], q["options"]
    if t == "assertion_reason": return f"Assertion (A): {q['assertion']}\nReason (R): {q['reason']}", AR
    if t == "match":
        rows = "\n".join(f"{a}   ->   {b}" for a, b in zip(q["list1"], q["list2"]))
        return "Match List I with List II:\n" + rows, q["options"]
    if t == "statement_two": return "\n".join(q["statements"]) + "\nWhich of the above statement(s) is/are correct?", S2
    if t == "statement_multi": return "\n".join(q["statements"]) + "\nWhich of the above statements is/are correct?", q["options"]
    if t == "statement_count": return "\n".join(q["statements"]) + f"\nHow many of the above statements are {q.get('mode','correct')}?", CT
    raise ValueError(t)

def quiz(qid, final, ref, ch, tp, st=None):
    d = F(final); qs = []
    for q in d["questions"]:
        text, opts = mcq(q)
        qs.append({"q": text, "options": opts, "answer": q["answer"], "explanation": q.get("explanation", "")})
    o = {"id": qid, "type": "MCQ", "ref": ref, "chapter": ch, "topic": tp, "title": d["title"], "passage": d["text"], "questions": qs}
    if st: o["subtopic"] = st
    return o

def tita(qid, title, passage, ref, ch, tp, rows, st=None):
    o = {"id": qid, "type": "TITA", "ref": ref, "chapter": ch, "topic": tp, "title": title, "passage": passage,
         "questions": [{"q": a, "answer": b, "accept": c, "explanation": e} for a, b, c, e in rows]}
    if st: o["subtopic"] = st
    return o

M = "2026-01"
eco = F("t05_p4"); space = F("t01_p5"); art = F("t09_p2")
data = {
 "month": {"id": M, "label": "January 2026 (sample)", "source": "Sample built from Tests 1-10 verified passages; booklet text not yet extracted", "pages": None},
 "chapters": [
  {"id": f"{M}-c1", "title": "Economy", "topics": [
    {"id": f"{M}-c1-t1", "title": "India's early-2026 economic data", "subtopics": [
      {"id": f"{M}-c1-t1-s1", "title": "Growth: NSO advance estimates and the Economic Survey", "summary": "The NSO's first advance estimates (7 Jan 2026) put FY26 real GDP growth at 7.4 per cent. The Economic Survey 2025-26 was tabled on 29 Jan 2026.",
       "facts": ["First advance estimates released 7 January 2026: FY26 real GDP growth 7.4% (FY25: 6.5%)", "GVA growth 7.3%; services 9.1%", "Economic Survey 2025-26 tabled in Lok Sabha on 29 January 2026 by FM Nirmala Sitharaman", "Private final consumption 61.5% of GDP, highest since FY2011-12"], "keywords": ["NSO", "advance estimates", "Economic Survey", "GVA"]},
      {"id": f"{M}-c1-t1-s2", "title": "Prices, industry and trade data", "summary": "December 2025 inflation was low, industrial output gained pace and the merchandise trade deficit was about $25 billion.",
       "facts": ["CPI inflation Dec 2025: 1.33% (Nov: 0.71%); food prices -2.71%; below the RBI band for a fourth month", "WPI inflation Dec 2025: 0.83% (released 14 Jan), ending two months of deflation", "IIP Nov 2025: 6.7%, highest in 25 months; manufacturing 8.0%, mining 5.4%, electricity -1.5%", "Eight core industries Dec 2025: 3.7% (released 20 Jan); cement +13.5%, steel +6.9%", "Merchandise exports $38.51 bn (+1.87%), imports $63.55 bn, deficit about $25.04 bn (released 15 Jan)"], "keywords": ["CPI", "WPI", "IIP", "core sector", "trade deficit"]},
      {"id": f"{M}-c1-t1-s3", "title": "The inflation-target framework", "summary": "Under the RBI Act the government sets the inflation target with the RBI. The current target is 4% with a 2-6% band for 2026-31.",
       "facts": ["Target 4% with tolerance band 2-6%, 1 April 2026 to 31 March 2031 (notification dated 25 March 2026)", "If inflation stays outside the band for three consecutive quarters, the RBI must report to the government with reasons and remedial action"], "keywords": ["inflation target", "RBI Act", "tolerance band"]}]}]},
  {"id": f"{M}-c2", "title": "Science, Space & Technology", "topics": [
    {"id": f"{M}-c2-t2", "title": "PSLV-C62 and Gaganyaan", "subtopics": [
      {"id": f"{M}-c2-t2-s4", "title": "PSLV-C62 failure (12 Jan 2026)", "summary": "PSLV-C62 lifted off from Sriharikota on 12 January 2026 but suffered an anomaly at the end of the third stage and the payloads did not reach orbit.",
       "facts": ["Carried EOS-N1 (Anvesha), a hyperspectral Earth-observation satellite, with 15 co-passenger payloads", "First two stages normal; anomaly at the end of PS3; ISRO chairman V. Narayanan cited a roll-rate disturbance", "Lost: Theos-2 (UK-Thailand) and AyulSat (refuelling demonstrator); Kestrel Initial Demonstrator sent some data", "Second consecutive PSLV failure after PSLV-C61 (May 2025)", "Reports citing sources: probe under K. VijayRaghavan, S. Somanath as co-chairman"], "keywords": ["PSLV-C62", "EOS-N1", "PS3", "Narayanan"]},
      {"id": f"{M}-c2-t2-s5", "title": "Gaganyaan test flights", "summary": "Gaganyaan depends on uncrewed test flights. G1 (carrying Vyommitra) slipped from its earlier target.",
       "facts": ["Oct 2025: G1 about 90% complete, planned for December", "June 2026: ISRO aimed to launch G1 by end-2026, though it could slip into 2027", "G1 carries the half-humanoid robot Vyommitra", "ISRO has said three uncrewed missions will precede the crewed flight", "A second spaceport for small satellites has been under construction since March 2025 (commissioning provisionally FY2026-27)"], "keywords": ["Gaganyaan", "G1", "Vyommitra", "second spaceport"]}]},
    {"id": f"{M}-c2-t3", "title": "Artemis Accords", "subtopics": [
      {"id": f"{M}-c2-t3-s6", "title": "Portugal becomes the 60th signatory", "summary": "Portugal signed the Artemis Accords on 11 January 2026 at a ceremony in Lisbon.",
       "facts": ["Signed by Helena Canhao, Secretary of State for Science and Innovation, on 11 January 2026", "Attended by US Ambassador John J. Arrigo and Hugo Costa of the Portuguese Space Agency", "NASA Administrator Jared Isaacman welcomed Portugal as the newest signatory"], "keywords": ["Artemis Accords", "Portugal", "NASA"]}]}]}],
 "mindmaps": [
  {"id": "mm-month", "scope": "month", "ref": M, "title": "January 2026 at a glance", "root": {"label": "January 2026", "children": [
    {"label": "Economy", "children": [{"label": "Growth", "children": [{"label": "NSO advance est. 7 Jan: GDP 7.4%"}, {"label": "Economic Survey 29 Jan"}]}, {"label": "Prices", "children": [{"label": "CPI Dec 1.33%"}, {"label": "WPI Dec 0.83%"}]}, {"label": "Target 4% (2-6% band)"}]},
    {"label": "Science & Space", "children": [{"label": "PSLV-C62 fails 12 Jan"}, {"label": "Gaganyaan G1 delayed"}, {"label": "Portugal: 60th Artemis Accords signatory"}]}]}},
  {"id": "mm-econ", "scope": "chapter", "ref": f"{M}-c1", "title": "Economy: early-2026 data", "root": {"label": "Economy Jan 2026", "children": [
    {"label": "Growth", "children": [{"label": "FY26 GDP 7.4% (FY25 6.5%)", "children": [{"label": "GVA 7.3%"}, {"label": "Services 9.1%"}]}, {"label": "Private consumption 61.5% of GDP"}]},
    {"label": "Prices", "children": [{"label": "CPI Dec 1.33%", "children": [{"label": "Nov 0.71%"}, {"label": "Food -2.71%"}]}, {"label": "WPI Dec 0.83%"}]},
    {"label": "Industry", "children": [{"label": "IIP Nov 6.7% (25-month high)"}, {"label": "Core sector Dec 3.7%", "children": [{"label": "Cement +13.5%"}, {"label": "Steel +6.9%"}]}]},
    {"label": "Trade", "children": [{"label": "Exports $38.51 bn"}, {"label": "Imports $63.55 bn"}, {"label": "Deficit ~$25.04 bn"}]},
    {"label": "Target", "children": [{"label": "4% with 2-6% band"}, {"label": "2026-31, notified 25 Mar 2026"}, {"label": "3 quarters outside band: RBI reports"}]}]}},
  {"id": "mm-pslv", "scope": "subtopic", "ref": f"{M}-c2-t2-s4", "title": "PSLV-C62 failure", "root": {"label": "PSLV-C62", "children": [
    {"label": "Launch", "children": [{"label": "12 Jan 2026, Sriharikota"}, {"label": "EOS-N1 (Anvesha) + 15 co-passengers"}]},
    {"label": "What failed", "children": [{"label": "Anomaly at end of PS3"}, {"label": "Roll-rate disturbance (Narayanan)"}]},
    {"label": "Payloads", "children": [{"label": "Lost: Theos-2, AyulSat"}, {"label": "Kestrel: some data"}]},
    {"label": "Context", "children": [{"label": "2nd straight failure (C61, May 2025)"}, {"label": "Probe: VijayRaghavan, Somanath"}]}]}}],
 "mnemonics": [
  {"id": "mn-pslv", "scope": "subtopic", "ref": f"{M}-c2-t2-s4", "title": "PSLV-C62 payloads", "mnemonic": "Two Are lost, Kestrel talks (T-A-K)", "decode": [
    {"key": "T", "meaning": "Theos-2 - UK-Thailand Earth-observation satellite, lost"}, {"key": "A", "meaning": "AyulSat - refuelling demonstrator, lost"}, {"key": "K", "meaning": "Kestrel Initial Demonstrator - Spanish prototype, sent some data"}]},
  {"id": "mn-eco", "scope": "subtopic", "ref": f"{M}-c1-t1-s1", "title": "Growth numbers, Jan 2026", "mnemonic": "Seven-four GDP, seven-three GVA, nine-one services", "decode": [
    {"key": "7.4", "meaning": "FY26 real GDP growth (NSO first advance estimates)"}, {"key": "7.3", "meaning": "FY26 GVA growth"}, {"key": "9.1", "meaning": "Services growth"}, {"key": "61.5", "meaning": "Private final consumption, % of GDP (Economic Survey)"}]}],
 "quizzes": [
  quiz("q-eco", "t05_p4", f"{M}-c1-t1", f"{M}-c1", f"{M}-c1-t1"),
  quiz("q-pslv", "t01_p5", f"{M}-c2-t2", f"{M}-c2", f"{M}-c2-t2"),
  quiz("q-art", "t09_p2", f"{M}-c2-t3", f"{M}-c2", f"{M}-c2-t3"),
  tita("t-eco", "India's early-2026 economic data (type the answer)", eco["text"], f"{M}-c1-t1", f"{M}-c1", f"{M}-c1-t1", [
    ("What was FY26 real GDP growth (in per cent) in the NSO's first advance estimates?", "7.4", ["7.4%", "7.4 per cent"], "Stated in the passage: 7.4 per cent against 6.5 per cent in FY25."),
    ("On which day of January 2026 was the Economic Survey 2025-26 tabled?", "29", ["29 january", "29 january 2026", "29th"], "Tabled in Lok Sabha on 29 January 2026."),
    ("What share of GDP (per cent) was private final consumption expenditure, per the Survey?", "61.5", ["61.5%"], "The highest share since FY2011-12."),
    ("What was CPI inflation (in per cent) for December 2025?", "1.33", ["1.33%"], "Up from 0.71 per cent in November."),
    ("Approximately how large was the December 2025 merchandise trade deficit (US$ billion)?", "25.04", ["25", "about 25.04", "25.0"], "Exports $38.51 bn minus imports $63.55 bn."),
    ("What is the RBI's inflation target (in per cent) for 2026-31?", "4", ["4%", "4 per cent"], "4 per cent with a 2 to 6 per cent tolerance band.")]),
  tita("t-pslv", "PSLV-C62 and Gaganyaan (type the answer)", space["text"], f"{M}-c2-t2", f"{M}-c2", f"{M}-c2-t2", [
    ("Who is the ISRO chairman who spoke of a roll-rate disturbance?", "V. Narayanan", ["narayanan", "v narayanan", "v. narayanan"], "ISRO chairman V. Narayanan."),
    ("Name the strategic hyperspectral satellite also called Anvesha.", "EOS-N1", ["eos n1", "eosn1"], "EOS-N1 was the main payload of PSLV-C62."),
    ("How many co-passenger payloads did PSLV-C62 carry?", "15", ["fifteen"], "Fifteen co-passenger payloads belonging to Indian and foreign organisations."),
    ("Which UK-Thailand Earth-observation satellite was among those lost?", "Theos-2", ["theos 2", "theos2"], "Theos-2 was lost; AyulSat was also lost."),
    ("Which half-humanoid robot will fly on the first uncrewed Gaganyaan flight?", "Vyommitra", ["vyom mitra"], "G1 will carry Vyommitra."),
    ("Which earlier PSLV mission failed in May 2025?", "PSLV-C61", ["pslv c61", "c61"], "PSLV-C61 also failed owing to a third-stage problem.")])]
}
os.makedirs(f"{R}/dashboard/data", exist_ok=True)
json.dump(data, open(f"{R}/dashboard/data/{M}.json", "w"), indent=1, ensure_ascii=False)
json.dump({"months": [{"id": M, "file": f"{M}.json"}]}, open(f"{R}/dashboard/data/index.json", "w"))
print({k: len(v) for k, v in data.items() if isinstance(v, list)}, "quizzes:", [(q["id"], len(q["questions"])) for q in data["quizzes"]])
