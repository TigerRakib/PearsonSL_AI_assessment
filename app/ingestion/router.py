from pathlib import Path

from app.api.schemas.mime import (
    DocumentType,
    MimeRoute,
    ProcessingRoute,
    ProcessingStrategy,
)
from app.ingestion.mime_detector import (
    DOCX_MIME_TYPES,
    IMAGE_MIME_TYPES,
    PDF_MIME_TYPES,
    TEXT_MIME_TYPES,
    detect_document_mime,
)
from app.ingestion.pdf_classifier import classify_pdf, pdf_route_details


def route_mime(path: Path, declared_mime: str | None = None) -> MimeRoute:
    detected_mime = detect_document_mime(path, declared_mime)
    normalized_mime = detected_mime.lower()

    if normalized_mime in PDF_MIME_TYPES:
        try:
            classification = classify_pdf(path)
        except Exception:
            return MimeRoute(
                detected_mime=detected_mime,
                declared_mime=declared_mime,
                route=ProcessingRoute.UNSUPPORTED,
                document_type=DocumentType.UNSUPPORTED,
                strategy=ProcessingStrategy.UNSUPPORTED,
                needs_ocr=False,
                is_supported=False,
                reason="PDF could not be opened for classification.",
            )
        document_type, strategy, needs_ocr, reason = pdf_route_details(classification)
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.PDF,
            document_type=document_type,
            strategy=strategy,
            needs_ocr=needs_ocr,
            is_supported=True,
            reason=reason,
            pdf_classification=classification,
        )

    if normalized_mime in IMAGE_MIME_TYPES:
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.IMAGE_OCR,
            document_type=DocumentType.IMAGE,
            strategy=ProcessingStrategy.OCR,
            needs_ocr=True,
            is_supported=True,
            reason="Image document routed to OpenCV preprocessing and OCR.",
        )

    if normalized_mime in DOCX_MIME_TYPES:
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.DOCX,
            document_type=DocumentType.DOCX,
            strategy=ProcessingStrategy.DOCX_EXTRACTION,
            needs_ocr=False,
            is_supported=True,
            reason="DOCX document routed to Word text extraction.",
        )

    if normalized_mime in TEXT_MIME_TYPES or normalized_mime.startswith("text/"):
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.TEXT,
            document_type=DocumentType.TEXT,
            strategy=ProcessingStrategy.TEXT_EXTRACTION,
            needs_ocr=False,
            is_supported=True,
            reason="Text-like document routed to plain text extraction.",
        )

    return MimeRoute(
        detected_mime=detected_mime,
        declared_mime=declared_mime,
        route=ProcessingRoute.UNSUPPORTED,
        document_type=DocumentType.UNSUPPORTED,
        strategy=ProcessingStrategy.UNSUPPORTED,
        needs_ocr=False,
        is_supported=False,
        reason="No ingestion route is configured for this MIME type.",
    )
