from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.verification import VerificationAnalyzeRequest, VerificationResponse
from app.services.paper_retriever import (
    DocumentRetrievalFailure,
    PaperNotFoundError,
    PaperProviderError,
)
from app.services.verification_service import analyze_verification
from app.utils.claim_preprocessor import InvalidClaimError
from app.utils.doi import InvalidDOIError

router = APIRouter(prefix="/api/verification", tags=["verification"])


@router.post("/analyze", response_model=VerificationResponse)
def analyze_verification_endpoint(
    request: VerificationAnalyzeRequest,
) -> VerificationResponse:
    """Analyze a scientific claim against a cited paper using the multi-agent verification layer."""
    try:
        return analyze_verification(request.claim, request.doi)
    except InvalidClaimError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InvalidDOIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PaperNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentRetrievalFailure as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PaperProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
