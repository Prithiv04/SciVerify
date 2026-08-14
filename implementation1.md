# SciVerify — Phase 15.1: Quota-Aware & Resumable Live Evaluation

## Objective

Make SciVerify's live evaluation system resilient to LLM provider quota exhaustion, rate limits, and interruptions.

The current live evaluation successfully connects to Groq and starts real verification, but the Groq free-tier 100k tokens/day limit is exhausted after approximately 5–6 cases because each case can consume roughly 15k–20k tokens.

Currently, the evaluator can remain running while waiting for the provider quota to recover.

This phase must change the **evaluation infrastructure only** so that:

1. Quota exhaustion is detected immediately.
2. The evaluation stops gracefully.
3. Completed cases are persisted.
4. Completed cases are not rerun.
5. Remaining cases can be resumed later.
6. Quota failures are never counted as wrong verdicts.
7. Existing production verification behavior remains unchanged.
8. Offline evaluation remains completely unchanged.

---

# Important Constraints

## DO NOT modify

* Verdict logic
* Prosecutor agent
* Defender agent
* Adjudicator agent
* Agent prompts
* Evidence ranking
* Evidence retrieval behavior
* Claim traceability logic
* Verification validation
* Production verification pipeline
* Offline fixtures
* Offline evaluation logic
* `baseline.json`
* Benchmark expected verdicts

This phase is strictly about **live evaluation orchestration and persistence**.

Do not modify the system simply to improve benchmark accuracy.

---

# Current Problem

Current behavior:

```text
Live evaluation
      ↓
Case 1
      ↓
LLM request
      ↓
Case 2
      ↓
...
      ↓
Groq quota exhausted
      ↓
LLM requests continue/retry
      ↓
Long wait
```

Desired behavior:

```text
Live evaluation
      ↓
Case 1 ── SUCCESS → save
Case 2 ── SUCCESS → save
Case 3 ── SUCCESS → save
...
Case N ── QUOTA EXCEEDED
      ↓
STOP IMMEDIATELY
      ↓
SAVE RESULTS
      ↓
REPORT QUOTA EXHAUSTION
      ↓
EXIT CLEANLY
```

Later:

```text
Resume
  ↓
Load previous results
  ↓
Skip completed cases
  ↓
Continue from remaining case
```

---

# Step 1 — Inspect Existing Evaluation Architecture

Before changing anything, inspect:

```text
backend/app/evaluation/run.py
backend/app/evaluation/live_diagnostics.py
backend/app/evaluation/evaluator.py
backend/app/schemas/verification.py
backend/app/services/verification_service.py
backend/app/services/llm/
backend/evaluation/results/
```

Determine:

* How live cases are currently selected
* How results are currently written
* How retries are implemented
* How `LLM_QUOTA_EXCEEDED` is currently classified
* Whether provider errors already expose status codes/messages
* How `latest.json` and `latest.md` are generated
* Whether a persistent per-case result structure already exists

Do not duplicate existing infrastructure unnecessarily.

---

# Step 2 — Verify Quota Failure Classification

Ensure quota exhaustion is represented as:

```text
LLM_QUOTA_EXCEEDED
```

and belongs to:

```text
VERIFICATION_FAILURE_CATEGORIES
```

It must NOT be classified as:

```text
WRONG_VERDICT
```

or:

```text
RETRIEVAL_FAILURE
```

If this classification already works correctly, do not modify it.

Add tests only if coverage is missing.

---

# Step 3 — Detect Quota Exhaustion Early

Identify the actual provider response/error used when Groq reaches its daily quota.

Handle provider responses such as:

```text
HTTP 429
rate limit
quota exceeded
daily token limit
tokens per day
TPD
insufficient quota
```

Do not rely solely on matching one exact error string.

Use the existing provider abstraction wherever possible.

The final classification must be deterministic:

```text
LLM_QUOTA_EXCEEDED
```

Do not classify every HTTP 429 as quota exhaustion if the existing system distinguishes ordinary rate limiting from daily quota exhaustion.

Preserve that distinction.

---

# Step 4 — Stop Retries on Permanent Quota Exhaustion

Current retry behavior must not repeatedly retry a known daily quota exhaustion.

For:

```text
LLM_QUOTA_EXCEEDED
```

the evaluator should:

```text
NO further retry
      ↓
mark current case as quota-failed
      ↓
stop the live evaluation run
```

Do not wait for the quota reset.

Normal transient failures may continue using the existing retry behavior.

For example:

```text
NETWORK_TIMEOUT
→ existing retry behavior

HTTP 500
→ existing retry behavior

temporary provider failure
→ existing retry behavior

LLM_QUOTA_EXCEEDED
→ no retry
→ stop evaluation
```

---

# Step 5 — Add Persistent Live Evaluation Checkpoint

Create a checkpoint mechanism for live evaluation.

Preferred location:

```text
backend/evaluation/results/live_checkpoint.json
```

The checkpoint should contain enough information to resume safely.

Example structure:

```json
{
  "dataset": "dataset.json",
  "started_at": "...",
  "updated_at": "...",
  "status": "quota_exhausted",
  "completed_case_ids": [],
  "failed_case_ids": [],
  "skipped_case_ids": [],
  "quota_failed_case_id": null
}
```

Use the actual project's existing result schema where possible.

Do NOT create unnecessary duplicate representations if `latest.json` can safely support checkpoint information.

---

# Step 6 — Persist After Every Case

Do not wait until all 15 cases finish before saving.

After every successfully completed case:

```text
evaluate case
     ↓
persist result
     ↓
update checkpoint
     ↓
continue
```

If the process crashes after case 4, cases 1–4 must remain available.

If quota exhaustion occurs during case 5, cases 1–4 must remain saved.

---

# Step 7 — Resume Support

Add a CLI option:

```text
--resume-live
```

Expected behavior:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --resume-live
```

The evaluator should:

1. Load the existing checkpoint.
2. Identify completed cases.
3. Skip completed cases.
4. Continue with remaining live-eligible cases.
5. Preserve previous results.
6. Continue saving after each case.

Example:

```text
Previous run:
15 live eligible

Completed:
case 1
case 2
case 3
case 4

Quota failure:
case 5

Resume:
skip case 1
skip case 2
skip case 3
skip case 4
retry case 5
continue with case 6...
```

Do not rerun successfully completed cases.

---

# Step 8 — Handle the Current Quota-Failed Case

The case that encounters:

```text
LLM_QUOTA_EXCEEDED
```

should be recorded as a verification failure.

It must NOT receive:

```text
actual_verdict
```

and must NOT contribute to:

```text
verdict accuracy
evidence metrics
traceability metrics
confidence metrics
```

It should appear in diagnostics as:

```text
status: failed
failure_category: LLM_QUOTA_EXCEEDED
```

When resuming later, the quota-failed case should be eligible for retry.

---

# Step 9 — Safe Result Aggregation

When resuming, combine:

```text
previous successful results
+
new successful results
```

without duplicating cases.

The final metrics must calculate only from successfully evaluated cases.

For example:

```text
15 live eligible
5 successful
1 quota failed
9 not yet evaluated
```

should NOT produce:

```text
Cases: 15
```

for verdict accuracy.

Instead:

```text
Evaluated: 5
Quota failures: 1
Remaining: 9
```

and:

```text
Verdict Accuracy
= correct successful evaluations
  /
  successfully evaluated cases
```

---

# Step 10 — Partial Run Reporting

When the evaluator stops because of quota exhaustion, print something similar to:

```text
Live Evaluation Interrupted
---------------------------

Reason:
LLM quota exhausted

Live eligible:              15
Successfully evaluated:      5
Current quota failure:       1
Remaining:                   9

Results saved.
Resume with:

python -m app.evaluation.run --live --skip-unhealthy --resume-live
```

Do not make the process appear as if the benchmark completed.

---

# Step 11 — Completion Reporting

When all live-eligible cases are successfully processed:

```text
Live Evaluation Complete
------------------------

Live eligible:              15
Successfully evaluated:     15
Retrieval failures:          X
Verification failures:       X
Skipped:                     X
Remaining:                   0
```

Then generate the final live metrics.

---

# Step 12 — Checkpoint Safety

Checkpoint handling must be robust against:

* Ctrl+C
* terminal closing
* Antigravity stopping the task
* provider quota exhaustion
* network interruption
* Python process failure

Use atomic or otherwise safe file writing where practical.

Do not corrupt the checkpoint if the process is interrupted while writing.

---

# Step 13 — Do Not Store Secrets

The checkpoint/result files must never contain:

* API keys
* authorization headers
* tokens
* `.env` contents
* provider credentials

Only evaluation metadata and results should be persisted.

---

# Step 14 — Tests

Add tests for every new behavior.

## Test 1 — Quota classification

Verify a provider quota error becomes:

```text
LLM_QUOTA_EXCEEDED
```

---

## Test 2 — Quota does not retry

Verify:

```text
LLM_QUOTA_EXCEEDED
```

does not trigger the existing retry loop.

---

## Test 3 — Quota stops evaluation

Given:

```text
case 1 → SUCCESS
case 2 → SUCCESS
case 3 → QUOTA EXCEEDED
case 4 → SUCCESS
```

verify:

```text
case 1 evaluated
case 2 evaluated
case 3 quota failed
case 4 not executed
```

---

## Test 4 — Checkpoint persistence

Verify that after two successful cases the checkpoint contains those case IDs.

---

## Test 5 — Resume

Given:

```text
completed:
case 1
case 2
case 3
```

verify `--resume-live` does not execute those cases again.

---

## Test 6 — Resume quota-failed case

Verify a case previously marked:

```text
LLM_QUOTA_EXCEEDED
```

can be retried on a later run.

---

## Test 7 — No duplicate results

Run evaluation twice and verify each case appears only once in the final aggregated results.

---

## Test 8 — Accuracy denominator

Verify failed/quota cases are excluded from verdict accuracy.

---

## Test 9 — Offline regression

Verify existing offline evaluation behavior remains unchanged.

---

# Step 15 — Required Validation

Run:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify\backend

python -m pytest -q
```

Then:

```powershell
python -m app.evaluation.run
```

Expected:

```text
Cases: 30
Verdict Accuracy: 100.0%
Regression: PASS
```

Then:

```powershell
python -m app.evaluation.run --live-health-check
```

Finally, with the real LLM provider configured:

```powershell
python -m app.evaluation.run --live --skip-unhealthy
```

If quota is exhausted, the command should terminate gracefully instead of waiting for the provider reset.

Then verify:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --resume-live
```

---

# Step 16 — Verify Git Changes

After implementation:

```powershell
git status
git diff --stat
git diff --name-only
```

Review every changed file.

Do not commit:

```text
.env
API keys
provider credentials
temporary logs
personal environment files
```

Do not modify `baseline.json` automatically.

Do not modify offline fixtures.

---

# Success Criteria

Phase 15.1 is complete only when:

1. `LLM_QUOTA_EXCEEDED` is detected correctly.
2. Permanent quota exhaustion does not trigger repeated retries.
3. Live evaluation stops gracefully on quota exhaustion.
4. Completed cases are persisted immediately.
5. A checkpoint is created.
6. `--resume-live` works.
7. Completed cases are not rerun.
8. Quota-failed cases can be retried later.
9. Failed cases are excluded from verdict accuracy.
10. No duplicate cases appear in aggregated results.
11. Ctrl+C/interruption does not destroy completed results.
12. Offline evaluation remains 30/30 and 100%.
13. All tests pass.
14. No production verification logic is changed.
15. No secrets are committed.

---

# Final Report Required

At completion report exactly:

## Files Changed

List every modified and created file.

## Tests

```text
pytest:
XXX passed
```

## Offline Evaluation

```text
Cases:
Accuracy:
Regression:
```

## Live Health Check

```text
Healthy:
Unindexed:
Paywalled:
Blocked:
Unknown:
```

## Live Evaluation

```text
Live eligible:
Successfully evaluated:
Retrieval failures:
Verification failures:
Quota failures:
Remaining:
```

## Resume Test

State whether:

```text
--resume-live
```

was successfully tested.

## Git Status

Report whether the working tree is clean.

---

# Phase Boundary

Do NOT proceed automatically to Phase 16 after this implementation.

Once Phase 15.1 is complete, the next step is to run the live benchmark across multiple quota windows and obtain a real live-quality dataset.

Only after the complete live benchmark is available should we create Phase 16 for actual live verification accuracy improvements.
