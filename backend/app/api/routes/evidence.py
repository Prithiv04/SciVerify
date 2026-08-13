from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.evidence import EvidenceRetrievalRequest, EvidenceRetrievalResponse
from app.services.evidence_pipeline import build_evidence_response, retrieve_evidence_for_claim
from app.services.paper_retriever import (
    DocumentRetrievalFailure,
    PaperNotFoundError,
    PaperProviderError,
    retrieve_paper,
)
from app.utils.claim_preprocessor import InvalidClaimError, preprocess_claim
from app.utils.doi import InvalidDOIError

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/retrieve", response_model=EvidenceRetrievalResponse)
def retrieve_evidence_endpoint(
    request: EvidenceRetrievalRequest,
) -> EvidenceRetrievalResponse:
    """Retrieve and rank the most relevant evidence chunks for a claim against a paper."""
    try:
        processed_claim = preprocess_claim(request.claim)
    except InvalidClaimError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        paper_result = retrieve_paper(request.doi)
    except InvalidDOIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PaperNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentRetrievalFailure as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PaperProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return build_evidence_response(processed_claim, paper_result)


__all__ = ["retrieve_evidence_for_claim", "router"]
