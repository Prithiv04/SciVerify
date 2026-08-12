from __future__ import annotations

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

DocumentFormat = Literal["pdf", "html"]


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

        full_text = (
            discover_full_text(openalex_work) if openalex_work is not None else None
        )
        if full_text is None:
            paper.full_text_available = False
            return RetrievePaperResponse(
                status=PaperRetrievalStatus.FULL_TEXT_UNAVAILABLE,
                paper=paper,
                sections=[],
                chunks=[],
                source=source,
            )

        paper.full_text_available = True
        paper.full_text_format = full_text.format
        paper.full_text_url = full_text.url

        try:
            document = retrieve_document(
                full_text.url,
                expected_format=full_text.format,
                client=http_client,
            )
        except DocumentRetrievalError as exc:
            paper.full_text_available = False
            paper.full_text_url = full_text.url
            raise DocumentRetrievalFailure(str(exc)) from exc

        try:
            sections = parse_document(
                content=document.content,
                doc_format=document.format,
                text=document.text,
            )
        except DocumentParseError as exc:
            return _parsing_failure_response(
                paper=paper,
                document=document,
                full_text=full_text,
                detail=exc.message,
            )

        chunks = chunk_sections(
            sections=sections,
            paper_id=paper.paper_id,
            source_url=document.source_url,
        )

        return RetrievePaperResponse(
            status=PaperRetrievalStatus.SUCCESS,
            paper=paper,
            sections=sections,
            chunks=chunks,
            source=PaperSource(
                url=document.source_url,
                provider=full_text.provider,
            ),
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
    candidates: list[FullTextCandidate] = []

    def add_location(location: dict[str, Any] | None, provider: str) -> None:
        if not isinstance(location, dict):
            return

        pdf_url = location.get("pdf_url")
        if isinstance(pdf_url, str) and pdf_url.strip():
            candidates.append(
                FullTextCandidate(
                    url=pdf_url.strip(),
                    format="pdf",
                    provider=provider,
                )
            )

        oa_url = location.get("oa_url")
        if isinstance(oa_url, str) and oa_url.strip():
            normalized_url = oa_url.strip()
            doc_format: DocumentFormat = (
                "pdf" if normalized_url.lower().endswith(".pdf") else "html"
            )
            candidates.append(
                FullTextCandidate(
                    url=normalized_url,
                    format=doc_format,
                    provider=provider,
                )
            )

    add_location(openalex_work.get("best_oa_location"), "openalex")
    add_location(openalex_work.get("primary_location"), "openalex")

    locations = openalex_work.get("locations")
    if isinstance(locations, list):
        for location in locations:
            if isinstance(location, dict):
                add_location(location, "openalex")

    deduped: list[FullTextCandidate] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        if candidate.url in seen_urls:
            continue
        seen_urls.add(candidate.url)
        deduped.append(candidate)

    for candidate in deduped:
        if candidate.format == "pdf":
            return candidate
    return deduped[0] if deduped else None


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
    "retrieve_paper",
]
