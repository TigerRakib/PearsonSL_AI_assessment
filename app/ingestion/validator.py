from app.models.document import (
    ExtractedPage,
    ExtractionQuality,
    ExtractionQualityLevel,
)

MIN_PAGE_CHARS = 40
MIN_PAGE_WORDS = 8


def validate_extraction_quality(pages: list[ExtractedPage]) -> ExtractionQuality:
    page_count = len(pages)
    total_chars = sum(page.char_count for page in pages)
    total_words = sum(page.word_count for page in pages)
    empty_pages = sum(1 for page in pages if page.char_count == 0)
    weak_pages = sum(
        1
        for page in pages
        if page.char_count < MIN_PAGE_CHARS or page.word_count < MIN_PAGE_WORDS
    )

    if page_count == 0 or total_chars == 0:
        return ExtractionQuality(
            level=ExtractionQualityLevel.EMPTY,
            score=0,
            total_chars=total_chars,
            total_words=total_words,
            empty_pages=empty_pages,
            weak_pages=weak_pages,
            page_count=page_count,
            needs_ocr_fallback=True,
            reasons=["No extractable text was found."],
        )

    healthy_pages = max(page_count - weak_pages, 0)
    page_coverage = healthy_pages / page_count
    density_score = min(total_words / max(page_count * MIN_PAGE_WORDS, 1), 1)
    score = round((page_coverage * 0.7) + (density_score * 0.3), 2)

    reasons = []
    if empty_pages:
        reasons.append(f"{empty_pages} page(s) have no extractable text.")
    if weak_pages:
        reasons.append(f"{weak_pages} page(s) have weak text extraction.")
    if not reasons:
        reasons.append("Embedded text extraction looks usable.")

    needs_ocr_fallback = score < 0.75 or empty_pages > 0
    level = ExtractionQualityLevel.GOOD
    if needs_ocr_fallback:
        level = ExtractionQualityLevel.WEAK

    return ExtractionQuality(
        level=level,
        score=score,
        total_chars=total_chars,
        total_words=total_words,
        empty_pages=empty_pages,
        weak_pages=weak_pages,
        page_count=page_count,
        needs_ocr_fallback=needs_ocr_fallback,
        reasons=reasons,
    )
