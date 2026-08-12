from __future__ import annotations

import re
from io import BytesIO
from typing import Literal

from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.schemas.paper import DocumentSection
from app.utils.text_cleaner import clean_section_text

DocumentFormat = Literal["pdf", "html"]

KNOWN_SECTIONS = {
    "abstract",
    "introduction",
    "background",
    "methods",
    "materials and methods",
    "methodology",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "limitations",
    "references",
    "acknowledgments",
    "acknowledgements",
}

SECTION_HEADING_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9 ,/&-]{0,60})$"
)


class DocumentParseError(Exception):
    """Raised when a document cannot be parsed."""

    def __init__(self, message: str, *, reason: str = "parse_error") -> None:
        super().__init__(message)
        self.message = message
        self.reason = reason


def parse_document(
    content: bytes,
    doc_format: DocumentFormat,
    text: str | None = None,
) -> list[DocumentSection]:
    """Parse a PDF or HTML document into ordered sections."""
    if doc_format == "pdf":
        return parse_pdf(content)
    if doc_format == "html":
        return parse_html(text or content.decode("utf-8", errors="replace"))
    raise DocumentParseError(
        f"Unsupported document format: {doc_format}",
        reason="unsupported_format",
    )


def parse_pdf(content: bytes) -> list[DocumentSection]:
    if not content:
        raise DocumentParseError(
            "PDF document is empty.",
            reason="pdf_empty",
        )

    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise DocumentParseError(
            "Failed to read PDF document.",
            reason="pdf_read_error",
        ) from exc

    page_texts: list[str] = []
    for page in reader.pages:
        try:
            extracted = page.extract_text() or ""
        except Exception as exc:
            raise DocumentParseError(
                "Failed to extract text from PDF pages.",
                reason="pdf_extract_error",
            ) from exc
        if extracted.strip():
            page_texts.append(extracted)

    if not page_texts:
        raise DocumentParseError(
            "PDF document contains no extractable text.",
            reason="pdf_no_text",
        )

    combined = "\n\n".join(page_texts)
    sections = _split_text_into_sections(combined)
    if sections:
        return sections

    cleaned = clean_section_text(combined)
    return [
        DocumentSection(
            section_name="Body",
            text=cleaned,
            order=0,
        )
    ]


def parse_html(html: str) -> list[DocumentSection]:
    if not html or not html.strip():
        raise DocumentParseError(
            "HTML document is empty.",
            reason="html_empty",
        )

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as exc:
        raise DocumentParseError(
            "Failed to parse HTML document.",
            reason="html_parse_error",
        ) from exc

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    sections: list[DocumentSection] = []
    current_name = "Body"
    current_parts: list[str] = []
    order = 0

    def flush_section() -> None:
        nonlocal order
        text = clean_section_text("\n\n".join(current_parts))
        if text:
            sections.append(
                DocumentSection(
                    section_name=current_name,
                    text=text,
                    order=order,
                )
            )
            order += 1
        current_parts.clear()

    for element in soup.find_all(["h1", "h2", "h3", "p", "div", "section", "article"]):
        name = element.name
        if name in {"h1", "h2", "h3"}:
            heading = element.get_text(" ", strip=True)
            if heading:
                flush_section()
                current_name = _normalize_section_name(heading)
            continue

        text = element.get_text("\n", strip=True)
        if text:
            current_parts.append(text)

    flush_section()

    if sections:
        return sections

    fallback_text = clean_section_text(soup.get_text("\n", strip=True))
    if not fallback_text:
        raise DocumentParseError(
            "HTML document contains no extractable text.",
            reason="html_no_text",
        )

    return [DocumentSection(section_name="Body", text=fallback_text, order=0)]


def _split_text_into_sections(text: str) -> list[DocumentSection]:
    lines = text.splitlines()
    sections: list[DocumentSection] = []
    current_name = "Body"
    current_lines: list[str] = []
    order = 0

    def flush_section() -> None:
        nonlocal order
        section_text = clean_section_text("\n".join(current_lines))
        if section_text:
            sections.append(
                DocumentSection(
                    section_name=current_name,
                    text=section_text,
                    order=order,
                )
            )
            order += 1
        current_lines.clear()

    for line in lines:
        candidate = line.strip()
        if _looks_like_section_heading(candidate):
            flush_section()
            current_name = _normalize_section_name(candidate)
            continue
        current_lines.append(line)

    flush_section()
    return sections


def _looks_like_section_heading(line: str) -> bool:
    if not line or len(line) > 80:
        return False
    if not SECTION_HEADING_PATTERN.match(line):
        return False
    normalized = _normalize_section_name(line).lower()
    if normalized in KNOWN_SECTIONS:
        return True
    words = normalized.split()
    return len(words) <= 6 and normalized.replace(" ", "").isalpha()


def _normalize_section_name(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name.strip())
    if not cleaned:
        return "Unknown"
    lower = cleaned.lower()
    if lower in KNOWN_SECTIONS:
        return cleaned.title() if lower == "abstract" else cleaned
    return cleaned
