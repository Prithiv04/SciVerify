import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend/.env is loaded even if CWD is repo root
backend_env = Path(__file__).resolve().parent.parent / ".env"
if backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
else:
    load_dotenv()

from app.api.routes.citations import router as citations_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.papers import router as papers_router
from app.api.routes.verification import router as verification_router

BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title="SciVerify Backend",
    description="Evidence-backed scientific citation verification API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(citations_router)
app.include_router(papers_router)
app.include_router(evidence_router)
app.include_router(verification_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "sciverify-backend"}
