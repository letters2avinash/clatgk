# Brief: add missing mind-maps and mnemonics to an existing topic file (Haiku)
Input: the topic's OCR text file and its existing JSON (paths in the task), which already has "topic" (with subtopics) and "quizzes" but lacks "mindmaps" and "mnemonics".
Use ONLY facts that read clearly in the text. No web search. Never call create_session or spawn_task.
Add (and save back into the same JSON file, keeping all existing keys untouched) :
 "mindmaps": [ {"scope":"topic","title":"...","root":{"label":"...","children":[{"label":"...","children":[...]}]}},  one {"scope":"subtopic","subtopic_index":i,"title":"...","root":{...}} per subtopic ]  - topic map 3 levels, 4-7 branches; subtopic maps 2-3 levels; labels <= 8 words, facts not sentences;
 "mnemonics": [ 2-3 of {"scope":"topic"|"subtopic","subtopic_index":<int if subtopic>,"title":"...","mnemonic":"memory phrase","decode":[{"key":"X","meaning":"..."}]} ] - genuine memory aids; every decode meaning a true fact from the text.
Validate with python3 -I (json loads; keys present) and reply with one line: counts of mindmaps and mnemonics.
