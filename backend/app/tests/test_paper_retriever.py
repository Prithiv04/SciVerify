from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.schemas.citation import CitationMetadata
from app.schemas.paper import PaperRetrievalStatus
from app.services.paper_retriever import (
    PaperNotFoundError,
    PaperProviderError,
    discover_full_text,
    retrieve_paper,
)

CITATION = CitationMetadata(
    doi="10.1038/s41586-020-2649-2",
    title="Example Paper",
    authors=["Ada Lovelace"],
    journal="Nature",
    publisher="Nature Publishing Group",
    year=2020,
    url="https://doi.org/10.1038/s41586-020-2649-2",
    source="crossref",
    type="journal-article",
)

OPENALEX_WITH_PDF = {
    "id": "https://openalex.org/W123",
    "abstract_inverted_index": {
        "Example": [0],
        "abstract": [1],
        "text.": [2],
    },
    "publication_date": "2020-05-28",
    "open_access": {"is_oa": True},
    "best_oa_location": {
        "pdf_url": "https://example.org/paper.pdf",
        "oa_url": "https://example.org/paper.html",
    },
    "primary_location": {
        "landing_page_url": "https://example.org/landing",
    },
    "locations": [],
}

OPENALEX_NO_FULL_TEXT = {
    "id": "https://openalex.org/W456",
    "abstract_inverted_index": {"Metadata": [0], "only.": [1]},
    "publication_date": "2020-01-01",
    "open_access": {"is_oa": False},
    "best_oa_location": None,
    "primary_location": {"landing_page_url": "https://example.org/landing"},
    "locations": [],
}


class TestDiscoverFullText:
    def test_public_pdf_available(self) -> None:
        candidate = discover_full_text(OPENALEX_WITH_PDF)
        assert candidate is not None
        assert candidate.format == "pdf"
        assert candidate.url == "https://example.org/paper.pdf"

    def test_public_html_available(self) -> None:
        work = {
            **OPENALEX_NO_FULL_TEXT,
            "best_oa_location": {"oa_url": "https://example.org/paper.html"},
        }
        candidate = discover_full_text(work)
        assert candidate is not None
        assert candidate.format == "html"

    def test_no_full_text_available(self) -> None:
        assert discover_full_text(OPENALEX_NO_FULL_TEXT) is None


class TestRetrievePaper:
    @patch("app.services.paper_retriever.chunk_sections")
    @patch("app.services.paper_retriever.parse_document")
    @patch("app.services.paper_retriever.retrieve_document")
    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_successful_retrieval(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
        mock_retrieve: MagicMock,
        mock_parse: MagicMock,
        mock_chunk: MagicMock,
    ) -> None:
        mock_resolve.return_value = CITATION
        mock_openalex.return_value = OPENALEX_WITH_PDF
        mock_retrieve.return_value = MagicMock(
            content=b"%PDF-1.4",
            text=None,
            format="pdf",
            content_type="application/pdf",
            source_url="https://example.org/paper.pdf",
        )
        mock_parse.return_value = []
        mock_chunk.return_value = []

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.SUCCESS
        assert result.paper.full_text_available is True
        assert result.paper.abstract == "Example abstract text."

    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_metadata_only_when_openalex_enrichment_fails(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
    ) -> None:
        mock_resolve.return_value = CITATION
        mock_openalex.side_effect = PaperProviderError("OpenAlex unavailable.")

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.METADATA_ONLY
        assert result.paper.full_text_available is False
        assert result.sections == []

    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_full_text_unavailable(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
    ) -> None:
        mock_resolve.return_value = CITATION
        mock_openalex.return_value = OPENALEX_NO_FULL_TEXT

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.FULL_TEXT_UNAVAILABLE
        assert result.paper.full_text_available is False

    @patch("app.services.paper_retriever.resolve_doi")
    def test_paper_not_found(self, mock_resolve: MagicMock) -> None:
        from app.services.citation_resolver import CitationNotFoundError

        mock_resolve.side_effect = CitationNotFoundError("not found")

        with pytest.raises(PaperNotFoundError):
            retrieve_paper("10.1038/not-found", client=MagicMock())

    @patch("app.services.paper_retriever.retrieve_document")
    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_provider_failure_on_download(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
        mock_retrieve: MagicMock,
    ) -> None:
        from app.services.document_retriever import DocumentRetrievalError
        from app.services.paper_retriever import DocumentRetrievalFailure

        mock_resolve.return_value = CITATION
        mock_openalex.return_value = OPENALEX_WITH_PDF
        mock_retrieve.side_effect = DocumentRetrievalError("timeout")

        with pytest.raises(DocumentRetrievalFailure):
            retrieve_paper(CITATION.doi, client=MagicMock())

    @patch("app.services.paper_retriever.chunk_sections")
    @patch("app.services.paper_retriever.parse_document")
    @patch("app.services.paper_retriever.retrieve_document")
    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_parsing_failure(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
        mock_retrieve: MagicMock,
        mock_parse: MagicMock,
        mock_chunk: MagicMock,
    ) -> None:
        from app.services.document_parser import DocumentParseError

        mock_resolve.return_value = CITATION
        mock_openalex.return_value = OPENALEX_WITH_PDF
        mock_retrieve.return_value = MagicMock(
            content=b"%PDF-1.4",
            text=None,
            format="pdf",
            content_type="application/pdf",
            source_url="https://example.org/paper.pdf",
        )
        mock_parse.side_effect = DocumentParseError(
            "PDF document contains no extractable text.",
            reason="pdf_no_text",
        )
        mock_chunk.return_value = []

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.PARSING_FAILURE
        assert result.paper.full_text_available is True
        assert result.paper.full_text_format == "pdf"
        assert result.paper.full_text_url == "https://example.org/paper.pdf"
        assert result.sections == []
        assert result.chunks == []
        assert result.detail == "PDF document contains no extractable text."
        assert result.source.url == "https://example.org/paper.pdf"
        mock_chunk.assert_not_called()

    @patch("app.services.paper_retriever.chunk_sections")
    @patch("app.services.paper_retriever.parse_document")
    @patch("app.services.paper_retriever.retrieve_document")
    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_successful_pdf_parsing(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
        mock_retrieve: MagicMock,
        mock_parse: MagicMock,
        mock_chunk: MagicMock,
    ) -> None:
        from app.schemas.paper import DocumentSection, EvidenceChunk

        mock_resolve.return_value = CITATION
        mock_openalex.return_value = OPENALEX_WITH_PDF
        mock_retrieve.return_value = MagicMock(
            content=b"%PDF-1.4",
            text=None,
            format="pdf",
            content_type="application/pdf",
            source_url="https://example.org/paper.pdf",
        )
        mock_parse.return_value = [
            DocumentSection(section_name="Abstract", text="Findings.", order=0),
        ]
        mock_chunk.return_value = [
            EvidenceChunk(
                chunk_id="10.1038/s41586-020-2649-2:Abstract:0",
                paper_id=CITATION.doi,
                section="Abstract",
                chunk_index=0,
                text="Findings.",
            )
        ]

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.SUCCESS
        assert len(result.sections) == 1
        assert len(result.chunks) == 1
        assert result.detail is None

    @patch("app.services.paper_retriever.chunk_sections")
    @patch("app.services.paper_retriever.parse_document")
    @patch("app.services.paper_retriever.retrieve_document")
    @patch("app.services.paper_retriever._fetch_openalex_work")
    @patch("app.services.paper_retriever.resolve_doi")
    def test_successful_html_parsing(
        self,
        mock_resolve: MagicMock,
        mock_openalex: MagicMock,
        mock_retrieve: MagicMock,
        mock_parse: MagicMock,
        mock_chunk: MagicMock,
    ) -> None:
        work = {
            **OPENALEX_NO_FULL_TEXT,
            "best_oa_location": {"oa_url": "https://example.org/paper.html"},
        }
        mock_resolve.return_value = CITATION
        mock_openalex.return_value = work
        mock_retrieve.return_value = MagicMock(
            content=b"<html><body><p>Content</p></body></html>",
            text="<html><body><p>Content</p></body></html>",
            format="html",
            content_type="text/html",
            source_url="https://example.org/paper.html",
        )
        mock_parse.return_value = []
        mock_chunk.return_value = []

        result = retrieve_paper(CITATION.doi, client=MagicMock())

        assert result.status == PaperRetrievalStatus.SUCCESS
        assert result.paper.full_text_format == "html"


class TestOpenAlexFetch:
    @patch("httpx.Client.get")
    def test_malformed_openalex_response(self, mock_get: MagicMock) -> None:
        from app.services.paper_retriever import _fetch_openalex_work

        response = MagicMock(spec=httpx.Response)
        response.status_code = 200
        response.json.return_value = {"unexpected": True}
        mock_get.return_value = response

        with pytest.raises(PaperProviderError):
            _fetch_openalex_work("10.1038/example", httpx.Client())
