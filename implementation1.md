# Implementation Plan: Verification History & Persistence

## Objective

Implement a reliable verification history system for SciVerify.

Users should be able to:

1. Run a verification
2. Save the result
3. See previous verifications
4. Search/filter history
5. Open a previous verification
6. View the complete original verification report

Do not modify the verification intelligence pipeline.

---

## Step 1 — Inspect existing history implementation

Inspect:

- frontend/src/pages/HistoryPage
- frontend/src/services
- frontend/src/store
- existing Supabase/database integration
- backend schemas/models related to history
- existing history API endpoints, if any

Determine whether history is currently:

- mocked
- local-only
- persisted in Supabase
- partially implemented

Do not create duplicate persistence mechanisms.

---

## Step 2 — Define verification history record

A history record should contain at minimum:

- id
- claim
- DOI
- paper title
- verdict
- confidence
- summary
- created_at

Where practical, preserve the complete verification result so that reopening history does not require another Groq call.

Optional:

- evidence
- agent results
- validation warnings
- suggested correction

---

## Step 3 — Persistence strategy

Use the project's existing database/Supabase setup.

Do NOT introduce another database.

Do NOT store API keys or secrets.

Create the minimum required schema/table if persistence does not already exist.

Suggested table:

verification_history

Fields:

- id
- claim
- doi
- paper_title
- verdict
- confidence
- result_json
- created_at

Use JSON for the complete verification response if that matches the existing architecture.

---

## Step 4 — Save successful verification

After a successful verification:

Frontend/backend should persist the result.

Important:

Do not make persistence failure cause an otherwise successful verification to fail.

Example:

Verification succeeds
→ attempt save
→ if save fails:
   show verification normally
   optionally show "Could not save to history"

---

## Step 5 — History page

Replace placeholder/mock history with persisted records.

Display:

- claim
- paper
- verdict
- confidence
- date

Example:

OVERSTATED · 85%

Cas9 can be programmed with guide RNA...

A Programmable Dual-RNA–Guided DNA Endonuclease...

Aug 13, 2026

---

## Step 6 — Search

Allow searching by:

- claim
- DOI
- paper title

Search should be case-insensitive.

Do not implement complicated full-text search unless already supported.

---

## Step 7 — Filtering

Add verdict filters:

- All
- SUPPORTS
- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

Add optional date sorting:

- Newest
- Oldest

---

## Step 8 — Open previous verification

Clicking a history item should open the complete verification report.

Important:

Do NOT call Groq again.

Load the stored result.

The report should use the same VerificationReportView used by live verification.

Avoid duplicating the report UI.

---

## Step 9 — Delete history

Allow deleting an individual history record.

Add confirmation before deletion.

Do not add bulk delete unless already required.

---

## Step 10 — Empty state

If there is no history:

Show a useful empty state:

"No verification history yet."

"Verify a scientific claim to see your results here."

Provide a CTA to the verification page.

---

## Step 11 — Loading/error states

Handle:

- loading history
- database/network failure
- delete failure
- malformed history record

Never show raw backend/database errors.

---

## Step 12 — Privacy

Do not log or expose:

- API keys
- internal prompts
- provider credentials

Treat stored verification results as user data.

---

## Step 13 — Tests

Add tests only using the existing testing infrastructure.

At minimum verify:

- successful result saved
- history loads
- search works
- verdict filtering works
- history item opens stored report
- deletion works
- empty state works
- persistence failure does not break verification
- malformed record is handled safely

Do not call Groq in tests.

---

## Step 14 — Regression

Backend:

python -m pytest -q

Expected baseline:

176 passed

Frontend:

npm run lint
npm run build

All must pass.

---

## Acceptance Criteria

- [ ] Verification results persist
- [ ] History page uses real persisted data
- [ ] Search works
- [ ] Verdict filtering works
- [ ] History can be opened
- [ ] Opening history does not call Groq
- [ ] History can be deleted
- [ ] Empty state works
- [ ] Persistence failure does not destroy successful verification
- [ ] Existing verification report UI is reused
- [ ] No verification intelligence logic changed
- [ ] No API keys/secrets stored
- [ ] Backend tests remain 176+
- [ ] Frontend lint passes
- [ ] Frontend build passes

Do not commit or push automatically.