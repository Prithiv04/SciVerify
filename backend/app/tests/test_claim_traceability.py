from __future__ import annotations

from app.schemas.evidence import EvidenceItem
from app.schemas.verification import (
    AdjudicatorAnalysis,
    ClaimSegmentStatus,
    ProsecutorAnalysis,
    Verdict,
)
from app.services.claim_traceability import build_claim_traceability
from app.utils.claim_segmenter import segment_claim


def _evidence(
    chunk_id: str,
    text: str,
    *,
    relevance: float = 0.8,
    claim_overlap: float = 0.7,
    numeric_overlap: float = 0.0,
    evidence_numbers: list[str] | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        chunk_id=chunk_id,
        section="Results",
        chunk_index=0,
        text=text,
        relevance_score=relevance,
        claim_overlap=claim_overlap,
        numeric_overlap=numeric_overlap,
        evidence_numbers=evidence_numbers or [],
    )


CAS9_CLAIM = (
    "Cas9 can be programmed with guide RNA to cleave specific "
    "double-stranded DNA target sequences."
)


class TestClaimSegmenter:
    def test_multi_segment_claim(self) -> None:
        segments = segment_claim(CAS9_CLAIM)
        assert len(segments) >= 2
        assert "Cas9" in segments[0]
        assert any("cleave" in segment for segment in segments)


class TestClaimTraceability:
    def test_single_segment_claim_with_strong_evidence(self) -> None:
        claim = "The model achieved 94.2% accuracy."
        evidence = [
            _evidence(
                "c1",
                "The model achieved an accuracy of 94.2% on the benchmark.",
                claim_overlap=0.9,
                numeric_overlap=1.0,
                evidence_numbers=["94.2%"],
            )
        ]
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        assert len(result.segments) == 1
        assert result.segments[0].status == ClaimSegmentStatus.SUPPORTED
        assert result.segments[0].evidence_ids == ["c1"]
        assert result.overall_coverage >= 0.65

    def test_multi_segment_cas9_claim(self) -> None:
        evidence = [
            _evidence(
                "c1",
                "Cas9 can be programmed with guide RNA in vitro.",
                claim_overlap=0.82,
            ),
            _evidence(
                "c2",
                "Cas9 introduces double-stranded breaks at specific DNA target sequences.",
                claim_overlap=0.78,
            ),
        ]
        result = build_claim_traceability(
            CAS9_CLAIM,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        assert len(result.segments) >= 2
        assert result.overall_coverage > 0

    def test_partially_supported_segment(self) -> None:
        claim = "The treatment improves survival and eliminates all side effects."
        evidence = [
            _evidence(
                "c1",
                "The treatment improved survival in the trial cohort.",
                claim_overlap=0.55,
                relevance=0.6,
            )
        ]
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.OVERSTATED,
        )

        assert result is not None
        statuses = {segment.status for segment in result.segments}
        assert ClaimSegmentStatus.PARTIALLY_SUPPORTED in statuses or ClaimSegmentStatus.UNSUPPORTED in statuses

    def test_unsupported_segment_without_evidence(self) -> None:
        result = build_claim_traceability(
            "Unknown compound cures all diseases instantly.",
            [],
            verdict=Verdict.INSUFFICIENT,
        )

        assert result is not None
        assert all(
            segment.status == ClaimSegmentStatus.UNSUPPORTED for segment in result.segments
        )
        assert result.overall_coverage == 0.0

    def test_contradicted_segment_uses_agent_contradicting_ids(self) -> None:
        claim = "The treatment reduces mortality."
        evidence = [
            _evidence(
                "c1",
                "No mortality reduction was observed in the treatment arm.",
                claim_overlap=0.72,
            )
        ]
        adjudicator = AdjudicatorAnalysis(
            agent="adjudicator",
            analysis="Final",
            verdict=Verdict.CONTRADICTS,
            confidence=0.8,
            reasoning="Evidence conflicts with the claim.",
            contradicting_evidence=["c1"],
        )
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.CONTRADICTS,
            adjudicator=adjudicator,
        )

        assert result is not None
        assert any(
            segment.status == ClaimSegmentStatus.CONTRADICTED for segment in result.segments
        )

    def test_numeric_claim_matching(self) -> None:
        claim = "Accuracy improved by 12%."
        evidence = [
            _evidence(
                "c1",
                "Accuracy improved by 12% relative to baseline.",
                claim_overlap=0.7,
                numeric_overlap=1.0,
                evidence_numbers=["12%"],
            )
        ]
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        assert result.segments[0].evidence_ids == ["c1"]

    def test_evidence_ids_preserved(self) -> None:
        evidence = [
            _evidence("alpha", "Cas9 uses guide RNA for DNA cleavage.", claim_overlap=0.8),
            _evidence("beta", "Target DNA sequences are cleaved by Cas9.", claim_overlap=0.75),
        ]
        result = build_claim_traceability(
            CAS9_CLAIM,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        linked = {chunk_id for segment in result.segments for chunk_id in segment.evidence_ids}
        assert linked.issubset({"alpha", "beta"})

    def test_overall_coverage_calculation(self) -> None:
        evidence = [
            _evidence("c1", "Cas9 can be programmed with guide RNA.", claim_overlap=0.9),
            _evidence("c2", "Cas9 cleaves double-stranded DNA target sequences.", claim_overlap=0.85),
        ]
        result = build_claim_traceability(
            CAS9_CLAIM,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        expected = sum(segment.coverage_score for segment in result.segments) / len(
            result.segments
        )
        assert result.overall_coverage == round(min(1.0, max(0.0, expected)), 4)

    def test_supports_verdict_warning_when_segment_unsupported(self) -> None:
        claim = "Accuracy improved and cured every disease."
        evidence = [
            _evidence("c1", "Accuracy improved in the benchmark.", claim_overlap=0.7),
        ]
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.SUPPORTS,
        )

        assert result is not None
        assert any("not directly supported" in warning for warning in result.warnings)

    def test_insufficient_verdict_warning(self) -> None:
        result = build_claim_traceability(
            CAS9_CLAIM,
            [],
            verdict=Verdict.INSUFFICIENT,
        )

        assert result is not None
        assert any("insufficient" in warning.lower() for warning in result.warnings)

    def test_overstated_verdict_warning(self) -> None:
        evidence = [
            _evidence("c1", "Cas9 uses RNA guides.", claim_overlap=0.55, relevance=0.5),
        ]
        result = build_claim_traceability(
            CAS9_CLAIM,
            evidence,
            verdict=Verdict.OVERSTATED,
        )

        assert result is not None
        assert result.warnings

    def test_contradicts_verdict_warning(self) -> None:
        evidence = [
            _evidence("c1", "Cas9 did not cleave the tested DNA target.", claim_overlap=0.7),
        ]
        adjudicator = AdjudicatorAnalysis(
            agent="adjudicator",
            analysis="Final",
            verdict=Verdict.CONTRADICTS,
            confidence=0.8,
            reasoning="Conflict",
            contradicting_evidence=["c1"],
        )
        result = build_claim_traceability(
            CAS9_CLAIM,
            evidence,
            verdict=Verdict.CONTRADICTS,
            adjudicator=adjudicator,
        )

        assert result is not None
        assert any("contradict" in warning.lower() for warning in result.warnings)

    def test_no_llm_calls_are_required(self) -> None:
        result = build_claim_traceability(
            CAS9_CLAIM,
            [_evidence("c1", "Cas9 guide RNA DNA cleavage.", claim_overlap=0.8)],
            verdict=Verdict.SUPPORTS,
        )
        assert result is not None

    def test_backward_compatibility_when_traceability_absent(self) -> None:
        assert build_claim_traceability("   ", [], verdict=Verdict.INSUFFICIENT) is None

    def test_prosecutor_contradicting_ids_can_mark_segment(self) -> None:
        claim = "The drug reduces inflammation."
        evidence = [
            _evidence(
                "c1",
                "Inflammation markers increased in treated subjects.",
                claim_overlap=0.68,
            )
        ]
        prosecutor = ProsecutorAnalysis(
            agent="prosecutor",
            analysis="Challenge",
            stance="skeptical",
            contradicting_evidence=["c1"],
            confidence=0.7,
        )
        result = build_claim_traceability(
            claim,
            evidence,
            verdict=Verdict.CONTRADICTS,
            prosecutor=prosecutor,
        )

        assert result is not None
        assert result.segments[0].evidence_ids == ["c1"]
