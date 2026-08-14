# Implementation Plan: Replace Placeholder Live Evaluation Cases with Real Scientific Papers

## Objective

The current SciVerify offline evaluation has 30 benchmark cases and passes with 100% verdict accuracy, but the live evaluation is not meaningful because several benchmark cases use placeholder DOIs such as:

10.1000/example.2024.001

These cases are skipped during live evaluation because the citations do not exist.

The goal is to replace placeholder live-evaluation cases with real, publicly verifiable scientific papers and realistic claims while preserving the intended verdict categories.

IMPORTANT:
Do NOT modify the production verification pipeline merely to make the evaluation pass.

Do NOT modify:

- Prosecutor
- Defender
- Adjudicator
- Groq/LLM provider
- evidence ranking
- evidence deduplication
- claim traceability
- verification validator
- frontend

Only modify the evaluation dataset/fixtures/evaluation-specific code where necessary.

---

# Step 1 — Inspect the current evaluation system

Inspect:

- backend/evaluation/dataset.json
- backend/evaluation/fixtures/
- backend/evaluation/README.md
- backend/app/evaluation/dataset_loader.py
- backend/app/evaluation/evaluator.py
- backend/app/evaluation/run.py
- backend/app/evaluation/fixture_factory.py
- backend/app/tests/test_evaluation_dataset.py
- backend/app/tests/test_evaluation_metrics.py

Identify every benchmark case containing:

- placeholder DOI
- fake citation
- unreachable citation
- example URL
- synthetic paper metadata

Create a list before making changes.

---

# Step 2 — Preserve the existing benchmark structure

Do NOT simply delete the problematic cases.

Keep approximately 30 benchmark cases.

Preserve the existing distribution as closely as possible:

- SUPPORTS
- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

The goal is to replace invalid citations with real papers, not reduce benchmark coverage.

---

# Step 3 — Use real scientific papers

Replace placeholder citations with real papers that have:

- valid DOI where available
- publicly discoverable metadata
- preferably open-access full text
- reliable title/author metadata
- stable source such as PMC, Europe PMC, or another legitimate repository

Prefer papers that are likely to be retrievable by the existing SciVerify pipeline.

Do NOT use papers behind inaccessible paywalls if an equivalent open-access paper can be used.

Do NOT bypass CAPTCHA, anti-bot protection, paywalls, or access controls.

---

# Step 4 — Create realistic claims

For each replacement case, create a claim that can actually be evaluated against the cited paper.

Claims should cover:

### SUPPORTS

The paper directly provides evidence for the claim.

Example pattern:

"The study found that X increased Y under the tested conditions."

### CONTRADICTS

The paper provides evidence inconsistent with the claim.

Example pattern:

"The study found that X increased Y."

when the paper reports that X did not increase Y.

### OVERSTATED

The claim contains a stronger conclusion than the paper supports.

Examples:

- "proves"
- "always"
- "never"
- "guarantees"
- universal claims
- causal claims when only association was demonstrated
- broad claims when the experiment was limited to specific conditions

### INSUFFICIENT

The paper is relevant, but does not provide enough evidence to establish the claim.

### FABRICATED

The claim describes a result, method, finding, or conclusion that is not actually present in the cited paper.

Be careful:

FABRICATED should mean the claim is not supported by the cited paper, not that the paper itself is fake.

---

# Step 5 — Prefer difficult but objectively verifiable cases

Add/replace cases involving:

1. Direct support
2. Direct contradiction
3. Conditional support
4. Overgeneralization
5. Unsupported numerical claim
6. Causal vs correlational confusion
7. Compound claim with one unsupported component
8. Universal claim
9. Fabricated finding
10. Relevant paper but insufficient evidence

Avoid ambiguous claims where reasonable scientists could disagree about the expected verdict.

---

# Step 6 — Separate live dataset metadata from offline fixtures

If the existing schema mixes:

- live DOI/citation information
- expected verdict
- offline fixture response

cleanly separate those concepts if necessary.

The same benchmark case may continue to have an offline fixture for deterministic tests while also having a real DOI for live testing.

Example conceptual structure:

{
  "id": "real_support_001",
  "claim": "...",
  "doi": "REAL_DOI",
  "expected_verdict": "SUPPORTS",
  "live_evaluable": true
}

Do not break backward compatibility with the existing dataset loader.

---

# Step 7 — Add live-evaluation eligibility validation

Improve the evaluation dataset validation so placeholder citations are detected before live execution.

Create deterministic validation for:

- placeholder DOI
- missing DOI
- malformed DOI
- missing claim
- missing expected verdict
- duplicate case IDs

A placeholder DOI should be reported clearly, for example:

"Case real_support_001 has a placeholder/non-live DOI and will not be used for live evaluation."

Do not silently skip cases.

---

# Step 8 — Distinguish offline and live evaluation

The CLI should clearly report:

Offline:

- total cases
- evaluated cases
- skipped cases

Live:

- total cases
- live-eligible cases
- evaluated cases
- skipped cases
- skip reasons

Example:

Live evaluation
----------------
Dataset cases:       30
Live eligible:       30
Evaluated:           24
Skipped:             6

Skip reasons:
- Citation unavailable: 4
- Full text unavailable: 2

If a real paper cannot be retrieved because of external access restrictions, report that as an infrastructure/retrieval limitation rather than silently treating it as a model failure.

---

# Step 9 — Do not modify the baseline automatically

IMPORTANT:

Do NOT run:

python -m app.evaluation.run --update-baseline

automatically.

First run:

python -m app.evaluation.run

and, if possible:

python -m app.evaluation.run --live

Inspect the results.

Only update baseline.json if the benchmark itself intentionally changes and the new benchmark is validated.

Document why the baseline changed.

---

# Step 10 — Add deterministic tests

Add tests for:

- placeholder DOI detection
- valid DOI acceptance
- malformed DOI detection
- live eligibility
- duplicate case detection
- clear skipped-case reporting
- separation of offline/live evaluation
- dataset still contains all 5 verdict categories

Do not make tests depend on internet access.

No Groq calls in unit tests.

---

# Step 11 — Keep fixtures deterministic

Existing offline fixtures must continue working.

Do NOT remove the existing fixture system just because real DOIs are being added.

Offline evaluation must remain:

- fast
- deterministic
- network-free
- LLM-free

Live evaluation is the only part allowed to retrieve real papers and call configured LLM providers.

---

# Step 12 — Run validation

Run:

cd backend

python -m pytest -q

python -m app.evaluation.run

Then, if Groq quota and external retrieval are available:

python -m app.evaluation.run --live

Also run:

python -m app.evaluation.run --help

Verify that the CLI clearly explains offline vs live behavior.

---

# Acceptance criteria

The implementation is complete only when:

1. No benchmark case uses fake/example DOIs.
2. Approximately 30 cases remain.
3. All five verdict categories remain represented.
4. Every live case has a real citation.
5. Offline fixtures still work.
6. Offline evaluation remains deterministic.
7. Live evaluation no longer skips cases because of placeholder/example DOIs.
8. Cases that fail because of external retrieval/access problems are clearly reported.
9. Placeholder citation validation is deterministic.
10. No production verification logic is modified.
11. No new LLM calls are added to offline evaluation.
12. All backend tests pass.
13. Existing evaluation metrics continue working.
14. Baseline is NOT silently overwritten.

---

# Final report required

After implementation, report:

## Dataset

- cases before
- cases after
- placeholder cases removed
- real-paper cases added
- verdict distribution

## Live eligibility

- total cases
- live-eligible cases
- skipped cases
- skip reasons

## Papers

For every newly added live case provide:

- case ID
- DOI
- paper title
- expected verdict
- why the claim receives that expected verdict

## Tests

- backend test count
- evaluation result
- live evaluation result if available
- frontend status if unchanged

## Baseline

State clearly whether baseline.json was changed.

Do not update the baseline merely because the command runs successfully.

## Remaining limitations

Clearly identify papers that are real but may still be inaccessible due to:

- anti-bot protection
- unavailable full text
- external HTTP failures
- rate limits
- LLM quota

Do not work around access controls.