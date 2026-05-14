import mimetypes
from pathlib import Path

from app.models.mime import MimeRoute, ProcessingRoute

PDF_MIME_TYPES = {"application/pdf"}
DOCX_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
TEXT_MIME_TYPES = {
    "application/json",
    "application/rtf",
    "application/xml",
    "text/csv",
    "text/markdown",
    "text/plain",
    "text/rtf",
    "text/xml",
}


def route_mime(path: Path, declared_mime: str | None = None) -> MimeRoute:
    detected_mime = _detect_mime(path) or declared_mime or _guess_mime(path) or "application/octet-stream"
    normalized_mime = detected_mime.lower()

    if normalized_mime in PDF_MIME_TYPES:
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.PDF,
            is_supported=True,
            reason="PDF document routed to PDF text extraction.",
        )

    if normalized_mime.startswith("image/"):
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.IMAGE_OCR,
            is_supported=True,
            reason="Image document routed to OCR preprocessing.",
        )

    if normalized_mime in DOCX_MIME_TYPES:
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.DOCX,
            is_supported=True,
            reason="DOCX document routed to Word text extraction.",
        )

    if normalized_mime in TEXT_MIME_TYPES or normalized_mime.startswith("text/"):
        return MimeRoute(
            detected_mime=detected_mime,
            declared_mime=declared_mime,
            route=ProcessingRoute.TEXT,
            is_supported=True,
            reason="Text-like document routed to plain text extraction.",
        )

    return MimeRoute(
        detected_mime=detected_mime,
        declared_mime=declared_mime,
        route=ProcessingRoute.UNSUPPORTED,
        is_supported=False,
        reason="No ingestion route is configured for this MIME type.",
    )


def _detect_mime(path: Path) -> str | None:
    try:
        import magic

        detected = magic.from_file(str(path), mime=True)
    except Exception:
        return None
    return detected if isinstance(detected, str) and detected else None


def _guess_mime(path: Path) -> str | None:
    guessed_mime, _ = mimetypes.guess_type(path.name)
    return guessed_mime
