# Brief: map a CLAT Express booklet's topics to page ranges (Haiku splitter)
Input: full OCR text of one monthly booklet (path given), pages marked `=== PAGE n ===` (n = PDF page number; the printed TOC page numbers may differ by 1-3 pages).
Use only that text. No web search.
Task: read the table of contents (usually on PDF page 2-4) and the actual pages, and find where each numbered topic starts and ends.
Write the JSON file (path given) as a list, valid JSON:
[ {"key":"t01_<short_slug>", "title":"<topic title as in the booklet>", "chapter":"<section/chapter heading it belongs to, e.g. International Relations and News>", "start":<first PDF page>, "end":<last PDF page>} , ... ]
Rules: topics are the numbered news items / lessons; keep TOC order and numbering; start/end are PDF page numbers that you verified by reading the first page of each topic (its heading must appear there); topic ranges must not overlap and must cover the topic content including its practice questions. Put trailing sections (Miscellaneous / Extra / AILET Corner / ads) as their own topic(s) ONLY if they contain real study content (one 'misc' topic spanning them is fine; cap any single range at 16 pages by splitting into misc1, misc2...). Skip cover, TOC and advertisement-only pages. Max 24 topics.
Validate with python3 -I (json loads, start<=end, no overlaps, ranges within the page count) and reply with one line: number of topics and any pages you left out.
