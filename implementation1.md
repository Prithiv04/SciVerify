PHASE 4.1 — UPDATE PUBLIC-FACING AGENT ARCHITECTURE

We need to make a focused correction to the SciVerify landing page.

IMPORTANT:
Do NOT redesign the landing page.
Do NOT change the overall visual design.
Do NOT change the routing.
Do NOT change authentication.
Do NOT modify the backend.
Do NOT add new functionality.
Do NOT remove or break the existing Phase 2 design system.

ONLY replace the public-facing agent architecture terminology and content.

==================================================
CURRENT PROBLEM
==================================================

The landing page currently presents the architecture as:

1. Citation Parser
2. Evidence Retriever
3. Verdict Synthesizer

This makes SciVerify look like a normal RAG/retrieval pipeline.

However, the core competitive idea of SciVerify is the multi-agent debate:

1. Prosecutor
2. Defender
3. Adjudicator

This architecture must be clearly visible on the public landing page because it demonstrates genuine multi-agent collaboration and directly matches the project's core idea.

==================================================
TARGET ARCHITECTURE
==================================================

Replace the current three-agent architecture with:

### 1. Prosecutor
Role:
Actively looks for weaknesses, contradictions, missing context, overstatements, and limitations in the citation's support for the claim.

Simple description:
"Challenges the claim and searches for evidence that the citation may be misleading, incomplete, or overstated."

Responsibility:
- Look for contradictions
- Find limitations
- Detect overstatement
- Question whether the source actually supports the exact claim

Status/demo state:
Keep whatever existing visual status system is already being used, but make the content appropriate for the Prosecutor.

Icon:
Reuse the existing AgentCard/icon system if possible.
Do not introduce a completely new icon system unless necessary.

--------------------------------------------------

### 2. Defender
Role:
Actively looks for evidence showing that the citation reasonably supports the claim.

Simple description:
"Builds the strongest evidence-based case for why the citation supports the claim."

Responsibility:
- Find supporting evidence
- Identify relevant findings
- Check whether the claim is reasonably supported
- Provide evidence that counters the Prosecutor's objections

Status/demo state:
Reuse the existing AgentCard status styling.

--------------------------------------------------

### 3. Adjudicator
Role:
Acts as the final decision-maker.

Simple description:
"Weighs the Prosecutor and Defender arguments against the evidence and produces the final verdict."

Responsibility:
- Compare both sides
- Evaluate the evidence
- Decide the final classification
- Produce confidence
- Explain the reasoning

Possible verdicts:
- SUPPORTS
- OVERSTATED
- CONTRADICTS
- INSUFFICIENT
- FABRICATED

Status/demo state:
Reuse the existing AgentCard status styling.

==================================================
IMPORTANT — PRESERVE EXISTING DESIGN
==================================================

Keep the existing:

- AgentCard component
- Card styling
- Dark research-focused theme
- Typography
- Spacing
- Animations
- Reveal effects
- Responsive layout
- Existing icons where appropriate
- Existing section structure
- Existing navigation anchors
- Existing landing page components

Do not create a completely new design.

This should be a CONTENT + ARCHITECTURE correction, not a redesign.

==================================================
LANDING PAGE SECTION
==================================================

Find the current section titled something similar to:

"Three-agent verification system"

Update it to something like:

"Three-agent debate system"

Subtitle should communicate:

"Three specialized agents examine the claim from different perspectives before reaching a final evidence-backed verdict."

The three cards should now clearly show:

Prosecutor
Challenge the claim.

Defender
Build the strongest evidence-based case.

Adjudicator
Weigh both sides and decide.

==================================================
MAKE THE DEBATE CONCEPT CLEAR
==================================================

The section should visually communicate:

Claim
  ↓
Prosecutor ─────┐
                ├──→ Adjudicator → Final Verdict
Defender ───────┘

Do NOT build a complex new interactive diagram.

If the existing AgentCard layout already presents three cards horizontally, keep that layout.

The text itself should make the debate flow obvious.

If appropriate, add a small supporting line such as:

"Two agents argue from opposing perspectives. A third agent evaluates both against the evidence."

This is important because the multi-agent debate is the main differentiator of SciVerify.

==================================================
UPDATE OTHER LANDING PAGE REFERENCES
==================================================

Search the landing page code for:

"Parser"
"Retriever"
"Synthesizer"
"Citation Parser"
"Evidence Retriever"
"Verdict Synthesizer"

If these references are specifically describing the three-agent architecture, update them to the new architecture.

Do NOT blindly replace words if they refer to a legitimate future internal processing step.

For example:

Citation parsing and evidence retrieval may still exist internally later.

The change is specifically about how the public-facing multi-agent architecture is presented.

==================================================
DO NOT CHANGE THE VERDICT SYSTEM
==================================================

Keep the existing five verdicts:

SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED

Keep the existing:

- VerdictBadge
- VerdictCard
- ConfidenceBar
- EvidenceCard

Do not modify their visual design unless required by the content update.

==================================================
IMPORTANT PRODUCT POSITIONING
==================================================

The landing page should make this distinction clear:

SciVerify is NOT:

"An AI chatbot that reads a paper and gives an answer."

SciVerify IS:

"An evidence-first multi-agent citation verification system where specialized agents challenge, defend, and adjudicate whether a scientific claim is actually supported by its citation."

Keep the wording simple and professional.

Do not overuse buzzwords.

==================================================
VALIDATION
==================================================

After making the changes:

1. Run:

npm run lint

2. Run:

npm run build

3. Start the dev server:

npm run dev

4. Verify:

/
 /ui-preview
 /login
 /register

still work.

5. Verify the landing page:

- Hero still works
- Navigation still works
- How it works still works
- Agent section now shows Prosecutor / Defender / Adjudicator
- Verdict section still works
- Evidence preview still works
- CTA still works
- Footer still works
- Mobile layout still works

==================================================
FINAL RESPONSE
==================================================

After implementation, report:

1. Files modified
2. What changed
3. Confirmation that Parser/Retriever/Synthesizer were replaced only where they represented the public-facing agent architecture
4. Confirmation that Prosecutor/Defender/Adjudicator are now shown
5. Lint result
6. Build result
7. Routes verified
8. Any issues remaining

Do not implement Phase 5.
Do not build the authenticated workspace.
Do not implement backend logic.
Do not implement actual AI agents.

This task is ONLY the Phase 4.1 landing-page architecture correction.