# SciVerify — Frontend Enhancement Phase
## Verification Experience & Research-Grade Results UI

You are working on the existing SciVerify frontend.

IMPORTANT:
This is an enhancement phase, NOT a rebuild.

The following already exist and MUST be preserved:
- Supabase authentication
- AuthProvider
- ProtectedRoute / GuestRoute
- Landing page
- Design system
- UI components
- `/ui-preview`
- `/login`
- `/register`
- `/forgot-password`
- `/reset-password`
- `/app`
- `/app/home`
- `/app/verify`
- `/app/history`
- `/app/settings`
- Zustand stores
- Existing verification types
- Existing mock verification service
- Existing responsive layout
- Existing AppLayout / sidebar / header
- Existing VerdictBadge, VerdictCard, EvidenceCard, AgentCard, ConfidenceBar, VerificationTimeline, etc.

Do NOT replace the architecture.
Do NOT create unnecessary new dependencies.
Reuse existing components wherever possible.

The goal of this phase is to make the verification experience look and behave like a serious research verification product.

==================================================
## 1. PRIMARY GOAL
==================================================

Improve `/app/verify` and the verification result experience so the complete workflow is visually clear:

User
  ↓
Claim + Citation
  ↓
Verification Progress
  ↓
Prosecutor + Defender
  ↓
Adjudicator
  ↓
Evidence
  ↓
Final Verdict
  ↓
Suggested Correction
  ↓
Verification Report

The frontend must be designed so that later we can replace the existing mock verification service with a real backend without redesigning the UI.

Do NOT implement real AI/API logic in this phase.

Keep the existing mock verification service working.

==================================================
## 2. VERIFICATION INPUT
==================================================

Review the existing `/app/verify` implementation.

Do NOT rebuild it if it already satisfies the requirements.

The input UI must clearly contain:

### Claim

A large textarea where the user enters the scientific claim.

Example:

"AI improves software development productivity."

### Citation / DOI

An input for:
- DOI
- citation string
- paper identifier

Example:

10.1145/example

### Optional context

If the current architecture already supports it, allow a small optional context field.

Do NOT add unnecessary fields.

### Primary CTA

Button:

"Verify Citation"

The form must:
- validate input
- show useful validation errors
- prevent empty submissions
- disable submission while verification is running
- preserve existing Zod validation
- work correctly on mobile

Reuse existing Button, Input, Textarea, Card and validation components.

==================================================
## 3. LIVE VERIFICATION PROGRESS
==================================================

Upgrade the current loading experience.

Do NOT simply show:

"Loading..."

Instead create a research-grade verification progress interface.

Show these stages:

1. Citation identified
2. Paper existence checked
3. Evidence retrieved
4. Prosecutor analysis
5. Defender analysis
6. Adjudicator decision
7. Final report generated

Example visual state:

VERIFYING CITATION

✓ Citation identified
✓ Paper existence verified
✓ Evidence retrieved

⚔ Prosecutor
   Searching for contradictions...

⚔ Defender
   Finding supporting evidence...

◉ Adjudicator
   Waiting for arguments...

Then transition to:

✓ Prosecutor completed
✓ Defender completed
✓ Adjudicator completed

Generating final verdict...

Requirements:

- Clearly show current active step
- Completed steps use success state
- Pending steps use neutral state
- Active agent has an obvious visual indicator
- Use the existing VerificationTimeline / ProgressStep components if suitable
- Reuse AgentCard where appropriate
- Do not create excessive animations
- Respect prefers-reduced-motion
- Keep animations subtle and professional

The loading flow should make the multi-agent architecture obvious during a hackathon demo.

==================================================
## 4. AGENT DEBATE VIEW
==================================================

Upgrade the result page to clearly show the three-agent debate.

Use:

PROSECUTOR
Role:
Challenge the claim

DEFENDER
Role:
Build the strongest supporting case

ADJUDICATOR
Role:
Make the final evidence-backed decision

Visual structure:

                 AGENT DEBATE

┌─────────────────────┐
│ ⚔ PROSECUTOR       │
│                     │
│ Challenge analysis  │
│                     │
│ Findings...         │
└─────────────────────┘

           VS

┌─────────────────────┐
│ 🛡 DEFENDER         │
│                     │
│ Supporting analysis │
│                     │
│ Findings...         │
└─────────────────────┘

           ↓

┌─────────────────────┐
│ ⚖ ADJUDICATOR      │
│                     │
│ Final reasoning...  │
│                     │
│ Verdict...          │
└─────────────────────┘

Important:

Do not use "Parser", "Retriever", or "Synthesizer" anywhere in the actual SciVerify verification workflow.

The public and product-facing architecture is:

Prosecutor
Defender
Adjudicator

Use the existing AgentCard component where possible.

Each agent should show:
- Name
- Role
- Status
- Summary/findings
- Evidence references if available

Keep the UI readable.

Do not expose hidden chain-of-thought or private model reasoning.

The UI should show concise, user-facing findings/evidence summaries, not internal reasoning traces.

==================================================
## 5. EVIDENCE CARDS
==================================================

Improve the existing EvidenceCard presentation.

Each evidence card should support:

SOURCE

Paper title

Authors

Year

Journal / venue

DOI or source identifier

--------------------------------

RELEVANT EVIDENCE

A relevant extracted passage or evidence summary.

--------------------------------

WHY THIS MATTERS

Short explanation of how this evidence relates to the claim.

--------------------------------

Evidence strength:
HIGH / MEDIUM / LOW

Relevance:
XX%

[Open Source]

Requirements:

- Reuse the existing EvidenceCard
- Make source information easy to scan
- Evidence must be visually separated from interpretation
- Include source links when available
- Do not fabricate URLs
- Do not make fake evidence look like real evidence
- Mock evidence should remain clearly represented by the existing mock system

Later the backend will provide real retrieved evidence.

==================================================
## 6. VERDICT EXPLANATION
==================================================

Improve the final verdict section.

Do not only display:

OVERSTATED — 76%

Instead show:

OVERSTATED

Confidence: 76%

Short explanation:

"The paper supports the general direction of the claim, but the cited statement exaggerates the reported effect."

Then show concise evidence factors:

✓ Direction of effect supported
✓ Study population matches
✗ Claimed effect size is higher than reported

Use the existing verdict configuration.

Supported verdicts are:

SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED

Do not introduce additional verdict types unless the existing architecture explicitly requires them.

Use the existing:
- VerdictBadge
- VerdictCard
- ConfidenceBar

Make the final verdict visually prominent but not flashy.

==================================================
## 7. SUGGESTED CORRECTION
==================================================

Improve the existing SuggestedCorrectionPanel.

Display:

ORIGINAL CLAIM

"The method improves accuracy by 40%."

↓

PROBLEM

"The cited paper reports a 23% improvement."

↓

SUGGESTED CORRECTION

"The method improved accuracy by 23% under the reported experimental conditions."

Add:

[Copy correction]

Also clearly display:

"Human approval required"

Important:

SciVerify MUST NOT automatically modify the user's paper.

The system only suggests a correction.

Use proper visual distinction between:
- Original claim
- Problem
- Suggested correction

The copy button should:
- copy the correction
- show success feedback
- work on supported browsers
- fail gracefully if clipboard access is unavailable

==================================================
## 8. FULL VERIFICATION REPORT
==================================================

Create or improve a complete verification report view.

This should feel like a research report, not a chatbot response.

Suggested structure:

SCIENCE VERIFICATION REPORT

--------------------------------
CLAIM
--------------------------------

[Claim]

--------------------------------
CITATION
--------------------------------

[Citation]

--------------------------------
CITATION AUTHENTICITY
--------------------------------

✓ VERIFIED

or

✕ FABRICATED

--------------------------------
AGENT DEBATE
--------------------------------

Prosecutor
[summary]

Defender
[summary]

Adjudicator
[summary]

--------------------------------
EVIDENCE
--------------------------------

Evidence Card 1

Evidence Card 2

--------------------------------
FINAL VERDICT
--------------------------------

[Verdict Badge]

Confidence: XX%

[Explanation]

--------------------------------
SUGGESTED CORRECTION
--------------------------------

[Correction]

[Copy correction]

Human approval required.

Requirements:

- Reuse existing components
- Make the report easy to scan
- Use strong visual hierarchy
- Avoid excessive decoration
- Ensure responsive layout
- Desktop should use available width effectively
- Mobile should stack sections naturally

==================================================
## 9. HISTORY
==================================================

Review the existing `/app/history`.

Keep it simple.

Each verification entry should show:

Claim
Citation
Verdict
Confidence
Date

Example:

AI improves...
SUPPORTS
91%
Aug 11, 2026

Method increases...
OVERSTATED
76%
Aug 11, 2026

Model achieves...
CONTRADICTS
84%
Aug 10, 2026

Unknown paper...
FABRICATED
98%
Aug 10, 2026

Clicking an entry should open the complete verification result/report.

Do not implement database persistence in this phase unless it already exists.

Continue using the existing frontend state/mock architecture.

==================================================
## 10. DASHBOARD
==================================================

Review `/app/home`.

Keep the dashboard focused.

It should communicate:

Welcome back, [user name]

Quick action:
[New Verification]

Optional lightweight statistics:

Total verifications
Supported
Overstated
Contradicted
Fabricated

Recent verifications

Do NOT build a huge analytics dashboard.

Do NOT add charts unless they provide real value.

The dashboard should primarily help the user start a verification quickly.

==================================================
## 11. UX STATES
==================================================

Every important screen must handle:

### Empty state

Example:

"No verifications yet."

[Start your first verification]

### Loading state

Use existing Skeleton / Spinner / Progress components.

### Success state

Clearly show completed verification.

### Error state

Show a useful error message and retry option.

Example:

"Verification could not be completed."

[Try again]

Do not expose raw stack traces to users.

### Invalid input

Show clear validation messages directly near the relevant field.

==================================================
## 12. RESPONSIVE DESIGN
==================================================

The complete workflow must work on:

- Desktop
- Laptop
- Tablet
- Mobile

Desktop:
- sidebar remains usable
- content uses available width
- evidence and agent cards can use grid layouts

Mobile:
- sidebar becomes drawer
- cards stack
- buttons remain accessible
- no horizontal scrolling
- long paper titles wrap correctly
- evidence text remains readable

==================================================
## 13. DESIGN RULES
==================================================

Preserve the existing SciVerify design system.

Use:
- dark research UI
- existing accent color
- existing verdict colors
- glass/surface styling already established
- existing spacing system
- existing typography
- existing cards

Do NOT introduce:
- new color systems
- random gradients
- gaming UI
- chatbot bubbles
- excessive glow
- excessive animations
- unnecessary icons
- unrelated design patterns

SciVerify should look like a serious academic/research verification product.

==================================================
## 14. COMPONENT REUSE
==================================================

Before creating a new component, check whether an existing component can be reused.

Existing relevant components include:

- Button
- Input
- Textarea
- Select
- Badge
- Card
- Panel
- Tabs
- Drawer
- Modal
- Spinner
- Skeleton
- VerdictBadge
- VerdictCard
- ConfidenceBar
- AgentCard
- EvidenceCard
- ProgressStep
- VerificationTimeline
- StatCard
- VerificationForm
- VerificationLoading
- VerificationResultView
- AgentAnalysisPanel
- SuggestedCorrectionPanel

Extend existing components when appropriate instead of duplicating them.

==================================================
## 15. DATA CONTRACT
==================================================

Do NOT redesign the entire verification data model.

First inspect:

src/types/verification.ts

and the existing:

mock verification service
verification store
verification result components

Make the UI consume the existing typed VerificationResult.

If additional fields are genuinely required for the improved UI, add them carefully and update all mock data.

Potential fields include:

- citationStatus
- verificationStages
- agent summaries
- evidence
- verdict
- confidence
- explanation
- correction

Do not add unnecessary fields.

The architecture must remain easy to connect to a real backend later.

==================================================
## 16. MOCK DATA
==================================================

Keep the mock verification system functional.

Create realistic examples covering all five verdicts:

SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED

At least one example should demonstrate:

Claim:
A statement that is directionally correct but exaggerates the reported effect.

Expected:

OVERSTATED

This should make the demo showcase the strongest SciVerify capability.

==================================================
## 17. IMPORTANT PRODUCT BOUNDARY
==================================================

Do NOT implement the real AI engine in this phase.

Do NOT add:
- OpenAI API
- Gemini API
- Claude API
- CrewAI backend
- LangGraph backend
- Crossref API
- Semantic Scholar API
- arXiv API

Those belong to the backend/verification-engine phase.

The frontend must simply be prepared to consume real verification results later.

==================================================
## 18. DO NOT BUILD
==================================================

Do NOT spend time on:

- Chatbot
- AI assistant sidebar
- Social features
- Notifications
- Team collaboration
- Profile customization
- Theme switching
- Complex animations
- PDF editor
- Full manuscript editor
- Huge analytics dashboards
- Dozens of charts
- Unnecessary settings
- Payment system
- Admin dashboard

These are outside the current scope.

==================================================
## 19. ACCESSIBILITY
==================================================

Ensure:

- buttons have meaningful labels
- inputs have labels
- keyboard navigation works
- focus states are visible
- sufficient contrast
- loading states are understandable
- reduced-motion preference is respected
- icon-only buttons have accessible labels

==================================================
## 20. TESTING
==================================================

After implementation run:

npm run lint

npm run build

Fix all errors.

Then manually verify:

1. `/`
2. `/login`
3. `/register`
4. `/ui-preview`
5. `/app/home`
6. `/app/verify`
7. `/app/history`
8. `/app/settings`

Test:

### Verification

- Empty claim rejected
- Empty citation rejected
- Valid claim accepted
- Valid citation accepted
- Verify button enters loading state
- Progress stages change correctly
- Prosecutor appears
- Defender appears
- Adjudicator appears
- Final verdict appears
- Confidence appears
- Evidence cards appear
- Suggested correction appears
- Copy correction works
- History entry is created
- History entry can reopen result
- Error state works
- Mobile layout works

### Authentication

Verify that protected routes still require authentication.

Do NOT break:
- login
- register
- logout
- session persistence
- protected routing

==================================================
## 21. IMPORTANT IMPLEMENTATION RULE
==================================================

Before modifying files:

1. Inspect the existing project structure.
2. Inspect existing verification components.
3. Inspect existing types.
4. Inspect existing Zustand store.
5. Inspect existing mock service.
6. Understand how `/app/verify` currently works.
7. Reuse existing architecture.

Do not blindly overwrite files.

Make the smallest clean changes required.

==================================================
## 22. FINAL ACCEPTANCE CRITERIA
==================================================

This phase is complete only when:

✓ Existing authentication still works
✓ Existing landing page is unchanged
✓ `/ui-preview` still works
✓ `/app/*` remains protected
✓ `/app/verify` has polished input UX
✓ Verification progress clearly shows the pipeline
✓ Prosecutor / Defender / Adjudicator are visually distinct
✓ Agent debate is easy to understand
✓ Evidence cards are easy to inspect
✓ Verdict explanation is clear
✓ All five verdict types work
✓ Confidence is displayed
✓ Suggested correction works
✓ Human approval warning is visible
✓ Copy correction works
✓ History works
✓ Complete verification report is available
✓ Empty/loading/error states exist
✓ Responsive design works
✓ No chatbot UI was introduced
✓ No unnecessary dependencies were added
✓ Mock verification still works
✓ `npm run lint` passes
✓ `npm run build` passes

==================================================
## 23. FINAL OUTPUT
==================================================

When finished, provide a concise implementation report containing:

1. Files created
2. Files modified
3. Components reused
4. Features implemented
5. Routes affected
6. Mock verification behavior
7. Tests performed
8. `npm run lint` result
9. `npm run build` result
10. Any remaining limitations

Do not claim real AI/backend functionality was implemented.

The purpose of this phase is to make the SciVerify frontend completely ready for the real multi-agent verification backend in the next phase.