# CLAT GK passage generator brief

Read `docs/clat_gk_schema.md` first (six question types, JSON shapes, build mix).

## Hard rules
1. One passage = ~450-500 words of news-style prose on events from the last 9 months, with exact dates, names and numbers.
2. Exactly 6 questions per passage, mixing the six types (see schema "Build mix").
3. **Golden rule: the correct answer must need a fact the passage does not state** (static GK next to the topic, or a related current-affairs fact). Passage-only answers are not allowed.
4. Every fact in the passage and every answer must be backed by a source URL you found in this session. Never fill a gap from memory; if you cannot confirm a fact, change the question.
5. Static-GK facts (Articles, years, institutions) should cite a primary or reference source (indiacode, legislative.gov.in, nobelprize.org, Wikipedia is acceptable as a last resort), not a news story that doesn't support the claim.
6. Avoid ambiguous wording ("originally enacted", "latest", "first") unless the answer is unique.
7. Distractors must be plausible: real names, real years, same category.
8. Anything unconfirmed, or still developing, goes in the test `notes`, not in an answer key.
9. Sources: PIB, The Hindu, Indian Express, LiveLaw, Bar & Bench, SCC Online, PRS, Sansad, official sites. Some hosts are blocked in the cloud environment (e.g. scconline.com, newsonair.gov.in); use WebSearch snippets when WebFetch fails.

## Output
Write the passage object (schema "Passage object", plus `title` and `topic_tags`) to the file named in the task. Do not write anything else.
