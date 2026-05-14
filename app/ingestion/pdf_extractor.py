from datetime import datetime, timezone
from pathlib import Path

from app.ingestion.validator import validate_extraction_quality
from app.models.document import ExtractedDocument, ExtractedPage, ExtractionMethod


def extract_pdf_text(file_id: str, filename: str, path: Path) -> ExtractedDocument:
    try:
        import fitz
    except Exception as exc:
        raise RuntimeError("PyMuPDF is required for PDF extraction.") from exc

    pages = []
    with fitz.open(path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            rect = page.rect
            pages.append(
                ExtractedPage(
                    page_number=page_index,
                    text=text,
                    char_count=len(text),
                    word_count=len(text.split()),
                    image_count=len(page.get_images(full=True)),
                    width=rect.width,
                    height=rect.height,
                )
            )

    return ExtractedDocument(
        file_id=file_id,
        filename=filename,
        method=ExtractionMethod.PYMUPDF,
        page_count=len(pages),
        pages=pages,
        quality=validate_extraction_quality(pages),
        extracted_at=datetime.now(timezone.utc),
    )
