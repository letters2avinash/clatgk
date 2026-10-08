# CLAT current affairs & GK test generator

Produce a CLAT UG-style "Current Affairs including General Knowledge" section.

## Pattern
- Passage-based: each passage is 450-500 words, drawn from news of the last 6-12 months.
- 4-5 MCQs per passage (a sample may use fewer), 4 options (A-D), exactly one correct.
- Mix: fact recall from the passage, inference, static GK linked to the news
  (Constitution, institutions, geography), and "which statement is correct" items.
- Cover: national affairs, Supreme Court/High Court rulings, legislation, international
  affairs, economy, awards, sports, science.
- Each question has a one-line explanation and a source URL.

## Sourcing rules
- Use only reliable sources: PIB, The Hindu, Indian Express, LiveLaw, Bar & Bench, SCC Online, Sansad/PRS.
- Every dated fact in a passage must be backed by a source found in this session. Never fill gaps from memory.
- If a fact is unconfirmed (e.g. presidential assent not yet reported), leave it out of the answer key or mark it in `notes`.
- Record in `notes` any source that could not be reached.

## Output
Write `tests/YYYY-MM-DD/test.json` using the schema in the sample test, then open a draft PR.
