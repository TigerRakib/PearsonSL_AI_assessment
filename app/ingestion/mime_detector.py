import mimetypes
from pathlib import Path

PDF_MIME_TYPES = {"application/pdf"}
IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/tiff", "image/x-tiff"}
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


def detect_document_mime(path: Path, declared_mime: str | None = None) -> str:
    return detect_mime(path) or declared_mime or guess_mime(path) or "application/octet-stream"


def detect_mime(path: Path) -> str | None:
    try:
        import magic

        detected = magic.from_file(str(path), mime=True)
    except Exception:
        return None
    return detected if isinstance(detected, str) and detected else None


def guess_mime(path: Path) -> str | None:
    guessed_mime, _ = mimetypes.guess_type(path.name)
    return guessed_mime
