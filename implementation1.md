PHASE — Dashboard Density & Vertical Whitespace Polish

The SciVerify dashboard is functionally complete, but there is too much unused vertical whitespace in the "Needs review" and "Workspace insights" sections.

DO NOT add new major features.
DO NOT change the dashboard's visual identity.
DO NOT change routing, data models, authentication, or verification logic.

The goal is to make the dashboard feel compact, intentional, premium, and research-grade.

==================================================
1. WORKSPACE INSIGHTS — COMPACT REDESIGN
==================================================

Current problem:

The Workspace Insights section contains:
- Verification health
- Average confidence

These are displayed as tall vertical cards, creating large empty areas.

Redesign this section so it uses the available horizontal space efficiently.

Preferred structure:

Workspace insights
Demo verification environment

[ System ready ]   [ 6 Runs ]   [ 79.8% ]
Verification health  Verifications  Avg confidence

Small disclaimer:
"Results are simulated demo data and do not reflect live scientific verification."

Requirements:
- Use a compact horizontal layout on desktop.
- Use 3 balanced metric blocks.
- Keep the system-ready indicator visually distinct.
- Keep 79.8% visually prominent.
- Avoid excessive vertical padding.
- No unnecessary empty space.
- On mobile, stack the metrics cleanly.
- Do not make the section excessively tall.

The section should feel like a professional workspace status panel rather than two oversized statistic cards.

==================================================
2. NEEDS REVIEW — REDUCE VERTICAL BULK
==================================================

Current problem:

"Needs review" contains 5 claims and becomes a very tall vertical card.

Keep all information, but make the list much more compact.

Preferred layout:

Needs review                         View all →
5 claims require attention

[Verdict] [Confidence] [Claim]
Overstated    76%       AI improves accuracy...
Contradicts   82%       Meta-analysis confirms...
Insufficient  58%       Dataset proves...
Fabricated    98%       RCT demonstrates...
Overstated    74%       AI improves productivity...

Requirements:
- Keep all 5 records.
- Use compact rows instead of large individual cards.
- Keep verdict badge, confidence, and claim visible.
- Truncate long claims gracefully with ellipsis where necessary.
- Each row should be clickable and open the exact verification report.
- Preserve the existing report routes.
- Use subtle row separators or hover states.
- Avoid excessive padding.
- "View all" remains in the header.
- On mobile, allow rows to stack cleanly.

Do NOT remove information just to reduce height.

==================================================
3. GRID / HEIGHT BEHAVIOR
==================================================

Inspect the parent dashboard grids.

Avoid unnecessary:
- items-stretch
- h-full
- large min-height values
- fixed heights
- excessive py/padding

where they cause cards to stretch vertically.

Cards should generally use natural content height unless equal heights are intentionally needed.

Use:
- items-start
- natural height
- consistent but compact padding

where appropriate.

IMPORTANT:
Do not break the existing stat-card alignment at the top of the dashboard.

==================================================
4. VISUAL CONSISTENCY
==================================================

Maintain the existing SciVerify design system:

- Dark research-oriented UI
- Existing typography
- Existing semantic verdict colors
- Existing card/panel components
- Existing borders
- Existing spacing scale
- Existing hover behavior

Do not introduce:
- Gradients everywhere
- Huge icons
- Excessive animations
- Decorative charts
- New color systems
- Unnecessary glassmorphism

The goal is refinement, not redesign.

==================================================
5. RESPONSIVE REQUIREMENTS
==================================================

Desktop:
- Workspace Insights should be compact and horizontal.
- Needs Review should use compact rows.
- Avoid large unused vertical areas.

Tablet:
- Allow metrics to wrap naturally.
- Maintain readable spacing.

Mobile:
- Workspace insight metrics may stack.
- Needs Review rows may become two-line layouts.
- No horizontal overflow.
- Claims should truncate gracefully.

==================================================
6. UX REQUIREMENTS
==================================================

Every Needs Review item must remain actionable.

Clicking a review item or "View report" must open the exact verification report.

Do not route all records to /app/verify.

Preserve exact IDs such as:

/app/verify/mock-001
/app/verify/mock-002
/app/verify/mock-004
/app/verify/mock-005
/app/verify/mock-006

==================================================
7. CODE QUALITY
==================================================

Before finishing:

1. Inspect the existing dashboard components and reuse existing UI primitives.
2. Do not duplicate components unnecessarily.
3. Keep TypeScript types intact.
4. Keep existing mock-data disclaimer.
5. Run:

npm run lint

npm run build

Fix any errors before completing.

==================================================
SUCCESS CRITERIA
==================================================

The dashboard should now feel:

- Compact
- Balanced
- Professional
- Research-grade
- Easy to scan
- Free of unnecessary vertical whitespace

Most importantly:

Workspace Insights should NOT look like two oversized vertical cards.

Needs Review should NOT look like five large cards stacked vertically.

Do not add more dashboard features.
Focus only on density, spacing, hierarchy, and professional presentation.