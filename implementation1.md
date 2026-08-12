# Phase 5.3 — Professional SciVerify Dashboard Completion

## Objective

Upgrade the existing authenticated `/app/home` dashboard from a polished MVP dashboard into a professional, research-grade workspace.

The dashboard already has:

- Welcome header
- New Verification CTA
- Verification statistics
- Verification Overview
- Verification Summary
- Claim Challenger → Evidence Defender → Final Reviewer workflow
- Recent Verification Activity
- History page
- Existing responsive layout
- Supabase authentication
- Existing Zustand verification state
- Existing mock verification data

DO NOT rebuild existing functionality.

This phase is focused on:
1. Professional dashboard UX
2. Useful workspace insights
3. Quick actions
4. Needs-review workflow
5. Correct historical report navigation
6. Empty-state polish
7. Responsive and visual refinement

---

# PRIORITY 0 — Exact Historical Verification Report Navigation

This is the most important requirement.

## Current problem

The "View report" links in Recent Verification Activity currently point to:

`/app/verify`

This can open the generic verification page instead of the specific historical verification.

## Required behavior

When the user clicks:

`View report`

for a historical verification, open the EXACT verification result associated with that record.

Expected flow:

Recent Verification
        ↓
View report
        ↓
Full Verification Report
        ↓
Claim
Citation
Citation authenticity
Agent debate
Evidence
Final verdict
Confidence
Suggested correction

## Implementation

Use the existing verification ID / record identity wherever possible.

Do NOT create duplicate verification data.

Do NOT introduce a backend/database requirement in this phase.

If the current Zustand store is the source of truth, use it to retrieve the selected verification.

The report should render using the existing:

- VerificationReportView
- VerdictExplanation
- AgentAnalysisPanel
- EvidenceCard
- SuggestedCorrectionPanel
- Existing verification types

If route state is already being used, improve it rather than creating a parallel system.

Prefer a stable route/state approach such as:

`/app/verify/:verificationId`

if that fits the existing routing architecture.

Do NOT break the existing `/app/verify` new-verification route.

Expected:

`/app/verify` → New Verification

`/app/verify/:verificationId` → Existing Verification Report

If using a route parameter, update routing carefully while preserving authentication protection.

---

# PRIORITY 1 — Quick Actions

Add a compact "Quick Actions" section to the dashboard.

Example:

Quick Actions

[ + New Verification ]   [ View History ]   [ Recent Reports ]

## Requirements

### New Verification

Navigate to:

`/app/verify`

### View History

Navigate to:

`/app/history`

### Recent Reports

Navigate to the most recent verification report.

If there is no verification history, disable or gracefully handle this action.

Use existing Button components and design-system styles.

Do not create unnecessary new button styles.

The section should feel like a professional workspace toolbar rather than a large card.

---

# PRIORITY 2 — Verification Health / Workspace Status

Add a small workspace-status section.

Example:

Verification health

● System ready

6 verification runs
83% average confidence

## Requirements

Use existing verification data/state.

Do NOT hardcode values.

The status should reflect the current application state.

For example:

System ready

when the frontend verification system is available.

If the application has an error/unavailable state, make the component capable of representing that state without breaking the UI.

## IMPORTANT

Current verification runs are MOCK verification runs.

Do not imply that the displayed results came from real scientific APIs or real AI agents.

Use subtle wording such as:

"Demo verification environment"

or

"Mock verification data"

where appropriate.

Do not clutter the dashboard with warnings.

---

# PRIORITY 3 — Average Confidence

Add an Average Confidence metric.

Example:

Average Confidence

76.2%

Across 6 verifications

## Requirements

Calculate this dynamically from existing verification records.

Do NOT hardcode:

76.2%

Use the actual confidence values.

Handle:

- No verification records
- One verification
- Multiple verifications

Round the displayed percentage appropriately, preferably to one decimal place.

Example:

76.2%

Do not create a chart for this.

Keep it visually consistent with the existing StatCard/design system.

---

# PRIORITY 4 — Needs Review

Add a "Needs Review" section.

This should highlight verification results that deserve user attention.

Example:

Needs Review                         View all →

2 claims require attention

⚠ Overstated
AI improves software development...
76% confidence

⚠ Insufficient
The dataset proves universal efficacy...
58% confidence

## Requirements

Derive this dynamically from verification data.

Do NOT hardcode the records.

Prioritize verdicts such as:

- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

SUPPORTS results should normally NOT appear in Needs Review.

Use the existing verdict types and semantic styling.

Each item should show:

- Verdict
- Claim
- Confidence
- Appropriate source/citation information when available
- View report action

Clicking the item or "View report" must open the exact verification report.

## View all

Navigate to:

`/app/history`

Optionally preserve an appropriate filter if the existing History page supports it.

Do not introduce complex filtering logic unless already supported.

---

# PRIORITY 5 — Recent Activity Empty State

The dashboard already has Recent Verification Activity.

Make its empty state polished.

When there are no verification records:

No verification runs yet

Start your first evidence-backed citation
verification to see results here.

[ Start Verification ]

Requirements:

- Center content appropriately
- Use an existing icon/illustration component if available
- Keep the design minimal
- CTA navigates to `/app/verify`
- Do not create a huge empty-state illustration
- Do not add unnecessary animations

The same principle should apply to:

- Needs Review
- Verification Overview
- Recent Activity

when there is no data.

---

# PRIORITY 6 — Dashboard Layout

Organize the dashboard into a clear hierarchy.

Recommended structure:

1. Welcome Header
2. Quick Actions
3. Primary Statistics
4. Overview + Verification Workflow
5. Needs Review + Workspace Insights
6. Recent Verification Activity

Conceptual layout:

┌─────────────────────────────────────────────────────┐
│ Welcome back, Prithiv R              [+ New Verify] │
│ Evidence-backed verification...                     │
└─────────────────────────────────────────────────────┘

Quick Actions

[ + New Verification ] [ View History ] [ Recent Reports ]


┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Total  │ │Support │ │Overst. │ │Contrad.│ │Fabric. │
│   6    │ │   1    │ │   2    │ │   1    │ │   1    │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘


┌──────────────────────────────┐ ┌──────────────────────┐
│ Verification Overview        │ │ Verify a Claim       │
│                              │ │                      │
│ Supports      ████ 1        │ │ Claim Challenger     │
│ Overstated    ████████ 2    │ │        ↓             │
│ Contradicted  ████ 1        │ │ Evidence Defender    │
│ Insufficient  ████ 1        │ │        ↓             │
│ Fabricated    ████ 1        │ │ Final Reviewer       │
│                              │ │                      │
│ Verification Summary         │ │ [Start Verification] │
└──────────────────────────────┘ └──────────────────────┘


┌──────────────────────────────┐ ┌──────────────────────┐
│ Needs Review                 │ │ Workspace Insights   │
│                              │ │                      │
│ Overstated     76%           │ │ Avg confidence 76%   │
│ Insufficient   58%           │ │ Total runs      6    │
│                              │ │ System ready ●       │
│ View all →                   │ │                      │
└──────────────────────────────┘ └──────────────────────┘


┌─────────────────────────────────────────────────────┐
│ Recent Verification Activity          View all →    │
│                                                     │
│ Overstated 76%  AI improves...       View report   │
│ Contradicted 82% Meta-analysis...    View report   │
│ Supported 91%  Compound...           View report   │
└─────────────────────────────────────────────────────┘

This is a conceptual layout, not a requirement to reproduce it pixel-for-pixel.

---

# PRIORITY 7 — Responsive Design

Desktop:

- Use the available horizontal space efficiently.
- Keep cards aligned.
- Avoid excessive empty space.
- Maintain consistent card heights where appropriate.

Tablet:

- Allow overview/workflow and insight sections to stack naturally.
- Avoid cramped horizontal cards.

Mobile:

- Single-column layout.
- Quick actions can wrap or stack.
- Statistics should remain readable.
- No horizontal scrolling.
- No text truncation.
- Buttons should remain easy to tap.
- Agent workflow remains vertical.
- Recent activity cards should remain readable.

---

# PRIORITY 8 — Visual Polish

Maintain the existing SciVerify visual identity.

Keep:

- Dark research-focused aesthetic
- Existing typography
- Existing semantic verdict colors
- Existing card components
- Existing borders
- Existing spacing system
- Existing icons
- Existing buttons
- Existing Tailwind conventions

Improve only where necessary:

- Consistent spacing
- Alignment
- Card heights
- Section hierarchy
- Typography hierarchy
- Hover states
- Focus states
- Responsive behavior

Avoid excessive glassmorphism, gradients, animations, shadows, or decorative effects.

SciVerify should feel like a serious scientific research tool.

---

# DATA REQUIREMENTS

Use the existing verification state/store and types.

Do NOT introduce duplicate state.

Do NOT hardcode:

- Total verification count
- Verdict counts
- Average confidence
- Needs Review records
- Recent activity
- Workspace statistics

Everything should derive from the existing verification records.

If helper selectors/functions are useful, create reusable selectors rather than duplicating calculations across components.

---

# COMPONENT ARCHITECTURE

Before creating new components, inspect existing components.

Reuse:

- StatCard
- VerdictBadge
- VerdictCard
- ConfidenceBar
- Card
- Panel
- Button
- Badge
- existing verification components
- existing layout components

Create new components only when they represent a meaningful reusable UI section.

Possible components:

- DashboardQuickActions
- WorkspaceHealthCard
- NeedsReviewCard
- DashboardInsights

Use the project's existing naming and folder conventions.

Do not over-componentize simple markup.

---

# DO NOT IMPLEMENT

Do NOT add:

- Chatbot
- AI assistant
- Notifications
- Team collaboration
- Calendar
- Social features
- User profile customization
- Huge analytics dashboards
- Pie charts
- Donut charts
- Activity heatmaps
- Complex data visualization
- PDF editor
- Manuscript editor
- Dark/light mode
- Billing
- Real-time notifications

These are outside this phase.

---

# IMPORTANT PRODUCT CONSTRAINT

The current verification system is still MOCK-ONLY.

Do not represent mock verification results as real scientific verification.

Do not add claims such as:

"AI verified this paper"

or

"Scientific evidence confirmed"

unless the existing data explicitly supports that behavior.

Use the existing demo/mock terminology where appropriate.

---

# VALIDATION

After implementation:

1. Run:

npm run lint

2. Run:

npm run build

3. Open:

`/app/home`

4. Verify:

- Quick Actions work
- New Verification opens `/app/verify`
- View History opens `/app/history`
- Recent Reports opens the latest actual report
- Average Confidence is calculated dynamically
- Needs Review is dynamically generated
- View report opens the correct verification
- Empty states work when no verification data exists
- Verification Overview still works
- Agent workflow remains intact
- Recent activity remains intact
- Mobile layout works
- No text truncation
- No horizontal overflow

5. Verify that existing routes still work:

`/`
`/login`
`/register`
`/app/home`
`/app/verify`
`/app/history`
`/app/settings`
`/ui-preview`

6. Do NOT modify Supabase configuration.

7. Do NOT modify authentication behavior.

8. Do NOT commit or push changes.

## Definition of Done

The dashboard should feel like a complete professional research workspace rather than a collection of UI cards.

A user should be able to:

Open dashboard
    ↓
Understand workspace status
    ↓
See verification statistics
    ↓
Identify claims needing review
    ↓
Start a new verification
    ↓
Open an exact historical report
    ↓
Review previous verification activity

The final UI should be clean, restrained, research-grade, responsive, and information-dense without becoming cluttered.