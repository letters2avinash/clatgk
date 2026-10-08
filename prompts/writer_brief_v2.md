# Writer brief v2 (batch 1: Tests 3-6)

Today is 2026-10-08. Read `docs/clat_gk_schema.md`, then follow this brief. You write ONE passage and EIGHT questions. An independent verifier will later cull the 8 to the best 6, so write 8 careful, distinct questions.

## Slot
Your slot is in `plan/batch1_slots.json` (use the id you were given): `category`, `period`, `niche`, and `targets`.
Other slots in that file cover other topics - do not use their niches. Also do not reuse topics already used: Keralam renaming, Union Budget 2026-27 and RBI repo rate, FIFA World Cup 2026, India's BRICS chairship, Article 21 menstrual-health/passive-euthanasia rulings, PSLV-C62/Gaganyaan, Padma Awards 2026, Supreme Court AI fake-judgments order, Agni missile tests May 2026, Botswana cheetahs at Kuno, Women AutHer Awards, Transgender Persons Amendment Bill 2026, 2026 Nobel Prizes.
If you cannot confirm a suitable event for your period, widen to the nearest weeks in 2026 but stay in your category.

## Passage
450-500 words (count them; under 450 is a failure), news-style, exact dates/names/numbers, every fact confirmed. No opinion, no filler. Only include facts you have confirmed from at least two independent publishers; leave out anything single-sourced.

## Questions (exactly 8)
Types: 3 direct, 1 match, 1 assertion_reason, 1 statement_two, 1 statement_count, 1 statement_multi.
- The correct answer must need a fact the passage does NOT state (adjacent static GK or a related current-affairs fact). No giveaways: the answer must not appear in the stem or in any other question's stem/options/statements, and no two questions may test the same fact. Spread the questions over different facts and different Articles/institutions.
- Hit the TARGET answers from your slot exactly for the three fixed-frame types:
  assertion_reason: 0 = both true and R is the direct definition/cause of A; 1 = both true but R does not explain A; 2 = A true, R plainly false; 3 = A plainly false, R true. For targets 0 or 1 the relation between R and A must be unambiguous - if you cannot make it so, still hit the target by choosing a clearer A/R pair.
  statement_two: 0 = I only; 1 = II only; 2 = both; 3 = neither.
  statement_count: set `mode` ("correct"/"incorrect") and statements so the count maps to the target index (0 Only one, 1 Only two, 2 Only three, 3 All four). Statements must be independent of each other (no statement implying another).
- Every distractor must be definitely wrong (a second defensible answer = ambiguous). Avoid vague words like 'latest', 'first', 'originally' unless the answer is unique.
- Each question: `explanation` (consistent with the key), `source` (URL(s) returned by your searches that actually support the answer; join several with " ; "), and for statement/assertion types a `truth` list of booleans per statement (assertion_reason: [A_true, R_true]).
- Static-GK facts: prefer constitutionofindia.net, indiacode, official sites. Never answer from memory alone.

## Research rules
Use WebSearch (load with ToolSearch "select:WebSearch" if not callable). WebFetch fails on many hosts - rely on snippets. Every fact needs two independent publishers (Wikipedia and its copies count as one).

## Output
Write JSON to the path in your task: {"title": "...", "topic_tags": [...], "slot": "<id>", "text": "...", "sources": [urls], "questions": [8 question objects]}.
Final reply: max 3 lines (path, word count, facts you could not double-source).
