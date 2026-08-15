# Phase 17.2 — Resumable Research-Paper Live Benchmark

## Objective

Fix the SciVerify live **research-paper benchmark** resume workflow.

The live benchmark evaluates the 30 research-paper verification cases in the benchmark dataset. The health check currently identifies 15 healthy/live-eligible cases.

When the Groq daily LLM quota is exhausted, the live evaluation correctly stops and saves those affected benchmark cases in the checkpoint.

The current problem is that `--resume-live` treats those quota-failed cases as already processed, so after the quota resets it does not retry them.

The goal is:

**Quota failure → save checkpoint → stop → quota resets → `--resume-live` → retry the affected research-paper cases.**

---

## Current Situation

The Phase 17 checkpoint currently contains:

```text
completed_case_ids: []
```

and 15 entries in:

```text
failed_cases
```

Each failure represents:

```text
LLM quota exhausted (daily token limit reached).
```

Running:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir ./evaluation/checkpoints/phase17 --resume-live
```

currently results in:

```text
Resuming from checkpoint with 0 completed cases.
Successfully evaluated: 0
```

This means quota-failed research-paper cases are not being retried.

---

# Implementation Requirements

## 1. Keep successful benchmark cases completed

Cases stored in:

```text
completed_case_ids
```

must NOT be executed again during resume.

Example:

```text
case_001 → successfully evaluated
        → completed_case_ids
        → skip on future --resume-live
```

This prevents unnecessary LLM quota consumption.

---

## 2. Retry quota-failed research-paper cases

During `--resume` / `--resume-live`, inspect `failed_cases`.

If a failure represents:

```text
LLM_QUOTA_EXCEEDED
```

or the persisted failure contains:

```text
LLM quota exhausted
```

then that benchmark case must be considered **retryable**.

Example:

```json
{
  "case_001": {
    "category": "llm_failure",
    "reason": "LLM quota exhausted (daily token limit reached)."
  }
}
```

`case_001` must be retried after the provider quota becomes available.

---

## 3. Do not retry every failure

Only quota-exhaustion failures should receive this special resume behavior.

Do NOT automatically retry all entries in `failed_cases`.

Preserve existing handling for:

* retrieval failures
* infrastructure failures
* generic LLM failures
* verification failures
* deterministic failures

---

## 4. Successful retry

If a previously quota-failed research-paper case succeeds:

1. Add the case ID to `completed_case_ids`.
2. Remove the case ID from `failed_cases`.
3. Persist the updated checkpoint.
4. Continue to the next eligible case.

Expected state:

```text
Before:

completed_case_ids = []

failed_cases = {
    case_001: quota failure
}
```

After successful resume:

```text
completed_case_ids = [
    case_001
]

failed_cases = {}
```

---

## 5. Quota is still exhausted

If the resumed benchmark encounters another daily quota exhaustion:

1. Record/update the case in `failed_cases`.
2. Do NOT add it to `completed_case_ids`.
3. Persist the checkpoint immediately.
4. Abort the live benchmark cleanly.
5. Return exit code `1`.
6. Do NOT repeatedly retry the same permanent quota failure.
7. Do NOT wait for the provider's long retry timer.

The existing provider-level permanent quota detection must remain intact.

---

# 6. Preserve Research-Paper Benchmark Scope

This phase is ONLY about the live research-paper evaluation benchmark.

Do NOT modify:

* research-paper benchmark dataset
* verification agents
* evidence ranking
* retrieval algorithms
* citation verification logic
* offline evaluation logic
* verdict classification
* production application behavior

The benchmark cases themselves must remain unchanged.

---

# 7. Checkpoint Safety

Preserve the existing checkpoint architecture.

Do not remove or redesign:

* `run_id`
* `completed_case_ids`
* `failed_cases`
* timestamp
* atomic checkpoint writing
* checkpoint directory support

The checkpoint must remain safe if the process is interrupted.

---

# 8. CLI Compatibility

Both commands must continue working:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir ./evaluation/checkpoints/phase17 --resume
```

and:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir ./evaluation/checkpoints/phase17 --resume-live
```

`--resume-live` must remain an alias for `--resume`.

---

# 9. Tests

Add/update tests for the following.

### Test A — Completed research-paper case is skipped

Given a case exists in:

```text
completed_case_ids
```

verify that resume does not execute it.

### Test B — Quota-failed research-paper case is retried

Given:

```json
{
  "failed_cases": {
    "case_001": {
      "category": "llm_failure",
      "reason": "LLM quota exhausted (daily token limit reached)."
    }
  }
}
```

verify that `--resume-live` attempts `case_001`.

### Test C — Successful retry clears failure

After successful evaluation:

```text
case_001 ∈ completed_case_ids
case_001 ∉ failed_cases
```

### Test D — Quota failure remains retryable

If the retry encounters quota exhaustion again:

```text
case_001 ∉ completed_case_ids
case_001 ∈ failed_cases
```

and the evaluator exits with:

```text
exit code 1
```

### Test E — Non-quota failures preserve existing behavior

Verify that a generic failure is NOT automatically converted into a retryable quota failure.

### Test F — CLI alias

Verify:

```text
--resume-live
```

correctly enables the existing resume behavior.

---

# 10. Full Regression Test

Run:

```powershell
cd backend
python -m pytest -q
```

All existing tests plus the new tests must pass.

Do not weaken or remove existing tests just to make the new tests pass.

---

# 11. Validate the Existing Phase 17 Checkpoint

Do NOT manually edit or delete:

```text
backend/evaluation/checkpoints/phase17/live_checkpoint.json
```

Use the existing checkpoint to validate the new resume behavior.

After implementation, run:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir ./evaluation/checkpoints/phase17 --resume-live
```

### If Groq quota is still exhausted

Expected behavior:

```text
Resuming from checkpoint...
Retrying quota-failed cases...
LLM quota exhausted...
Checkpoint saved
Live evaluation interrupted
Exit code: 1
```

The process should stop quickly rather than hanging for several minutes.

### If Groq quota has reset

The 15 previously quota-failed research-paper cases should actually be attempted.

Successful cases should move into:

```text
completed_case_ids
```

Remaining quota failures should stay in:

```text
failed_cases
```

---

# 12. Validation Output

After implementation, report:

```text
Tests:
XXX passed

Resume behavior:
PASS / FAIL

Quota-failed cases retryable:
PASS / FAIL

Completed cases skipped:
PASS / FAIL

Checkpoint persistence:
PASS / FAIL

Quota abort:
PASS / FAIL

--resume-live alias:
PASS / FAIL
```

Do not claim that the real live benchmark succeeded unless the external LLM provider actually allowed the calls.

---

## Constraints

* No API keys or `.env` modifications.
* No benchmark dataset modifications.
* No changes to verification agents.
* No changes to evidence ranking.
* No changes to offline evaluation logic.
* No unnecessary refactoring.
* Do not consume external LLM quota merely for testing if unit/mock tests can validate the behavior.
* Preserve all existing Phase 17 quota-abort functionality.

## Success Criteria

Phase 17.2 is complete when:

```text
Research-paper live benchmark
        ↓
LLM quota exhausted
        ↓
Checkpoint saved
        ↓
Process exits cleanly
        ↓
Quota resets
        ↓
--resume-live
        ↓
Previously successful cases skipped
        ↓
Previously quota-failed cases retried
        ↓
Successful retries → completed_case_ids
        ↓
Remaining quota failures → failed_cases
```

The final implementation must pass the complete test suite and preserve all existing SciVerify functionality.
