# CLAT GK Question-Type Schema

Six recurring formats, each with a fixed JSON shape. A test is a list of passages;
each passage has `text`, `sources`, and a `questions` list mixing these types freely.

Golden rule for every type: the **answer must require a fact the passage does not
state outright** — static GK adjacent to the passage topic, or a related
current-affairs fact. If the passage alone answers it, it's an RC question, not GK.

## 1. direct
Single best-answer MCQ, 4 options.
```json
{"type": "direct", "q": "...", "options": ["A","B","C","D"], "answer": 0,
 "explanation": "...", "source": "..."}
```

## 2. assertion_reason
Fixed 4-option frame — never vary the option wording, only A/R content.
```json
{"type": "assertion_reason", "assertion": "...", "reason": "...", "answer": 0,
 "explanation": "...", "source": "..."}
```
`answer`: 0 = both true, R correctly explains A · 1 = both true, R does NOT explain A ·
2 = A true, R false · 3 = A false, R true.

## 3. match
List I / List II pairing; options are lettered combinations.
```json
{"type": "match", "list1": ["I. ...", "II. ...", "III. ...", "IV. ..."],
 "list2": ["A. ...", "B. ...", "C. ...", "D. ..."],
 "options": ["I-A, II-B, III-C, IV-D", "I-B, II-A, III-D, IV-C", "...", "..."],
 "answer": 0, "explanation": "...", "source": "..."}
```

## 4. statement_two
Exactly 2 statements, fixed option frame.
```json
{"type": "statement_two", "statements": ["I. ...", "II. ..."], "answer": 2,
 "explanation": "...", "source": "..."}
```
`answer`: 0 = I only · 1 = II only · 2 = Both I and II · 3 = Neither I nor II.

## 5. statement_multi
2–3 statements; options are explicit combinations (write them out — they vary per question).
```json
{"type": "statement_multi", "statements": ["I. ...", "II. ...", "III. ..."],
 "options": ["I and II only", "II and III only", "I and III only", "All of the above"],
 "answer": 3, "explanation": "...", "source": "..."}
```

## 6. statement_count
3–4 statements; options are always Only one / Only two / Only three / All four.
Specify `mode` so the explanation and options agree on what's being counted.
```json
{"type": "statement_count", "statements": ["1. ...", "2. ...", "3. ...", "4. ..."],
 "mode": "incorrect", "answer": 1, "explanation": "...", "source": "..."}
```
`answer` index maps to ["Only one","Only two","Only three","All four"].

## Passage object
```json
{"text": "...", "sources": ["url", "..."], "questions": [ ...mixed types above... ]}
```

## Test object
```json
{"title": "...", "date": "YYYY-MM-DD", "duration_minutes": 10,
 "marks_correct": 1, "marks_wrong": -0.25, "notes": "...", "passages": [ ... ]}
```

## Build mix per passage (matches observed CLAT pattern)
~6 questions/passage: 1–2 direct, 1 assertion_reason, 1 match, 1 statement_two,
1 statement_multi or statement_count. Vary which types repeat across passages so
no two consecutive passages use the identical sequence.
