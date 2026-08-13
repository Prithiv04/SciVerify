from __future__ import annotations

import logging

from app.schemas.evidence import EvidenceRetrievalStatus
from app.schemas.verification import (
    VerificationResponse,
    VerificationStatus,
    Verdict,
)
from app.services.agents import run_adjudicator, run_defender, run_prosecutor
from app.services.evidence_pipeline import retrieve_evidence_for_claim
from app.services.llm.provider import (
    LLMProvider,
    LLMProviderError,
    LLMResponseError,
    LLMUnavailableError,
    get_llm_provider,
)
from app.services.paper_retriever import (
    DocumentRetrievalFailure,
    PaperNotFoundError,
    PaperProviderError,
)
from app.services.verification_validator import validate_verification_result
from app.utils.claim_preprocessor import InvalidClaimError, preprocess_claim
from app.utils.doi import InvalidDOIError

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_STATUSES = {
    EvidenceRetrievalStatus.NO_CHUNKS,
    EvidenceRetrievalStatus.NO_RELEVANT_EVIDENCE,
    EvidenceRetrievalStatus.FULL_TEXT_UNAVAILABLE,
    EvidenceRetrievalStatus.METADATA_ONLY,
    EvidenceRetrievalStatus.PARSING_FAILURE,
}


class VerificationServiceError(Exception):
    """Raised when verification cannot be completed."""


def analyze_verification(
    claim: str,
    doi: str,
    *,
    llm: LLMProvider | None = None,
) -> VerificationResponse:
    """Run the full multi-agent verification pipeline for a claim and DOI."""
    logger.info("verification_started")

    processed_claim = preprocess_claim(claim)
    logger.info("claim_preprocessed")

    evidence_response = retrieve_evidence_for_claim(processed_claim.original, doi)
    paper = evidence_response.paper

    if evidence_response.status == EvidenceRetrievalStatus.NOT_FOUND:
        logger.info("verification_completed status=not_found")
        raise PaperNotFoundError(evidence_response.detail or "Paper not found.")

    if evidence_response.status == EvidenceRetrievalStatus.PROVIDER_ERROR:
        logger.info("verification_completed status=provider_error")
        raise PaperProviderError(evidence_response.detail or "External provider unavailable.")

    if evidence_response.status in INSUFFICIENT_EVIDENCE_STATUSES or not evidence_response.evidence:
        logger.info("verification_completed status=insufficient_evidence")
        return VerificationResponse(
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            claim=processed_claim.original,
            verdict=Verdict.INSUFFICIENT,
            confidence=0.0,
            summary="Insufficient evidence available to verify this claim against the cited paper.",
            reasoning=evidence_response.detail
            or "Evidence retrieval did not produce usable chunks for agent analysis.",
            paper=paper,
            evidence=[],
            detail=evidence_response.detail,
        )

    logger.info("evidence_retrieved chunks=%s", len(evidence_response.evidence))

    provider = llm or get_llm_provider()
    try:
        prosecutor = run_prosecutor(processed_claim.original, evidence_response.evidence, provider)
        logger.info("prosecutor_completed")
        defender = run_defender(processed_claim.original, evidence_response.evidence, provider)
        logger.info("defender_completed")
        adjudicator = run_adjudicator(
            processed_claim.original,
            evidence_response.evidence,
            prosecutor,
            defender,
            provider,
        )
        logger.info("adjudicator_completed")
    except LLMUnavailableError as exc:
        logger.info("verification_completed status=llm_unavailable")
        return VerificationResponse(
            status=VerificationStatus.LLM_UNAVAILABLE,
            claim=processed_claim.original,
            paper=paper,
            evidence=evidence_response.evidence,
            detail=str(exc),
        )
    except (LLMProviderError, LLMResponseError) as exc:
        logger.info("verification_completed status=verification_failed")
        return VerificationResponse(
            status=VerificationStatus.VERIFICATION_FAILED,
            claim=processed_claim.original,
            paper=paper,
            evidence=evidence_response.evidence,
            detail=str(exc),
        )

    validated = validate_verification_result(
        claim=processed_claim.original,
        evidence=evidence_response.evidence,
        prosecutor=prosecutor,
        defender=defender,
        adjudicator=adjudicator,
    )

    logger.info(
        "verification_completed status=success original_verdict=%s validated_verdict=%s",
        adjudicator.verdict.value,
        validated.verdict.value,
    )
    return VerificationResponse(
        status=VerificationStatus.SUCCESS,
        claim=processed_claim.original,
        verdict=validated.verdict,
        confidence=validated.confidence,
        summary=adjudicator.analysis,
        reasoning=adjudicator.reasoning,
        paper=paper,
        evidence=evidence_response.evidence,
        prosecutor=prosecutor,
        defender=defender,
        adjudicator=adjudicator,
        suggested_correction=validated.suggested_correction,
        agent_agreement=validated.agent_agreement,
        validation_warnings=validated.validation_warnings or None,
    )


__all__ = [
    "DocumentRetrievalFailure",
    "InvalidClaimError",
    "InvalidDOIError",
    "PaperNotFoundError",
    "PaperProviderError",
    "VerificationServiceError",
    "analyze_verification",
]
