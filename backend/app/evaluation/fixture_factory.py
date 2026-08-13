from __future__ import annotations

import json
from pathlib import Path

from app.schemas.evidence import EvidenceItem, EvidencePaperSummary
from app.schemas.verification import (
    AdjudicatorAnalysis,
    ClaimSegmentStatus,
    ClaimSegmentTrace,
    ClaimTraceability,
    DefenderAnalysis,
    ProsecutorAnalysis,
    Verdict,
    VerificationResponse,
    VerificationStatus,
)

PAPER = EvidencePaperSummary(
    paper_id="10.1000/benchmark",
    doi="10.1000/benchmark",
    title="Benchmark Paper",
)


def _evidence(
    chunk_id: str,
    text: str,
    *,
    relevance: float = 0.8,
    overlap: float = 0.75,
) -> EvidenceItem:
    return EvidenceItem(
        chunk_id=chunk_id,
        section="Results",
        chunk_index=0,
        text=text,
        relevance_score=relevance,
        claim_overlap=overlap,
        numeric_overlap=0.0,
    )


def _traceability(segments: list[tuple[str, ClaimSegmentStatus, float, list[str]]]) -> ClaimTraceability:
    return ClaimTraceability(
        segments=[
            ClaimSegmentTrace(
                id=segment_id,
                text=text,
                status=status,
                coverage_score=coverage,
                evidence_ids=evidence_ids,
            )
            for segment_id, text, status, coverage, evidence_ids in segments
        ],
        overall_coverage=sum(item[3] for item in segments) / len(segments),
        warnings=[],
    )


def build_fixture(case_id: str) -> VerificationResponse:
    builders = {
        "cas9_supports_001": _cas9_supports,
        "accuracy_overstated_001": _accuracy_overstated,
        "mortality_contradicts_001": _mortality_contradicts,
        "insufficient_evidence_001": _insufficient_evidence,
        "fabricated_claim_001": _fabricated_claim,
        "numeric_supports_001": _numeric_supports,
        "universal_overstated_001": _universal_overstated,
        "weak_insufficient_001": _weak_insufficient,
        "mechanism_supports_002": _mechanism_supports,
        "direction_contradicts_002": _direction_contradicts,
        "magnitude_overstated_002": _magnitude_overstated,
        "legacy_no_traceability_001": _legacy_no_traceability,
    }
    return builders[case_id]()


def write_all_fixtures(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for case_id in (
        "cas9_supports_001",
        "accuracy_overstated_001",
        "mortality_contradicts_001",
        "insufficient_evidence_001",
        "fabricated_claim_001",
        "numeric_supports_001",
        "universal_overstated_001",
        "weak_insufficient_001",
        "mechanism_supports_002",
        "direction_contradicts_002",
        "magnitude_overstated_002",
        "legacy_no_traceability_001",
    ):
        response = build_fixture(case_id)
        path = output_dir / f"{case_id}.json"
        path.write_text(
            json.dumps(response.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )


def _cas9_supports() -> VerificationResponse:
    claim = (
        "Cas9 can be programmed with guide RNA to cleave specific "
        "double-stranded DNA target sequences."
    )
    evidence = [
        _evidence("c1", "Cas9 can be programmed with guide RNA in vitro.", relevance=0.91, overlap=0.88),
        _evidence("c2", "Cas9 cleaves specific double-stranded DNA target sequences.", relevance=0.89, overlap=0.86),
    ]
    return _success_response(
        claim,
        Verdict.SUPPORTS,
        0.86,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    "Cas9 can be programmed with guide RNA",
                    ClaimSegmentStatus.SUPPORTED,
                    0.91,
                    ["c1"],
                ),
                (
                    "segment_2",
                    "to cleave specific double-stranded DNA target sequences",
                    ClaimSegmentStatus.SUPPORTED,
                    0.88,
                    ["c2"],
                ),
            ]
        ),
        agent_agreement=True,
    )


def _accuracy_overstated() -> VerificationResponse:
    claim = "The method improves accuracy by 40%."
    evidence = [_evidence("c1", "The method improves accuracy by 12%.", relevance=0.82, overlap=0.74)]
    return _success_response(
        claim,
        Verdict.OVERSTATED,
        0.78,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.PARTIALLY_SUPPORTED,
                    0.62,
                    ["c1"],
                )
            ]
        ),
        agent_agreement=False,
        adjudicator_verdict=Verdict.OVERSTATED,
    )


def _mortality_contradicts() -> VerificationResponse:
    claim = "The treatment reduces mortality."
    evidence = [_evidence("c1", "No mortality reduction was observed.", relevance=0.84, overlap=0.8)]
    prosecutor = ProsecutorAnalysis(
        agent="prosecutor",
        analysis="Challenge",
        stance="skeptical",
        contradicting_evidence=["c1"],
        confidence=0.74,
    )
    return _success_response(
        claim,
        Verdict.CONTRADICTS,
        0.81,
        evidence,
        prosecutor=prosecutor,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.CONTRADICTED,
                    0.79,
                    ["c1"],
                )
            ]
        ),
        agent_agreement=False,
        adjudicator_verdict=Verdict.CONTRADICTS,
    )


def _insufficient_evidence() -> VerificationResponse:
    return VerificationResponse(
        status=VerificationStatus.INSUFFICIENT_EVIDENCE,
        claim="The dataset proves universal efficacy.",
        verdict=Verdict.INSUFFICIENT,
        confidence=0.0,
        summary="Insufficient evidence.",
        reasoning="Not enough evidence.",
        paper=PAPER,
        evidence=[],
        claim_traceability=_traceability(
            [
                (
                    "segment_1",
                    "The dataset proves universal efficacy.",
                    ClaimSegmentStatus.UNSUPPORTED,
                    0.0,
                    [],
                )
            ]
        ),
    )


def _fabricated_claim() -> VerificationResponse:
    claim = "The trial demonstrated a 95% cure rate."
    return _success_response(
        claim,
        Verdict.FABRICATED,
        0.72,
        [],
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.UNSUPPORTED,
                    0.05,
                    [],
                )
            ]
        ),
        validation_warnings=["The claim lacks adequate supporting evidence in the cited paper."],
    )


def _numeric_supports() -> VerificationResponse:
    claim = "The model achieved 94.2% accuracy."
    evidence = [
        _evidence(
            "c1",
            "The model achieved an accuracy of 94.2%.",
            relevance=0.9,
            overlap=0.88,
        )
    ]
    item = evidence[0].model_copy(update={"numeric_overlap": 1.0, "evidence_numbers": ["94.2%"]})
    return _success_response(
        claim,
        Verdict.SUPPORTS,
        0.88,
        [item],
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.SUPPORTED,
                    0.9,
                    ["c1"],
                )
            ]
        ),
    )


def _universal_overstated() -> VerificationResponse:
    claim = "The therapy improves survival across all subgroups."
    evidence = [_evidence("c1", "Survival improved in one predefined subgroup.", relevance=0.7, overlap=0.55)]
    return _success_response(
        claim,
        Verdict.OVERSTATED,
        0.76,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    "The therapy improves survival",
                    ClaimSegmentStatus.PARTIALLY_SUPPORTED,
                    0.58,
                    ["c1"],
                ),
                (
                    "segment_2",
                    "across all subgroups",
                    ClaimSegmentStatus.UNSUPPORTED,
                    0.12,
                    [],
                ),
            ]
        ),
    )


def _weak_insufficient() -> VerificationResponse:
    claim = "The compound fully eliminates tumors in every model."
    evidence = [_evidence("c1", "Tumor volume decreased in one model.", relevance=0.22, overlap=0.18)]
    return _success_response(
        claim,
        Verdict.INSUFFICIENT,
        0.41,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.UNSUPPORTED,
                    0.15,
                    [],
                )
            ]
        ),
        adjudicator_verdict=Verdict.INSUFFICIENT,
    )


def _mechanism_supports() -> VerificationResponse:
    claim = "RNA interference can silence target genes."
    evidence = [_evidence("c1", "RNA interference silences target genes in vitro.", relevance=0.87, overlap=0.84)]
    return _success_response(
        claim,
        Verdict.SUPPORTS,
        0.85,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.SUPPORTED,
                    0.86,
                    ["c1"],
                )
            ]
        ),
    )


def _direction_contradicts() -> VerificationResponse:
    claim = "Expression of the gene increases under stress."
    evidence = [_evidence("c1", "Expression decreased under stress conditions.", relevance=0.83, overlap=0.79)]
    return _success_response(
        claim,
        Verdict.CONTRADICTS,
        0.8,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.CONTRADICTED,
                    0.77,
                    ["c1"],
                )
            ]
        ),
        adjudicator_verdict=Verdict.CONTRADICTS,
    )


def _magnitude_overstated() -> VerificationResponse:
    claim = "Productivity improved by 50%."
    evidence = [_evidence("c1", "Productivity improved by 12%.", relevance=0.8, overlap=0.7)]
    return _success_response(
        claim,
        Verdict.OVERSTATED,
        0.77,
        evidence,
        traceability=_traceability(
            [
                (
                    "segment_1",
                    claim,
                    ClaimSegmentStatus.PARTIALLY_SUPPORTED,
                    0.6,
                    ["c1"],
                )
            ]
        ),
    )


def _legacy_no_traceability() -> VerificationResponse:
    claim = "Sample preparation improved reproducibility."
    evidence = [_evidence("c1", "Sample preparation improved reproducibility in the protocol.", relevance=0.8, overlap=0.78)]
    return _success_response(
        claim,
        Verdict.SUPPORTS,
        0.82,
        evidence,
        traceability=None,
        agent_agreement=None,
    )


def _success_response(
    claim: str,
    verdict: Verdict,
    confidence: float,
    evidence: list[EvidenceItem],
    *,
    traceability: ClaimTraceability | None,
    agent_agreement: bool | None = True,
    adjudicator_verdict: Verdict | None = None,
    prosecutor: ProsecutorAnalysis | None = None,
    validation_warnings: list[str] | None = None,
) -> VerificationResponse:
    final_verdict = verdict
    adjudicator = AdjudicatorAnalysis(
        agent="adjudicator",
        analysis="Benchmark adjudicator analysis.",
        verdict=adjudicator_verdict or verdict,
        confidence=confidence,
        reasoning="Benchmark reasoning.",
        supporting_evidence=[item.chunk_id for item in evidence[:1]],
        contradicting_evidence=[],
    )
    if adjudicator_verdict and adjudicator_verdict != final_verdict:
        validation_warnings = validation_warnings or ["Verdict adjusted during validation."]

    return VerificationResponse(
        status=VerificationStatus.SUCCESS,
        claim=claim,
        verdict=final_verdict,
        confidence=confidence,
        summary="Benchmark summary.",
        reasoning="Benchmark reasoning.",
        paper=PAPER,
        evidence=evidence,
        prosecutor=prosecutor
        or ProsecutorAnalysis(
            agent="prosecutor",
            analysis="Benchmark prosecutor analysis.",
            stance="neutral",
            confidence=0.65,
        ),
        defender=DefenderAnalysis(
            agent="defender",
            analysis="Benchmark defender analysis.",
            stance="supportive",
            supporting_evidence=[item.chunk_id for item in evidence[:1]],
            confidence=0.7,
        ),
        adjudicator=adjudicator,
        agent_agreement=agent_agreement,
        validation_warnings=validation_warnings,
        claim_traceability=traceability,
    )
