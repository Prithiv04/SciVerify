"""Central configuration defaults for the SciVerify backend."""

from __future__ import annotations

import os

PAPER_REQUEST_TIMEOUT = float(os.getenv("PAPER_REQUEST_TIMEOUT", "30"))
MAX_DOCUMENT_SIZE = int(os.getenv("MAX_DOCUMENT_SIZE", str(20 * 1024 * 1024)))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
EVIDENCE_TOP_K = int(os.getenv("EVIDENCE_TOP_K", "10"))
EVIDENCE_MIN_RELEVANCE = float(os.getenv("EVIDENCE_MIN_RELEVANCE", "0.05"))
