# Implementation Plan: Verification Decision Quality & Verdict Consistency

## Objective

Improve the reliability and consistency of SciVerify's final verification verdict.

The current pipeline successfully:

OpenAlex
→ Full-text retrieval
→ CAPTCHA/interstitial detection
→ HTML/PDF parsing
→ Evidence deduplication
→ Evidence ranking
→ Top 5 evidence
→ Prosecutor
→ Defender
→ Adjudicator
→ Final verdict

The next improvement should focus on ensuring that the final verdict is logically consistent with the retrieved evidence and agent outputs.

DO NOT rewrite the existing retrieval/ranking pipeline.

DO NOT modify the Groq/LLM provider unless absolutely necessary.

DO NOT redesign the Prosecutor, Defender, or Adjudicator prompts unless required to fix a demonstrated inconsistency.

---

# Step 1 — Inspect the existing verification pipeline

Before making changes, inspect:

- backend/app/services/
- verification-related services
- Prosecutor implementation
- Defender implementation
- Adjudicator implementation
- verification schemas/models
- evidence pipeline
- existing verification tests

Understand exactly how:

1. Evidence is passed to Prosecutor
2. Evidence is passed to Defender
3. Agent outputs are normalized
4. Adjudicator receives the agent results
5. Final verdict is generated
6. Confidence is calculated
7. Suggested correction is generated

Do not rewrite working functionality.

---

# Step 2 — Define verdict consistency rules

Create deterministic validation rules for the final result.

Supported verdicts:

- SUPPORTS
- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

The validator should check whether the final verdict is compatible with the available evidence and agent outputs.

Examples:

### SUPPORTS

Appropriate when:

- Strong supporting evidence exists
- Evidence directly addresses the claim
- Defender supports the claim
- There is no strong contradiction

### OVERSTATED

Appropriate when:

- Core claim is supported
- But the claim is broader/stronger than the evidence
- Important conditions, limitations, or qualifiers are missing

Example:

Claim:
"Cas9 can cleave any DNA sequence."

Evidence:
Cas9 can cleave target DNA when an appropriate PAM is present.

Expected:
OVERSTATED

### CONTRADICTS

Appropriate when:

- Evidence directly conflicts with the claim
- Strong contradictory evidence exists

### INSUFFICIENT

Appropriate when:

- Evidence is missing
- Evidence is irrelevant
- Evidence quality is too weak
- Evidence cannot establish whether the claim is true or false

### FABRICATED

Appropriate only when:

- The cited paper does not contain the claimed information
- The claim appears to attribute unsupported information to the paper
- There is strong evidence that the citation cannot support the claim

Do not classify normal uncertainty as FABRICATED.

---

# Step 3 — Add deterministic verdict validation

Create a small validation layer after the Adjudicator result.

Possible location:

backend/app/services/verification_validator.py

or another appropriate existing verification service.

The validator should receive:

- claim
- retrieved evidence
- Prosecutor result
- Defender result
- Adjudicator result

It should return:

- validated verdict
- confidence adjustment if necessary
- validation warnings/reasons

Important:

The validator must NOT blindly override the LLM.

It should only correct obvious contradictions between:

- evidence
- agent stances
- final verdict

---

# Step 4 — Evidence strength checks

Use existing evidence metadata where possible.

Consider:

- relevance_score
- claim_overlap
- numeric_overlap
- section
- supporting_evidence
- contradicting_evidence
- number of unique evidence items

Do NOT introduce hard-coded biology-specific keywords.

The logic must remain domain-independent.

Example:

If the adjudicator says SUPPORTS but:

- there are zero supporting evidence IDs
- all evidence is unrelated
- claim overlap is extremely low

then flag the result as inconsistent.

Example:

If adjudicator says CONTRADICTS but:

- no contradicting evidence exists
- all evidence supports the claim

then flag the result.

---

# Step 5 — Confidence calibration

Improve confidence reliability.

Do not allow confidence to remain extremely high when evidence quality is poor.

For example:

If:

- verdict = SUPPORTS
- evidence count = 1
- relevance_score is low
- claim overlap is low

then confidence should be reduced.

If:

- multiple unique evidence chunks strongly match the claim
- evidence comes from meaningful article sections
- Prosecutor and Defender agree

then confidence can remain high.

Do not invent scientific probabilities.

Confidence should represent verification confidence, not scientific certainty.

---

# Step 6 — Agent disagreement handling

Explicitly detect disagreement.

Examples:

Prosecutor:
Challenge

Defender:
Support

Adjudicator:
SUPPORTS

This is not automatically wrong.

However, the system should record that there was agent disagreement.

Add a field if appropriate:

agent_agreement

or

validation_warnings

Do not break the existing API unnecessarily.

Prefer backward-compatible additions.

---

# Step 7 — Suggested correction consistency

Validate suggested corrections.

If verdict is:

SUPPORTS

then suggested_correction should normally be null.

If verdict is:

OVERSTATED

then a useful correction should normally exist.

If verdict is:

CONTRADICTS

a correction may be provided if the evidence allows one.

If verdict is:

INSUFFICIENT

do not invent a corrected scientific claim.

The correction must not introduce information unsupported by the evidence.

Do not use another LLM call just to validate the correction unless absolutely necessary.

---

# Step 8 — Preserve existing API behavior

Do NOT break the current response schema.

Existing fields must continue to work:

- status
- claim
- verdict
- confidence
- summary
- reasoning
- paper
- evidence
- prosecutor
- defender
- adjudicator
- suggested_correction
- detail

If new fields are needed, make them optional/backward-compatible.

---

# Step 9 — Unit tests

Add deterministic unit tests.

Do NOT call Groq in these tests.

Test at minimum:

1. SUPPORTS with strong supporting evidence
2. SUPPORTS with weak/irrelevant evidence
3. OVERSTATED with strong evidence but missing qualifier
4. CONTRADICTS with strong contradictory evidence
5. INSUFFICIENT with no useful evidence
6. FABRICATED with unsupported citation evidence
7. Adjudicator SUPPORTS but no supporting evidence
8. Adjudicator CONTRADICTS but no contradicting evidence
9. Prosecutor/Defender disagreement
10. High confidence with weak evidence → confidence reduced
11. OVERSTATED → suggested correction exists
12. SUPPORTS → correction normally null
13. INSUFFICIENT → no fabricated correction
14. Evidence IDs referenced by agents must exist in retrieved evidence

All tests must be deterministic.

---

# Step 10 — Regression testing

Run the complete test suite:

python -m pytest -q

Expected:

All existing tests continue passing.

The current baseline is:

162 passed

Do not accept regressions.

---

# Step 11 — Live verification

Do not repeatedly call Groq while developing.

The Groq organization currently has a daily token limit and may return:

HTTP 429
tokens per day (TPD)

Therefore:

- Use mocked/unit tests during implementation
- Avoid unnecessary live calls
- Perform only one or two live verification tests after implementation
- Use the existing Cas9 DOI test once Groq quota resets

DOI:

10.1126/science.1225829

Claim:

Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences.

Expected behavior:

The evidence strongly supports the core claim but indicates an important PAM requirement.

A reasonable verdict is:

OVERSTATED

with a correction similar to:

"Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences, provided that the target sequence is adjacent to a PAM sequence."

Do not hard-code this expected verdict into production logic.

---

# Step 12 — Logging

Add concise diagnostic logging.

Log:

- original adjudicator verdict
- validated verdict
- evidence count
- supporting evidence count
- contradicting evidence count
- agent agreement/disagreement
- confidence before/after validation
- validation warnings

Never log:

- API keys
- secrets
- full prompts
- unnecessary sensitive content

---

# Step 13 — Acceptance criteria

The implementation is complete only when:

- [ ] Existing evidence retrieval remains unchanged
- [ ] Existing evidence ranking remains unchanged
- [ ] Prosecutor/Defender behavior remains unchanged unless absolutely necessary
- [ ] Adjudicator behavior remains unchanged unless absolutely necessary
- [ ] Final verdict consistency is validated
- [ ] Weak evidence cannot produce unjustifiably high confidence
- [ ] Agent disagreement is detectable
- [ ] Suggested correction is consistent with verdict
- [ ] Evidence IDs are validated
- [ ] No domain-specific hard-coded rules are introduced
- [ ] No Groq calls are used in unit tests
- [ ] All existing tests pass
- [ ] New deterministic tests pass
- [ ] API remains backward compatible

Target:

162+ tests passing.

---

# Important Constraints

1. Do not modify the retrieval/parser/ranking implementation.
2. Do not undo the previous evidence-quality improvements.
3. Do not add biology-specific rules.
4. Do not add unnecessary LLM calls.
5. Do not depend on Groq availability for tests.
6. Prefer deterministic validation over another AI call.
7. Keep the implementation modular and easy to remove/adjust.
8. Inspect the existing code before editing.
9. Show the files that will be modified before making broad changes.
10. After implementation, provide:
   - files changed
   - logic added
   - tests added
   - total test count
   - any remaining limitations