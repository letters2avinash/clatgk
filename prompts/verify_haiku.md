# Brief: blind verification of one booklet topic (Haiku verifier)

You are an independent checker. You have NOT seen the stored answers. Use ONLY the booklet text file given in your task
(OCR, ~5-10% garbled). No web search, no outside knowledge: an answer counts as supported only if the booklet text itself supports it.

Input blind file (JSON): topic, subtopics (summary + facts), quizzes (passage + questions; MCQ questions have options; TITA questions have none).
Write the verdict JSON (path in your task), valid JSON, no markdown fences:
{
 "quizzes": [ {"id": "<quiz id>",
    "questions": [ {"n": 1,
        "my_answer": <MCQ: option index 0-3 ; TITA: your short typed answer>,
        "supported": true|false,          // false if the booklet text does not clearly support any answer (or the supporting text is garbled)
        "evidence": {"page": <int>, "quote": "<=25 words copied exactly from the text"},
        "issues": [ "ambiguous" | "multiple_correct" | "no_correct_option" | "answer_stated_in_passage" | "garbled_basis" | "other: <text>" ]   // [] if none
    } ],
    "passage_flags": [ {"claim": "<sentence or clause from the passage>", "problem": "contradicts or is not found in booklet text", "page": <int or null>} ] } ],
 "fact_flags": [ {"subtopic": <i>, "fact": "<summary/fact text>", "problem": "...", "page": <int or null>} ]
}
Procedure: for EVERY question, search the booklet text, decide the answer yourself from the text, copy the evidence quote, then fill the fields.
Be strict: if two options could be defended, issues must include "multiple_correct"; if the question is only answerable from the passage and the passage restates it, include "answer_stated_in_passage" (note: the passage is allowed to give context; flag only when the answer is a near word-for-word restatement).
For match-the-following questions, solve the pairing yourself from the text and give the option index whose pairing is fully correct.
Also check every passage sentence and every subtopic summary/fact against the text; list only genuine contradictions or unsupported specifics in passage_flags / fact_flags (not style).
After writing, validate with python3 -I -c "import json;json.load(open(PATH))" and reply with one line: path, questions checked, number you could not support, passage flags, fact flags.
