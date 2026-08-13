# Implementation Plan: SciVerify Evaluation & Regression Framework

## Objective

Build a developer-only evaluation and regression framework for SciVerify.

The purpose is to measure whether changes to:

- evidence retrieval
- evidence parsing
- evidence deduplication
- evidence ranking
- verdict validation
- claim traceability

actually improve SciVerify instead of relying only on manual testing.

The evaluation framework must NOT redesign or modify the production verification pipeline.

---

# Critical Constraints

DO NOT modify unless absolutely necessary:

- Prosecutor
- Defender
- Adjudicator
- LLM provider
- PMC retrieval
- CAPTCHA/interstitial handling
- document parser
- evidence ranking logic
- verification validator logic
- claim traceability logic
- frontend verification UI
- Supabase history architecture

The evaluation framework must be isolated from production code.

DO NOT make automated benchmark tests call Groq.

DO NOT require an API key to run the deterministic evaluation tests.

The existing production API behavior must remain unchanged.

---

# Step 1 — Inspect Existing Architecture

Before implementing anything, inspect:

Backend:

- backend/app/services/evidence_retriever.py
- backend/app/services/evidence_pipeline.py
- backend/app/services/document_retriever.py
- backend/app/services/paper_retriever.py
- backend/app/services/verification_service.py
- backend/app/services/verification_validator.py
- backend/app/services/claim_traceability.py
- backend/app/utils/claim_preprocessor.py
- backend/app/utils/claim_segmenter.py
- backend/app/schemas/verification.py
- backend/app/tests/

Also inspect:

- existing configuration
- existing test fixtures
- existing logging
- current verification response structure

First determine which existing deterministic functions can be reused.

Do not duplicate ranking, validation, or traceability logic.

---

# Step 2 — Create Evaluation Dataset

Create a developer-only benchmark dataset.

Suggested location:

backend/evaluation/

Possible files:

backend/evaluation/dataset.json
backend/evaluation/README.md

The dataset should contain multiple scientific verification cases.

Each case should contain:

- id
- claim
- doi
- expected_verdict
- description
- optional expected_traceability_statuses
- optional expected_min_evidence_count

Example structure:

{
  "id": "cas9_supports_001",
  "claim": "Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences.",
  "doi": "10.1126/science.1225829",
  "expected_verdict": "SUPPORTS",
  "description": "The cited paper directly demonstrates programmable Cas9 DNA cleavage."
}

DO NOT hard-code this Cas9 claim into production code.

It is only a benchmark case.

---

# Step 3 — Benchmark Categories

The dataset should eventually cover:

## SUPPORTS

The paper directly supports the claim.

## CONTRADICTS

The paper provides evidence inconsistent with the claim.

## OVERSTATED

The paper supports a weaker or narrower statement, but the claim makes a stronger assertion.

## INSUFFICIENT

The paper is relevant but does not contain enough evidence to establish the claim.

## FABRICATED

The claim cannot be supported by the cited paper and appears to assert information not present in the source.

Do not force all categories into the initial dataset if reliable scientific examples are unavailable.

Quality of benchmark cases is more important than dataset size.

Start with a small high-quality dataset.

Target approximately 10–20 cases initially.

---

# Step 4 — Deterministic Evaluation Components

Create an evaluation package such as:

backend/app/evaluation/

Possible modules:

- dataset_loader.py
- metrics.py
- evaluator.py
- report.py

Keep evaluation code separate from production services.

The evaluator should be able to consume an existing VerificationResponse/VerificationResult.

It should NOT reimplement the verification pipeline.

---

# Step 5 — Verdict Accuracy Metric

Implement:

verdict_accuracy

Formula:

correct verdicts / total evaluated cases

Also calculate a confusion matrix:

Expected → Actual

Example:

SUPPORTS → SUPPORTS
SUPPORTS → OVERSTATED
SUPPORTS → INSUFFICIENT
etc.

Do not hide mismatches.

The evaluation report must clearly show incorrect predictions.

---

# Step 6 — Evidence Quality Metrics

Calculate deterministic metrics from the existing evidence response.

At minimum:

## Evidence count

Number of evidence items returned.

## Duplicate rate

Detect duplicate normalized evidence text.

Expected:

Duplicate rate should ideally be 0 after the existing deduplication layer.

## Average relevance score

Average relevance_score of returned evidence.

## Average claim overlap

Average claim_overlap.

## Evidence coverage

Use the existing claim traceability data where available.

Example:

overall_coverage

Also calculate:

- percentage of segments SUPPORTED
- percentage PARTIALLY_SUPPORTED
- percentage UNSUPPORTED
- percentage CONTRADICTED

Do not invent new semantic scoring logic if existing traceability metrics can be reused.

---

# Step 7 — Traceability Metrics

If claim_traceability exists, calculate:

- segment_count
- supported_segments
- partially_supported_segments
- unsupported_segments
- contradicted_segments
- overall_coverage

Also calculate:

traceability_completeness =
cases_with_traceability / total_cases

The evaluator must handle old responses where traceability is absent.

---

# Step 8 — Validation Metrics

Measure the existing deterministic validator behavior.

For each case track:

- adjudicator verdict
- final validated verdict
- whether verdict changed
- confidence before validation
- confidence after validation
- validation warnings
- invalid evidence IDs if exposed

Calculate:

validation_override_rate =
cases_where_final_verdict_differs_from_adjudicator
/
total_cases

This is an evaluation metric only.

Do not modify validator behavior.

---

# Step 9 — Agent Agreement Metrics

Where available, calculate:

- agent_agreement = true
- agent_agreement = false
- missing agreement information

Calculate:

agent_agreement_rate

Also show agreement by expected verdict if useful.

Do not reinterpret agent disagreement.

Use the existing field.

---

# Step 10 — Confidence Metrics

Do NOT claim to calculate statistically rigorous calibration unless enough labeled data exists.

For the initial framework, report:

- average confidence
- average confidence for correct verdicts
- average confidence for incorrect verdicts
- minimum confidence
- maximum confidence

Optionally implement a simple confidence error metric:

confidence_error = abs(confidence - correctness)

where:

correctness = 1 for correct verdict
correctness = 0 for incorrect verdict

Clearly label this as a simple diagnostic, not formal calibration.

---

# Step 11 — Regression Detection

The framework must support comparing:

current evaluation results

against

a stored baseline.

Create something such as:

backend/evaluation/baseline.json

The baseline should contain metrics from a known-good version.

Detect regressions such as:

- verdict accuracy decreased
- evidence coverage decreased
- duplicate rate increased
- traceability completeness decreased
- average evidence relevance decreased

Do not fail the build because of tiny floating-point differences.

Use configurable tolerances.

Example:

VERDICT_ACCURACY_TOLERANCE=0.02
EVIDENCE_COVERAGE_TOLERANCE=0.03

Keep thresholds configurable.

---

# Step 12 — Evaluation Report

Generate a human-readable report.

Possible output:

backend/evaluation/results/latest.json
backend/evaluation/results/latest.md

Example summary:

SciVerify Evaluation
====================

Cases: 15

Verdict Accuracy: 86.7%

Evidence:
- Average evidence count: 4.8
- Average relevance: 0.43
- Average claim overlap: 0.61
- Duplicate rate: 0%

Traceability:
- Coverage: 91%
- Supported segments: 78%
- Partial segments: 13%
- Unsupported segments: 9%

Validation:
- Override rate: 6.7%
- Warning rate: 13.3%

Agent Agreement:
- Agreement: 80%

Confidence:
- Correct verdict avg: 0.84
- Incorrect verdict avg: 0.61

Regression:
PASS

The report should also list individual failing cases.

---

# Step 13 — CLI Interface

Create a simple CLI.

Possible command:

cd backend

python -m app.evaluation.run

Optional commands:

python -m app.evaluation.run --dataset evaluation/dataset.json

python -m app.evaluation.run --compare-baseline

python -m app.evaluation.run --update-baseline

The exact CLI structure can be chosen based on the existing project conventions.

Do not add unnecessary dependencies.

Prefer Python standard library where practical.

---

# Step 14 — Offline / Deterministic Mode

The default evaluation test suite must NOT:

- call Groq
- call OpenAI
- call external LLM APIs
- require API keys

Instead, create deterministic fixtures representing VerificationResponse objects.

These fixtures should test the evaluator itself.

Example fixture:

{
  "verdict": "SUPPORTS",
  "confidence": 0.86,
  "evidence": [...],
  "claim_traceability": {...},
  "agent_agreement": true
}

This allows the evaluation framework to be tested offline.

---

# Step 15 — Optional Live Evaluation Mode

Add a clearly separate optional live mode.

Example:

python -m app.evaluation.run --live

Live mode may:

- retrieve actual papers
- run the real verification pipeline
- use Groq

But:

- it must never run by default
- it must clearly warn that API usage may consume quota
- it should require explicit user intent
- it must not be used by automated unit tests

Do not implement live mode if doing so requires invasive production changes.

Offline evaluation is the priority.

---

# Step 16 — Unit Tests

Create:

backend/app/tests/test_evaluation_metrics.py
backend/app/tests/test_evaluation_dataset.py
backend/app/tests/test_evaluation_regression.py

Test at minimum:

1. Dataset loads correctly.
2. Invalid dataset entries are rejected clearly.
3. Verdict accuracy calculation.
4. Confusion matrix.
5. Evidence count metric.
6. Duplicate rate.
7. Average relevance.
8. Average claim overlap.
9. Traceability metrics.
10. Validation override rate.
11. Agent agreement rate.
12. Confidence metrics.
13. Confidence error.
14. Regression detection.
15. Baseline comparison.
16. Floating-point tolerance.
17. Missing optional fields.
18. Empty dataset handling.
19. Incorrect verdict detection.
20. Report generation.

All tests must be deterministic.

No Groq calls.

---

# Step 17 — Dataset Validation

Add validation for benchmark cases.

Each case must have:

- non-empty id
- non-empty claim
- valid DOI or explicitly documented identifier
- valid expected verdict

Expected verdict must be one of:

- SUPPORTS
- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

Reject duplicate case IDs.

Provide clear validation errors.

---

# Step 18 — Baseline Policy

Do NOT automatically update the baseline.

The baseline should only change when explicitly requested.

For example:

python -m app.evaluation.run --update-baseline

Before updating the baseline:

- run the evaluation
- print the new metrics
- require explicit update flag

Never silently overwrite the baseline.

---

# Step 19 — Documentation

Create:

backend/evaluation/README.md

Document:

- purpose
- dataset structure
- how to run offline evaluation
- how to compare against baseline
- how to update baseline
- meaning of metrics
- limitations
- optional live evaluation

Important limitation:

A benchmark result is only as good as the quality of its expected labels.

Do not claim that the benchmark represents scientific truth universally.

---

# Step 20 — Regression Safety

The evaluation framework must not affect normal application startup.

Running:

python -m uvicorn app.main:app --reload

must work exactly as before.

Do not import evaluation modules into production startup code.

Do not add evaluation dependencies to runtime paths unnecessarily.

---

# Step 21 — Final Testing

Run:

cd backend

python -m pytest -q

All existing tests must continue passing.

Then run the evaluation unit tests.

Then run:

cd ../frontend

npm run lint
npm run build

The frontend should remain unchanged functionally.

Finally run the backend normally:

python -m uvicorn app.main:app --reload

Confirm:

- /docs works
- /api/verification/analyze still works
- existing Cas9 verification still works
- no evaluation code runs during normal verification

---

# Acceptance Criteria

Implementation is complete only when:

- [ ] Evaluation dataset exists.
- [ ] Dataset validation exists.
- [ ] At least 10 high-quality benchmark cases exist or a clearly documented initial subset exists.
- [ ] Cases cover multiple verdict categories where reliable examples are available.
- [ ] Offline deterministic evaluation works.
- [ ] No Groq calls occur during automated evaluation tests.
- [ ] Verdict accuracy is calculated.
- [ ] Confusion matrix is generated.
- [ ] Evidence quality metrics are calculated.
- [ ] Duplicate rate is calculated.
- [ ] Traceability metrics are calculated.
- [ ] Validation metrics are calculated.
- [ ] Agent agreement metrics are calculated.
- [ ] Confidence diagnostics are calculated.
- [ ] Baseline comparison works.
- [ ] Regression detection works.
- [ ] Human-readable report is generated.
- [ ] CLI works.
- [ ] Baseline is never overwritten automatically.
- [ ] Existing production verification code is unchanged.
- [ ] Existing backend tests continue passing.
- [ ] Frontend lint passes.
- [ ] Frontend build passes.
- [ ] No new LLM calls are introduced.
- [ ] Normal backend startup is unaffected.

---

# Final Implementation Rule

Before changing code, briefly report:

1. Which existing deterministic functions will be reused.
2. Where VerificationResponse fixtures can be created.
3. Which existing schemas can be reused.
4. Where evaluation code will live.
5. How the benchmark will remain isolated from production.

Then implement the smallest clean solution.

Do NOT rewrite existing working code.

Do NOT modify the verification pipeline just to make evaluation easier.

The evaluation framework must measure SciVerify, not change SciVerify.