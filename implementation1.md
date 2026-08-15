# SciVerify — Phase 17: Real Live Benchmark Execution & Provider Validation

## Objective

Execute SciVerify's **real live LLM evaluation** against the healthy benchmark cases and obtain the first trustworthy live-performance measurements.

Phase 15.1 and 15.2 already implemented quota-aware evaluation, checkpoint persistence, quota detection, and resume support. Phase 16 stabilized the tests and edge cases.

**Do not redesign or rewrite those systems.**

The primary goal of Phase 17 is to **run the existing system successfully and capture real live benchmark results**.

---

## Current State

The project currently has:

* 30 benchmark cases.
* 15 healthy/live-eligible cases.
* 11 unindexed cases.
* 4 paywalled cases.
* Offline evaluation: **30/30 cases, 100% verdict accuracy**.
* Existing live evaluation CLI.
* Health-check support.
* `--skip-unhealthy`.
* Checkpoint persistence.
* `--resume`.
* Quota detection.
* Graceful quota-abort behavior.
* 330+ passing automated tests.
* No production verification logic should be changed for this phase.

The previous live evaluation was blocked by the Groq free-tier daily token limit.

---

# Phase 17 Scope

## 1. Repository Preflight

Before making any code changes:

Run:

```powershell
git status
git log -1 --oneline
```

Verify the working tree is clean.

Then inspect the current evaluation implementation:

```text
backend/app/evaluation/run.py
backend/app/evaluation/live_diagnostics.py
backend/app/evaluation/checkpoint.py
backend/app/evaluation/metrics.py
backend/app/evaluation/results/
backend/evaluation/
```

Do not modify files merely because they exist.

---

# 2. Run the Existing Test Suite

Run:

```powershell
cd backend
python -m pytest -q
```

Expected:

```text
330+ passed
```

If tests fail:

1. Diagnose the failure.
2. Fix only regressions directly related to the live evaluation workflow.
3. Do not change production verification behavior.
4. Re-run the complete test suite.

Do not proceed to the real LLM benchmark while the test suite is failing.

---

# 3. Run Live Health Check

Run:

```powershell
python -m app.evaluation.run --live-health-check
```

Verify the health report.

Expected benchmark distribution is approximately:

```text
Total cases: 30
Healthy: 15
Unindexed: 11
Paywalled: 4
Blocked: 0
Unknown: 0
```

The exact values should come from the current health-check output rather than being hardcoded.

Confirm that the health report is written successfully.

---

# 4. Provider Validation

Before starting the full benchmark, verify that the configured LLM provider is actually usable.

The previous Groq provider exhausted its daily TPD quota.

Do NOT repeatedly call an exhausted provider.

The provider must have enough available quota to process the live benchmark.

Requirements:

* Use the existing provider abstraction.
* Do not hardcode API keys.
* Do not modify `.env` files programmatically.
* Do not commit secrets.
* Do not bypass the provider abstraction.
* Do not change verification agents simply to accommodate a provider.

If the configured provider is unavailable because of quota:

```text
STOP the live benchmark.
```

Report clearly that the benchmark cannot proceed until a provider with sufficient quota is configured.

Do not wait for extremely long provider retry intervals.

---

# 5. Clean Benchmark Checkpoint

Before starting a completely new benchmark run, ensure that an old checkpoint is not accidentally reused.

Use a dedicated directory, for example:

```text
backend/evaluation/checkpoints/phase17/
```

The checkpoint directory must remain ignored by Git.

Verify:

```powershell
Get-ChildItem .\evaluation\checkpoints\phase17
```

If this is a fresh Phase 17 run, remove only stale Phase 17 checkpoint state.

Do NOT delete unrelated evaluation results or source files.

---

# 6. Execute the Live Benchmark

Run:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir .\evaluation\checkpoints\phase17
```

The evaluator should process only the healthy benchmark cases.

Expected:

```text
Total benchmark cases: 30
Healthy/live eligible: 15
Skipped unhealthy: 15
```

The exact values must come from the health-check result.

---

# 7. Checkpoint Behavior

During execution, verify that the checkpoint is updated after successful cases.

Expected checkpoint behavior:

```text
Case 1 completed
    ↓
checkpoint updated

Case 2 completed
    ↓
checkpoint updated

Case 3 completed
    ↓
checkpoint updated
```

If the provider encounters a quota failure:

```text
LLM quota detected
        ↓
record failure
        ↓
persist checkpoint
        ↓
stop safely
```

The process must NOT sit for hundreds of seconds retrying a known daily TPD exhaustion.

---

# 8. Resume Validation

If the benchmark is interrupted or stops because of provider quota, verify that the checkpoint contains completed cases.

Inspect:

```powershell
Get-Content .\evaluation\checkpoints\phase17\*.json
```

Then resume with:

```powershell
python -m app.evaluation.run --live --skip-unhealthy --checkpoint-dir .\evaluation\checkpoints\phase17 --resume
```

Verify:

* Previously completed cases are skipped.
* Completed cases are not sent to the LLM again.
* Remaining eligible cases continue processing.
* Checkpoint state is updated after each newly completed case.
* No duplicate benchmark results are created.

---

# 9. Capture Live Results

Once the benchmark completes, locate the generated evaluation results.

Inspect:

```text
backend/evaluation/results/
```

and the Phase 17 checkpoint directory.

Identify:

* Number of completed live cases.
* Number of skipped cases.
* Number of failed cases.
* Number of quota failures.
* Verdict distribution.
* Verdict accuracy.
* Evidence metrics.
* Traceability metrics.
* Agent agreement.
* Confidence metrics.
* Failure categories.
* Per-case results.

Do not invent missing metrics.

If a metric cannot be calculated from the live results, explicitly report it as unavailable.

---

# 10. Live vs Offline Comparison

Compare the live evaluation against the existing offline benchmark.

Offline baseline currently reports:

```text
Cases: 30
Verdict Accuracy: 100.0%

Average evidence count: 0.9
Average relevance: 0.61
Average claim overlap: 0.55
Evidence coverage: 56.7%

Traceability completeness: 96.7%
Traceability coverage: 48.9%
Traceability link rate: 41.7%

Agent agreement: 85.7%

Unsupported-claim detection: 100.0%
```

These are the current offline values and must be treated as the baseline.

The live results should be compared against them without changing the offline baseline.

---

# 11. Generate a Phase 17 Benchmark Report

Create a concise report containing:

## Executive Summary

* Number of benchmark cases.
* Number of live-eligible cases.
* Number successfully evaluated.
* Number skipped.
* Number failed.
* Provider used.
* Whether quota interruption occurred.

## Live Metrics

Include:

* Verdict accuracy.
* Per-verdict accuracy where available.
* Evidence coverage.
* Average evidence count.
* Evidence relevance.
* Claim overlap.
* Traceability completeness.
* Traceability coverage.
* Traceability link rate.
* Agent agreement.
* Confidence metrics.
* Failure categories.

## Offline vs Live

Create a comparison table:

| Metric                 | Offline | Live | Difference |
| ---------------------- | ------: | ---: | ---------: |
| Verdict Accuracy       |     ... |  ... |        ... |
| Evidence Coverage      |     ... |  ... |        ... |
| Traceability Coverage  |     ... |  ... |        ... |
| Traceability Link Rate |     ... |  ... |        ... |
| Agent Agreement        |     ... |  ... |        ... |
| Unsupported Detection  |     ... |  ... |        ... |

Only include metrics that are genuinely available.

## Failure Analysis

Identify the most common live failure categories.

Examples:

```text
Weak Evidence
Poor Traceability
Agent Disagreement
Overconfident
Retrieval Failure
LLM Failure
LLM Quota Exceeded
```

Do not artificially assign failures.

---

# 12. Preserve Raw Results

Do not overwrite the offline benchmark results.

Keep Phase 17 live results separate, preferably under:

```text
backend/evaluation/results/live/phase17/
```

or another clearly named directory consistent with the existing project structure.

The final live benchmark should be reproducible from the stored results and checkpoint data.

---

# 13. Tests

Do not add large amounts of new functionality.

Run:

```powershell
python -m pytest -q
```

Expected:

```text
330+ passed
```

If any Phase 17-specific tests are added, they should test only:

* Live result persistence.
* Benchmark aggregation.
* Resume behavior.
* Provider failure handling.
* Result/report consistency.

Do NOT make real LLM calls inside automated tests.

Use mocks/fakes for provider behavior.

---

# 14. Git Safety Check

Before committing:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify

git status
git diff --stat
git diff --check
```

Ensure that:

* `.env` is not staged.
* API keys are not staged.
* Checkpoint JSON files are ignored.
* Temporary live results are ignored unless intentionally committed.
* No unrelated files are modified.

Do not commit generated checkpoint state or secrets.

---

# 15. Success Criteria

Phase 17 is considered successful when:

### Repository

* Working tree is clean before the benchmark.
* Existing tests pass.

### Health

* Health check completes successfully.
* Healthy cases are correctly identified.

### Provider

* A provider with sufficient quota is configured.
* No unnecessary long retries occur.

### Live Evaluation

* Healthy benchmark cases are processed.
* Real LLM responses are obtained.
* Per-case results are persisted.
* Checkpoint state is persisted.

### Resume

If interrupted:

* Completed cases are skipped.
* Remaining cases resume correctly.
* No duplicate processing occurs.

### Benchmark

A final live benchmark result is available with:

```text
Live cases
Verdict accuracy
Evidence metrics
Traceability metrics
Agent agreement
Confidence
Failure analysis
```

### Comparison

Offline vs live performance is clearly reported.

---

# Important Constraints

DO NOT:

* Modify verification agents.
* Modify evidence-ranking logic.
* Modify retrieval algorithms.
* Modify benchmark fixtures.
* Change offline benchmark results.
* Hardcode provider credentials.
* Commit `.env`.
* Commit API keys.
* Consume unnecessary LLM quota.
* Retry indefinitely after daily quota exhaustion.
* Rewrite working Phase 15.1/15.2 checkpoint logic without evidence of a bug.
* Add unrelated features.

Phase 17 is primarily an **execution and measurement phase**, not a major architecture rewrite.

---

# Final Output

At the end, report:

```text
PHASE 17 RESULT
================

Tests:
XXX passed

Health:
XX / 30 healthy

Live eligible:
XX

Successfully evaluated:
XX

Skipped:
XX

Failed:
XX

Quota failures:
XX

Live verdict accuracy:
XX.X%

Evidence coverage:
XX.X%

Traceability coverage:
XX.X%

Agent agreement:
XX.X%

Benchmark status:
COMPLETED / PARTIAL / BLOCKED

Offline vs Live:
[brief comparison]

Next recommended phase:
Phase 18 — Live vs Offline Analysis & Benchmark Improvement
```

If the live benchmark is blocked by provider quota, do NOT keep retrying. Mark Phase 17 as **BLOCKED BY PROVIDER QUOTA**, preserve the checkpoint, and report exactly what remains to be completed.
