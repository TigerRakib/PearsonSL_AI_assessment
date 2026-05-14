from enum import Enum

from pydantic import BaseModel


class ProcessingRoute(str, Enum):
    PDF = "pdf"
    IMAGE_OCR = "image_ocr"
    DOCX = "docx"
    TEXT = "text"
    UNSUPPORTED = "unsupported"


class DocumentType(str, Enum):
    DIGITAL_PDF = "digital_pdf"
    SCANNED_PDF = "scanned_pdf"
    HYBRID_PDF = "hybrid_pdf"
    IMAGE = "image"
    DOCX = "docx"
    TEXT = "text"
    UNSUPPORTED = "unsupported"


class ProcessingStrategy(str, Enum):
    DIRECT_EXTRACTION = "direct_extraction"
    OCR = "ocr"
    EXTRACTION_WITH_OCR_FALLBACK = "extraction_with_ocr_fallback"
    DOCX_EXTRACTION = "docx_extraction"
    TEXT_EXTRACTION = "text_extraction"
    UNSUPPORTED = "unsupported"


class PdfPageSignal(BaseModel):
    page_number: int
    text_char_count: int
    image_count: int
    has_text: bool
    has_images: bool


class PdfClassification(BaseModel):
    page_count: int
    text_page_count: int
    image_page_count: int
    total_text_chars: int
    page_signals: list[PdfPageSignal]


class MimeRoute(BaseModel):
    detected_mime: str
    declared_mime: str | None = None
    route: ProcessingRoute
    document_type: DocumentType
    strategy: ProcessingStrategy
    needs_ocr: bool
    is_supported: bool
    reason: str
    pdf_classification: PdfClassification | None = None
