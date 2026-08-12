# SciVerify — Phase 6 Implementation Plan
## Backend Foundation + Real Citation Verification Pipeline

We are now moving SciVerify from a polished frontend/mock verification system toward a real evidence-backed verification platform.

IMPORTANT:
- Do NOT redesign or modify the existing frontend unless required to connect it to the backend.
- Do NOT remove or break the existing dashboard, verification report UI, history UI, Supabase authentication, or existing routes.
- Preserve the current visual design and component architecture.
- Do NOT replace the existing mock system immediately. Keep it available as a fallback/dev mode until the real pipeline is working.
- Work incrementally and keep the project buildable after every major step.
- Do NOT commit or push changes.

---

# Current Architecture

Frontend:
- React
- Vite
- TypeScript
- Tailwind CSS
- Zustand
- React Router
- Supabase Auth
- Existing verification UI and report components

Existing frontend routes:
- /app/home
- /app/verify
- /app/history
- /app/settings

Existing verification concepts:
- Supports
- Overstated
- Contradicts
- Insufficient
- Fabricated

Existing agent concepts:
- Claim Challenger
- Evidence Defender
- Final Reviewer

Current verification flow is MOCK ONLY.

We now need to build the backend foundation for REAL verification.

---

# Phase 6 Goal

Build this pipeline:

User Claim + Citation/DOI
        ↓
FastAPI Backend
        ↓
Citation Resolver
        ↓
Paper Metadata Retrieval
        ↓
Paper Content Retrieval
        ↓
Text Extraction / Chunking
        ↓
Relevant Evidence Retrieval
        ↓
Claim Challenger
        ↓
Evidence Defender
        ↓
Final Reviewer
        ↓
Structured Verdict
        ↓
Supabase Persistence
        ↓
Existing React Verification Report

The first milestone is NOT the complete AI system.

The first milestone is:

React → FastAPI → DOI/Citation → real paper metadata → paper content/evidence → structured response.

Only after this works should the multi-agent layer be implemented.

---

# STEP 1 — Inspect Existing Repository

Before modifying anything:

1. Inspect the entire repository structure.
2. Identify whether a backend already exists.
3. Identify:
   - FastAPI entry point
   - existing API routes
   - configuration/environment handling
   - Supabase integration
   - existing verification service interfaces
   - existing TypeScript verification types
   - existing mock verification service
   - existing Zustand stores
   - existing report components
4. Reuse existing abstractions where possible.
5. Do NOT create duplicate clients, duplicate environment loaders, or duplicate verification types.

At the end of inspection, create:

docs/phase6-architecture.md

containing the proposed backend architecture and data flow.

---

# STEP 2 — Backend Foundation

If FastAPI already exists, extend it instead of creating another backend.

Create/organize the backend approximately like:

backend/
  app/
    main.py
    api/
      routes/
        verification.py
        citations.py
    core/
      config.py
    services/
      citation_resolver.py
      paper_retriever.py
      document_parser.py
      evidence_retriever.py
      verification_service.py
    schemas/
      verification.py
      citation.py
      evidence.py
    clients/
      crossref.py
      openalex.py
    utils/

Use clean separation between:
- API routes
- external API clients
- retrieval services
- AI/agent services
- database persistence

Do not put all logic inside FastAPI route handlers.

---

# STEP 3 — Environment Configuration

Use environment variables for all external services.

Expected configuration should support:

SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
CROSSREF_API_URL
OPENALEX_API_URL
LLM_API_KEY
LLM_MODEL

Use the existing project's environment/configuration conventions where possible.

IMPORTANT SECURITY RULES:

- Never expose service-role keys to the React frontend.
- Never place backend secrets inside VITE_* variables.
- Never commit .env files.
- Never hardcode API keys.
- Keep frontend publishable Supabase credentials separate from backend secrets.

Update .env.example with placeholders only.

---

# STEP 4 — Citation Resolver

Implement a citation resolver service.

Input examples:

1. DOI
   10.xxxx/example

2. DOI URL
   https://doi.org/10.xxxx/example

3. Citation string
   Smith et al., 2024, Example Journal...

4. URL

Normalize the input first.

Create a normalized citation model:

{
  "identifier": "...",
  "identifier_type": "doi|url|citation",
  "title": "...",
  "authors": [],
  "journal": "...",
  "publication_year": 2024,
  "doi": "...",
  "source_url": "...",
  "abstract": "...",
  "retrieval_status": "resolved|partial|not_found"
}

For DOI resolution, use Crossref first.

If useful, use OpenAlex as a secondary metadata source.

Do NOT fabricate metadata.

If a citation cannot be resolved, return a structured failure.

---

# STEP 5 — Paper Retrieval

After resolving metadata, attempt to retrieve usable paper content.

Priority:

1. Open-access full text
2. Accessible HTML/XML
3. Accessible PDF
4. Abstract/metadata fallback

Do NOT attempt to bypass paywalls or restricted access.

The system should explicitly distinguish:

FULL_TEXT
ABSTRACT_ONLY
METADATA_ONLY
UNAVAILABLE

Create a structured document model:

{
  "document_id": "...",
  "title": "...",
  "source_url": "...",
  "content_type": "html|xml|pdf|abstract",
  "access_level": "full_text|abstract_only|metadata_only",
  "text": "..."
}

---

# STEP 6 — Document Parsing

Create a document parser that converts retrieved paper content into normalized text.

Support the most practical format first.

For PDFs:
- extract text
- preserve page information when possible

For HTML/XML:
- remove navigation and irrelevant markup
- preserve meaningful sections

Normalize into chunks.

Each chunk should contain:

{
  "chunk_id": "...",
  "text": "...",
  "section": "...",
  "page": 1,
  "source_url": "..."
}

Do not over-engineer this initially.

The objective is reliable evidence extraction.

---

# STEP 7 — Evidence Retrieval

Implement a first version of evidence retrieval.

Input:

- scientific claim
- document chunks

Output:

Top relevant evidence passages.

Each evidence item:

{
  "evidence_id": "...",
  "chunk_id": "...",
  "text": "...",
  "source": "...",
  "section": "...",
  "page": 1,
  "relevance_score": 0.92
}

Start with a simple reliable approach.

Possible implementation:
- embeddings + vector similarity
OR
- lexical/keyword retrieval as an initial fallback

Do not introduce unnecessary infrastructure if the existing project doesn't need it.

The retrieval layer must be replaceable later.

---

# STEP 8 — Verification API Contract

Create:

POST /api/verification

Request:

{
  "claim": "AI improves software development productivity by 50%",
  "citation": "10.xxxx/example",
  "source_type": "doi",
  "context": "optional context"
}

Response should initially support:

{
  "verification_id": "...",
  "status": "completed|processing|failed",
  "citation": {...},
  "evidence": [...],
  "verdict": null,
  "confidence": null
}

For Phase 6A, verdict may remain null until the agent layer is implemented.

Also create:

GET /api/verification/{verification_id}

and:

GET /api/verification/{verification_id}/evidence

Use proper HTTP status codes.

---

# STEP 9 — Multi-Agent Verification Layer

Once citation + retrieval works, implement the three agents.

## Agent 1 — Claim Challenger

Purpose:
Attempt to find evidence that weakens, contradicts, qualifies, or exposes exaggeration in the claim.

Input:
- claim
- context
- retrieved evidence

Output:

{
  "agent": "claim_challenger",
  "position": "supports|challenges|uncertain",
  "reasoning": "...",
  "evidence_ids": [],
  "confidence": 0.0
}

The agent MUST cite evidence IDs rather than inventing references.

---

## Agent 2 — Evidence Defender

Purpose:
Build the strongest evidence-based argument that the citation supports the claim.

Output:

{
  "agent": "evidence_defender",
  "position": "supports|challenges|uncertain",
  "reasoning": "...",
  "evidence_ids": [],
  "confidence": 0.0
}

Again, every important factual statement should be linked to retrieved evidence.

---

## Agent 3 — Final Reviewer

Input:
- original claim
- citation metadata
- retrieved evidence
- Claim Challenger analysis
- Evidence Defender analysis

Output:

{
  "verdict": "SUPPORTS|OVERSTATED|CONTRADICTS|INSUFFICIENT|FABRICATED",
  "confidence": 0.0,
  "explanation": "...",
  "evidence_factors": [],
  "suggested_correction": "..."
}

The Final Reviewer must NOT invent evidence.

It should only reason over retrieved evidence and the two agent analyses.

---

# STEP 10 — Strict Verdict Definitions

Implement these definitions consistently.

SUPPORTS:
Evidence strongly supports the claim as stated.

OVERSTATED:
The evidence supports the general direction but the claim exaggerates magnitude, certainty, scope, population, or conclusion.

CONTRADICTS:
Reliable evidence directly conflicts with the claim.

INSUFFICIENT:
Available evidence is not sufficient to determine whether the claim is supported or contradicted.

FABRICATED:
The citation cannot be verified as a legitimate source or appears to be fabricated.

Do not use "FABRICATED" merely because a paper is inaccessible.

An inaccessible paper should normally produce INSUFFICIENT unless there is evidence that the citation itself is fabricated.

---

# STEP 11 — Supabase Persistence

Extend the existing Supabase database.

Create migrations for:

verifications
citations
evidence
agent_analyses

Possible relationships:

profiles
   ↓
verifications
   ↓
citations
   ↓
evidence

verifications
   ↓
agent_analyses

Design the schema carefully before implementing it.

Each verification should belong to the authenticated user.

Enable RLS.

Users should only be able to access their own verification records.

Do NOT expose service-role credentials to the frontend.

Create indexes for commonly queried fields.

---

# STEP 12 — Connect Frontend

Once the backend endpoint is stable:

Replace the current mock verification call with an API service abstraction.

Create something similar to:

frontend/src/services/verificationService.ts

The frontend should NOT directly call Crossref/OpenAlex/LLM APIs.

It should communicate with the backend.

Keep:

mockVerificationService.ts

available for development/demo fallback.

Use a clear configuration flag or service abstraction to switch between:

MOCK
REAL

Do not duplicate verification UI logic.

---

# STEP 13 — Preserve Existing UI

The existing UI already contains:

- VerificationLoading
- VerificationReportView
- VerdictExplanation
- EvidenceCard
- AgentAnalysisPanel
- SuggestedCorrectionPanel
- VerificationResultView

Adapt the backend response to the existing frontend types.

Do not redesign these components unless an API mismatch requires a small change.

The final report should show:

Claim
↓
Citation
↓
Retrieved evidence
↓
Claim Challenger
↓
Evidence Defender
↓
Final Reviewer
↓
Verdict
↓
Confidence
↓
Explanation
↓
Suggested correction

---

# STEP 14 — Error Handling

Handle these cases explicitly:

- Invalid DOI
- Citation not found
- Paper unavailable
- Full text unavailable
- Abstract only
- External API timeout
- Rate limiting
- LLM failure
- Evidence retrieval failure
- Invalid agent output
- Database failure

Never display raw stack traces to users.

Return user-friendly structured errors.

---

# STEP 15 — Testing

Create tests for:

### Citation
- DOI normalization
- valid DOI
- invalid DOI
- missing citation

### Retrieval
- metadata retrieval
- unavailable source
- full-text fallback
- chunk generation

### Evidence
- relevant evidence returned
- empty evidence
- ranking

### Agents
- valid structured output
- invalid output handling
- evidence ID validation

### Verdict
Test all five verdict types.

### API
- successful verification
- authentication failure
- invalid request
- retrieval failure

### Security
- user A cannot access user B's verification
- service role never reaches frontend
- RLS policies work correctly

---

# STEP 16 — Observability

Add structured logging for:

- verification ID
- citation resolution
- retrieval status
- evidence count
- agent execution
- final verdict
- failures

Do NOT log:
- API keys
- passwords
- service-role keys
- unnecessary private user data

---

# STEP 17 — Development Milestones

Do NOT implement everything in one step.

Follow this sequence:

### Milestone 1
Backend health endpoint.

### Milestone 2
Citation resolver.

### Milestone 3
Paper metadata retrieval.

### Milestone 4
Paper content retrieval.

### Milestone 5
Document parsing + chunking.

### Milestone 6
Evidence retrieval.

### Milestone 7
Verification API.

### Milestone 8
Claim Challenger.

### Milestone 9
Evidence Defender.

### Milestone 10
Final Reviewer.

### Milestone 11
Supabase persistence.

### Milestone 12
Frontend integration.

### Milestone 13
End-to-end real verification.

---

# IMPORTANT IMPLEMENTATION RULES

1. Inspect existing code before creating files.
2. Reuse existing types and utilities.
3. Do not break the current frontend.
4. Do not remove mock verification yet.
5. Do not hardcode credentials.
6. Do not expose backend secrets.
7. Do not fabricate scientific evidence.
8. Every agent conclusion must reference retrieved evidence.
9. Do not call an inaccessible citation FABRICATED without evidence of fabrication.
10. Keep API schemas strongly typed.
11. Validate all LLM outputs.
12. Keep external providers replaceable.
13. Keep the architecture modular.
14. Run lint and build after frontend changes.
15. Run backend tests after backend changes.
16. Do not commit or push anything.

---

# FIRST TASK

Do NOT implement the entire plan immediately.

Start by:

1. Inspecting the existing repository.
2. Identifying the current backend/frontend architecture.
3. Identifying existing verification types and mock service.
4. Identifying existing Supabase integration.
5. Proposing the exact Phase 6 folder/file structure.
6. Proposing the database schema.
7. Proposing the API contracts.
8. Creating docs/phase6-architecture.md.

Then STOP and report what you found and what you recommend implementing first.

Do not modify unrelated frontend files.