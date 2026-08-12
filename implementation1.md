# SciVerify — Phase 6, Milestone 3 Implementation Plan
## Paper Metadata & Content Retrieval

You are working on the SciVerify repository.

The project currently has:

- A completed React/Vite frontend with mock verification workflow
- A FastAPI backend scaffold
- Phase 6 Milestone 1 completed:
  - FastAPI application
  - CORS
  - GET /api/health
- Phase 6 Milestone 2 completed:
  - DOI normalization
  - Crossref citation resolver
  - OpenAlex fallback
  - POST /api/citations/resolve
  - 17 citation resolver tests
- Frontend is still intentionally using mock verification data
- Git cleanup has been completed
- Changes have already been committed and pushed

Do NOT modify the frontend verification workflow in this milestone.

The goal of Milestone 3 is to build a reliable backend pipeline that can take a resolved DOI/citation and retrieve accessible scientific paper metadata and content, normalize it, parse it, and split it into evidence-ready chunks.

--------------------------------------------------
## CORE OBJECTIVE
--------------------------------------------------

Build this pipeline:

DOI
 ↓
Citation Resolver
 ↓
Normalized Paper Metadata
 ↓
Full-text Discovery
 ↓
Accessible PDF/HTML Retrieval
 ↓
Document Parsing
 ↓
Section Detection
 ↓
Text Cleaning
 ↓
Evidence Chunking
 ↓
Evidence-ready paper representation

This milestone must prepare the backend for Milestone 4:
Evidence Retrieval / Ranking.

Do NOT implement the three verification agents yet.

Do NOT implement the LLM verification pipeline yet.

--------------------------------------------------
## IMPORTANT CONSTRAINTS
--------------------------------------------------

1. Inspect the existing repository before modifying anything.

2. Reuse existing:
   - DOI normalization
   - CitationMetadata
   - citation resolver
   - FastAPI architecture
   - existing environment configuration
   - existing test conventions

3. Do not duplicate DOI normalization or citation-resolution logic.

4. Do not break:
   - GET /api/health
   - POST /api/citations/resolve
   - existing citation resolver tests
   - frontend build
   - frontend mock verification workflow

5. Do not add unnecessary dependencies.

6. Do not scrape or bypass paywalls.

7. Only retrieve publicly accessible content.

8. Do not require API keys for basic Crossref/OpenAlex metadata retrieval unless the existing architecture already supports optional keys.

9. External provider failures must be handled gracefully.

10. Do not hard-code secrets.

11. Keep provider URLs configurable through environment variables.

12. Do not modify frontend files unless absolutely necessary. Prefer zero frontend changes for this milestone.

13. Do not commit or push changes.

--------------------------------------------------
## PHASE 3.1 — PAPER DATA MODEL
--------------------------------------------------

Create a normalized paper representation.

Suggested file:

backend/app/schemas/paper.py

Create appropriate Pydantic models.

At minimum support:

PaperMetadata

Fields should include approximately:

- paper_id
- doi
- title
- authors
- abstract
- journal
- publisher
- publication_date
- year
- url
- source_url
- open_access
- full_text_available
- full_text_format
- full_text_url

Use appropriate optional types.

Do not make fields mandatory when providers commonly omit them.

Create models for:

- PaperMetadata
- RetrievePaperRequest
- RetrievePaperResponse
- DocumentSection
- EvidenceChunk

Adapt naming/types to the existing project conventions rather than blindly copying this specification.

--------------------------------------------------
## PHASE 3.2 — PAPER RETRIEVAL SERVICE
--------------------------------------------------

Create:

backend/app/services/paper_retriever.py

The service should:

1. Accept a DOI or normalized citation identifier.
2. Reuse the existing citation resolver.
3. Obtain normalized metadata.
4. Determine whether accessible full text exists.
5. Discover the best available full-text source.
6. Return a normalized paper object.

Do not duplicate Crossref/OpenAlex metadata parsing if it can be reused cleanly.

Create clear service-level exceptions.

For example:

- PaperNotFoundError
- FullTextUnavailableError
- PaperProviderError
- DocumentRetrievalError

Use names that fit the existing architecture.

--------------------------------------------------
## PHASE 3.3 — FULL-TEXT DISCOVERY
--------------------------------------------------

Implement public full-text discovery.

Preferred strategy:

1. OpenAlex metadata
2. Open-access location
3. Public PDF URL
4. Public HTML URL
5. Other explicitly accessible source URL

Do not:

- bypass authentication
- bypass paywalls
- use illegal mirrors
- scrape restricted content
- fabricate a full-text URL

If metadata exists but full text is unavailable, return a valid response indicating:

full_text_available = false

This should NOT automatically be treated as a server failure.

The system must distinguish:

SUCCESS
METADATA_ONLY
FULL_TEXT_UNAVAILABLE
NOT_FOUND
PROVIDER_ERROR

Use a clean enum or equivalent representation where appropriate.

--------------------------------------------------
## PHASE 3.4 — DOCUMENT DOWNLOAD
--------------------------------------------------

Create a dedicated document retrieval service, for example:

backend/app/services/document_retriever.py

Responsibilities:

- HTTP GET accessible document
- reasonable timeout
- follow redirects safely
- validate response status
- inspect Content-Type
- prevent obviously unsupported content
- enforce a sensible maximum document size
- return bytes/text plus detected format

Supported formats:

- PDF
- HTML

Do not support arbitrary binary files.

Handle:

- timeout
- connection error
- HTTP errors
- invalid content type
- oversized documents
- malformed responses

with clear exceptions.

--------------------------------------------------
## PHASE 3.5 — DOCUMENT PARSING
--------------------------------------------------

Create:

backend/app/services/document_parser.py

Implement:

PDF → text
HTML → text

Use lightweight, well-maintained Python libraries.

Before adding a dependency, inspect requirements.txt.

Possible libraries may include:

- pypdf
- beautifulsoup4

Only add what is actually necessary.

The parser should return structured content rather than one giant unstructured string.

Example:

DocumentSection

- section_name
- text
- order

Attempt to identify common scientific sections:

- Abstract
- Introduction
- Background
- Methods
- Materials and Methods
- Results
- Discussion
- Conclusion
- Limitations
- References

Do not assume every paper contains every section.

Unknown sections should still be preserved.

Do not discard useful text merely because a heading is unfamiliar.

--------------------------------------------------
## PHASE 3.6 — TEXT CLEANING
--------------------------------------------------

Create a utility/service for document cleaning.

Responsibilities:

- remove excessive whitespace
- normalize line breaks
- remove obvious repeated headers/footers when possible
- preserve paragraph boundaries
- preserve section structure
- avoid destructive cleaning
- preserve scientific terminology
- preserve numbers, units, percentages and citations

Do NOT aggressively summarize or rewrite the scientific text.

The output must remain faithful to the source.

--------------------------------------------------
## PHASE 3.7 — EVIDENCE CHUNKING
--------------------------------------------------

Create:

backend/app/services/evidence_chunker.py

Split parsed document content into evidence-ready chunks.

Each chunk should retain:

- chunk_id
- paper_id
- section
- chunk_index
- text
- source_url
- page number if available
- metadata where available

Important:

Chunks must not lose their relationship to the original paper.

Prefer section-aware chunking over blindly splitting the entire paper.

Use reasonable configurable chunk size and overlap.

Do not hard-code values throughout the codebase.

Put configurable defaults in one place.

Example conceptual structure:

Paper
 ├── Abstract
 ├── Introduction
 ├── Methods
 ├── Results
 │    ├── Chunk 1
 │    ├── Chunk 2
 │    └── Chunk 3
 ├── Discussion
 └── Conclusion

--------------------------------------------------
## PHASE 3.8 — API ENDPOINT
--------------------------------------------------

Create:

backend/app/api/routes/papers.py

Add:

POST /api/papers/retrieve

Request:

{
  "doi": "10.xxxx/xxxxx"
}

The endpoint should:

1. Validate/normalize DOI.
2. Resolve citation metadata.
3. Discover accessible full text.
4. Retrieve the document when available.
5. Parse the document.
6. Clean the text.
7. Generate evidence chunks.
8. Return normalized paper information.

The endpoint response should clearly distinguish:

- metadata successfully retrieved
- full text available
- full text unavailable
- document parsing failure
- paper not found
- provider failure

Do not expose internal stack traces.

Use appropriate HTTP status codes.

For example:

400 → invalid request/DOI
404 → paper not found
422 → validation failure
503 → external provider unavailable

But choose status codes according to the existing API conventions.

--------------------------------------------------
## PHASE 3.9 — RESPONSE DESIGN
--------------------------------------------------

The response should contain enough information for Milestone 4.

Conceptually:

{
  "status": "success",
  "paper": {
    "doi": "...",
    "title": "...",
    "authors": [],
    "abstract": "...",
    "journal": "...",
    "publication_date": "...",
    "open_access": true,
    "full_text_available": true,
    "full_text_format": "pdf"
  },
  "sections": [],
  "chunks": [],
  "source": {
    "url": "...",
    "provider": "openalex"
  }
}

Do not expose unnecessary raw provider responses.

Keep the API contract clean and stable.

--------------------------------------------------
## PHASE 3.10 — TESTING
--------------------------------------------------

Create comprehensive automated tests.

Suggested test files:

backend/app/tests/test_paper_retriever.py
backend/app/tests/test_document_retriever.py
backend/app/tests/test_document_parser.py
backend/app/tests/test_evidence_chunker.py
backend/app/tests/test_papers_api.py

Tests should cover:

### Metadata

- valid DOI
- metadata returned
- missing optional metadata
- paper not found

### Full-text discovery

- public PDF available
- public HTML available
- no full text available
- provider failure
- malformed provider response

### Document retrieval

- successful PDF download
- successful HTML download
- HTTP error
- timeout
- unsupported content type
- oversized response

### Parsing

- simple PDF
- simple HTML
- malformed HTML
- missing sections
- unknown sections
- multiple sections

### Cleaning

- excessive whitespace
- repeated line breaks
- preserved paragraphs
- scientific numbers/units preserved

### Chunking

- chunks generated
- section metadata preserved
- chunk ordering preserved
- overlap behavior
- short sections
- empty sections
- chunk IDs unique

### API

- successful retrieval
- metadata-only response
- unavailable full text
- invalid DOI
- paper not found
- provider failure

All external HTTP calls must be mocked in tests.

Tests must NOT depend on live Crossref/OpenAlex/PDF servers.

--------------------------------------------------
## PHASE 3.11 — CONFIGURATION
--------------------------------------------------

Update:

backend/.env.example

Only if required.

Potential configuration:

CROSSREF_BASE_URL
OPENALEX_BASE_URL
CITATION_USER_AGENT

PAPER_REQUEST_TIMEOUT
MAX_DOCUMENT_SIZE
CHUNK_SIZE
CHUNK_OVERLAP

Use sensible defaults.

Never put real API keys or secrets into .env.example.

--------------------------------------------------
## PHASE 3.12 — DOCUMENTATION
--------------------------------------------------

Update:

backend/README.md

Document:

1. Paper retrieval endpoint
2. Request example
3. Response example
4. Supported document formats
5. Full-text unavailable behavior
6. Chunking behavior
7. Running tests
8. Local development

Include a curl example.

--------------------------------------------------
## ARCHITECTURE REQUIREMENTS
--------------------------------------------------

Keep responsibilities separated:

backend/app/
├── api/
│   └── routes/
│       ├── citations.py
│       └── papers.py
│
├── schemas/
│   ├── citation.py
│   └── paper.py
│
├── services/
│   ├── citation_resolver.py
│   ├── paper_retriever.py
│   ├── document_retriever.py
│   ├── document_parser.py
│   └── evidence_chunker.py
│
├── utils/
│   └── doi.py
│
└── tests/
    ├── test_citation_resolver.py
    ├── test_paper_retriever.py
    ├── test_document_retriever.py
    ├── test_document_parser.py
    ├── test_evidence_chunker.py
    └── test_papers_api.py

Adapt this structure if the existing repository already has a better established pattern.

--------------------------------------------------
## IMPORTANT: DO NOT BUILD THESE YET
--------------------------------------------------

Do NOT implement:

- Claim Challenger
- Evidence Defender
- Final Reviewer
- LLM calls
- RAG/vector database
- embeddings
- Supabase verification persistence
- frontend/backend verification integration
- dashboard changes
- authentication changes

Those belong to later milestones.

This milestone only creates the reliable paper → evidence foundation.

--------------------------------------------------
## VALIDATION REQUIREMENTS
--------------------------------------------------

Before declaring the milestone complete, run:

Backend:

python -m pytest

Frontend:

npm run lint
npm run build

Backend health:

GET /api/health

Citation resolver:

POST /api/citations/resolve

Paper retrieval:

POST /api/papers/retrieve

Use a known public scientific DOI for integration testing if internet access is available.

If live integration tests are used, keep them separate from the normal automated test suite so CI does not depend on external services.

--------------------------------------------------
## FINAL REPORT
--------------------------------------------------

When implementation is complete, do NOT commit or push.

Report:

1. Files created
2. Files modified
3. API endpoints added
4. Dependencies added
5. Paper retrieval flow
6. Supported document formats
7. Full-text fallback behavior
8. Chunking strategy
9. Test count and results
10. npm lint result
11. npm build result
12. Health endpoint result
13. Citation resolver result
14. Paper retrieval integration result
15. Any limitations
16. Recommended next milestone

Do not claim success unless the validation commands actually pass.

Most importantly:

IMPLEMENT THIS MILESTONE ONLY.
Do not proceed to Milestone 4 or implement the multi-agent verification system.