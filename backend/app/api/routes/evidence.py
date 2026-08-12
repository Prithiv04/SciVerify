from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.evidence import (
    EvidenceItem,
    EvidencePaperSummary,
    EvidenceRetrievalRequest,
    EvidenceRetrievalResponse,
    EvidenceRetrievalStatus,
)
from app.schemas.paper import PaperRetrievalStatus, RetrievePaperResponse
from app.services.evidence_retriever import rank_evidence_for_claim
from app.services.paper_retriever import (
    DocumentRetrievalFailure,
    PaperNotFoundError,
    PaperProviderError,
    retrieve_paper,
)
from app.utils.claim_preprocessor import InvalidClaimError, ProcessedClaim, preprocess_claim
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

    return _build_evidence_response(processed_claim, paper_result)


def _build_evidence_response(
    processed_claim: ProcessedClaim,
    paper_result: RetrievePaperResponse,
) -> EvidenceRetrievalResponse:
    claim = processed_claim.original
    paper_summary = EvidencePaperSummary(
        paper_id=paper_result.paper.paper_id,
        doi=paper_result.paper.doi,
        title=paper_result.paper.title,
    )

    if paper_result.status == PaperRetrievalStatus.NOT_FOUND:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.NOT_FOUND,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail="Paper not found.",
        )

    if paper_result.status == PaperRetrievalStatus.PROVIDER_ERROR:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.PROVIDER_ERROR,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail=paper_result.detail or "External provider unavailable.",
        )

    if paper_result.status == PaperRetrievalStatus.METADATA_ONLY:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.METADATA_ONLY,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail="Paper metadata retrieved, but evidence chunks are unavailable.",
        )

    if paper_result.status == PaperRetrievalStatus.FULL_TEXT_UNAVAILABLE:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.FULL_TEXT_UNAVAILABLE,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail="Full text is unavailable for evidence retrieval.",
        )

    if paper_result.status == PaperRetrievalStatus.PARSING_FAILURE:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.PARSING_FAILURE,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail=paper_result.detail or "Document parsing failed.",
        )

    chunks = paper_result.chunks
    if not chunks:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.NO_CHUNKS,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=0,
            detail="Paper retrieved but no evidence chunks were produced.",
        )

    ranked = rank_evidence_for_claim(processed_claim, chunks)

    if not ranked:
        return EvidenceRetrievalResponse(
            status=EvidenceRetrievalStatus.NO_RELEVANT_EVIDENCE,
            claim=claim,
            paper=paper_summary,
            evidence=[],
            total_chunks_considered=len(chunks),
            detail="No evidence chunks met the minimum relevance threshold.",
        )

    return EvidenceRetrievalResponse(
        status=EvidenceRetrievalStatus.SUCCESS,
        claim=claim,
        paper=paper_summary,
        evidence=_dedupe_evidence_items(ranked),
        total_chunks_considered=len(chunks),
    )


def _dedupe_evidence_items(items: list[EvidenceItem]) -> list[EvidenceItem]:
    seen: set[str] = set()
    deduped: list[EvidenceItem] = []
    for item in items:
        if item.chunk_id in seen:
            continue
        seen.add(item.chunk_id)
        deduped.append(item)
    return deduped
