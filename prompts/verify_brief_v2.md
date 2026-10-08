# Verifier brief v2 (independent check + cull to final passage)

You did not write this passage. Assume it contains errors. Read `docs/clat_gk_schema.md` and `prompts/verify_brief.md` (method and rules still apply: fresh searches, two independent publishers per claim, check every distractor, truth values, giveaways, explanation mismatches, weak sources).

Differences in v2:
- The draft has 8 questions. Your job is to produce the FINAL passage with the best 6 that pass every check. Drop failures; if more than 6 pass, drop the weakest/most overlapping so that the final 6 test different facts and keep a mix (at least 2 direct, 1 match, 1 assertion_reason and 1 statement type; fewer than that only if too many fail).
- If fewer than 5 pass, keep the passing ones and say so.
- Apply passage fixes yourself: delete or reword every passage claim that is not CONFIRMED by two independent publishers (do not add new facts to the passage; keep it at roughly 430+ words; make sure each edited sentence still reads grammatically and no dangling clause or trailing comma remains).
- Do not change a kept question's answer index or target frame. You may fix a question's `source` to the URL(s) you found that really support it, and tighten wording to remove ambiguity or a giveaway, but only if the fact itself is confirmed by two independent publishers.
- A giveaway across questions means: the answer to one question appears in another question's stem/options/statements. Drop or reword.
- Do not invent replacement questions.

## Output
1. Write the verification record to the path given as `verify_out` (format as in prompts/verify_brief.md; questions indexed 1-8).
2. Write the FINAL passage object (same shape as the draft, with only the kept questions, in their original relative order, `truth` fields retained) to the path given as `final_out`.
Final reply: max 4 lines: paths, kept count, how many of the 8 were dropped and why (one phrase each), and any claim left single-sourced.
