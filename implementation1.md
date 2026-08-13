# SciVerify Phase 6 — Milestone 5: Multi-Agent Verification Layer

Implement **Phase 6 — Milestone 5** for the existing SciVerify repository.

## Objective

Build the backend multi-agent verification layer that transforms the existing pipeline:

DOI → Citation Resolution → Paper Retrieval → Evidence Retrieval & Ranking

into:

DOI → Citation Resolution → Paper Retrieval → Evidence Retrieval → **Prosecutor → Defender → Adjudicator → Final Verification Result**

This milestone must initially be **backend-only**.

**Do NOT modify the frontend.**

The existing frontend mock verification flow must continue working exactly as it does now.

---

# 1. Inspect the existing repository first

Before writing code, inspect:

* `backend/app/`
* Existing schemas
* Citation resolver
* Paper retriever
* Evidence retriever
* Existing `VerificationResult` frontend type
* Existing mock verification service
* Existing API client
* Existing configuration
* Existing tests
* `backend/README.md`

Reuse existing abstractions wherever appropriate.

Do not duplicate DOI resolution, paper retrieval, or evidence-ranking logic.

---

# 2. Architecture

The verification pipeline must be:

```text
POST /api/verification/analyze
        ↓
Validate claim + DOI
        ↓
Citation Resolver
        ↓
Paper Retrieval
        ↓
Evidence Retrieval & Ranking
        ↓
┌───────────────────────────────┐
│      Multi-Agent Layer        │
│                               │
│  Prosecutor                   │
│       ↓                       │
│  Defender                     │
│       ↓                       │
│  Adjudicator                  │
└───────────────────────────────┘
        ↓
Final Verification Result
```

The agents should operate on the retrieved evidence rather than independently downloading papers.

---

# 3. Agent 1 — Prosecutor

Create a dedicated prosecutor service.

Purpose:

> Attempt to disprove, weaken, or challenge the scientific claim using the retrieved evidence.

The Prosecutor should analyze:

* Contradictory evidence
* Numerical mismatches
* Unsupported conclusions
* Overstated claims
* Missing conditions
* Scope limitations
* Population/sample mismatches
* Methodological limitations
* Evidence that only partially supports the claim

Return a structured result.

Suggested fields:

```text
agent
analysis
stance
key_points
supporting_evidence
contradicting_evidence
confidence
```

The Prosecutor must **not invent evidence**.

Every evidence reference must correspond to an actual retrieved evidence chunk.

---

# 4. Agent 2 — Defender

Create a dedicated defender service.

Purpose:

> Build the strongest evidence-based case that the claim is supported by the cited paper.

Analyze:

* Direct supporting statements
* Matching numerical values
* Relevant Results/Methods evidence
* Experimental findings
* Appropriate context
* Conditions under which the claim is valid
* Strength and relevance of supporting evidence

Return the same general structured contract where practical.

The Defender must also **never invent evidence**.

All evidence references must map to retrieved evidence chunks.

---

# 5. Agent 3 — Adjudicator

Create a dedicated adjudicator service.

Purpose:

> Evaluate the original claim, retrieved evidence, Prosecutor analysis, and Defender analysis and produce the final verdict.

The Adjudicator must consider both sides rather than simply selecting whichever agent sounds more confident.

Supported verdicts must match the existing SciVerify frontend contract:

```text
SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED
```

The result should include:

```text
verdict
confidence
summary
reasoning
supporting_evidence
contradicting_evidence
suggested_correction
```

The adjudicator must distinguish:

### SUPPORTS

The cited evidence directly supports the claim with appropriate context.

### OVERSTATED

The evidence supports part of the claim, but the claim exaggerates magnitude, certainty, scope, or conclusion.

### CONTRADICTS

The available evidence directly conflicts with the claim.

### INSUFFICIENT

There is not enough evidence to determine whether the claim is supported or contradicted.

### FABRICATED

The claimed result/content cannot be substantiated from the cited source or the citation/evidence relationship is fundamentally invalid.

Do not use `FABRICATED` simply because evidence retrieval failed.

---

# 6. LLM abstraction

Do not hard-code an LLM provider throughout the application.

Create a provider abstraction such as:

```text
LLMProvider
```

with a method similar to:

```text
generate(...)
```

The agent services should depend on this abstraction.

Allow the implementation to support an LLM provider through environment configuration.

Use environment variables for provider configuration.

For example:

```text
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
LLM_BASE_URL=
```

Do not commit real API keys.

Update:

```text
backend/.env.example
```

with placeholders only.

---

# 7. Deterministic fallback

The architecture must not make the entire backend unusable when an LLM API key is missing.

Implement a safe development/test mode.

If the configured LLM provider is unavailable, return a controlled application-level result rather than crashing.

Do not fabricate a successful scientific verdict just because the LLM is unavailable.

A safe response should clearly indicate that verification could not be completed.

---

# 8. Evidence grounding

This is critical.

The agents must receive only the evidence returned by:

```text
POST /api/evidence/retrieve
```

Each evidence item should retain:

* `chunk_id`
* `section`
* `chunk_index`
* `text`
* `relevance_score`
* `source_url`
* `page`
* numeric overlap information

The agent prompt must explicitly instruct:

> Use only the supplied evidence. Do not invent papers, quotes, numbers, citations, or experimental results.

Agent outputs should reference evidence using `chunk_id`.

Validate returned evidence references against the actual retrieved chunks.

Ignore or reject hallucinated chunk IDs.

---

# 9. Structured agent outputs

Do not rely on free-form LLM responses if structured output can be enforced.

Create Pydantic schemas for:

```text
ProsecutorAnalysis
DefenderAnalysis
AdjudicatorAnalysis
VerificationResponse
```

Keep the schemas strongly typed and easy for the frontend to consume later.

---

# 10. Verification API

Create:

```text
POST /api/verification/analyze
```

Request:

```json
{
  "claim": "The method improves accuracy by 40%.",
  "doi": "10.xxxx/xxxxx"
}
```

The endpoint should execute:

```text
resolve citation
→ retrieve paper
→ retrieve evidence
→ prosecutor
→ defender
→ adjudicator
→ final response
```

Do not duplicate logic from existing services.

---

# 11. Response contract

The final response should be compatible with the existing frontend `VerificationResult` concept.

Include information such as:

```json
{
  "status": "success",
  "claim": "...",
  "verdict": "SUPPORTS",
  "confidence": 0.91,
  "summary": "...",
  "reasoning": "...",

  "paper": {
    "paper_id": "...",
    "doi": "...",
    "title": "..."
  },

  "evidence": [],

  "prosecutor": {
    "stance": "...",
    "analysis": "...",
    "key_points": [],
    "confidence": 0.0
  },

  "defender": {
    "stance": "...",
    "analysis": "...",
    "key_points": [],
    "confidence": 0.0
  },

  "adjudicator": {
    "analysis": "...",
    "confidence": 0.0
  },

  "suggested_correction": null
}
```

Adapt the exact structure to the existing repository contracts rather than unnecessarily replacing them.

---

# 12. Error handling

Handle each stage separately.

Expected cases:

### Invalid claim

Return:

```text
400
```

### Invalid DOI

Return:

```text
400
```

### Citation not found

Return:

```text
404
```

### Paper unavailable

Return an appropriate controlled response.

### No full text

Do not run the agents without evidence.

Return a meaningful status such as:

```text
insufficient_evidence
```

### No relevant evidence

Return:

```text
insufficient_evidence
```

### LLM provider failure

Return a controlled service/application error.

Never expose API keys or internal provider credentials.

### Agent output validation failure

Do not silently accept malformed or hallucinated agent output.

Return a controlled error and log enough information for debugging without exposing secrets.

---

# 13. Agent execution strategy

For the first implementation, prioritize correctness and traceability over performance.

Use a clear sequence:

```text
Prosecutor
   ↓
Defender
   ↓
Adjudicator
```

The Adjudicator receives:

* Original claim
* Evidence
* Prosecutor analysis
* Defender analysis

The Prosecutor and Defender should not receive each other's analysis.

This keeps their perspectives independent.

---

# 14. Configuration

Extend:

```text
backend/app/config.py
```

with appropriate LLM configuration.

Do not hard-code:

* API keys
* model secrets
* provider credentials
* private URLs

Update:

```text
backend/.env.example
```

with safe placeholders.

---

# 15. Tests

This milestone must have comprehensive automated tests.

Add tests for:

### Agent tests

* Prosecutor correctly receives claim + evidence
* Defender correctly receives claim + evidence
* Adjudicator receives both analyses
* Evidence references are validated
* Hallucinated chunk IDs are rejected
* Structured output validation works

### Verdict tests

Test all five verdicts:

```text
SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED
```

### API tests

Test:

* Valid request
* Invalid claim
* Invalid DOI
* Citation failure
* Paper retrieval failure
* No evidence
* LLM unavailable
* Malformed agent output
* Successful end-to-end mocked verification

All external LLM calls must be mocked.

Do not make the automated test suite depend on a real LLM API key.

---

# 16. End-to-end mocked test

Create at least one test covering:

```text
claim
 ↓
citation resolver mock
 ↓
paper retrieval mock
 ↓
evidence retrieval mock
 ↓
prosecutor mock
 ↓
defender mock
 ↓
adjudicator mock
 ↓
final VerificationResponse
```

Verify that:

* The correct claim reaches every stage
* Evidence reaches both agents
* The Adjudicator receives both analyses
* The final verdict is returned correctly
* Evidence references are preserved
* No frontend code is required

---

# 17. Logging

Add useful backend logging for:

```text
verification_started
citation_resolved
paper_retrieved
evidence_retrieved
prosecutor_completed
defender_completed
adjudicator_completed
verification_completed
```

Do not log:

* API keys
* Authorization headers
* Secrets
* Full sensitive provider responses unnecessarily

---

# 18. Frontend constraint

Do **not** modify:

* React components
* Dashboard
* VerifyPage
* Zustand stores
* Mock verification service
* Existing UI

The frontend should continue using the mock verification flow after Milestone 5.

Frontend integration will be handled in a later milestone.

---

# 19. Backward compatibility

Do not break:

```text
GET /api/health
POST /api/citations/resolve
POST /api/papers/retrieve
POST /api/evidence/retrieve
```

All existing tests must continue passing.

---

# 20. Documentation

Update:

```text
backend/README.md
```

with:

* Milestone 5 architecture
* Agent responsibilities
* Verification endpoint
* Request/response example
* Environment variables
* How to run
* How to test
* LLM provider configuration
* Limitations

Do not document fake capabilities.

---

# 21. Validation requirements

Before declaring Milestone 5 complete, run:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

Then:

```powershell
cd frontend
npm run lint
npm run build
```

All existing and new backend tests must pass.

The frontend must remain unchanged and continue to build successfully.

---

# 22. Important implementation constraints

Do NOT:

* Implement frontend integration
* Replace the existing mock workflow
* Add a vector database
* Introduce unnecessary infrastructure
* Hard-code an API key
* Bypass citation/paper/evidence services
* Invent evidence
* Allow agents to cite nonexistent chunks
* Treat LLM confidence as scientific truth
* Claim verification succeeded when evidence is unavailable

Keep the implementation modular so that the next milestone can easily connect the real frontend to:

```text
POST /api/verification/analyze
```

---

# 23. Completion criteria

Milestone 5 is complete only when:

* [ ] Prosecutor service implemented
* [ ] Defender service implemented
* [ ] Adjudicator service implemented
* [ ] LLM provider abstraction implemented
* [ ] Structured Pydantic agent schemas implemented
* [ ] Evidence grounding implemented
* [ ] Evidence-reference validation implemented
* [ ] `POST /api/verification/analyze` implemented
* [ ] All five verdicts supported
* [ ] Error handling implemented
* [ ] LLM calls mocked in tests
* [ ] End-to-end mocked verification test passes
* [ ] Existing Milestone 1–4 tests still pass
* [ ] Backend README updated
* [ ] `.env.example` contains placeholders only
* [ ] Frontend files remain unchanged
* [ ] `npm run lint` passes
* [ ] `npm run build` passes

## Final instruction

First inspect the existing codebase and architecture.

Then implement **Milestone 5 only**.

Do not move on to frontend integration or any later milestone.

After implementation, provide a concise report containing:

1. Files created
2. Files modified
3. API endpoint
4. Agent responsibilities
5. LLM provider abstraction
6. Test count/results
7. Frontend validation
8. Any limitations
9. Whether anything was committed or pushed

Do not commit or push anything automatically.
