# SciVerify — Phase 15: Live LLM Verification Validation & Accuracy Benchmark

## Objective

Validate SciVerify's **complete live verification pipeline** using a real configured LLM provider against the benchmark's healthy real-paper cases.

Phase 14 fixed the live evaluation status-handling bug. Phase 15 must now determine the **actual live verification quality** when retrieval succeeds and an LLM is available.

The goal is to measure:

* Real live verdict accuracy
* Evidence retrieval quality
* Claim/evidence overlap
* Traceability coverage
* Agent agreement
* Confidence quality
* LLM failure rate
* Retrieval failure rate
* Per-case live diagnostics

Do **not** modify the production verification logic merely to improve benchmark numbers.

---

## Current Known State

Offline evaluation:

* 30 cases
* 30 evaluated
* 100% verdict accuracy
* All five verdict categories pass
* Regression: PASS

Live health check:

* Total cases: 30
* Healthy: 15
* Unindexed: 11
* Paywalled: 4

Current live evaluation without an LLM:

* Live eligible: 15
* Successfully evaluated: 0
* Retrieval/infrastructure failures: 2
* LLM failures: 13
* LLM provider is not configured

Therefore, the current live accuracy result must **not** be interpreted as verification accuracy because no successful live verification occurred.

---

# Phase 15 Scope

## Step 1 — Verify Git State

Before modifying code:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify

git status
git log -1 --oneline
git branch -vv
```

Confirm the Phase 14 commit is pushed to `origin/main`.

Do not overwrite or reset existing work.

---

# Step 2 — Configure a Real LLM Provider

Use the existing LLM abstraction already present in the project.

Do NOT redesign the LLM architecture.

Do NOT hard-code API keys.

Do NOT commit secrets.

Use the existing environment-variable mechanism.

Verify the provider configuration expected by the project, including:

```text
LLM_PROVIDER
LLM_API_KEY
```

and any existing provider/model configuration already supported by SciVerify.

If `.env.example` needs documentation updates, modify only the example configuration and never add real credentials.

Add or update `.gitignore` protections if necessary to ensure secrets cannot be committed.

---

# Step 3 — Validate LLM Connectivity

Before running the entire benchmark, verify that the configured provider can successfully answer through SciVerify's existing LLM abstraction.

Use the existing application path.

Do not bypass:

* agents
* verification_service
* evidence retrieval
* validation
* traceability
* existing prompts

The test must exercise the real verification pipeline.

If the LLM cannot be reached, stop and report the configuration/provider failure rather than modifying verification logic.

---

# Step 4 — Run Live Health Check

Run:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify\backend

python -m app.evaluation.run --live-health-check
```

Record:

* Total cases
* Healthy cases
* Unindexed cases
* Paywalled cases
* Blocked cases
* Unknown cases

Do not automatically replace benchmark DOIs.

---

# Step 5 — Run Live Evaluation

Run:

```powershell
python -m app.evaluation.run --live --skip-unhealthy
```

This should evaluate only the healthy/live-eligible cases.

Record:

```text
Live eligible
Successfully evaluated
Retrieval/infrastructure failures
Verification failures
Skipped
```

Also record:

```text
Retrieval success rate
Retrieval failure rate
Total retrieval attempts
Average attempts per case
Total elapsed time
```

---

# Step 6 — Analyze Successful Live Cases

For every case with:

```text
status = evaluated
```

inspect:

* expected verdict
* actual verdict
* confidence
* evidence count
* evidence relevance
* claim overlap
* evidence coverage
* traceability coverage
* agent agreement
* validation status

Create a per-case diagnostic table in the generated report if the existing reporting system supports it.

Do not modify verdict logic to force benchmark agreement.

---

# Step 7 — Separate Failure Classes

Live failures must remain separated into:

### Retrieval/infrastructure failures

Examples:

* DOI_NOT_FOUND
* FULL_TEXT_UNAVAILABLE
* PAYWALLED
* ANTI_BOT_BLOCKED
* HTTP_403
* HTTP_404
* RATE_LIMITED
* INVALID_DOCUMENT
* NETWORK_TIMEOUT
* NETWORK_ERROR

### Verification failures

Examples:

* LLM_FAILURE
* LLM_QUOTA_EXCEEDED
* LLM_TIMEOUT
* INVALID_RESPONSE
* UNKNOWN_FAILURE

### Successful verification

Only cases with:

```text
VerificationStatus.SUCCESS
```

should contribute to live verdict accuracy.

Do not count retrieval failures as wrong verdicts.

Do not count LLM failures as wrong verdicts.

---

# Step 8 — Validate the Phase 14 Fix

Specifically verify that the previous false-negative behavior is gone.

Previously:

```text
INSUFFICIENT_EVIDENCE
        ↓
incorrectly counted as WRONG VERDICT
```

It must now behave as:

```text
INSUFFICIENT_EVIDENCE
        ↓
skipped / retrieval failure
        ↓
not included in verdict accuracy
```

Similarly:

```text
LLM_UNAVAILABLE
LLM_TIMEOUT
VERIFICATION_FAILED
        ↓
verification failure
        ↓
not counted as wrong verdict
```

---

# Step 9 — Investigate Actual Wrong Verdicts

Only if there are successfully evaluated cases with incorrect verdicts:

```text
status = evaluated
actual_verdict != expected_verdict
```

investigate them.

For each wrong case determine which layer is responsible:

1. Paper retrieval
2. Document parsing
3. Chunking
4. Evidence retrieval
5. Evidence ranking
6. Claim decomposition
7. Prosecutor agent
8. Defender agent
9. Adjudicator agent
10. Traceability
11. Validation
12. Final verdict mapping

Do not immediately modify the responsible component.

First produce evidence showing the root cause.

---

# Step 10 — Compare Live vs Offline Results

Create a comparison:

| Metric                |          Offline |                    Live |
| --------------------- | ---------------: | ----------------------: |
| Cases                 |               30 | healthy evaluated count |
| Verdict accuracy      |             100% |                measured |
| Evidence coverage     |            56.7% |                measured |
| Traceability coverage |            48.9% |                measured |
| Agent agreement       |            85.7% |                measured |
| Confidence            | 0.70 correct avg |                measured |
| Retrieval failures    |              N/A |                measured |
| LLM failures          |              N/A |                measured |

Important:

Offline results must remain unchanged.

Do not modify:

* `baseline.json`
* offline fixtures
* dataset schema for the purpose of improving scores
* offline evaluation logic

---

# Step 11 — Improve Metrics Only If a Real Bug Exists

If metrics are incorrect, fix only the measurement/reporting bug.

Examples:

* Retrieval success incorrectly counted
* LLM failure incorrectly counted as retrieval failure
* Skipped case incorrectly included in accuracy denominator
* Successful case incorrectly omitted
* Per-case diagnostics incorrectly reported

Do NOT change scoring definitions simply because the live result is low.

---

# Step 12 — Tests

Add tests only for bugs or behavior discovered during Phase 15.

Required regression coverage:

### LLM configuration

Test that missing provider configuration produces a structured LLM failure.

### Successful LLM response

Test that a successful verification response is:

```text
status = evaluated
```

and contributes to live metrics.

### LLM failure

Test that:

```text
LLM_UNAVAILABLE
LLM_TIMEOUT
VERIFICATION_FAILED
```

are classified as verification failures and not wrong verdicts.

### Retrieval failure

Ensure retrieval failures remain excluded from verdict accuracy.

### Accuracy denominator

Ensure only successfully evaluated cases contribute to live verdict accuracy.

---

# Step 13 — Required Validation

Run all of the following:

```powershell
python -m pytest -q
```

Then:

```powershell
python -m app.evaluation.run
```

Then:

```powershell
python -m app.evaluation.run --live-health-check
```

Then, with the LLM configured:

```powershell
python -m app.evaluation.run --live --skip-unhealthy
```

Expected minimum:

* All tests pass
* Offline evaluation remains 30/30
* Offline accuracy remains 100%
* Regression remains PASS
* Live evaluation produces actual evaluated cases when the LLM is configured
* Retrieval failures remain separated
* LLM failures remain separated
* No secrets are committed

---

# Step 14 — Do Not Change These Components Unless a Proven Bug Requires It

Preserve:

```text
verification_service.py
services/agents/
evidence_retriever.py
claim_traceability.py
verification_validator.py
metrics.py
failure_analysis.py
fixture_factory.py
evaluation/fixtures/
baseline.json
frontend/
```

Do not alter agent prompts or verdict rules merely to increase live benchmark accuracy.

---

# Step 15 — Reporting

At completion, provide an exact report containing:

## Files Changed

List every modified/created file.

## Tests

Example:

```text
pytest:
XXX passed
```

## Offline Evaluation

```text
Cases: 30
Accuracy: 100.0%
Regression: PASS
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
Retrieval/infrastructure failures:
Verification failures:
Skipped:
```

## Live Quality

```text
Verdict accuracy:
Evidence coverage:
Traceability coverage:
Agent agreement:
Average confidence:
```

## Failure Categories

List counts for each failure category.

## Root Cause Findings

If wrong verdicts exist, explain the actual responsible layer.

If no successful live cases exist because of provider configuration, clearly state that live verification accuracy could not yet be measured.

---

# Phase 15 Success Criteria

Phase 15 is complete when:

1. A real LLM provider is successfully connected through the existing SciVerify pipeline.
2. Healthy benchmark cases can execute through the complete live pipeline.
3. Successful live cases are correctly counted as `evaluated`.
4. Retrieval failures are excluded from verdict accuracy.
5. LLM failures are excluded from verdict accuracy.
6. Phase 14 status handling remains correct.
7. Offline evaluation remains 30/30 with 100% accuracy.
8. All automated tests pass.
9. No production verification behavior is changed without a proven bug.
10. No API keys or secrets are committed.
11. Live verdict accuracy is measured from actual successful live cases.
12. Any remaining accuracy problem has a documented root cause before further implementation.

---

# Important Rule

Do NOT try to make the live benchmark reach 100% accuracy artificially.

The purpose of Phase 15 is **measurement and root-cause discovery**.

If live accuracy is low, document why first.

Only after identifying a reproducible defect should a new Phase 16 implementation plan be created.

---

# Final Deliverable

Produce:

```text
Phase 15 Live Validation Report
```

containing:

* environment/provider status
* health-check results
* live evaluation results
* successful case count
* retrieval failure count
* LLM failure count
* verdict accuracy
* evidence metrics
* traceability metrics
* agent agreement
* confidence metrics
* wrong-case analysis
* regression status
* files changed
* test results
* recommendation for Phase 16

```
```
