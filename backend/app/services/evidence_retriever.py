from __future__ import annotations

from dataclasses import dataclass

from app.config import EVIDENCE_MIN_RELEVANCE, EVIDENCE_TOP_K
from app.schemas.evidence import EvidenceItem
from app.schemas.paper import EvidenceChunk
from app.utils.claim_preprocessor import ProcessedClaim, _extract_numbers, _normalize_claim_text

# Section weights influence ranking only — they do not determine correctness.
SECTION_WEIGHTS: dict[str, float] = {
    "results": 1.0,
    "findings": 1.0,
    "experiments": 0.95,
    "experimental results": 0.95,
    "methods": 0.85,
    "materials and methods": 0.85,
    "methodology": 0.85,
    "abstract": 0.75,
    "discussion": 0.7,
    "conclusion": 0.65,
    "conclusions": 0.65,
    "limitations": 0.6,
    "introduction": 0.6,
    "background": 0.55,
    "body": 0.5,
    "references": 0.2,
}

DEFAULT_SECTION_WEIGHT = 0.5

TOKEN_WEIGHT = 0.50
PHRASE_WEIGHT = 0.25
NUMERIC_WEIGHT = 0.15
SECTION_WEIGHT = 0.10


@dataclass(frozen=True)
class RankedEvidence:
    item: EvidenceItem
    sort_key: tuple[float, float, int, str]


def rank_evidence_for_claim(
    claim: ProcessedClaim,
    chunks: list[EvidenceChunk],
    *,
    top_k: int | None = None,
    min_relevance: float | None = None,
) -> list[EvidenceItem]:
    """Rank paper chunks against a processed claim."""
    effective_top_k = top_k if top_k is not None else EVIDENCE_TOP_K
    effective_min_relevance = (
        min_relevance if min_relevance is not None else EVIDENCE_MIN_RELEVANCE
    )

    deduped_chunks = _dedupe_chunks(chunks)
    ranked: list[RankedEvidence] = []

    for chunk in deduped_chunks:
        item = _score_chunk(claim, chunk)
        ranked.append(
            RankedEvidence(
                item=item,
                sort_key=(
                    -item.relevance_score,
                    -item.claim_overlap,
                    chunk.chunk_index,
                    chunk.chunk_id,
                ),
            )
        )

    ranked.sort(key=lambda entry: entry.sort_key)

    filtered = [
        entry.item
        for entry in ranked
        if entry.item.relevance_score >= effective_min_relevance
    ]

    if not filtered and ranked:
        return []

    return filtered[:effective_top_k]


def _score_chunk(claim: ProcessedClaim, chunk: EvidenceChunk) -> EvidenceItem:
    chunk_normalized = _normalize_claim_text(chunk.text)
    chunk_tokens = set(_tokenize(chunk_normalized))
    claim_tokens = set(claim.tokens)

    claim_overlap = _claim_overlap_score(claim_tokens, chunk_tokens)
    phrase_overlap = _phrase_overlap_score(claim.normalized, chunk_normalized)
    evidence_numbers = tuple(_extract_numbers(chunk.text))
    numeric_overlap = _numeric_overlap_score(claim.claim_numbers, evidence_numbers)
    section_weight = _section_weight(chunk.section)

    relevance_score = _clamp(
        TOKEN_WEIGHT * claim_overlap
        + PHRASE_WEIGHT * phrase_overlap
        + NUMERIC_WEIGHT * numeric_overlap
        + SECTION_WEIGHT * section_weight
    )

    return EvidenceItem(
        chunk_id=chunk.chunk_id,
        section=chunk.section or "Unknown",
        chunk_index=chunk.chunk_index,
        text=chunk.text,
        relevance_score=relevance_score,
        claim_overlap=_clamp(claim_overlap),
        numeric_overlap=_clamp(numeric_overlap),
        claim_numbers=list(claim.claim_numbers),
        evidence_numbers=list(evidence_numbers),
        source_url=chunk.source_url,
        page=chunk.page,
    )


def _claim_overlap_score(claim_tokens: set[str], chunk_tokens: set[str]) -> float:
    if not claim_tokens:
        return 0.0
    overlap = claim_tokens.intersection(chunk_tokens)
    return len(overlap) / len(claim_tokens)


def _phrase_overlap_score(claim_normalized: str, chunk_normalized: str) -> float:
    claim_words = claim_normalized.split()
    if len(claim_words) < 2:
        return 0.0

    best = 0.0
    for size in (3, 2):
        if len(claim_words) < size:
            continue
        for index in range(len(claim_words) - size + 1):
            phrase = " ".join(claim_words[index : index + size])
            if phrase and phrase in chunk_normalized:
                best = max(best, size / len(claim_words))
    return _clamp(best)


def _numeric_overlap_score(
    claim_numbers: tuple[str, ...],
    evidence_numbers: tuple[str, ...],
) -> float:
    if not claim_numbers:
        return 1.0
    if not evidence_numbers:
        return 0.0

    claim_set = set(claim_numbers)
    evidence_set = set(evidence_numbers)
    if claim_set.intersection(evidence_set):
        return 1.0

    # Both sides contain numbers, but values differ — still topically relevant.
    return 0.5


def _section_weight(section: str | None) -> float:
    if not section:
        return DEFAULT_SECTION_WEIGHT
    return SECTION_WEIGHTS.get(section.strip().lower(), DEFAULT_SECTION_WEIGHT)


def _tokenize(normalized_text: str) -> list[str]:
    from app.utils.claim_preprocessor import STOPWORDS

    tokens: list[str] = []
    for raw_token in normalized_text.split():
        token = raw_token.strip(".")
        if len(token) < 2 or token in STOPWORDS or token.isdigit():
            continue
        tokens.append(token)
    return tokens


def _dedupe_chunks(chunks: list[EvidenceChunk]) -> list[EvidenceChunk]:
    seen_ids: set[str] = set()
    deduped: list[EvidenceChunk] = []
    for chunk in chunks:
        if chunk.chunk_id in seen_ids:
            continue
        seen_ids.add(chunk.chunk_id)
        deduped.append(chunk)
    return deduped


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)
