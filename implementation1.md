PHASE 5 — AUTHENTICATED SCIVerify WORKSPACE
============================================

PROJECT: SciVerify
PHASE: 5
SCOPE: Frontend workspace only

==================================================
OBJECTIVE
==================================================

Build the authenticated SciVerify Workspace.

The landing page is already complete.
Supabase authentication is already implemented.
The design system is already implemented.

Now replace the current `/app/home` placeholder with the actual SciVerify product workspace.

The user should be able to:

1. Log in/register
2. Enter the authenticated workspace
3. Start a new citation verification
4. Enter a scientific claim
5. Enter a citation / DOI / URL
6. Submit the verification request
7. See a realistic verification loading state
8. See a MOCK verification result
9. View previous verification history using mock data
10. Navigate between workspace sections
11. View their profile
12. Logout
13. Use the workspace responsively on desktop/tablet/mobile

IMPORTANT:

THIS PHASE IS FRONTEND ONLY.

DO NOT implement the real verification engine.

DO NOT integrate:
- Crossref
- Semantic Scholar
- OpenAlex
- arXiv APIs
- PubMed
- LangGraph
- CrewAI
- AutoGen
- OpenAI
- Llama
- DeepSeek
- Any external AI/model API
- Real evidence retrieval
- Real citation verification

Use mock data and clean service abstractions so the real backend can be connected later without redesigning the frontend.

==================================================
1. EXISTING PROJECT — DO NOT BREAK
==================================================

Completed phases:

Phase 1 — Frontend Foundation
Phase 2 — Design System
Phase 3 — Supabase Authentication
Phase 4 — SciVerify Landing Page
Phase 4.1 — Prosecutor / Defender / Adjudicator architecture

Existing routes:

/
 /ui-preview
 /login
 /register
 /forgot-password
 /reset-password
 /app/home

Existing authentication:

- Supabase Auth
- AuthProvider
- authStore
- ProtectedRoute
- GuestRoute
- Profile handling
- Session persistence
- Logout
- Password reset

Existing design system:

src/components/ui/
src/components/sciverify/

Existing SciVerify components:

- VerdictBadge
- VerdictCard
- ConfidenceBar
- AgentCard
- EvidenceCard
- SourceCard
- ProgressStep
- VerificationTimeline
- StatCard

Reuse these components.

Do NOT recreate components that already exist.

Do NOT change the existing landing page unless absolutely necessary.

Do NOT modify authentication implementation unless required for integration.

==================================================
2. PRODUCT POSITIONING
==================================================

SciVerify is:

"An evidence-first multi-agent scientific citation verification system."

The authenticated workspace should feel like professional research software.

It must NOT look like:

- Generic chatbot UI
- Gaming dashboard
- Social media dashboard
- Generic AI assistant
- Overly colorful SaaS dashboard

Maintain:

- Dark research-focused aesthetic
- Professional typography
- Clean spacing
- Subtle borders
- Refined cards
- Evidence-focused UI
- Clear information hierarchy

Reuse the existing SciVerify design tokens and components.

==================================================
3. ROUTE STRUCTURE
==================================================

Create the following protected routes:

/app
/app/home
/app/verify
/app/history
/app/settings

All `/app/*` routes must require authentication.

If unauthenticated:

/app/* → /login

If authenticated:

/login or /register → existing authenticated redirect behavior

Preserve existing redirect behavior.

Recommended behavior:

/app
    ↓
/app/home

==================================================
4. APPLICATION LAYOUT
==================================================

Create an authenticated application layout.

Recommended structure:

src/layouts/AppLayout.tsx

The layout should contain:

LEFT SIDEBAR
- SciVerify logo/name
- Dashboard
- New Verification
- History
- Settings

BOTTOM SIDEBAR
- User avatar
- User name
- Email
- Profile/settings option
- Logout

MAIN CONTENT
- Top/header area where appropriate
- Page content
- Responsive behavior

Desktop:

Sidebar remains visible.

Mobile:

Sidebar becomes a drawer/mobile navigation.

Use the existing Drawer component if suitable.

Do not create unnecessary UI libraries.

==================================================
5. APP HEADER
==================================================

Create a reusable workspace header.

Example:

Dashboard

"Review your citation verification activity."

OR:

New Verification

"Check whether a scientific claim is actually supported by its cited source."

Header should support:

- Page title
- Short description
- Optional actions

Keep it minimal.

==================================================
6. DASHBOARD — /app/home
==================================================

Replace the current placeholder.

Create a useful research dashboard.

Top:

"Welcome back, {user name}"

Subtitle:

"Verify scientific claims against their cited evidence."

Primary CTA:

"New Verification"

Dashboard statistics using mock data:

- Total Verifications
- Supported
- Overstated
- Contradicted
- Unclear

Do not claim these are real statistics.

Use clearly structured mock data.

Example:

Total Verifications
24

Supported
14

Overstated
5

Contradicted
3

Insufficient
2

Below statistics:

"Recent Verifications"

Show 3–5 mock verification records.

Each record can display:

- Claim preview
- Citation/source
- Verdict
- Confidence
- Date
- View button

Use existing:

VerdictBadge
ConfidenceBar
Card

If there are no records, create a professional empty state.

==================================================
7. NEW VERIFICATION — /app/verify
==================================================

This is the most important page in Phase 5.

Create a clean verification form.

Page title:

"New Verification"

Description:

"Check whether a scientific claim is supported by its cited source."

FORM:

SECTION 1 — CLAIM

Label:

"Scientific Claim"

Textarea placeholder:

"Example: The proposed method improves model accuracy by 20% on real-world datasets."

Supporting text:

"Enter the exact claim you want to verify."

SECTION 2 — CITATION

Label:

"Citation / Source"

Textarea or input placeholder:

"Paste a DOI, URL, citation, or reference."

Supporting text:

"Provide the citation that supposedly supports the claim."

OPTIONAL:

Source type selector:

- DOI
- URL
- Citation
- Reference text

Do not make this unnecessarily complex.

==================================================
8. FORM VALIDATION
==================================================

Use the project's existing validation approach.

Validate:

Claim:
- Required
- Minimum reasonable length
- Maximum reasonable length

Citation:
- Required
- Minimum reasonable length

Show clear inline validation messages.

Examples:

"Please enter the scientific claim."

"Please provide the citation or source."

Do not use browser alert().

Use existing UI components.

==================================================
9. VERIFY BUTTON
==================================================

Primary button:

"Verify Citation"

When clicked:

1. Validate form
2. Enter loading state
3. Simulate verification
4. Display mock result

For now:

DO NOT call an AI API.

DO NOT call a real backend.

Create a mock verification service.

Example:

src/services/mockVerificationService.ts

Function:

verifyCitationMock()

Return a realistic verification result.

Use a short artificial delay such as 1–2 seconds.

This is only for demonstrating the frontend workflow.

==================================================
10. VERIFICATION LOADING STATE
==================================================

When verification begins, show a professional progress state.

Example:

"Analyzing citation..."

Then:

"Checking source..."

"Reviewing evidence..."

"Running agent analysis..."

"Preparing verdict..."

These are simulated frontend states only.

Use existing:

ProgressStep
VerificationTimeline
Spinner
Skeleton

Do not pretend these are actual AI operations yet.

The UI should make it visually clear that this is a demonstration/mock workflow.

==================================================
11. MOCK VERIFICATION RESULT
==================================================

After loading, show a complete realistic result.

Example:

Verdict:

OVERSTATED

Confidence:

76%

Claim:

"The proposed intervention reduces the primary biomarker by 40%."

Citation:

Example citation

Summary:

"The cited source supports a reduction in the measured outcome, but the reported magnitude in the claim is stronger than the evidence presented."

==================================================
12. AGENT RESULTS
==================================================

Show the three real SciVerify agents:

PROSECUTOR

Role:

"Challenges the claim and searches for weaknesses, limitations, contradictions, and overstatements."

Example result:

"The source reports a smaller effect size than the claim suggests."

DEFENDER

Role:

"Builds the strongest evidence-based case supporting the claim."

Example result:

"The cited study does demonstrate a statistically significant improvement under the tested conditions."

ADJUDICATOR

Role:

"Weighs both arguments against the available evidence."

Example result:

"The direction of the effect is supported, but the magnitude is overstated."

Use existing AgentCard component.

Do not implement actual agent logic.

This is mock presentation data.

==================================================
13. EVIDENCE CARDS
==================================================

Use existing EvidenceCard and SourceCard components.

Show mock evidence.

Each evidence card should contain:

- Source title
- Authors or publication
- Year
- Relevant excerpt
- Relevance score
- Evidence type
- Source identifier if appropriate

Example:

Primary evidence

"Example Scientific Study"

2024

"The intervention group showed a statistically significant reduction..."

Relevance: 94%

Do not use fabricated real-world claims that could be mistaken for actual verified research.

Prefer clearly labeled demo/mock content.

==================================================
14. FINAL VERDICT CARD
==================================================

Use the existing VerdictCard.

Display:

Verdict
OVERSTATED

Confidence
76%

Reasoning

"The cited evidence supports the direction of the claim but does not support the reported magnitude."

Also show:

Claim
vs
Evidence

This should be one of the strongest visual sections of the page.

==================================================
15. SUGGESTED CORRECTION
==================================================

Add a mock correction section.

Title:

"Suggested Correction"

Show:

Original claim

"The intervention reduces the biomarker by 40%."

Suggested wording

"The intervention was associated with a statistically significant reduction in the biomarker under the tested conditions."

Important:

Add a clear label:

"Suggested correction — requires human approval"

SciVerify must NOT automatically modify a research paper.

==================================================
16. HISTORY — /app/history
==================================================

Create a verification history page.

Show mock verification records.

Columns/cards:

- Claim
- Source
- Verdict
- Confidence
- Date
- Action

Possible actions:

"View"

Clicking View should open the result detail UI.

For Phase 5, this can use mock data.

Add:

- Search input
- Verdict filter

Keep filtering frontend-only.

No database persistence yet.

==================================================
17. SETTINGS — /app/settings
==================================================

Create a simple user settings page.

Display:

Profile

- Full Name
- Email
- Avatar placeholder

Account:

- Logout

Do not build complex account management.

Do not implement password changing unless already supported by the existing auth architecture.

Reuse the existing profile data from Supabase auth/profile services.

==================================================
18. MOCK DATA ARCHITECTURE
==================================================

Create a dedicated mock data structure.

Suggested:

src/mocks/
    verification.ts

Define typed interfaces.

Example conceptual structure:

VerificationResult

{
  id,
  claim,
  citation,
  verdict,
  confidence,
  summary,
  prosecutor,
  defender,
  adjudicator,
  evidence,
  suggestedCorrection,
  createdAt
}

Use existing verdict types/constants.

Do not duplicate verdict definitions.

Import verdict configuration from:

src/constants/verdicts.ts

==================================================
19. TYPES
==================================================

Create or extend proper TypeScript types.

Suggested:

src/types/verification.ts

Include:

- VerificationRecord
- VerificationResult
- AgentAnalysis
- EvidenceItem
- SuggestedCorrection

Keep types reusable for future backend integration.

Do NOT use `any`.

==================================================
20. STATE MANAGEMENT
==================================================

Use the existing Zustand setup if appropriate.

Do not introduce another state management library.

The verification form may use local React state unless global state is actually necessary.

Keep the architecture simple.

==================================================
21. RESPONSIVE DESIGN
==================================================

Desktop:

- Persistent sidebar
- Wide content area
- Two-column result layouts where appropriate

Tablet:

- Reduced sidebar width
- Flexible cards

Mobile:

- Sidebar becomes drawer
- Single-column content
- Inputs full width
- Cards stack vertically
- Agent cards stack
- Evidence cards stack

Test at:

Desktop
Tablet
Mobile

Do not allow horizontal scrolling.

==================================================
22. ACCESSIBILITY
==================================================

Ensure:

- Proper labels
- Keyboard navigation
- Visible focus states
- Buttons have meaningful text
- Form errors are accessible
- Color is not the only way to communicate verdicts

Use existing semantic components.

==================================================
23. ERROR / EMPTY / LOADING STATES
==================================================

Implement:

Dashboard:
- Empty history state

History:
- No results state
- Search returns no results

Verification:
- Loading state
- Validation errors
- Mock verification failure state

Use existing:

Spinner
Skeleton
Badge
Card
Modal/Drawer where appropriate

==================================================
24. NAVIGATION
==================================================

Sidebar navigation:

Dashboard
→ /app/home

New Verification
→ /app/verify

History
→ /app/history

Settings
→ /app/settings

Logout
→ existing Supabase logout flow

Logo:
→ /app/home

Do not break public navigation.

==================================================
25. AUTHENTICATION INTEGRATION
==================================================

Use the existing authentication system.

Do NOT create another auth provider.

Use:

AuthProvider
useAuth
authStore
ProtectedRoute
profileService

The workspace must only be accessible when authenticated.

User information should come from the existing authenticated session/profile.

==================================================
26. DESIGN REQUIREMENTS
==================================================

Maintain the current SciVerify design system:

- Dark background
- Refined surface cards
- Blue/purple primary accent
- Semantic verdict colors
- Subtle borders
- Professional research aesthetic
- Minimal visual noise
- No excessive gradients
- No gaming-style effects
- No chatbot bubbles

Use existing components before creating new ones.

==================================================
27. COMPONENT STRUCTURE
==================================================

Use a clean structure similar to:

src/
  components/
    app/
      AppSidebar.tsx
      AppHeader.tsx
      UserMenu.tsx
      WorkspaceNav.tsx

    verification/
      VerificationForm.tsx
      VerificationLoading.tsx
      VerificationResult.tsx
      AgentAnalysisPanel.tsx
      VerificationSummary.tsx
      SuggestedCorrection.tsx

  layouts/
    AppLayout.tsx

  pages/
    AppHomePage.tsx
    VerifyPage.tsx
    HistoryPage.tsx
    SettingsPage.tsx

  mocks/
    verification.ts

  services/
    mockVerificationService.ts

  types/
    verification.ts

Adjust names to match the existing project conventions.

Do not blindly create every file if existing components already fulfill the purpose.

==================================================
28. DO NOT OVERBUILD
==================================================

Do NOT implement:

- Real citation checking
- DOI validation through external APIs
- Literature retrieval
- PDF processing
- AI agents
- LLM calls
- LangGraph
- CrewAI
- Database verification records
- Cloud storage
- Real-time collaboration
- Team management
- Notifications
- Billing
- Analytics backend

These belong to future phases.

==================================================
29. TESTING
==================================================

After implementation run:

npm run lint

npm run build

Verify routes:

/
 /ui-preview
 /login
 /register
 /app/home
 /app/verify
 /app/history
 /app/settings

Manual test:

1. Open `/app/home` while logged out
2. Confirm redirect to `/login`
3. Log in
4. Confirm `/app/home` loads
5. Navigate to `/app/verify`
6. Submit empty form
7. Confirm validation appears
8. Enter claim + citation
9. Click Verify Citation
10. Confirm loading state
11. Confirm mock result appears
12. Confirm Prosecutor appears
13. Confirm Defender appears
14. Confirm Adjudicator appears
15. Confirm verdict appears
16. Confirm evidence cards appear
17. Confirm suggested correction appears
18. Navigate to History
19. Confirm mock records appear
20. Navigate to Settings
21. Confirm user information appears
22. Logout
23. Confirm redirect to `/login`
24. Attempt `/app/home`
25. Confirm protected route redirects to login

==================================================
30. IMPORTANT FUTURE COMPATIBILITY
==================================================

The mock verification service MUST be isolated.

Later we should be able to replace:

mockVerificationService.verifyCitationMock()

with:

realVerificationService.verifyCitation()

without rebuilding the entire UI.

The UI should consume a typed VerificationResult.

This is extremely important.

Phase 5 should establish the frontend contract for the future verification engine.

==================================================
31. FINAL ACCEPTANCE CRITERIA
==================================================

Phase 5 is complete only when:

[ ] Authenticated workspace exists
[ ] `/app/*` routes are protected
[ ] Sidebar works
[ ] Mobile navigation works
[ ] Dashboard works
[ ] New Verification page works
[ ] Claim input works
[ ] Citation input works
[ ] Validation works
[ ] Mock verification loading works
[ ] Mock verification result works
[ ] Prosecutor result displayed
[ ] Defender result displayed
[ ] Adjudicator result displayed
[ ] Verdict displayed
[ ] Confidence displayed
[ ] Evidence cards displayed
[ ] Suggested correction displayed
[ ] History page works
[ ] Settings page works
[ ] Logout works
[ ] Empty states work
[ ] Error states work
[ ] Responsive layout works
[ ] Existing landing page still works
[ ] `/ui-preview` still works
[ ] Authentication routes still work
[ ] `npm run lint` passes
[ ] `npm run build` passes
[ ] No TypeScript `any`
[ ] No real AI/API integrations were added
[ ] No backend verification logic was added

==================================================
32. PHASE COMPLETION REPORT
==================================================

When finished, provide a concise report containing:

1. Files created
2. Files modified
3. Routes added
4. Components created
5. Mock verification flow
6. Authentication integration
7. Responsive behavior
8. Tests performed
9. `npm run lint` result
10. `npm run build` result
11. Any remaining issues

Do NOT proceed to Phase 6.

Phase 5 must remain frontend-only.