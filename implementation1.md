# Implementation Plan: Evidence-to-Claim Traceability & Verification Explainability

## Objective

Improve SciVerify's verification transparency by showing exactly which parts of the user's claim are supported, contradicted, or not sufficiently supported by the retrieved evidence.

The current pipeline already works:

Claim
→ OpenAlex / paper retrieval
→ Evidence extraction
→ Evidence ranking
→ Prosecutor
→ Defender
→ Adjudicator
→ Deterministic validation
→ Verification Result
→ Frontend
→ Supabase History

Do NOT redesign this pipeline.

The goal is to add an explainability/traceability layer on top of the existing evidence and verification result.

---

# Important Constraints

DO NOT modify unless absolutely necessary:

- Prosecutor logic
- Defender logic
- Adjudicator logic
- LLM provider
- PMC retrieval
- CAPTCHA/interstitial handling
- Evidence ranking algorithm
- Existing verification validator behavior
- Existing history persistence architecture

Reuse the existing evidence metadata wherever possible.

Do not introduce another LLM call just for traceability.

The traceability system should be deterministic and based on the existing claim preprocessing, evidence text, claim overlap, numeric overlap, evidence ranking, and verdict information.

---

# Step 1 — Inspect Existing Implementation

Before making changes, inspect:

Backend:

- backend/app/services/evidence_retriever.py
- backend/app/services/evidence_pipeline.py
- backend/app/services/verification_service.py
- backend/app/services/verification_validator.py
- backend/app/utils/claim_preprocessor.py
- backend/app/schemas/verification.py
- existing evidence-related schemas/models
- existing verification tests

Frontend:

- frontend/src/types/backend-verification.ts
- frontend/src/types/verification.ts
- frontend/src/services/verificationMapper.ts
- frontend/src/components/verification/VerificationReportView.tsx
- frontend/src/components/verification/VerificationEvidenceCard.tsx
- frontend/src/components/verification/VerdictHeader.tsx
- frontend/src/components/verification/AgentAnalysisPanel.tsx
- frontend/src/components/verification/ValidationWarningsPanel.tsx
- frontend/src/components/verification/SuggestedCorrectionPanel.tsx
- frontend/src/pages/HistoryPage.tsx
- frontend/src/stores/verificationStore.ts

Understand the current data flow before modifying anything.

Do not rewrite working components unnecessarily.

---

# Step 2 — Define Claim Segments

Create a deterministic claim segmentation utility.

Example claim:

"Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences."

Possible segments:

1. "Cas9 can be programmed with guide RNA"
2. "to cleave specific double-stranded DNA target sequences"

The implementation should NOT hard-code biology terminology.

The segmentation logic must work for general scientific claims.

Use lightweight deterministic rules such as:

- sentence boundaries
- conjunctions
- comma/semicolon boundaries
- meaningful phrase boundaries
- claim preprocessing/tokenization already present in the project

Avoid producing dozens of tiny fragments.

A short claim may produce only 1–3 segments.

---

# Step 3 — Match Evidence to Claim Segments

For each claim segment, determine which evidence items provide support.

Use existing evidence data:

- evidence.text
- relevance_score
- claim_overlap
- numeric_overlap
- claim_numbers
- evidence_numbers
- section

Do NOT make another LLM call.

Create a deterministic matching score.

Possible approach:

segment_match_score =
    lexical_overlap
    + phrase_overlap
    + numeric_overlap
    + existing evidence claim_overlap
    + relevance_score

Normalize the final score to 0–1.

The exact formula should be chosen after inspecting the existing ranking utilities.

Avoid duplicating existing ranking logic if reusable helpers already exist.

---

# Step 4 — Determine Segment Coverage

Each claim segment should receive a coverage status.

Supported statuses:

- SUPPORTED
- PARTIALLY_SUPPORTED
- UNSUPPORTED
- CONTRADICTED

Use conservative thresholds.

Example:

High-quality matching evidence
→ SUPPORTED

Some relevant evidence but incomplete coverage
→ PARTIALLY_SUPPORTED

Little/no relevant evidence
→ UNSUPPORTED

Explicit contradicting evidence
→ CONTRADICTED

Do not infer contradiction merely because evidence is missing.

Absence of evidence should never automatically become CONTRADICTED.

---

# Step 5 — Build Traceability Metadata

Add a new optional traceability object to the verification response.

Suggested structure:

claim_traceability: {
    "segments": [
        {
            "id": "segment_1",
            "text": "Cas9 can be programmed with guide RNA",
            "status": "SUPPORTED",
            "coverage_score": 0.91,
            "evidence_ids": [
                "..."
            ]
        },
        {
            "id": "segment_2",
            "text": "to cleave specific double-stranded DNA target sequences",
            "status": "SUPPORTED",
            "coverage_score": 0.88,
            "evidence_ids": [
                "..."
            ]
        }
    ],
    "overall_coverage": 0.89
}

Keep this field optional/backward compatible.

Do not break existing API consumers.

---

# Step 6 — Validate Traceability Against Verdict

The traceability layer must be consistent with the final validated verdict.

Examples:

SUPPORTS:
- Most important claim segments should have supporting evidence.
- If a major segment is unsupported, consider adding a traceability warning.
- Do NOT automatically change the verdict.

OVERSTATED:
- Identify the unsupported/exaggerated segment.
- Show which evidence supports only the weaker version of the claim.

CONTRADICTS:
- Identify the contradicted segment.
- Link it to contradicting evidence where available.

INSUFFICIENT:
- Identify the segments where evidence coverage is insufficient.

FABRICATED:
- Show that the claim lacks adequate supporting evidence, while preserving the existing validator behavior.

Traceability must explain the verdict, not replace the verdict validator.

---

# Step 7 — Add Traceability Warnings

Add optional warnings such as:

- "Part of the claim has limited evidence coverage."
- "The claim contains a segment that is not directly supported."
- "Evidence supports the general mechanism but not the full specificity of the claim."
- "No retrieved evidence directly supports this claim segment."

Keep warnings deterministic and concise.

Do not generate warnings using the LLM.

---

# Step 8 — Backend Tests

Add deterministic unit tests.

Create:

backend/app/tests/test_claim_traceability.py

Test at minimum:

1. Single-segment claim with strong evidence
2. Multi-segment claim
3. Supported segment
4. Partially supported segment
5. Unsupported segment
6. Contradicted segment
7. No evidence
8. Numeric claim matching
9. Evidence ID preservation
10. Overall coverage calculation
11. Traceability consistency with SUPPORTS
12. Traceability consistency with INSUFFICIENT
13. Traceability consistency with OVERSTATED
14. Traceability consistency with CONTRADICTS
15. No LLM calls
16. Backward compatibility when traceability is absent

All tests must be deterministic.

---

# Step 9 — Frontend Types

Update:

frontend/src/types/backend-verification.ts

and

frontend/src/types/verification.ts

Add types for:

ClaimTraceability
ClaimSegment
ClaimSegmentStatus

Example:

type ClaimSegmentStatus =
  | "SUPPORTED"
  | "PARTIALLY_SUPPORTED"
  | "UNSUPPORTED"
  | "CONTRADICTED";

Each segment should contain:

- id
- text
- status
- coverageScore
- evidenceIds

---

# Step 10 — Frontend Mapper

Update:

frontend/src/services/verificationMapper.ts

Map backend:

claim_traceability

to frontend:

claimTraceability

Preserve backward compatibility.

If the backend does not provide traceability:

- do not crash
- hide the traceability UI
- continue rendering the existing verification report

---

# Step 11 — Create Claim Traceability UI

Create:

frontend/src/components/verification/ClaimTraceabilityPanel.tsx

Design requirements:

- Match existing SciVerify dark research UI.
- Clean and minimal.
- No excessive animations.
- Responsive.
- Clearly show the original claim.
- Split claim into segments.
- Show status for each segment.
- Show coverage score.
- Show linked evidence count.

Example:

CLAIM TRACEABILITY

"Cas9 can be programmed with guide RNA"
✓ SUPPORTED
Coverage: 91%
2 supporting evidence items

"to cleave specific double-stranded DNA target sequences"
✓ SUPPORTED
Coverage: 88%
3 supporting evidence items

Overall coverage: 89%

---

# Step 12 — Evidence Linking Interaction

When the user clicks a claim segment:

- Highlight the corresponding evidence cards.

When the user clicks an evidence reference:

- Scroll to the corresponding evidence card.
- Visually highlight it briefly.

Do not create a completely separate evidence system.

Reuse the existing:

VerificationEvidenceCard

and evidence IDs.

If implementing interactive highlighting requires shared state, use the existing Zustand architecture where appropriate.

Do not introduce unnecessary global state.

---

# Step 13 — Evidence Card Enhancement

Update:

frontend/src/components/verification/VerificationEvidenceCard.tsx

Add an optional indicator such as:

"Supports: Claim segment 1"

or:

"Linked to 2 claim segments"

Keep the existing evidence text and metadata unchanged.

Do not make the card excessively large.

---

# Step 14 — Verification Report Layout

Update:

frontend/src/components/verification/VerificationReportView.tsx

Suggested order:

1. Verdict Header
2. Claim Traceability
3. Evidence
4. Agent Analysis
5. Validation Warnings
6. Suggested Correction

The traceability section should appear near the top because it explains WHY the verdict was reached.

Do not remove existing sections.

---

# Step 15 — History Compatibility

Existing Supabase history stores the complete VerificationResult JSON.

Ensure claim_traceability is stored automatically as part of result_json.

Do NOT create a separate Supabase table for traceability.

Old history records without claim_traceability must still load correctly.

The UI should gracefully hide the traceability panel for old records.

---

# Step 16 — API Backward Compatibility

Existing API fields must remain unchanged.

Add only:

claim_traceability: optional

Do not rename:

- verdict
- confidence
- evidence
- prosecutor
- defender
- adjudicator
- suggested_correction
- agent_agreement
- validation_warnings

---

# Step 17 — Validation Against Current Cas9 Example

Use the existing test claim:

"Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences."

DO NOT hard-code this claim into production logic.

Use it only for manual verification.

Expected behavior:

The claim should be split into meaningful segments.

Evidence from:

- Conclusions
- One-Sentence Summary
- Fig. 5
- Cas9 chimeric RNA sections

should map to the relevant segments.

The UI should clearly show why the claim is considered supported.

---

# Step 18 — Run Full Test Suite

Backend:

cd backend

python -m pytest -q

Expected:

All existing tests remain passing.

Frontend:

cd frontend

npm run lint
npm run build

All must pass.

Do not add a new frontend test framework.

---

# Step 19 — Final Verification

After implementation:

1. Start backend.
2. Start frontend.
3. Run the existing Cas9 verification through Swagger/frontend.
4. Confirm:
   - verification still returns 200
   - verdict unchanged
   - evidence unchanged
   - agents unchanged
   - validator unchanged
   - traceability appears
   - evidence links work
   - history still saves
   - old history records still load
5. Confirm no additional Groq/LLM request is introduced.

---

# Acceptance Criteria

The implementation is complete only if:

- [ ] Claim is deterministically segmented.
- [ ] Each segment receives a coverage status.
- [ ] Evidence is linked to relevant claim segments.
- [ ] No additional LLM call is introduced.
- [ ] Existing evidence ranking remains unchanged.
- [ ] Existing verdict validation remains unchanged.
- [ ] Existing agents remain unchanged.
- [ ] Traceability is optional/backward compatible.
- [ ] Existing history records still work.
- [ ] New traceability metadata is persisted automatically in result_json.
- [ ] Clicking a claim segment highlights its evidence.
- [ ] Clicking evidence navigates back to the related evidence.
- [ ] Backend tests pass.
- [ ] Frontend lint passes.
- [ ] Frontend build passes.
- [ ] Cas9 verification still returns SUPPORTS.
- [ ] No fabricated or unsupported evidence is introduced.

# Important

Before implementing, inspect the existing code and explain briefly:

1. Where claim preprocessing currently happens.
2. Where evidence ranking already calculates overlap.
3. Where the final validated verdict is produced.
4. Where VerificationResult is constructed.
5. Where evidence cards are rendered.
6. How evidence IDs are currently mapped between backend and frontend.

Then implement the smallest clean change that satisfies this plan.

Do not rewrite unrelated code.