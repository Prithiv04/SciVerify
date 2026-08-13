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

        assert len(ranked) == 1
        assert ranked[0].chunk_id == "c1"

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

    def test_duplicate_evidence_text_keeps_highest_score(self) -> None:
        claim = preprocess_claim("Cas9 can be directed by RNA to cleave DNA.")
        shared_text = (
            "Cas9 can be directed by RNA to introduce site-specific "
            "double-stranded breaks in target DNA."
        )
        chunks = [
            _chunk("permalink:63", "PERMALINK", shared_text, 63),
            _chunk("permalink:90", "PERMALINK", shared_text, 90),
            _chunk("results:1", "Results", shared_text + " Additional context.", 1),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert len(ranked) == 2
        assert ranked[0].chunk_id == "results:1"
        assert all(
            item.text
            != ranked[1].text
            or item.chunk_id == ranked[1].chunk_id
            for item in ranked
        )
        permalink_items = [item for item in ranked if item.chunk_id.startswith("permalink:")]
        assert len(permalink_items) == 1
        assert permalink_items[0].chunk_id == "permalink:63"

    def test_valid_distinct_evidence_is_preserved(self) -> None:
        claim = preprocess_claim("Cas9 RNA DNA cleavage")
        chunks = [
            _chunk("c1", "Abstract", "Cas9 uses RNA guides for DNA cleavage.", 0),
            _chunk("c2", "Results", "The endonuclease introduces double-stranded breaks.", 1),
        ]

        ranked = rank_evidence_for_claim(claim, chunks, min_relevance=0.0)

        assert len(ranked) == 2
        assert {item.chunk_id for item in ranked} == {"c1", "c2"}

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
