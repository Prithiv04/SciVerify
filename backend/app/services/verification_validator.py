from __future__ import annotations

import logging
from dataclasses import dataclass

from app.schemas.evidence import EvidenceItem
from app.schemas.verification import (
    AdjudicatorAnalysis,
    DefenderAnalysis,
    ProsecutorAnalysis,
    Verdict,
)
from app.services.evidence_validation import (
    available_chunk_ids,
    sanitize_adjudicator_analysis,
    sanitize_defender_analysis,
    sanitize_prosecutor_analysis,
)

logger = logging.getLogger(__name__)

WEAK_RELEVANCE_THRESHOLD = 0.15
WEAK_OVERLAP_THRESHOLD = 0.15
STRONG_RELEVANCE_THRESHOLD = 0.35
STRONG_OVERLAP_THRESHOLD = 0.25

CHALLENGE_STANCE_KEYWORDS = (
    "challenge",
    "skeptic",
    "contradict",
    "oppose",
    "weaken",
    "dispute",
    "reject",
    "uncertain",
)
SUPPORT_STANCE_KEYWORDS = (
    "support",
    "defend",
    "confirm",
    "uphold",
    "substantiat",
    "align",
)


@dataclass(frozen=True)
class EvidenceStrength:
    count: int
    avg_relevance: float
    avg_overlap: float
    max_relevance: float
    max_overlap: float
    strong_count: int
    weak_only: bool


@dataclass(frozen=True)
class ValidatedVerification:
    verdict: Verdict
    confidence: float
    suggested_correction: str | None
    agent_agreement: bool
    validation_warnings: list[str]
    original_verdict: Verdict
    original_confidence: float


def validate_verification_result(
    *,
    claim: str,
    evidence: list[EvidenceItem],
    prosecutor: ProsecutorAnalysis,
    defender: DefenderAnalysis,
    adjudicator: AdjudicatorAnalysis,
) -> ValidatedVerification:
    """Apply deterministic checks to the adjudicator result."""
    _ = claim  # Reserved for future claim-aware checks without domain keywords.
    valid_ids = available_chunk_ids(evidence)
    warnings = _invalid_reference_warnings(prosecutor, defender, adjudicator, valid_ids)
    prosecutor = sanitize_prosecutor_analysis(prosecutor, valid_ids)
    defender = sanitize_defender_analysis(defender, valid_ids)
    adjudicator = sanitize_adjudicator_analysis(adjudicator, valid_ids)

    strength = _compute_evidence_strength(evidence)
    agent_agreement = _agents_agree(prosecutor, defender)

    verdict, verdict_warnings = _validate_verdict(
        adjudicator,
        prosecutor,
        defender,
        strength,
    )
    warnings.extend(verdict_warnings)

    correction, correction_warnings = _normalize_suggested_correction(
        verdict,
        adjudicator.suggested_correction,
    )
    warnings.extend(correction_warnings)

    original_confidence = adjudicator.confidence
    confidence = _calibrate_confidence(
        original_confidence,
        verdict=verdict,
        strength=strength,
        agent_agreement=agent_agreement,
        warnings=warnings,
        verdict_changed=verdict != adjudicator.verdict,
    )

    logger.info(
        "Verification validation: original_verdict=%s validated_verdict=%s "
        "evidence_count=%s supporting_count=%s contradicting_count=%s "
        "agent_agreement=%s confidence_before=%s confidence_after=%s warnings=%s",
        adjudicator.verdict.value,
        verdict.value,
        strength.count,
        len(adjudicator.supporting_evidence),
        len(adjudicator.contradicting_evidence),
        agent_agreement,
        original_confidence,
        confidence,
        len(warnings),
    )

    return ValidatedVerification(
        verdict=verdict,
        confidence=confidence,
        suggested_correction=correction,
        agent_agreement=agent_agreement,
        validation_warnings=warnings,
        original_verdict=adjudicator.verdict,
        original_confidence=original_confidence,
    )


def _compute_evidence_strength(evidence: list[EvidenceItem]) -> EvidenceStrength:
    if not evidence:
        return EvidenceStrength(
            count=0,
            avg_relevance=0.0,
            avg_overlap=0.0,
            max_relevance=0.0,
            max_overlap=0.0,
            strong_count=0,
            weak_only=True,
        )

    relevances = [item.relevance_score for item in evidence]
    overlaps = [item.claim_overlap for item in evidence]
    strong_count = sum(
        1
        for item in evidence
        if item.relevance_score >= STRONG_RELEVANCE_THRESHOLD
        and item.claim_overlap >= STRONG_OVERLAP_THRESHOLD
    )
    weak_only = all(
        item.relevance_score < WEAK_RELEVANCE_THRESHOLD
        and item.claim_overlap < WEAK_OVERLAP_THRESHOLD
        for item in evidence
    )

    return EvidenceStrength(
        count=len(evidence),
        avg_relevance=sum(relevances) / len(relevances),
        avg_overlap=sum(overlaps) / len(overlaps),
        max_relevance=max(relevances),
        max_overlap=max(overlaps),
        strong_count=strong_count,
        weak_only=weak_only,
    )


def _stance_indicates_challenge(stance: str) -> bool:
    normalized = stance.lower()
    return any(keyword in normalized for keyword in CHALLENGE_STANCE_KEYWORDS)


def _stance_indicates_support(stance: str) -> bool:
    normalized = stance.lower()
    return any(keyword in normalized for keyword in SUPPORT_STANCE_KEYWORDS)


def _agents_agree(
    prosecutor: ProsecutorAnalysis,
    defender: DefenderAnalysis,
) -> bool:
    prosecutor_challenging = bool(prosecutor.contradicting_evidence) or _stance_indicates_challenge(
        prosecutor.stance
    )
    defender_supporting = bool(defender.supporting_evidence) or _stance_indicates_support(
        defender.stance
    )
    defender_challenging = bool(defender.contradicting_evidence) or _stance_indicates_challenge(
        defender.stance
    )
    prosecutor_supporting = bool(prosecutor.supporting_evidence) or _stance_indicates_support(
        prosecutor.stance
    )

    if prosecutor_challenging and defender_supporting:
        return False
    if defender_challenging and prosecutor_supporting:
        return False
    return True


def _invalid_reference_warnings(
    prosecutor: ProsecutorAnalysis,
    defender: DefenderAnalysis,
    adjudicator: AdjudicatorAnalysis,
    valid_ids: set[str],
) -> list[str]:
    referenced: set[str] = set()
    for analysis in (prosecutor, defender, adjudicator):
        referenced.update(analysis.supporting_evidence)
        referenced.update(analysis.contradicting_evidence)

    invalid = [chunk_id for chunk_id in referenced if chunk_id not in valid_ids]
    if invalid:
        return ["Agent referenced evidence IDs that are not in retrieved evidence."]
    return []


def _has_contradicting_references(
    adjudicator: AdjudicatorAnalysis,
    prosecutor: ProsecutorAnalysis,
    defender: DefenderAnalysis,
) -> bool:
    return bool(
        adjudicator.contradicting_evidence
        or prosecutor.contradicting_evidence
        or defender.contradicting_evidence
    )


def _validate_verdict(
    adjudicator: AdjudicatorAnalysis,
    prosecutor: ProsecutorAnalysis,
    defender: DefenderAnalysis,
    strength: EvidenceStrength,
) -> tuple[Verdict, list[str]]:
    verdict = adjudicator.verdict
    warnings: list[str] = []

    if verdict == Verdict.SUPPORTS:
        if not adjudicator.supporting_evidence:
            warnings.append("Adjudicator returned SUPPORTS without supporting evidence IDs.")
        if strength.weak_only or strength.strong_count == 0:
            verdict = Verdict.INSUFFICIENT
            warnings.append(
                "Verdict adjusted from SUPPORTS to INSUFFICIENT because evidence quality is too weak."
            )

    elif verdict == Verdict.CONTRADICTS:
        if not _has_contradicting_references(adjudicator, prosecutor, defender):
            warnings.append("Adjudicator returned CONTRADICTS without contradicting evidence.")
            if strength.strong_count > 0 and not strength.weak_only:
                verdict = Verdict.OVERSTATED
                warnings.append(
                    "Verdict adjusted from CONTRADICTS to OVERSTATED because evidence appears supportive."
                )
            elif strength.weak_only:
                verdict = Verdict.INSUFFICIENT
                warnings.append(
                    "Verdict adjusted from CONTRADICTS to INSUFFICIENT because evidence is too weak."
                )

    elif verdict == Verdict.FABRICATED:
        if strength.strong_count > 0 or (strength.count > 0 and not strength.weak_only):
            verdict = Verdict.INSUFFICIENT
            warnings.append(
                "Verdict adjusted from FABRICATED to INSUFFICIENT because retrieved evidence relates to the claim."
            )
        elif strength.count == 0:
            verdict = Verdict.INSUFFICIENT
            warnings.append(
                "Verdict adjusted from FABRICATED to INSUFFICIENT because no usable evidence was retrieved."
            )

    elif verdict == Verdict.INSUFFICIENT:
        if strength.strong_count >= 2 and adjudicator.supporting_evidence:
            warnings.append(
                "Adjudicator returned INSUFFICIENT despite multiple strong supporting evidence items."
            )

    elif verdict == Verdict.OVERSTATED:
        if strength.weak_only:
            verdict = Verdict.INSUFFICIENT
            warnings.append(
                "Verdict adjusted from OVERSTATED to INSUFFICIENT because evidence quality is too weak."
            )

    return verdict, warnings


def _normalize_suggested_correction(
    verdict: Verdict,
    suggested_correction: str | None,
) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    correction = (suggested_correction or "").strip() or None

    if verdict in {Verdict.SUPPORTS, Verdict.INSUFFICIENT}:
        if correction is not None:
            warnings.append(
                f"Suggested correction removed because verdict is {verdict.value}."
            )
        return None, warnings

    if verdict == Verdict.OVERSTATED and correction is None:
        warnings.append("OVERSTATED verdict lacks a suggested correction.")

    return correction, warnings


def _calibrate_confidence(
    original_confidence: float,
    *,
    verdict: Verdict,
    strength: EvidenceStrength,
    agent_agreement: bool,
    warnings: list[str],
    verdict_changed: bool,
) -> float:
    confidence = original_confidence

    if strength.count == 0:
        return 0.0

    if strength.count == 1:
        confidence *= 0.85

    if strength.avg_relevance < 0.2:
        confidence *= 0.75

    if strength.avg_overlap < 0.15:
        confidence *= 0.75

    if strength.weak_only:
        confidence = min(confidence, 0.45)

    if verdict == Verdict.SUPPORTS and strength.strong_count == 0:
        confidence = min(confidence, 0.5)

    if not agent_agreement:
        confidence *= 0.88

    if warnings:
        confidence *= max(0.7, 0.95 ** len(warnings))

    if verdict_changed:
        confidence *= 0.85

    return max(0.0, min(1.0, confidence))


__all__ = [
    "EvidenceStrength",
    "ValidatedVerification",
    "validate_verification_result",
]
