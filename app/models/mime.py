from enum import Enum

from pydantic import BaseModel


class ProcessingRoute(str, Enum):
    PDF = "pdf"
    IMAGE_OCR = "image_ocr"
    DOCX = "docx"
    TEXT = "text"
    UNSUPPORTED = "unsupported"


class MimeRoute(BaseModel):
    detected_mime: str
    declared_mime: str | None = None
    route: ProcessingRoute
    is_supported: bool
    reason: str
