from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ExtractionMethod(str, Enum):
    PYMUPDF = "pymupdf"


class ExtractionQualityLevel(str, Enum):
    GOOD = "good"
    WEAK = "weak"
    EMPTY = "empty"


class ExtractedPage(BaseModel):
    page_number: int
    text: str
    char_count: int = Field(ge=0)
    word_count: int = Field(ge=0)
    image_count: int = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class ExtractionQuality(BaseModel):
    level: ExtractionQualityLevel
    score: float = Field(ge=0, le=1)
    total_chars: int = Field(ge=0)
    total_words: int = Field(ge=0)
    empty_pages: int = Field(ge=0)
    weak_pages: int = Field(ge=0)
    page_count: int = Field(ge=0)
    needs_ocr_fallback: bool
    reasons: list[str]


class ExtractedDocument(BaseModel):
    file_id: str
    filename: str
    method: ExtractionMethod
    page_count: int = Field(ge=0)
    pages: list[ExtractedPage]
    quality: ExtractionQuality
    extracted_at: datetime
