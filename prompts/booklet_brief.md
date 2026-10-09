# Brief: build dashboard content for ONE booklet topic (Haiku writer)

Input: a text file of OCR text of a CLAT Express booklet topic (pages marked `=== PAGE n ===`). OCR is ~5-10% garbled
(map labels, tables, diagrams are worst). USE ONLY facts that read clearly in the text. Never use web search, never use
outside knowledge to add facts. If a name/number/date is garbled or two readings are possible, do NOT use it: add it to
`needs_check` with the page number.

Write ONE JSON file (path given in your task) with exactly this shape (no markdown fences, valid JSON):
{
 "topic": {"title": "...", "chapter_title": "<section name given in your task>",
   "subtopics": [ {"title": "...", "summary": "2-4 sentences", "facts": ["5-10 short fact lines"], "keywords": ["..."]} ]},   // 3-5 subtopics that split the topic logically
 "mindmaps": [ {"scope": "topic", "title": "...", "root": {"label": "...", "children": [{"label":"...","children":[...]}]}},
               {"scope": "subtopic", "subtopic_index": 0, "title": "...", "root": {...}} ],   // 1 topic map (3 levels, 4-7 branches) + 1 map per subtopic (2-3 levels). Labels <= 8 words, facts not sentences.
 "mnemonics": [ {"scope": "topic"|"subtopic", "subtopic_index": <int, only if subtopic>, "title": "...", "mnemonic": "memory phrase", "decode": [{"key":"X","meaning":"..."}]} ],  // 2-3 genuine, usable memory aids (acronym/phrase/story) for facts in the text. decode meanings must be true facts from the text.
 "quizzes": [
  {"type": "MCQ", "subtopic_index": 0, "title": "...", "passage": "200-280 words, plain prose, built only from the text",
   "questions": [ {"q":"...","options":["..","..","..",".."],"answer":0,"explanation":"one sentence citing the fact"} ]},   // 8 questions
  {"type": "TITA", "subtopic_index": 1, "title": "...", "passage": "...",
   "questions": [ {"q":"...","answer":"short typed answer","accept":["variants"],"explanation":"..."} ]}   // 7 questions
 ],
 "needs_check": [ {"page": 0, "what": "garbled fact that could not be used"} ]
}

Question rules (CLAT style):
- The answer to most questions must need a fact from the booklet text that the passage does NOT state (the passage gives context; the booklet text gives the tested fact). Never a sentence-for-sentence restatement of the passage.
- MCQ mix of 8: 3 direct, 1 assertion-reason (stem lines "Assertion (A): ..." and "Reason (R): ..." on separate lines, use the 4 standard options: both true & R explains A / both true & R does not explain A / A true R false / A false R true), 1 match-the-following (stem = "Match List I with List II:" then one row per line as "I. item   ->   A. item"; 4 rows; options like "I-B, II-A, III-C, IV-D"), 1 multi-statement (stem = statements each on its own line starting "I. ", "II. ", "III. "; then "Which of the above statements is/are correct?"; options like "I and II only"), 1 how-many-statements ("Only one","Only two","Only three","All of the above/None" style), 1 more direct or two-statement.
- Exactly one defensible answer; distractors plausible but clearly wrong from the text; no "all of the above" unless needed. Spread correct-answer positions across 0,1,2,3 (each used at least once; no pattern like 0,1,2,3,0,1,2,3).
- TITA answers: a number, name, place, year or one short word/phrase, unambiguous. Put units in the question, not the answer (e.g. "(in per cent)"). Add alternative spellings in accept.
- No question may depend on a garbled fact. No opinions. Keep every explanation to one sentence.
After writing, re-open the file, confirm it parses as JSON (python3 -c "import json;json.load(open(path))"), and reply with one line: path, subtopic count, MCQ count, TITA count, needs_check count.
