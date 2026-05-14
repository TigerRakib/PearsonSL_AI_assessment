from pathlib import Path

from app.api.schemas.mime import (
    DocumentType,
    PdfClassification,
    PdfPageSignal,
    ProcessingStrategy,
)

MIN_TEXT_CHARS_PER_TEXT_PAGE = 40


def classify_pdf(path: Path) -> PdfClassification:
    try:
        import fitz
    except Exception as exc:
        raise RuntimeError("PyMuPDF is required for PDF classification.") from exc

    page_signals = []
    total_text_chars = 0
    text_page_count = 0
    image_page_count = 0

    with fitz.open(path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            text_char_count = len(text)
            image_count = len(page.get_images(full=True))
            has_text = text_char_count >= MIN_TEXT_CHARS_PER_TEXT_PAGE
            has_images = image_count > 0

            total_text_chars += text_char_count
            if has_text:
                text_page_count += 1
            if has_images:
                image_page_count += 1

            page_signals.append(
                PdfPageSignal(
                    page_number=page_index,
                    text_char_count=text_char_count,
                    image_count=image_count,
                    has_text=has_text,
                    has_images=has_images,
                )
            )

        return PdfClassification(
            page_count=document.page_count,
            text_page_count=text_page_count,
            image_page_count=image_page_count,
            total_text_chars=total_text_chars,
            page_signals=page_signals,
        )


def pdf_route_details(
    classification: PdfClassification,
) -> tuple[DocumentType, ProcessingStrategy, bool, str]:
    if classification.page_count == 0:
        return (
            DocumentType.SCANNED_PDF,
            ProcessingStrategy.OCR,
            True,
            "Empty PDF routed to OCR fallback.",
        )

    if classification.text_page_count == classification.page_count:
        return (
            DocumentType.DIGITAL_PDF,
            ProcessingStrategy.DIRECT_EXTRACTION,
            False,
            "Digital PDF routed to direct PyMuPDF text extraction.",
        )

    if classification.text_page_count == 0:
        return (
            DocumentType.SCANNED_PDF,
            ProcessingStrategy.OCR,
            True,
            "Scanned PDF routed to page rendering, OpenCV preprocessing, and OCR.",
        )

    return (
        DocumentType.HYBRID_PDF,
        ProcessingStrategy.EXTRACTION_WITH_OCR_FALLBACK,
        True,
        "Hybrid PDF routed to direct extraction with OCR fallback for weak pages.",
    )
