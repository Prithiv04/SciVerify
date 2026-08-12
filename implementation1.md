# Phase 5.2 — Premium Research Workspace UI & UX Polish

## Objective

Upgrade the existing SciVerify authenticated workspace from a functional dashboard into a polished, research-grade AI verification product.

The current frontend is functional and the core flows already work. DO NOT rebuild the application.

This phase is strictly a UI/UX enhancement phase.

The goal is:

"Research-grade scientific verification workspace with visible multi-agent intelligence."

The interface should feel comparable in polish to modern products such as Linear, Vercel, Perplexity, Raycast, and high-quality research tools while preserving SciVerify's existing dark research-focused visual identity.

---

# IMPORTANT CONSTRAINTS

DO NOT:

- rebuild the routing architecture
- rewrite authentication
- change Supabase integration
- replace Zustand
- replace React Router
- replace Tailwind
- replace existing UI primitives
- remove existing functionality
- add a chatbot
- add an AI assistant sidebar
- add unnecessary analytics
- add social features
- add team collaboration
- add theme switching
- add excessive animations
- add fake functionality
- introduce external APIs
- change the mock verification engine
- modify the landing page unless required for shared design consistency

Reuse the existing components wherever possible.

Before changing anything, inspect the existing component architecture and identify reusable components.

---

# DESIGN DIRECTION

SciVerify should visually communicate:

- scientific credibility
- evidence-first verification
- multi-agent reasoning
- trust
- precision
- structured analysis

Avoid:

- gaming UI
- excessive neon
- chatbot aesthetics
- oversized gradients
- excessive glassmorphism
- decorative UI that does not communicate information

Use restrained visual hierarchy.

The existing dark theme should remain.

---

# 1. GLOBAL APP SHELL

Improve:

src/layouts/AppLayout.tsx
src/components/app/AppSidebar.tsx
src/components/app/AppHeader.tsx

## Sidebar

Keep the existing sidebar structure:

SciVerify
Dashboard
New Verification
History
Settings

Improve it with:

- better active-state treatment
- subtle hover states
- clearer icon alignment
- improved spacing
- slightly stronger visual separation
- workspace identity
- subtle bottom account section
- polished collapse/mobile behavior

The active navigation item should be immediately recognizable without being overly bright.

Add a subtle section label if appropriate:

WORKSPACE

Dashboard
New Verification
History

ACCOUNT

Settings

Do not make the sidebar unnecessarily large.

---

# 2. APP HEADER

Improve the header hierarchy.

Current:

Welcome back, Prithiv R
Verify scientific claims against their cited evidence.

Improve to something like:

Welcome back, Prithiv R

Evidence-backed verification for your scientific claims.

Add a visually strong primary CTA:

+ New Verification

The CTA should be clearly visible near the top-right.

On smaller screens:

- stack appropriately
- maintain accessibility
- avoid overflow

---

# 3. DASHBOARD — MAKE IT FEEL LIKE A REAL PRODUCT

Modify:

src/pages/AppHomePage.tsx

The dashboard should have these sections:

1. Hero/header
2. Verification statistics
3. Recent verification activity
4. Quick verification CTA

---

## 3.1 Statistics

Keep the existing five statistics:

Total Verifications
Supported
Overstated
Contradicted
Fabricated

Improve the StatCard visually.

Do NOT change the existing data.

Each card should have:

- label
- large number
- subtle icon
- consistent height
- consistent number alignment
- subtle hover elevation
- subtle border treatment
- optional tiny supporting text where useful

Example:

TOTAL VERIFICATIONS
6

All verification runs

SUPPORTED
1

Evidence aligned

OVERSTATED
2

Claims requiring review

CONTRADICTED
1

Evidence conflicts

FABRICATED
1

Citation authenticity issue

Do not invent statistics.

If supporting text is not available from existing data, keep it minimal.

---

# 4. RECENT VERIFICATIONS

Improve the current verification cards.

Current cards feel too flat.

Each verification should visually communicate:

Claim
Citation
Verdict
Confidence
Date
Action

Create a stronger card hierarchy:

┌────────────────────────────────────────────────────┐
│ OVERSTATED                              76%         │
│                                                    │
│ The method improves accuracy by 40% on real-world │
│ software development tasks.                       │
│                                                    │
│ 10.1000/demo.2024.001                              │
│                                                    │
│ Confidence ━━━━━━━━━━━━━━━━━━━━━━━ 76%             │
│                                                    │
│ Aug 11, 2026                         View report → │
└────────────────────────────────────────────────────┘

The verdict should be visually prominent.

Confidence should have a clean progress indicator.

Do not make cards excessively tall.

Add subtle hover interaction:

- border becomes slightly more visible
- card lifts by a few pixels
- View report arrow shifts slightly

Keep animations restrained.

---

# 5. DASHBOARD EMPTY/NEW VERIFICATION CTA

Create a polished "Start a verification" section if appropriate.

Example:

┌──────────────────────────────────────────────────────┐
│                                                      │
│  Verify a scientific claim                           │
│                                                      │
│  Compare the claim against its cited evidence        │
│  using Prosecutor, Defender, and Adjudicator.        │
│                                                      │
│                 [ Start verification → ]             │
│                                                      │
└──────────────────────────────────────────────────────┘

This should visually reinforce the core product concept.

---

# 6. NEW VERIFICATION PAGE

Modify:

src/pages/VerifyPage.tsx
src/components/verification/VerificationForm.tsx

The current form works, so DO NOT rebuild the functionality.

Improve the visual experience.

The page should feel like a specialized scientific verification workspace.

Add a compact introductory header:

NEW VERIFICATION

Evaluate whether a scientific claim is supported by its cited evidence.

Then organize the form into a clear card.

---

## Claim input

Make "Scientific claim" the dominant field.

Use a large textarea.

Placeholder:

"Example: The method improves software development productivity by 40%."

Add character guidance if already supported by validation.

---

## Source type

Improve the current DOI / URL / Citation / Reference text selector.

Make the options visually clear.

Example:

SOURCE TYPE

[ DOI ] [ URL ] [ Citation ] [ Reference ]

Do not add functionality unless already supported.

---

## Citation

Improve the citation field hierarchy.

Show a small helper:

"Provide the DOI, citation, or paper identifier that supposedly supports the claim."

---

## Optional context

Keep it visually secondary.

Label:

ADDITIONAL CONTEXT (OPTIONAL)

This should not compete with the claim field.

---

# 7. VERIFICATION PIPELINE PREVIEW

Before the user submits, add a subtle informational panel explaining what happens.

Example:

VERIFICATION PIPELINE

01  Evidence retrieval
02  Prosecutor challenge
03  Defender analysis
04  Adjudicator decision

This should be informational only.

Do not pretend that the agents are running before verification starts.

This reinforces SciVerify's unique architecture.

---

# 8. VERIFICATION LOADING EXPERIENCE

Modify:

src/components/verification/VerificationLoading.tsx

This is one of the most important UI improvements.

Make the multi-agent process visually impressive but professional.

Use:

VERIFYING CITATION

✓ Citation identified
✓ Paper existence verified
✓ Evidence retrieved

Then:

┌─────────────────────────────┐
│ ⚔ Prosecutor               │
│ Challenging the claim...   │
│ ● Running                  │
└─────────────────────────────┘

VS

┌─────────────────────────────┐
│ 🛡 Defender                │
│ Building supporting case   │
│ ● Running                  │
└─────────────────────────────┘

↓

┌─────────────────────────────┐
│ ⚖ Adjudicator              │
│ Evaluating both arguments  │
│ ○ Waiting                  │
└─────────────────────────────┘

Use the existing progress system.

Do not introduce undefined icons or dependencies.

Verify every imported icon exists.

This specifically prevents runtime errors such as:

ReferenceError: Swords is not defined

Run lint/build after implementation.

---

# 9. AGENT DEBATE RESULT

Modify:

src/components/verification/AgentAnalysisPanel.tsx

This should become one of SciVerify's strongest UI sections.

Create clear visual separation:

PROSECUTOR
Challenge the claim

DEFENDER
Build the supporting case

Then:

ADJUDICATOR
Final assessment

Use the existing AgentCard/design system where possible.

Add:

- agent role
- conclusion
- evidence summary
- status
- subtle agent icon
- clear VS relationship

Do not create fake additional agent reasoning beyond existing mock data.

---

# 10. VERDICT RESULT

Modify:

src/components/verification/VerdictExplanation.tsx

Make the verdict feel like the final decision of the verification process.

Example:

FINAL VERDICT

OVERSTATED

76% confidence

The evidence supports the general direction of the claim,
but the cited magnitude is higher than the reported result.

Evidence factors:

✓ Direction of effect supported
✓ Study population matches
✕ Claimed effect size is higher than reported

Make the verdict visually dominant.

Use the existing VerdictBadge / verdict styling.

---

# 11. EVIDENCE CARDS

Improve:

src/components/sciverify/EvidenceCard.tsx

The card should feel like a research evidence object.

Structure:

SOURCE

Paper title

Authors / publication / year

DOI

────────────────────────

RELEVANT EVIDENCE

"Actual extracted passage..."

────────────────────────

WHY THIS MATTERS

Explanation of how the evidence relates to the claim.

────────────────────────

Evidence strength: HIGH
Relevance: 94%

[Open source →]

Improve typography and spacing.

Do not fabricate additional evidence.

Use the existing mock data.

---

# 12. SUGGESTED CORRECTION

Improve:

src/components/verification/SuggestedCorrectionPanel.tsx

Make this feel like a professional research editing recommendation.

Structure:

SUGGESTED CORRECTION

ORIGINAL CLAIM

"The method improves accuracy by 40%."

↓

WHY IT NEEDS REVISION

The cited study reports a 23% improvement.

↓

RECOMMENDED WORDING

"The method improved accuracy by 23% under the
reported experimental conditions."

[ Copy correction ]

Human approval required.

The human approval message should be visually obvious.

Never automatically modify user content.

---

# 13. FULL VERIFICATION REPORT

Improve:

src/components/verification/VerificationReportView.tsx

This should feel like SciVerify's signature screen.

Add strong visual hierarchy:

SCIENCE VERIFICATION REPORT

Claim
────────────────────────

Citation
────────────────────────

Citation authenticity
✓ VERIFIED

Agent debate
────────────────────────

Prosecutor
...

Defender
...

Adjudicator
...

Evidence
────────────────────────

Evidence cards

Final verdict
────────────────────────

OVERSTATED
76% confidence

Suggested correction
────────────────────────

...

Add a polished report header.

Include a clear:

← Back to verification

or equivalent existing navigation.

Do not add export functionality unless already implemented.

If export is not implemented, do not show a fake export button.

---

# 14. HISTORY PAGE

Modify:

src/pages/HistoryPage.tsx

Current functionality should remain.

Improve each history item with:

- verdict badge
- confidence
- claim
- citation
- date
- View report action

Improve search/filter controls.

Make the list easier to scan.

Use consistent spacing.

Consider grouping the verdict/filter controls into a compact toolbar.

Do not add unnecessary charts.

---

# 15. SETTINGS

Keep Settings intentionally simple.

Do not over-design it.

Improve:

- profile card
- account information hierarchy
- logout action
- spacing
- typography

Do not add unnecessary settings.

---

# 16. MICRO-INTERACTIONS

Add restrained interactions:

- card hover
- button hover
- navigation hover
- subtle progress transitions
- smooth section appearance

Respect:

prefers-reduced-motion

Do not add:

- excessive particles
- floating animations
- flashy gradients
- continuous motion
- distracting effects

---

# 17. RESPONSIVE DESIGN

Verify:

Desktop
Tablet
Mobile

Desktop:

- sidebar visible
- content centered
- cards properly sized

Tablet:

- sidebar/drawer behavior preserved
- cards adapt

Mobile:

- drawer navigation
- single-column cards
- readable typography
- no horizontal scrolling
- CTA remains accessible

---

# 18. ACCESSIBILITY

Ensure:

- buttons have accessible labels
- interactive cards are keyboard accessible where applicable
- focus states remain visible
- color is not the only indicator of verdict
- text contrast remains readable
- reduced motion is respected

---

# 19. VISUAL CONSISTENCY

Reuse existing:

Button
Badge
Card
Panel
Input
Textarea
Select
Divider
Spinner
AgentCard
EvidenceCard
VerdictBadge
VerdictCard
ConfidenceBar
ProgressStep
VerificationTimeline
StatCard

Do not create duplicate components if an existing component can be improved/reused.

---

# 20. IMPORTANT TECHNICAL CHECK

Before finishing:

Search the entire frontend for:

- undefined Lucide icons
- unused imports
- missing components
- invalid routes
- console errors
- broken imports
- hardcoded external URLs that should not exist
- fake buttons with no functionality

Especially verify all icons imported into:

VerificationLoading.tsx
AgentAnalysisPanel.tsx
VerificationReportView.tsx
StatCard.tsx

are actually exported by the installed icon library.

Do not use an icon unless it exists.

---

# 21. VERIFICATION CHECKLIST

Run:

npm run lint

npm run build

Then manually verify:

/app/home
/app/verify
/app/history
/app/settings

Test:

1. Dashboard loads.
2. Stats are aligned.
3. New Verification CTA works.
4. Verification form renders.
5. Submit mock verification.
6. Loading pipeline renders.
7. Prosecutor renders.
8. Defender renders.
9. Adjudicator renders.
10. Result renders.
11. Evidence cards render.
12. Verdict explanation renders.
13. Suggested correction renders.
14. Copy correction works.
15. History renders.
16. Search works.
17. Verdict filtering works.
18. View report works.
19. Settings renders.
20. Logout still works.
21. No blank screen.
22. No console ReferenceError.
23. No horizontal overflow on mobile.

---

# 22. SUCCESS CRITERIA

The finished UI should no longer feel like:

"basic CRUD dashboard."

It should feel like:

"professional scientific verification workspace powered by a multi-agent evidence pipeline."

The multi-agent architecture must remain the visual identity of the product:

Claim
↓
Evidence
↓
Prosecutor + Defender
↓
Adjudicator
↓
Verdict
↓
Correction

Do not change the underlying functionality.

Focus on visual hierarchy, information density, research credibility, consistency, accessibility, and polished UX.

At the end, provide a concise implementation report containing:

- files created
- files modified
- components reused
- visual improvements
- responsive improvements
- accessibility improvements
- lint result
- build result
- any remaining limitations

Do NOT commit or push changes.