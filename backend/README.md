# SciVerify Backend

FastAPI backend for the SciVerify evidence-backed citation verification platform.

Phase 6 Milestone 1 provides the initial server scaffold and health check only. Verification, citation resolution, and agent pipelines are implemented in later milestones.

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

Copy environment placeholders (optional for Milestone 1):

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
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use values from `.env`:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Default host/port match `BACKEND_HOST` / `BACKEND_PORT` in `.env.example`.

## Local URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API root (FastAPI) |
| http://localhost:8000/api/health | Health check |
| http://localhost:8000/docs | Swagger UI (auto-generated) |

## Health check

```bash
curl http://localhost:8000/api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "sciverify-backend"
}
```

## CORS

The backend allows requests from the Vite frontend origin configured in `FRONTEND_URL` (default `http://localhost:5173`).

Do not set `allow_origins=["*"]` in production. Add additional origins via environment configuration when needed.

## Frontend integration

The React app reads `VITE_API_BASE_URL` (see `frontend/.env.example`). Milestone 1 does not wire verification calls to this backend yet; the frontend continues to use the mock verification service.

## Security

- Never expose Supabase service-role keys or LLM API keys to the frontend.
- Keep secrets in `backend/.env` only (gitignored).
- Use `VITE_*` variables in the frontend for publishable configuration only.
