from __future__ import annotations

from app.schemas.paper import EvidenceChunk
from app.services.evidence_retriever import rank_evidence_for_claim
from app.utils.claim_preprocessor import preprocess_claim


def _chunk(
    chunk_id: str,
    section: str,
    text: str,
    chunk_index: int = 0,
) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        paper_id="10.1000/test",
        section=section,
        chunk_index=chunk_index,
        text=text,
        source_url="https://example.org/paper.pdf",
        page=4,
    )


class TestEvidenceRanking:
    def test_exact_phrase_match_ranks_highly(self) -> None:
        claim = preprocess_claim("The method improves accuracy by 40%.")
        chunks = [
            _chunk("c1", "Results", "The method improves accuracy by 12% on real tasks.", 0),
            _chunk("c2", "References", "Unrelated citation list.", 1),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].chunk_id == "c1"
        assert ranked[0].relevance_score > ranked[1].relevance_score

    def test_keyword_overlap(self) -> None:
        claim = preprocess_claim("accuracy improved on software development tasks")
        chunks = [
            _chunk("c1", "Results", "We measured accuracy on software development tasks.", 0),
            _chunk("c2", "Introduction", "This paper discusses unrelated biology.", 1),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].chunk_id == "c1"
        assert ranked[0].claim_overlap > ranked[1].claim_overlap

    def test_irrelevant_chunk_ranks_low(self) -> None:
        claim = preprocess_claim("accuracy improved by 40%")
        chunks = [
            _chunk("c1", "Results", "The weather was sunny during the experiments.", 0),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].relevance_score < 0.3

    def test_numeric_overlap_with_different_values(self) -> None:
        claim = preprocess_claim("The method improves accuracy by 40%.")
        chunks = [
            _chunk("c1", "Results", "The proposed method improves accuracy by 12%.", 0),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].numeric_overlap == 0.5
        assert ranked[0].claim_numbers == ["40%"]
        assert ranked[0].evidence_numbers == ["12%"]

    def test_numeric_claim_without_numeric_evidence(self) -> None:
        claim = preprocess_claim("The method improves accuracy by 40%.")
        chunks = [
            _chunk("c1", "Results", "The method improves accuracy on real tasks.", 0),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].numeric_overlap == 0.0

    def test_section_weighting(self) -> None:
        claim = preprocess_claim("accuracy improved")
        shared = "The experiment reports improved accuracy in the benchmark."
        chunks = [
            _chunk("c1", "Results", shared, 0),
            _chunk("c2", "References", shared, 1),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].chunk_id == "c1"
        assert ranked[0].relevance_score >= ranked[1].relevance_score

    def test_deterministic_ordering(self) -> None:
        claim = preprocess_claim("accuracy improved on software tasks")
        chunks = [
            _chunk("c1", "Results", "accuracy improved on software tasks significantly", 0),
            _chunk("c2", "Discussion", "accuracy improved on software tasks moderately", 1),
        ]

        first = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)
        second = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert [item.chunk_id for item in first] == [item.chunk_id for item in second]

    def test_scores_are_bounded(self) -> None:
        claim = preprocess_claim("accuracy improved by 40%")
        chunks = [
            _chunk("c1", "Results", "accuracy improved by 40% on software tasks", 0),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert 0.0 <= ranked[0].relevance_score <= 1.0
        assert 0.0 <= ranked[0].claim_overlap <= 1.0
        assert 0.0 <= ranked[0].numeric_overlap <= 1.0

    def test_duplicate_chunks_are_deduped(self) -> None:
        claim = preprocess_claim("accuracy improved")
        chunk = _chunk("c1", "Results", "accuracy improved on benchmark", 0)
        ranked = rank_evidence_for_claim(claim, [chunk, chunk], min_relevance=0.0)

        assert len(ranked) == 1

    def test_missing_section_and_page_are_preserved(self) -> None:
        claim = preprocess_claim("accuracy improved")
        chunks = [
            EvidenceChunk(
                chunk_id="c1",
                paper_id="10.1000/test",
                section="",
                chunk_index=0,
                text="accuracy improved in practice",
            )
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert ranked[0].section == "Unknown"
        assert ranked[0].page is None
        assert ranked[0].source_url is None
