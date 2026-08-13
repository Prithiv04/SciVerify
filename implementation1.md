# Implementation Plan: SciVerify Verification Result Transparency UI

## Objective

Update the SciVerify frontend to clearly present the complete verification result returned by the backend.

The backend now returns:

- verdict
- confidence
- summary
- reasoning
- evidence
- prosecutor
- defender
- adjudicator
- suggested_correction
- agent_agreement
- validation_warnings

The frontend must expose these results clearly without changing backend behavior.

---

## Step 1 — Inspect existing frontend

Inspect:

- frontend/src/
- verification pages
- verification result components
- evidence components
- API/client services
- Zustand stores
- existing UI components
- routing
- loading/error states

Understand the current verification flow:

Verification Form
→ API request
→ Loading
→ Verification Result

Do not rewrite working components unnecessarily.

---

## Step 2 — Update API types

Update the frontend TypeScript types/interfaces to match the current backend response.

Include:

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
- agent_agreement
- validation_warnings

Make new fields optional for backward compatibility.

Do not use `any` unless absolutely necessary.

---

## Step 3 — Improve the main verdict section

Create a clear verdict header.

Example:

VERIFICATION RESULT

OVERSTATED

Confidence: 85%

Then display:

- claim
- paper title
- DOI
- confidence
- agent agreement

Use the existing SciVerify design system.

Do not introduce a completely different visual style.

---

## Step 4 — Add verdict-specific UI

Support:

SUPPORTS
- Positive/support indication

OVERSTATED
- Warning indication
- Show suggested correction

CONTRADICTS
- Contradiction indication

INSUFFICIENT
- Insufficient evidence indication
- Clearly explain that the paper evidence was insufficient

FABRICATED
- Strong warning indication

Do not hard-code scientific conclusions.

Only style based on the verdict value.

---

## Step 5 — Evidence section

Display the top 5 evidence items returned by the backend.

For every evidence item show:

- section
- relevance score
- claim overlap
- numeric overlap if available
- evidence text
- source URL
- chunk ID if useful

Example:

Evidence #1

Section:
Results

Relevance:
91%

Claim overlap:
87%

Evidence:
"...."

Keep the original evidence text unchanged.

Do not perform additional evidence processing in the frontend.

---

## Step 6 — Evidence quality visualization

Add a simple visual representation of:

- relevance score
- claim overlap

For example:

Relevance
█████████░ 91%

Claim overlap
████████░░ 87%

Keep the visualization lightweight.

Do not add unnecessary charts.

---

## Step 7 — Agent analysis section

Create an expandable agent analysis section.

Show:

### Prosecutor

- stance
- confidence
- analysis
- key points
- supporting evidence
- contradicting evidence

### Defender

- stance
- confidence
- analysis
- key points
- supporting evidence
- contradicting evidence

### Adjudicator

- verdict
- confidence
- reasoning
- supporting evidence
- contradicting evidence
- suggested correction

The Adjudicator section should be visually distinguished as the final reasoning stage.

---

## Step 8 — Agent agreement

Use:

agent_agreement

Display:

Agents agree

or

Agents disagree

If null:

Agreement information unavailable

Do not infer agreement in the frontend.

Use the backend value directly.

---

## Step 9 — Validation warnings

If:

validation_warnings.length > 0

display a "Validation Notes" section.

Example:

Validation Notes

⚠ Confidence reduced because evidence strength was weak.

⚠ Agent disagreement detected.

If there are no warnings:

Do not show an empty warning box.

---

## Step 10 — Suggested correction

Display suggested correction only when it exists.

For example:

Suggested Correction

"Cas9 can be programmed with guide RNA to cleave specific double-stranded DNA target sequences, provided that the target sequence is adjacent to a PAM sequence."

For SUPPORTS/INSUFFICIENT, respect the backend's null value.

Do not generate corrections in the frontend.

---

## Step 11 — Error states

Handle backend responses gracefully.

Support:

- network failure
- HTTP 422
- HTTP 429
- retrieval failure
- FULL_TEXT_UNAVAILABLE
- insufficient evidence
- generic server error

Never show raw stack traces to the user.

Provide a useful message.

For example:

"Full text could not be retrieved from the available sources. Please try another paper."

For rate limiting:

"The AI verification service is temporarily rate limited. Please try again later."

Do not expose API keys or internal configuration.

---

## Step 12 — Loading state

Improve the existing verification loading experience.

Show the pipeline stages:

1. Finding paper
2. Retrieving full text
3. Extracting evidence
4. Prosecutor analysis
5. Defender analysis
6. Adjudication
7. Validating result

These are UI stages only.

Do not change backend execution.

---

## Step 13 — Responsive design

Ensure the result page works on:

- desktop
- laptop
- tablet
- mobile

Avoid horizontal overflow.

Evidence cards and agent panels should collapse appropriately.

---

## Step 14 — Accessibility

Ensure:

- sufficient text contrast
- keyboard-accessible expandable sections
- meaningful button labels
- semantic headings
- accessible status/error messages

Do not rely solely on colors to communicate verdicts.

---

## Step 15 — Tests

Run existing frontend tests.

If the project has no frontend test setup, do not introduce a large testing framework unnecessarily.

At minimum verify:

- successful result rendering
- each verdict renders correctly
- evidence renders
- agent agreement renders
- validation warnings render
- suggested correction renders
- null optional fields do not crash the UI
- API errors render correctly
- loading state renders correctly

---

## Step 16 — Backend compatibility

Do NOT modify:

- evidence retrieval
- document parser
- evidence ranking
- Prosecutor
- Defender
- Adjudicator
- LLM provider
- verification validator

unless a genuine API compatibility issue is discovered.

The frontend should consume the existing backend response.

---

## Acceptance Criteria

- [ ] TypeScript types match backend response
- [ ] Final verdict is clearly visible
- [ ] Confidence is visible
- [ ] Claim and paper information are visible
- [ ] Top 5 evidence items are displayed
- [ ] Evidence relevance/claim overlap are displayed
- [ ] Prosecutor analysis is visible
- [ ] Defender analysis is visible
- [ ] Adjudicator analysis is visible
- [ ] Agent agreement is displayed
- [ ] Validation warnings are displayed when present
- [ ] Suggested correction is displayed when present
- [ ] All verdict types are supported
- [ ] API errors are handled gracefully
- [ ] Loading stages are clear
- [ ] Responsive layout works
- [ ] Existing frontend functionality remains intact

After implementation, report:

1. Files changed
2. Components added/modified
3. API types updated
4. Tests performed
5. Screenshots/manual verification performed
6. Any remaining limitations

Do not commit or push automatically.