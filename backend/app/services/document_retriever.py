from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import httpx

from app.config import MAX_DOCUMENT_SIZE, PAPER_REQUEST_TIMEOUT
from app.services.citation_resolver import USER_AGENT

DocumentFormat = Literal["pdf", "html"]

PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}
HTML_CONTENT_TYPES = {
    "text/html",
    "application/xhtml+xml",
}


class DocumentRetrievalError(Exception):
    """Raised when a document cannot be retrieved."""


class UnsupportedContentTypeError(DocumentRetrievalError):
    """Raised when the response content type is not supported."""


class DocumentTooLargeError(DocumentRetrievalError):
    """Raised when a document exceeds the configured size limit."""


@dataclass(frozen=True)
class RetrievedDocument:
    content: bytes
    text: str | None
    format: DocumentFormat
    content_type: str
    source_url: str


def retrieve_document(
    url: str,
    expected_format: DocumentFormat | None = None,
    client: httpx.Client | None = None,
) -> RetrievedDocument:
    """Download an accessible PDF or HTML document."""
    owns_client = client is None
    http_client = client or httpx.Client(
        timeout=PAPER_REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )

    try:
        try:
            response = http_client.get(url)
        except httpx.TimeoutException as exc:
            raise DocumentRetrievalError("Document request timed out.") from exc
        except httpx.RequestError as exc:
            raise DocumentRetrievalError("Document request failed.") from exc

        if response.status_code >= 400:
            raise DocumentRetrievalError(
                f"Document request failed with status {response.status_code}."
            )

        content_type = _normalize_content_type(
            response.headers.get("content-type", "")
        )
        detected_format = _detect_format(content_type, url, expected_format)

        raw_content = _read_limited_content(response)
        _validate_downloaded_content(raw_content, detected_format, expected_format)
        text = raw_content.decode("utf-8", errors="replace") if detected_format == "html" else None

        return RetrievedDocument(
            content=raw_content,
            text=text,
            format=detected_format,
            content_type=content_type or detected_format,
            source_url=str(response.url),
        )
    finally:
        if owns_client:
            http_client.close()


def _read_limited_content(response: httpx.Response) -> bytes:
    content_length = response.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_DOCUMENT_SIZE:
                raise DocumentTooLargeError(
                    "Document exceeds the configured maximum size."
                )
        except ValueError:
            pass

    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > MAX_DOCUMENT_SIZE:
            raise DocumentTooLargeError(
                "Document exceeds the configured maximum size."
            )
        chunks.append(chunk)

    if not chunks:
        content = response.content
        if len(content) > MAX_DOCUMENT_SIZE:
            raise DocumentTooLargeError(
                "Document exceeds the configured maximum size."
            )
        return content

    return b"".join(chunks)


def _validate_downloaded_content(
    content: bytes,
    detected_format: DocumentFormat,
    expected_format: DocumentFormat | None,
) -> None:
    if not content:
        raise DocumentRetrievalError("Downloaded document is empty.")

    effective_format = expected_format or detected_format

    if effective_format == "pdf":
        if not content.startswith(b"%PDF"):
            raise DocumentRetrievalError(
                "Downloaded content is not a valid PDF document."
            )
        return

    if effective_format == "html":
        sample = content[:512].lstrip().lower()
        if sample.startswith(b"<!doctype html") or sample.startswith(b"<html"):
            return
        if b"<body" in sample or b"<p" in sample or b"<div" in sample:
            return
        raise DocumentRetrievalError(
            "Downloaded content is not a valid HTML document."
        )


def _normalize_content_type(value: str) -> str:
    return value.split(";", 1)[0].strip().lower()


def _detect_format(
    content_type: str,
    url: str,
    expected_format: DocumentFormat | None,
) -> DocumentFormat:
    if expected_format is not None:
        return expected_format

    if content_type in PDF_CONTENT_TYPES or url.lower().endswith(".pdf"):
        return "pdf"

    if content_type in HTML_CONTENT_TYPES or url.lower().endswith((".html", ".htm")):
        return "html"

    raise UnsupportedContentTypeError(
        f"Unsupported document content type: {content_type or 'unknown'}"
    )
