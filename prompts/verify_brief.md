# Verifier brief (independent accuracy check of one CLAT GK passage)

You are the independent verifier. You did not write this passage. Assume it contains errors until you have proved otherwise.

Read `docs/clat_gk_schema.md` for the question types and answer index meanings
(assertion_reason: 0 both true & R explains A, 1 both true & R does not explain A, 2 A true R false, 3 A false R true;
statement_two: 0 I only, 1 II only, 2 both, 3 neither; statement_count: index = count-1, `mode` says what is counted).

## Method
1. Do NOT start from the sources listed in the passage. Run your own WebSearch queries (load with ToolSearch "select:WebSearch" if needed). WebFetch fails on many hosts; use snippets and fetch where it works.
2. A claim is CONFIRMED only when at least TWO independent publishers back it (different organisations; Wikipedia and a page copying Wikipedia count as one; exam-prep blogs are weak and count only if they cite a primary source). Primary sources (constitution text, indiacode, official sites) count as strong.
3. Check every factual claim in the passage text (dates, names, numbers, places, titles).
4. For every question:
   - derive the correct answer yourself from your own sources, then compare with the key;
   - for every distractor, check it is actually wrong (a second defensible answer = ambiguous);
   - for statement/assertion types, give a truth value for each statement and re-derive the answer index;
   - flag a GIVEAWAY if the answer appears in the question stem or is stated in the passage;
   - flag EXPLANATION_MISMATCH if the explanation contradicts the key;
   - flag WEAK_SOURCE if the cited `source` does not support the claim.
5. If a question can be repaired with facts you CONFIRMED (2 independent sources), supply a replacement question object of the same type and the same target answer index (the replacement must pass the same checks). Otherwise recommend DROP.

## Output
Write JSON to the path given in the task (do not edit the passage file):
{
 "passage_file": "...",
 "passage_claims": [{"claim": "...", "verdict": "CONFIRMED|SINGLE_SOURCE|DISPUTED|WRONG|UNVERIFIABLE", "sources": ["url","url"], "note": "..."}],
 "questions": [{"index": 1, "verdict": "OK|FIX|DROP", "my_answer": "...", "key_answer_correct": true,
                "truth_values": null, "issues": ["GIVEAWAY","AMBIGUOUS","WRONG_ANSWER","EXPLANATION_MISMATCH","WEAK_SOURCE","UNSUPPORTED"],
                "sources": ["url","url"], "fix": null, "note": "..."}],
 "passage_fixes": [{"old": "exact text", "new": "replacement text or empty to delete", "reason": "..."}],
 "summary": "2-3 sentences"
}
Be strict. "OK" means two independent sources confirm the answer AND no distractor is defensible AND no issue flags apply.
Final reply: max 6 lines (file path, counts of OK/FIX/DROP, number of passage claims by verdict).
