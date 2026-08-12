# SciVerify Backend

FastAPI backend for the SciVerify evidence-backed citation verification platform.

## Milestones

| Milestone | Status | Description |
|-----------|--------|-------------|
| 1 | Complete | FastAPI scaffold, health check, CORS |
| 2 | Complete | DOI citation resolver (Crossref → OpenAlex) |
| 3+ | Planned | Paper retrieval, evidence, agents, persistence |

## Prerequisites

- Python 3.11+ recommended
- pip

## Setup

From the repository root:

```bash
cd backend
```

Create and activate a virtual environment:

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment placeholders (optional):

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

## Run the server

With the virtual environment activated, from the `backend/` directory:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Default development URLs:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8001 | API root |
| http://127.0.0.1:8001/api/health | Health check |
| http://127.0.0.1:8001/docs | Swagger UI |

## Health check

```bash
curl http://127.0.0.1:8001/api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "sciverify-backend"
}
```

## Citation resolver (Milestone 2)

`POST /api/citations/resolve` resolves a DOI to normalized paper metadata.

**This endpoint only resolves citation metadata. It does NOT verify scientific claims.**

### Resolution flow

1. Normalize the DOI input (raw DOI, `doi:` prefix, or `doi.org` URL)
2. Query **Crossref** (`GET /works/{doi}`)
3. If Crossref cannot resolve usable metadata, fall back to **OpenAlex**
4. Return a consistent internal `CitationMetadata` structure

No API keys are required for Crossref or OpenAlex public metadata endpoints.

### Example request

```bash
curl -X POST http://127.0.0.1:8001/api/citations/resolve \
  -H "Content-Type: application/json" \
  -d "{\"doi\": \"10.1038/s41586-020-2649-2\"}"
```

### Example response

```json
{
  "doi": "10.1038/s41586-020-2649-2",
  "title": "Example Paper Title",
  "authors": ["Ada Lovelace", "Alan Turing"],
  "journal": "Nature",
  "publisher": "Nature Publishing Group",
  "year": 2020,
  "url": "https://doi.org/10.1038/s41586-020-2649-2",
  "source": "crossref",
  "type": "journal-article"
}
```

### HTTP status codes

| Code | Meaning |
|------|---------|
| 200 | Citation resolved |
| 400 | Invalid DOI |
| 404 | Citation not found in Crossref or OpenAlex |
| 503 | External provider failure (timeout, unavailable) |

## Tests

All external HTTP calls are mocked in tests.

```bash
cd backend
python -m pytest
```

## CORS

The backend allows requests from the Vite frontend origin configured in `FRONTEND_URL` (default `http://localhost:5173`).

## Frontend integration

The React app continues to use **mock verification** for `/app/verify`. The citation resolver is backend-only in Milestone 2 and is not wired to the verification UI yet.

## Security

- Never expose Supabase service-role keys or LLM API keys to the frontend.
- Keep secrets in `backend/.env` only (gitignored).
- Use `VITE_*` variables in the frontend for publishable configuration only.
