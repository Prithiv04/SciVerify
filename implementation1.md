# SciVerify — Live Evaluation Reliability & Retrieval Diagnostics

## Goal

Improve `python -m app.evaluation.run --live` so retrieval/API failures are clearly separated from actual SciVerify verification failures.

Do NOT modify:
- Prosecutor / Defender / Adjudicator
- Evidence ranking
- Verification validator
- Claim traceability
- Frontend
- Offline evaluation behavior
- Existing baseline unless absolutely necessary

---

## Phase 1 — Inspect Existing Code

Inspect:

- `backend/app/evaluation/`
- `backend/evaluation/dataset.json`
- paper/DOI retrieval services
- full-text/document retrieval
- `app.evaluation.run`
- existing live evaluator/error handling

Reuse existing retrieval logic. Do not duplicate it.

---

## Phase 2 — Structured Live Failure Classification

Add deterministic failure categories:

- `DOI_NOT_FOUND`
- `FULL_TEXT_UNAVAILABLE`
- `ANTI_BOT_BLOCKED`
- `HTTP_403`
- `HTTP_404`
- `RATE_LIMITED`
- `INVALID_DOCUMENT`
- `NETWORK_TIMEOUT`
- `NETWORK_ERROR`
- `LLM_FAILURE`
- `LLM_QUOTA_EXCEEDED`
- `LLM_TIMEOUT`
- `INVALID_RESPONSE`
- `UNKNOWN_FAILURE`

Infrastructure/retrieval failures must NOT be classified as verification failures.

Example:

PMC anti-bot page
→ `ANTI_BOT_BLOCKED`
→ status `skipped`
→ NOT a wrong verdict.

---

## Phase 3 — Per-Case Live Result

Extend live evaluation results with structured information:

```json
{
  "case_id": "...",
  "status": "evaluated | skipped | failed",
  "expected_verdict": "...",
  "actual_verdict": "...",
  "confidence": 0.82,
  "failure_category": null,
  "failure_reason": null,
  "retrieval_attempts": 3,
  "elapsed_seconds": 4.2
}