You are implementing Phase 6 — Milestone 4 of the SciVerify project.

IMPORTANT:
- First inspect the existing repository and understand the architecture from Milestones 1–3.
- Do NOT modify the frontend.
- Do NOT implement the Prosecutor, Defender, or Adjudicator agents yet.
- Do NOT add an LLM API or vector database yet.
- Reuse the existing paper retrieval and evidence chunking infrastructure.
- Keep the implementation modular, deterministic, testable, and production-oriented.
- Do NOT break any existing functionality.

==================================================
MILESTONE 4 — EVIDENCE RETRIEVAL & RANKING
==================================================

Goal:

Build the backend evidence retrieval layer that takes:

1. A scientific claim
2. A paper DOI / paper identifier

and retrieves the most relevant evidence chunks from the paper produced by Milestone 3.

The pipeline should become:

Claim
  ↓
Citation Resolver              [DONE]
  ↓
Paper Retrieval                [DONE]
  ↓
Sections + Evidence Chunks     [DONE]
  ↓
Evidence Retrieval & Ranking   [IMPLEMENT NOW]
  ↓
Multi-Agent Verification       [LATER]

==================================================
STEP 1 — INSPECT EXISTING CODE
==================================================

Before writing code, inspect:

- backend/app/
- backend/app/services/
- backend/app/schemas/
- backend/app/api/routes/
- backend/app/tests/
- existing paper retrieval implementation
- evidence_chunker.py
- citation resolver
- configuration
- existing API conventions
- existing error handling
- README documentation

Understand the existing:

- Paper model/schema
- Evidence chunk structure
- DOI normalization
- Paper retrieval flow
- API response patterns
- Test conventions

Do not duplicate existing functionality.

==================================================
STEP 2 — CLAIM PREPROCESSING
==================================================

Create a small reusable claim preprocessing utility/service.

Input:

"The method improves accuracy by 40% on real-world software development tasks."

Output should contain normalized information useful for retrieval.

At minimum:

- original claim
- normalized claim
- meaningful tokens/terms

Requirements:

- preserve the original claim
- lowercase only for matching purposes
- remove unnecessary punctuation
- normalize whitespace
- do not alter scientific meaning
- do not perform aggressive stemming that could damage scientific terms
- keep implementation deterministic

Example:

original:
"The method improves accuracy by 40%."

normalized:
"method improves accuracy 40%"

==================================================
STEP 3 — EVIDENCE RETRIEVAL
==================================================

Create:

backend/app/services/evidence_retriever.py

The service should:

1. Accept a claim.
2. Accept paper chunks from Milestone 3.
3. Compare the claim against every chunk.
4. Calculate a deterministic relevance score.
5. Rank chunks from most relevant to least relevant.
6. Return the top relevant evidence.

For the first implementation, use a lightweight deterministic ranking strategy.

DO NOT introduce embeddings, OpenAI, Gemini, LangChain, vector databases, or external AI APIs yet.

The scoring can consider:

- token overlap
- meaningful keyword overlap
- phrase overlap
- numeric/value overlap
- section importance
- exact phrase matches

Use a transparent scoring approach so the result can be explained and tested.

==================================================
STEP 4 — NUMERIC CLAIM HANDLING
==================================================

Scientific claims often contain numbers.

For example:

Claim:
"The method improves accuracy by 40%."

Evidence:
"The proposed method improves accuracy by 12%."

The retrieval system should recognize that both discuss accuracy/improvement, while preserving the different numeric value.

Expose useful metadata such as:

- claim_numbers
- evidence_numbers
- numeric_overlap

Do NOT make the final SUPPORTS/CONTRADICTS decision here.

That decision belongs to the future Adjudicator agent.

==================================================
STEP 5 — SECTION AWARENESS
==================================================

Use the existing chunk section information.

Give reasonable ranking preference to sections such as:

- Results
- Findings
- Experiments
- Methods
- Abstract
- Discussion
- Conclusion

Do NOT blindly assume that Results is always correct.

Section weighting should only influence relevance ranking.

Preserve:

- section
- chunk_id
- chunk_index
- source_url
- page if available
- existing metadata

==================================================
STEP 6 — EVIDENCE SCORE
==================================================

Each retrieved evidence item should expose a normalized relevance score.

Example:

{
  "chunk_id": "chunk-12",
  "section": "Results",
  "text": "...",
  "relevance_score": 0.92,
  "claim_overlap": 0.75,
  "numeric_overlap": 1.0,
  "source_url": "...",
  "page": 4
}

The exact scoring formula is up to you, but it must be:

- deterministic
- bounded between 0 and 1
- documented
- unit tested

Avoid pretending that this score is an AI confidence score.

Call it something like:

relevance_score

not:

confidence

==================================================
STEP 7 — API
==================================================

Create:

backend/app/api/routes/evidence.py

Add:

POST /api/evidence/retrieve

Request:

{
  "claim": "The method improves accuracy by 40%.",
  "doi": "10.xxxx/xxxxx"
}

The endpoint should:

1. Validate the claim.
2. Resolve/retrieve the paper using the existing services.
3. Obtain the paper's evidence chunks.
4. Rank the chunks against the claim.
5. Return the highest-ranked evidence.

Do not duplicate DOI resolution logic.

Reuse existing services.

==================================================
STEP 8 — RESPONSE SCHEMA
==================================================

Create appropriate schemas under:

backend/app/schemas/

For example:

EvidenceRetrievalRequest
EvidenceItem
EvidenceRetrievalResponse

Response structure should be similar to:

{
  "status": "success",
  "claim": "The method improves accuracy by 40%.",
  "paper": {
    "paper_id": "...",
    "doi": "...",
    "title": "..."
  },
  "evidence": [
    {
      "chunk_id": "chunk-12",
      "section": "Results",
      "chunk_index": 3,
      "text": "...",
      "relevance_score": 0.92,
      "claim_overlap": 0.75,
      "numeric_overlap": 1.0,
      "source_url": "...",
      "page": 4
    }
  ],
  "total_chunks_considered": 25
}

Keep the response compatible with the existing architecture and future agent pipeline.

==================================================
STEP 9 — EDGE CASES
==================================================

Handle these properly:

1. Empty claim
2. Claim that is too long
3. Invalid DOI
4. DOI not found
5. Paper metadata available but full text unavailable
6. Paper has no chunks
7. No relevant evidence
8. Duplicate chunks
9. Missing section
10. Missing page
11. Missing source URL
12. Numeric claim with no numeric evidence
13. Evidence with numbers that differ from claim

Use appropriate HTTP status codes consistent with Milestones 1–3.

Do not return HTTP 500 for expected user/input/document conditions.

==================================================
STEP 10 — TESTS
==================================================

Create comprehensive automated tests.

At minimum test:

### Claim preprocessing
- normalization
- whitespace
- punctuation
- empty claim
- numeric extraction

### Ranking
- exact phrase match ranks highly
- keyword overlap
- irrelevant chunk ranks low
- numeric overlap
- different numeric values remain distinguishable
- section weighting
- deterministic ordering
- score is between 0 and 1

### API
- successful retrieval
- invalid DOI
- missing paper
- no full text
- no chunks
- empty claim
- successful response schema

Mock external HTTP calls.

Do NOT depend on Crossref/OpenAlex/Nature being available during tests.

Preserve all existing tests.

==================================================
STEP 11 — PERFORMANCE
==================================================

Keep the first implementation simple.

Expected scale:

- tens to hundreds of chunks per paper

Do not prematurely introduce:

- vector databases
- embeddings
- Redis
- Elasticsearch
- LLM calls

A deterministic ranking implementation is sufficient for this milestone.

Structure the service so an embedding-based retriever can be added later without rewriting the API.

==================================================
STEP 12 — ROUTER REGISTRATION
==================================================

Register the new evidence router in:

backend/app/main.py

Follow the same pattern used by:

- citations router
- papers router

==================================================
STEP 13 — DOCUMENTATION
==================================================

Update:

backend/README.md

Document:

- Milestone 4
- evidence retrieval flow
- scoring approach
- API endpoint
- request example
- response example
- limitations

Clearly state:

"This milestone performs deterministic evidence retrieval and ranking. It does not produce the final scientific verdict."

==================================================
STEP 14 — VALIDATION
==================================================

After implementation run:

Backend:

python -m pytest

Frontend:

cd frontend
npm run lint
npm run build

Also manually test:

POST /api/evidence/retrieve

using a known DOI and claim.

Verify:

- API starts correctly
- existing health endpoint works
- citation resolver still works
- paper retrieval still works
- evidence retrieval returns ranked chunks
- existing tests remain green
- no frontend functionality is broken

==================================================
IMPORTANT ARCHITECTURE RULE
==================================================

DO NOT implement the three verification agents in this milestone.

The future architecture is:

Evidence Retrieval
        ↓
┌─────────────────────────┐
│ Prosecutor              │
│ Challenges the claim    │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│ Defender                │
│ Builds supporting case  │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│ Adjudicator             │
│ Final evidence verdict  │
└─────────────────────────┘

Milestone 4 only produces:

"Here are the most relevant pieces of evidence for this claim."

It must NOT produce:

SUPPORTS
OVERSTATED
CONTRADICTS
INSUFFICIENT
FABRICATED

Those verdicts belong to the later multi-agent verification layer.

==================================================
FINAL DELIVERABLE
==================================================

At the end, provide a concise implementation report containing:

1. Files created
2. Files modified
3. API endpoint added
4. Ranking methodology
5. Response structure
6. Edge cases handled
7. Number of tests
8. Test results
9. Frontend lint result
10. Frontend build result
11. Manual API test result
12. Known limitations
13. Confirmation that NO frontend functionality was changed
14. Confirmation that NO LLM/vector database was introduced

DO NOT commit or push anything.

Stop after Milestone 4 is fully implemented and validated.