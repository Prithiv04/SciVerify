from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from app.schemas.citation import CitationMetadata
from app.schemas.paper import (
    PaperMetadata,
    PaperRetrievalStatus,
    PaperSource,
    RetrievePaperResponse,
)
from app.services.citation_resolver import (
    CitationNotFoundError,
    CitationResolverError,
    OPENALEX_API_URL,
    USER_AGENT,
    resolve_doi,
)
from app.services.document_parser import DocumentParseError, parse_document
from app.services.document_retriever import (
    DocumentRetrievalError,
    RetrievedDocument,
    retrieve_document,
)
from app.services.evidence_chunker import chunk_sections
from app.utils.doi import normalize_doi

logger = logging.getLogger(__name__)

DocumentFormat = Literal["pdf", "html"]

_PMC_ARTICLE_PATTERN = re.compile(
    r"(?:pmc\.ncbi\.nlm\.nih\.gov|ncbi\.nlm\.nih\.gov/pmc|europepmc\.org/pmc)/articles/(?:PMC)?(\d+)",
    re.IGNORECASE,
)
_KNOWN_OA_REPOSITORY_HOSTS = (
    "europepmc.org",
    "escholarship.org",
    "pubmedcentral.nih.gov",
    "ncbi.nlm.nih.gov/pmc",
    "pmc.ncbi.nlm.nih.gov",
)


class PaperNotFoundError(Exception):
    """Raised when a paper cannot be found."""


class PaperProviderError(Exception):
    """Raised when an external provider fails unexpectedly."""


class FullTextUnavailableError(Exception):
    """Raised when metadata exists but accessible full text is unavailable."""


class DocumentRetrievalFailure(PaperProviderError):
    """Raised when full-text download fails."""


@dataclass(frozen=True)
class FullTextCandidate:
    url: str
    format: DocumentFormat
    provider: str


def retrieve_paper(
    doi: str,
    client: httpx.Client | None = None,
) -> RetrievePaperResponse:
    """Retrieve paper metadata and, when available, parsed evidence chunks."""
    normalized = normalize_doi(doi)
    owns_client = client is None
    http_client = client or httpx.Client(
        timeout=30.0,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )

    try:
        try:
            citation = resolve_doi(normalized, client=http_client)
        except CitationNotFoundError as exc:
            raise PaperNotFoundError(str(exc)) from exc
        except CitationResolverError as exc:
            raise PaperProviderError(str(exc)) from exc

        openalex_work: dict[str, Any] | None = None
        provider_error: PaperProviderError | None = None
        try:
            openalex_work = _fetch_openalex_work(normalized, http_client)
        except PaperProviderError as exc:
            provider_error = exc

        paper = _build_paper_metadata(citation, openalex_work)
        source = _build_source(citation, openalex_work)

        if provider_error is not None and openalex_work is None:
            return RetrievePaperResponse(
                status=PaperRetrievalStatus.METADATA_ONLY,
                paper=paper,
                sections=[],
                chunks=[],
                source=source,
            )

        candidates = (
            discover_full_text_candidates(openalex_work)
            if openalex_work is not None
            else []
        )
        if not candidates:
            paper.full_text_available = False
            return RetrievePaperResponse(
                status=PaperRetrievalStatus.FULL_TEXT_UNAVAILABLE,
                paper=paper,
                sections=[],
                chunks=[],
                source=source,
            )

        last_detail: str | None = None
        for candidate in candidates:
            logger.info(
                "Trying full-text candidate: url=%s format=%s provider=%s",
                candidate.url,
                candidate.format,
                candidate.provider,
            )
            paper.full_text_available = True
            paper.full_text_format = candidate.format
            paper.full_text_url = candidate.url

            try:
                document = retrieve_document(
                    candidate.url,
                    expected_format=candidate.format,
                    client=http_client,
                )
            except DocumentRetrievalError as exc:
                last_detail = str(exc)
                logger.warning(
                    "Full-text candidate rejected: url=%s reason=%s",
                    candidate.url,
                    last_detail,
                )
                continue

            try:
                sections = parse_document(
                    content=document.content,
                    doc_format=document.format,
                    text=document.text,
                )
            except DocumentParseError as exc:
                last_detail = exc.message
                logger.warning(
                    "Full-text candidate parsing failed: url=%s reason=%s",
                    candidate.url,
                    last_detail,
                )
                continue

            chunks = chunk_sections(
                sections=sections,
                paper_id=paper.paper_id,
                source_url=document.source_url,
            )
            if not chunks:
                last_detail = "Paper retrieved but no evidence chunks were produced."
                logger.warning(
                    "Full-text candidate produced no chunks: url=%s",
                    candidate.url,
                )
                continue

            return RetrievePaperResponse(
                status=PaperRetrievalStatus.SUCCESS,
                paper=paper,
                sections=sections,
                chunks=chunks,
                source=PaperSource(
                    url=document.source_url,
                    provider=candidate.provider,
                ),
            )

        paper.full_text_available = False
        paper.full_text_format = candidates[0].format
        paper.full_text_url = candidates[0].url
        return RetrievePaperResponse(
            status=PaperRetrievalStatus.FULL_TEXT_UNAVAILABLE,
            paper=paper,
            sections=[],
            chunks=[],
            source=source,
            detail=last_detail or "Full text is unavailable for evidence retrieval.",
        )
    finally:
        if owns_client:
            http_client.close()


def _parsing_failure_response(
    *,
    paper: PaperMetadata,
    document: RetrievedDocument,
    full_text: FullTextCandidate,
    detail: str,
) -> RetrievePaperResponse:
    """Return a structured parsing-failure response after a successful download."""
    paper.full_text_available = True
    paper.full_text_format = full_text.format
    paper.full_text_url = full_text.url

    return RetrievePaperResponse(
        status=PaperRetrievalStatus.PARSING_FAILURE,
        paper=paper,
        sections=[],
        chunks=[],
        source=PaperSource(
            url=document.source_url,
            provider=full_text.provider,
        ),
        detail=detail,
    )


def discover_full_text(openalex_work: dict[str, Any]) -> FullTextCandidate | None:
    """Discover the best publicly accessible full-text source."""
    candidates = discover_full_text_candidates(openalex_work)
    if not candidates:
        return None
    for candidate in candidates:
        if candidate.format == "pdf":
            return candidate
    return candidates[0]


def discover_full_text_candidates(openalex_work: dict[str, Any]) -> list[FullTextCandidate]:
    """Discover ordered publicly accessible full-text sources."""
    candidates: list[FullTextCandidate] = []
    open_access = openalex_work.get("open_access")
    work_is_oa = (
        isinstance(open_access, dict) and open_access.get("is_oa") is True
    )

    def add_candidate(url: str, doc_format: DocumentFormat, provider: str) -> None:
        normalized_url = url.strip()
        if normalized_url:
            candidates.append(
                FullTextCandidate(
                    url=normalized_url,
                    format=doc_format,
                    provider=provider,
                )
            )

    def add_location(location: dict[str, Any] | None, provider: str) -> None:
        if not isinstance(location, dict):
            return

        pdf_url = location.get("pdf_url")
        if isinstance(pdf_url, str) and pdf_url.strip():
            add_candidate(pdf_url, "pdf", provider)

        oa_url = location.get("oa_url")
        if isinstance(oa_url, str) and oa_url.strip():
            add_candidate(oa_url, _format_from_url(oa_url), provider)

        is_oa = location.get("is_oa")
        landing_page_url = location.get("landing_page_url")
        if isinstance(landing_page_url, str) and landing_page_url.strip():
            if is_oa is True or (
                work_is_oa and _is_known_oa_repository(landing_page_url)
            ):
                add_candidate(
                    landing_page_url,
                    _format_from_url(landing_page_url),
                    provider,
                )

    add_location(openalex_work.get("best_oa_location"), "openalex")
    add_location(openalex_work.get("primary_location"), "openalex")

    locations = openalex_work.get("locations")
    if isinstance(locations, list):
        for location in locations:
            if isinstance(location, dict):
                add_location(location, "openalex")

    if isinstance(open_access, dict):
        work_oa_url = open_access.get("oa_url")
        if isinstance(work_oa_url, str) and work_oa_url.strip():
            add_candidate(work_oa_url, _format_from_url(work_oa_url), "openalex")

    deduped = _dedupe_candidates(candidates)
    expanded = _expand_candidate_mirrors(deduped)
    return _order_candidates(_dedupe_candidates(expanded))


def _format_from_url(url: str) -> DocumentFormat:
    return "pdf" if url.lower().endswith(".pdf") else "html"


def _is_known_oa_repository(url: str) -> bool:
    lowered = url.lower()
    return any(host in lowered for host in _KNOWN_OA_REPOSITORY_HOSTS)


def _dedupe_candidates(candidates: list[FullTextCandidate]) -> list[FullTextCandidate]:
    deduped: list[FullTextCandidate] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        if candidate.url in seen_urls:
            continue
        seen_urls.add(candidate.url)
        deduped.append(candidate)
    return deduped


def _order_candidates(candidates: list[FullTextCandidate]) -> list[FullTextCandidate]:
    pdfs = [candidate for candidate in candidates if candidate.format == "pdf"]
    html = [candidate for candidate in candidates if candidate.format == "html"]
    return pdfs + html


def _pmc_pdf_url_from_html(url: str) -> str | None:
    match = _PMC_ARTICLE_PATTERN.search(url)
    if match is None:
        return None
    pmc_id = match.group(1)
    normalized_id = pmc_id if pmc_id.upper().startswith("PMC") else f"PMC{pmc_id}"
    return f"https://pmc.ncbi.nlm.nih.gov/articles/{normalized_id}/pdf/"


def _europe_pmc_url_from_pmc_html(url: str) -> str | None:
    match = _PMC_ARTICLE_PATTERN.search(url)
    if match is None:
        return None
    pmc_id = match.group(1)
    normalized_id = pmc_id if pmc_id.upper().startswith("PMC") else f"PMC{pmc_id}"
    return f"https://europepmc.org/articles/{normalized_id}"


def _expand_candidate_mirrors(
    candidates: list[FullTextCandidate],
) -> list[FullTextCandidate]:
    expanded = list(candidates)
    for candidate in candidates:
        if candidate.format != "html" or "pmc" not in candidate.url.lower():
            continue

        pdf_url = _pmc_pdf_url_from_html(candidate.url)
        if pdf_url is not None:
            expanded.insert(
                0,
                FullTextCandidate(url=pdf_url, format="pdf", provider="pmc"),
            )

        europe_pmc_url = _europe_pmc_url_from_pmc_html(candidate.url)
        if europe_pmc_url is not None:
            expanded.append(
                FullTextCandidate(
                    url=europe_pmc_url,
                    format="html",
                    provider="europepmc",
                )
            )
    return expanded


def _fetch_openalex_work(doi: str, client: httpx.Client) -> dict[str, Any]:
    url = f"{OPENALEX_API_URL}/works/https://doi.org/{doi}"
    try:
        response = client.get(url)
    except httpx.TimeoutException as exc:
        raise PaperProviderError("OpenAlex request timed out.") from exc
    except httpx.RequestError as exc:
        raise PaperProviderError("OpenAlex request failed.") from exc

    if response.status_code == 404:
        raise PaperNotFoundError(f"Paper not found for DOI: {doi}")

    if response.status_code >= 500:
        raise PaperProviderError("OpenAlex service is unavailable.")

    if response.status_code >= 400:
        raise PaperProviderError("OpenAlex rejected the request.")

    try:
        payload = response.json()
    except ValueError as exc:
        raise PaperProviderError("OpenAlex returned invalid JSON.") from exc

    if not isinstance(payload, dict) or not payload.get("id"):
        raise PaperProviderError("OpenAlex returned an unexpected response.")

    return payload


def _build_paper_metadata(
    citation: CitationMetadata,
    openalex_work: dict[str, Any] | None,
) -> PaperMetadata:
    abstract = None
    publication_date = None
    open_access = None
    source_url = citation.url

    if openalex_work is not None:
        abstract = _extract_openalex_abstract(openalex_work)
        publication_date = openalex_work.get("publication_date")
        if not isinstance(publication_date, str):
            publication_date = None

        open_access_info = openalex_work.get("open_access")
        if isinstance(open_access_info, dict):
            open_access = open_access_info.get("is_oa")

        primary_location = openalex_work.get("primary_location")
        if isinstance(primary_location, dict):
            landing_page = primary_location.get("landing_page_url")
            if isinstance(landing_page, str) and landing_page.strip():
                source_url = landing_page.strip()

    return PaperMetadata(
        paper_id=citation.doi,
        doi=citation.doi,
        title=citation.title,
        authors=citation.authors,
        abstract=abstract,
        journal=citation.journal,
        publisher=citation.publisher,
        publication_date=publication_date,
        year=citation.year,
        url=citation.url,
        source_url=source_url,
        open_access=open_access if isinstance(open_access, bool) else None,
        full_text_available=False,
        full_text_format=None,
        full_text_url=None,
    )


def _build_source(
    citation: CitationMetadata,
    openalex_work: dict[str, Any] | None,
) -> PaperSource:
    if openalex_work is not None:
        openalex_id = openalex_work.get("id")
        if isinstance(openalex_id, str) and openalex_id.strip():
            return PaperSource(url=openalex_id.strip(), provider="openalex")
    return PaperSource(url=citation.url, provider=citation.source)


def _extract_openalex_abstract(work: dict[str, Any]) -> str | None:
    abstract = work.get("abstract")
    if isinstance(abstract, str) and abstract.strip():
        return abstract.strip()

    inverted_index = work.get("abstract_inverted_index")
    if not isinstance(inverted_index, dict):
        return None

    max_index = -1
    for positions in inverted_index.values():
        if isinstance(positions, list) and positions:
            max_index = max(max_index, max(pos for pos in positions if isinstance(pos, int)))

    if max_index < 0:
        return None

    words = [""] * (max_index + 1)
    for word, positions in inverted_index.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int) and 0 <= position <= max_index:
                words[position] = word

    reconstructed = " ".join(word for word in words if word).strip()
    return reconstructed or None


__all__ = [
    "DocumentRetrievalFailure",
    "FullTextCandidate",
    "FullTextUnavailableError",
    "PaperNotFoundError",
    "PaperProviderError",
    "discover_full_text",
    "discover_full_text_candidates",
    "retrieve_paper",
]
