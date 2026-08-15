# Phase 17.3 — Checkpoint Failure Category Consistency & Resume Validation

## Objective

Fix the Phase 17.2 resume behavior so quota-exhausted research-paper cases stored in the checkpoint are correctly recognized and retried.

The current Phase 17 checkpoint contains 15 failed cases with:

```text
category: "llm_failure"
reason: "LLM quota exhausted (daily token limit reached)."
```

However, `run.py` currently retries a failed case only when:

```text
failed_info["category"] == LiveFailureCategory.LLM_QUOTA_EXCEEDED.name
```

Therefore the existing checkpoint entries do not match the retry condition and are skipped.

Do not change verification agents, retrieval logic, evidence ranking, offline evaluation, or benchmark dataset definitions.

---

## 1. Inspect the failure-category flow

Review:

```text
backend/app/evaluation/run.py
backend/app/evaluation/live_diagnostics.py
backend/app/services/llm/provider.py
backend/app/evaluation/checkpoint.py
```

Trace the complete flow:

```text
LLM provider exception
        ↓
LLMProviderError
        ↓
LiveFailureCategory classification
        ↓
LiveCaseResult
        ↓
checkpoint failed_cases
        ↓
resume decision
```

Determine why a quota exhaustion is currently persisted as:

```text
llm_failure
```

instead of:

```text
LLM_QUOTA_EXCEEDED
```

Do not blindly change the resume comparison without fixing the underlying category representation.

---

## 2. Establish one canonical checkpoint category

Checkpoint failure categories must use the canonical `LiveFailureCategory` names.

For quota exhaustion, persist:

```text
LLM_QUOTA_EXCEEDED
```

not:

```text
llm_failure
```

The checkpoint should therefore look conceptually like:

```json
{
  "failed_cases": {
    "cas9_supports_001": {
      "category": "LLM_QUOTA_EXCEEDED",
      "reason": "LLM quota exhausted (daily token limit reached)."
    }
  }
}
```

Use the existing enum rather than introducing a second category system.

---

## 3. Make resume logic robust

Update resume handling so that:

### Completed cases

If a case exists in:

```text
completed_case_ids
```

skip it permanently.

### Quota failures

If a case exists in `failed_cases` and its category is:

```text
LLM_QUOTA_EXCEEDED
```

retry it.

### Non-quota failures

If a case failed for another category, do not automatically retry it.

### Legacy checkpoint compatibility

The existing Phase 17 checkpoint already contains:

```text
category: "llm_failure"
```

with a reason explicitly stating:

```text
LLM quota exhausted (daily token limit reached).
```

The implementation must handle this existing checkpoint safely.

Preferred approach:

* Detect legacy quota-failure records using both category and reason.
* Treat the record as quota-exhausted when the reason clearly identifies daily LLM quota exhaustion.
* Do not classify arbitrary `llm_failure` records as quota failures.

This allows the current Phase 17 checkpoint to resume without manually editing the JSON.

---

## 4. Persist the canonical category on retry failure

When a retried case fails again because of quota exhaustion:

```text
failed_cases[case_id]["category"]
```

must be saved as:

```text
LLM_QUOTA_EXCEEDED
```

The reason should remain human-readable.

When a quota-failed case succeeds:

1. Add its ID to `completed_case_ids`.
2. Remove its entry from `failed_cases`.
3. Persist the checkpoint immediately.

---

## 5. Verify checkpoint state before processing

On resume, print useful diagnostics such as:

```text
Resuming from checkpoint with 0 completed cases.
Retryable quota-failed cases: 15
Non-retryable failed cases: 0
```

Do not expose API keys, provider credentials, or sensitive information.

The count must be calculated from the actual checkpoint and live-eligible dataset.

---

## 6. Fix resume accounting

The current run can finish with:

```text
Successfully evaluated: 0
Retrieval/infrastructure failures: 0
Verification failures: 0
Skipped: 0
```

even though the checkpoint contains 15 failed cases.

Fix the accounting so cases skipped because they are completed or permanently failed are handled consistently.

For quota-failed cases selected for retry:

```text
retry → evaluate → update result/checkpoint
```

They must not disappear silently from the run.

---

## 7. Preserve quota-abort behavior

Do not reintroduce long provider retry sleeps.

Permanent daily quota exhaustion must continue to:

```text
LLM_QUOTA_EXCEEDED
```

and abort immediately.

Do not call `time.sleep()` for the provider's permanent daily-token quota retry.

The existing provider behavior from Phase 17.1 must remain intact.

---

## 8. Add focused tests

Add or extend tests covering:

### Test 1 — Canonical quota checkpoint

Given an `LLM_QUOTA_EXCEEDED` failure:

```text
checkpoint["failed_cases"][case_id]["category"]
```

must equal:

```text
LLM_QUOTA_EXCEEDED
```

### Test 2 — Legacy checkpoint compatibility

Given:

```json
{
  "category": "llm_failure",
  "reason": "LLM quota exhausted (daily token limit reached)."
}
```

the resume logic must identify the case as retryable.

### Test 3 — Non-quota LLM failure

Given:

```json
{
  "category": "llm_failure",
  "reason": "Some unrelated provider failure"
}
```

the case must not automatically retry.

### Test 4 — Successful quota retry

When a previously quota-failed case succeeds:

```text
completed_case_ids += case_id
failed_cases -= case_id
```

and the checkpoint is persisted.

### Test 5 — Repeated quota failure

When retrying a quota-failed case results in another daily quota exhaustion:

```text
failed_cases[case_id]["category"] == "LLM_QUOTA_EXCEEDED"
```

and the run exits cleanly.

### Test 6 — Existing checkpoint

Load the actual checkpoint structure used by Phase 17 and verify that the 15 legacy quota-failed cases are detected as retryable.

Do not make real LLM calls in unit tests.

---

## 9. Run regression tests

Run:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify\backend
python -m pytest -q
```

Expected result:

```text
332+ passed
```

No existing tests should regress.

---

## 10. Validate the resume flow

Do NOT delete the existing Phase 17 checkpoint.

Run:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir .\evaluation\checkpoints\phase17 --resume-live
```

Because the checkpoint contains 15 quota-failed cases, the evaluator should now identify them as retryable.

If the Groq quota is still exhausted, expected behavior is:

```text
Retryable quota-failed cases: 15
...
LLM quota exhausted
...
Live Evaluation Interrupted
```

and the checkpoint should remain intact.

It must NOT:

* silently process zero cases
* wait for 168 seconds
* wait for 3526 seconds
* crash with `AttributeError`
* delete the checkpoint
* mark quota failures as successful

---

## 11. Verify checkpoint after the run

Run:

```powershell
Get-Content .\evaluation\checkpoints\phase17\live_checkpoint.json
```

Verify:

* `completed_case_ids` remains correct.
* Quota failures remain recorded if quota is still exhausted.
* Their category is canonical `LLM_QUOTA_EXCEEDED`.
* The timestamp is timezone-aware.
* No checkpoint corruption occurred.

---

## 12. Final validation

Run:

```powershell
git status
git diff --check
git diff --stat
```

Do not modify:

```text
implementation1.md
```

unless explicitly required by the project workflow.

Do not modify `.env` or API keys.

Do not change the benchmark dataset.

Do not change verification-agent behavior.

---

## Definition of Done

Phase 17.3 is complete only when:

* [ ] Existing Phase 17 checkpoint is recognized.
* [ ] Its 15 legacy quota failures are detected as retryable.
* [ ] New quota failures are persisted as `LLM_QUOTA_EXCEEDED`.
* [ ] Non-quota failures are not automatically retried.
* [ ] Successful retries move cases to `completed_case_ids`.
* [ ] Permanent quota exhaustion aborts immediately without provider retry sleep.
* [ ] No `AttributeError` occurs during quota abort.
* [ ] Checkpoint remains valid after interruption.
* [ ] Focused resume tests pass.
* [ ] Full test suite passes.
* [ ] No real API calls are made by unit tests.
* [ ] No unrelated project modules are changed.
