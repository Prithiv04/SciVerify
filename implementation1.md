# Phase 5.2.1 — Final Dashboard Refinements

The SciVerify dashboard is already implemented and working.

Make ONLY the following 3 visual/content refinements.

IMPORTANT:
Do not redesign the entire dashboard.
Do not modify authentication, Supabase, routes, verification logic, Zustand state, history behavior, or settings.
Do not add new dependencies unless absolutely necessary.
Preserve the existing design system and components.

---

## 1. Fix duplicated citation/source text

There is currently a duplicated source/reference line in some Recent Verification Activity cards.

Example:

Insufficient
58%

The dataset proves universal efficacy with no observed adverse events.

Demo unpublished manuscript reference text
Demo unpublished manuscript reference text

Confidence
58%

The source/reference should appear ONLY ONCE.

Expected:

Insufficient    58%

The dataset proves universal efficacy with no observed adverse events.

Demo unpublished manuscript reference text

Confidence
58%
Aug 4, 2026
View report

Inspect the data mapping and component rendering to determine why the source is being displayed twice.

IMPORTANT:
- Fix the underlying rendering issue rather than hiding one copy with CSS.
- Make sure all recent verification cards display citation/source information exactly once.
- Preserve all existing source information.
- Handle DOI, URL, citation, and reference-text source types correctly.

---

## 2. Improve the Verification Overview visualization

Current section:

Verification overview
Distribution of verification outcomes across your workspace.

Supports
1

Overstated
2

Contradicted
1

Insufficient
1

Fabricated
1

Keep the existing data and section, but make it more visually informative.

Create compact horizontal distribution bars.

Example:

Verification overview
Distribution of verification outcomes

Supports       ████████                 1
Overstated     ████████████████         2
Contradicted   ████████                 1
Insufficient   ████████                 1
Fabricated     ████████                 1

Requirements:

- Use the existing verification statistics/store data.
- NEVER hardcode the counts.
- Calculate bar widths dynamically based on the largest verdict count.
- Each verdict gets its existing semantic styling.
- Display:
  - verdict label
  - horizontal bar
  - count
- Keep the visualization compact.
- Use CSS/Tailwind where possible.
- Do not install a charting library.
- Add subtle animation only if it already fits the existing design system.
- Make zero-count categories display correctly.
- Make it responsive.
- Ensure sufficient contrast and accessibility.
- Do not turn this into a large analytics chart.

The section should remain consistent with the existing SciVerify dark research UI.

---

## 3. Strengthen the Prosecutor → Defender → Adjudicator presentation

Improve the existing "Verify a scientific claim" CTA card.

Current concept:

Verify a scientific claim
Run a multi-agent evidence check

Compare a claim against its cited evidence using three specialized verification agents.

Prosecutor
Challenges the claim

Defender
Builds supporting case

Adjudicator
Final evidence decision

Start verification

Make the three-agent workflow visually connected.

### Desktop target

Display the agents horizontally:

⚔ Prosecutor  ───→  🛡 Defender  ───→  ⚖ Adjudicator

Each agent should remain a distinct visual block/card.

Prosecutor
Challenges the claim

Defender
Builds supporting case

Adjudicator
Final evidence decision

Use subtle connecting lines/arrows between the three stages.

### Mobile target

Stack them vertically:

⚔ Prosecutor
Challenges the claim
        ↓
🛡 Defender
Builds supporting case
        ↓
⚖ Adjudicator
Final evidence decision

Requirements:

- Reuse existing AgentCard/icons/components where appropriate.
- Keep the existing agent names exactly:
  - Prosecutor
  - Defender
  - Adjudicator
- Keep the existing descriptions.
- Do not create fake live-status animations.
- Keep "Start verification" functional and pointing to `/app/verify`.
- Make the flow visually obvious.
- Keep the design subtle and research-grade.
- Do not make the card excessively large.
- Maintain responsive behavior.

The goal is to make it immediately obvious that SciVerify uses a three-agent verification process.

---

# DESIGN CONSTRAINTS

Keep the current SciVerify design language:

- Dark
- Premium
- Research-focused
- Clean
- Professional
- Minimal
- Evidence-oriented

Avoid:

- Excessive gradients
- Neon effects
- Gaming-style UI
- Chatbot styling
- Excessive animations
- Large unnecessary charts
- New dashboard sections
- New functionality

---

# DO NOT CHANGE

Do not modify:

- Supabase
- Authentication
- Database
- RLS
- Routes
- Verification service
- VerificationStore
- VerificationResult
- History functionality
- Settings
- Landing page
- `/app/verify`
- `/app/history`
- `/app/settings`

Only make the three requested dashboard refinements.

---

# VALIDATION

After implementation:

1. Run:

npm run lint

2. Run:

npm run build

3. Open `/app/home`.

4. Verify:
   - No duplicated source/citation text.
   - Verification Overview has dynamic horizontal bars.
   - Counts are correct.
   - Prosecutor → Defender → Adjudicator flow is visually connected.
   - Desktop layout works.
   - Mobile layout works.
   - "Start verification" still navigates to `/app/verify`.
   - Existing Recent Verification "View report" buttons still work.
   - No existing dashboard functionality is broken.

Do not commit or push anything.

At the end, provide a concise implementation report listing:
- Files changed
- What was fixed
- Lint result
- Build result
- Any remaining issues