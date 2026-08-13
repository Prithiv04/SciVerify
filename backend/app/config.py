from __future__ import annotations

import os

PAPER_REQUEST_TIMEOUT = float(os.getenv("PAPER_REQUEST_TIMEOUT", "30"))
MAX_DOCUMENT_SIZE = int(os.getenv("MAX_DOCUMENT_SIZE", str(20 * 1024 * 1024)))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
EVIDENCE_TOP_K = int(os.getenv("EVIDENCE_TOP_K", "5"))
EVIDENCE_MIN_RELEVANCE = float(os.getenv("EVIDENCE_MIN_RELEVANCE", "0.05"))
EVIDENCE_DIVERSITY_THRESHOLD = float(os.getenv("EVIDENCE_DIVERSITY_THRESHOLD", "0.75"))
EVIDENCE_MAX_PER_SECTION = int(os.getenv("EVIDENCE_MAX_PER_SECTION", "2"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").strip().lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
LLM_REQUEST_TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "60"))
