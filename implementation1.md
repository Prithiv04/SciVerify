# Phase 14 — Real-Paper Evidence Pipeline Diagnostics & Verification Quality

## Objective

Diagnose why SciVerify achieves **100% retrieval success but only 6.7% live verdict accuracy** on the 15 healthy real-paper benchmark cases.

The live evaluation currently shows:

* 15/15 cases successfully retrieved
* 0 retrieval/infrastructure failures
* 14/15 incorrect verdicts
* 0% evidence coverage
* 0% traceability coverage
* 100% unsupported segments
* Average evidence relevance: 0.17
* Average claim overlap: 0.15

The immediate goal is to identify the exact stage where useful evidence is lost before changing production verification logic.

---

## Phase 1 — Freeze Current Baseline

Before modifying behavior:

1. Preserve the current Phase 13 implementation.
2. Do not modify:

   * `baseline.json`
   * offline fixtures
   * offline evaluation behavior
   * verdict definitions
3. Record the current live benchmark result as the diagnostic baseline:

   * 15 evaluated
   * 6.7% accuracy
   * 0% evidence coverage
   * 0% traceability coverage
4. Run:
   `python -m pytest -q`
5. Run:
   `python -m app.evaluation.run`

Expected:

* Existing tests pass.
* Offline evaluation remains 30/30 and 100%.

---

## Phase 2 — Add Evidence Pipeline Diagnostics

Create a diagnostic layer that does NOT change the production verdict logic.

For every live benchmark case capture:

### Document diagnostics

* DOI
* paper title
* resolved source
* document URL
* document type
* downloaded document size
* extracted text length
* extraction success/failure
* number of pages when available

### Chunk diagnostics

* total chunks generated
* minimum/maximum/average chunk length
* chunks containing claim keywords
* chunks containing important entities/numbers from the claim

### Evidence retrieval diagnostics

Capture the top evidence candidates before final filtering:

* rank
* evidence text
* relevance score
* claim overlap score
* source metadata
* retrieval method
* whether candidate survived filtering

### Traceability diagnostics

Capture:

* claim segments
* matched evidence IDs
* supported segments
* partial segments
* unsupported segments
* contradicted segments

### Verification diagnostics

Capture the information actually passed to the agents:

* claim
* evidence
* citation metadata
* retrieved context length
* agent outputs
* final adjudicator input
* final verdict

Do not change the agents or verdict logic in this phase.

---

## Phase 3 — Create Diagnostic Report

Add a dedicated report for live evidence quality.

Example:

```text
Live Evidence Diagnostic Report
================================

Cases analyzed: 15

Document extraction:
- Successful: 15
- Failed: 0

Chunking:
- Average chunks/case: X
- Average text length: X

Evidence retrieval:
- Cases with useful evidence: X/15
- Average top-5 relevance: X
- Average claim overlap: X
- Evidence coverage: X%

Traceability:
- Linked segments: X%
- Unsupported segments: X%

Verification:
- Correct: 1
- Incorrect: 14

Pipeline bottleneck:
- DOCUMENT_EXTRACTION
- CHUNKING
- EVIDENCE_RETRIEVAL
- CLAIM_MATCHING
- TRACEABILITY
- AGENT_INPUT
- VERDICT
```

The report must identify the likely bottleneck using measured data rather than assumptions.

---

## Phase 4 — Inspect Existing Production Components

Read-only inspection first.

Inspect:

* `backend/app/services/paper_retriever.py`
* `backend/app/services/document_retriever.py`
* `backend/app/services/evidence_retriever.py`
* `backend/app/services/evidence_pipeline.py`
* `backend/app/services/claim_traceability.py`
* `backend/app/services/agents/`
* `backend/app/services/verification_validator.py`

Determine:

1. Whether real-paper text is actually reaching the evidence retriever.
2. Whether extracted text is malformed, truncated, or excessively noisy.
3. Whether chunking produces useful scientific passages.
4. Whether retrieval scores are too low because of query construction.
5. Whether relevant evidence is being filtered out.
6. Whether traceability expects metadata that real retrieved evidence does not contain.
7. Whether agents receive the retrieved evidence correctly.
8. Whether the final verdict is being produced from empty/weak evidence.

Do not modify these components during inspection.

---

## Phase 5 — Diagnose the 15 Real Cases

Generate a per-case diagnostic table.

Required fields:

| Case | Expected | Actual | Text Length | Chunks | Top Evidence | Relevance | Claim Overlap | Evidence Coverage | Traceability |
| ---- | -------- | ------ | ----------: | -----: | ------------ | --------: | ------------: | ----------------: | -----------: |

Categorize each case into one primary bottleneck:

* `DOCUMENT_EXTRACTION_FAILURE`
* `CHUNKING_FAILURE`
* `QUERY_CONSTRUCTION_FAILURE`
* `EVIDENCE_RETRIEVAL_FAILURE`
* `EVIDENCE_FILTERING_FAILURE`
* `TRACEABILITY_FAILURE`
* `AGENT_CONTEXT_FAILURE`
* `VERDICT_REASONING_FAILURE`
* `UNKNOWN`

A case must not be classified as a verdict reasoning failure if useful evidence never reached the agents.

---

## Phase 6 — Identify the Root Cause

After diagnostics, determine the dominant failure.

Examples:

### If extracted text is poor

Fix document extraction/chunking only.

### If relevant chunks exist but retrieval misses them

Investigate query construction and evidence retrieval.

### If relevant evidence is retrieved but discarded

Fix evidence filtering/ranking.

### If evidence reaches agents but traceability is zero

Fix the evidence-to-claim linking layer.

### If agents receive strong evidence but still produce incorrect verdicts

Only then investigate agent/verdict reasoning.

Do NOT make multiple unrelated changes simultaneously.

---

## Phase 7 — Targeted Fix

Implement only the fix supported by the diagnostic results.

Constraints:

* Preserve existing offline behavior.
* Preserve benchmark fixtures.
* Preserve verdict categories.
* Preserve Phase 13 diagnostics.
* Do not bypass access controls.
* Do not add unnecessary LLM calls.
* Do not modify `baseline.json`.
* Do not modify the frontend.
* Maintain backward compatibility.

Every production change must have a regression test.

---

## Phase 8 — Re-run Offline Regression

Run:

```bash
python -m pytest -q
python -m app.evaluation.run
```

Verify:

* All tests pass.
* Offline dataset remains 30 cases.
* Offline verdict accuracy remains 100%.
* Existing metrics do not regress.
* Baseline remains unchanged.

If offline behavior changes, stop and fix the regression before continuing.

---

## Phase 9 — Re-run Real Live Benchmark

Run:

```bash
python -m app.evaluation.run --live --skip-unhealthy
```

Compare against the Phase 14 baseline:

| Metric            | Before | After |
| ----------------- | -----: | ----: |
| Live cases        |     15 |     — |
| Verdict accuracy  |   6.7% |     — |
| Evidence coverage |     0% |     — |
| Traceability      |     0% |     — |
| Avg relevance     |   0.17 |     — |
| Avg claim overlap |   0.15 |     — |
| Retrieval success |   100% |     — |

The objective is measurable improvement, not merely passing tests.

---

## Phase 10 — Acceptance Criteria

Phase 14 is complete only when:

1. The root cause of the 6.7% live accuracy is identified with evidence.
2. Per-case evidence diagnostics are available.
3. The diagnostic report clearly identifies the bottleneck.
4. A targeted fix is implemented only where justified.
5. All automated tests pass.
6. Offline evaluation remains unchanged.
7. Baseline remains unchanged.
8. Production verification behavior is changed only if the diagnostics demonstrate that it is necessary.
9. Live evidence coverage improves from the current 0%.
10. Live verdict accuracy improves from the current 6.7%, or a documented root cause explains why further improvement requires an external limitation.
11. No paywalls, CAPTCHAs, or anti-bot protections are bypassed.
12. Final results are documented with before/after metrics.

---

## Files

### Initially inspect

* `backend/app/services/paper_retriever.py`
* `backend/app/services/document_retriever.py`
* `backend/app/services/evidence_retriever.py`
* `backend/app/services/evidence_pipeline.py`
* `backend/app/services/claim_traceability.py`
* `backend/app/services/agents/`
* `backend/app/services/verification_validator.py`

### Potential new files

* `backend/app/evaluation/live_evidence_diagnostics.py`
* `backend/app/tests/test_live_evidence_diagnostics.py`

Only modify production service files after the diagnostic phase identifies the actual bottleneck.

### Must remain unchanged unless the root-cause analysis proves otherwise

* `backend/evaluation/baseline.json`
* `backend/evaluation/fixtures/`
* offline evaluation logic
* verdict definitions
* frontend

---

## Final Validation

Run:

```bash
python -m pytest -q
python -m app.evaluation.run
python -m app.evaluation.run --live --skip-unhealthy
```

Then report:

* Exact files changed
* Number of tests passed
* Offline accuracy
* Live accuracy
* Evidence coverage before/after
* Traceability before/after
* Retrieval metrics before/after
* Identified root cause
* Implemented fix
* Remaining limitations

Do not declare success based solely on test count. The real-paper benchmark must be evaluated.
