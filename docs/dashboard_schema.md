# CLAT GK dashboard - data schema (one JSON file per month: dashboard/data/YYYY-MM.json)

{
 "month": {"id": "2026-01", "label": "January 2026", "source": "CLAT_Express__January_2026.pdf", "pages": <int or null>},
 "chapters": [ {"id": "2026-01-c1", "title": "...", "topics": [
     {"id": "2026-01-c1-t1", "title": "...", "subtopics": [
         {"id": "2026-01-c1-t1-s1", "title": "...", "summary": "2-4 sentences from the booklet",
          "facts": ["short fact lines taken from the booklet"], "keywords": ["..."]} ] } ] } ],
 "mindmaps": [ {"id": "mm-...", "scope": "month|chapter|topic|subtopic", "ref": "<id of the node it maps>", "title": "...",
                "root": {"label": "...", "children": [ {"label": "...", "children": [ ... ]} ]}} ],
 "mnemonics": [ {"id": "mn-...", "scope": "chapter|topic|subtopic", "ref": "<node id>", "title": "...",
                 "mnemonic": "the memory phrase", "decode": [ {"key": "letter or word", "meaning": "what it stands for"} ]} ],
 "quizzes": [
   {"id": "q-...", "type": "MCQ", "ref": "<node id>", "chapter": "<chapter id>", "topic": "<topic id>", "subtopic": "<subtopic id>",
    "title": "...", "passage": "200-300 words built ONLY from the booklet text",
    "questions": [ {"q": "...", "options": ["A text","B text","C text","D text"], "answer": 0, "explanation": "..."} ]},   // >= 6 questions
   {"id": "t-...", "type": "TITA", "ref": "...", "chapter": "...", "topic": "...", "subtopic": "...",
    "title": "...", "passage": "...",
    "questions": [ {"q": "...", "answer": "short typed answer (a number, name or word)", "accept": ["other accepted spellings"], "explanation": "..."} ]}  // >= 6 questions
 ]
}
Rules: every fact must come from the booklet text; every id referenced must exist; TITA answers are short and unambiguous
(a number, a name, a place, a year); MCQ answers are an index 0-3; vary the answer positions (no A-heavy sets).
