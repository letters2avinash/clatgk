# Top-up writer brief

You are adding replacement questions to an already-verified CLAT GK passage. Read `docs/clat_gk_schema.md` and `prompts/clat_ca.md` first.

Rules:
1. Read the passage file and its existing questions. The new questions must NOT repeat or hint at any fact used in the passage text or in any existing question's stem/options/statements/explanation. Pick different static-GK or related current-affairs facts.
2. The golden rule applies: the answer needs a fact the passage does not state. No giveaways inside the new question either (no answer words in the stem; no statement that restates another statement).
3. Every fact you use must be confirmed by TWO independent publishers via your own WebSearch (load with ToolSearch "select:WebSearch" if needed). Wikipedia plus a page copying it counts as one. Prefer primary sources (constitutionofindia.net, indiacode, official sites). If you cannot get two, choose a different fact. Never use memory alone.
4. For assertion_reason / statement_two / statement_count, hit the TARGET answer given in the task exactly (assertion_reason: 0 both true & R explains A; 1 both true & R does not explain A; 2 A true R false; 3 A false R true. statement_count: set `mode` and statements so the count maps to the target index: 0 Only one, 1 Only two, 2 Only three, 3 All four). For assertion_reason avoid cases where whether R "explains" A is arguable; if you target index 2 or 3 one of the two must be plainly false.
5. Add a field `truth` to every statement/assertion question: list of booleans per statement (for assertion_reason: [A_true, R_true]).
6. `source` must be a URL (or several joined by " ; ") that backs the answer; every URL must have been returned by your searches.
7. Output: a JSON list of question objects (schema shapes) written to the path in the task. Final reply max 4 lines: path, question types, any fact you could not double-source.
