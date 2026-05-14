from app.ingestion.pdf_extractor import extract_pdf_text


def test_extract_pdf_text_returns_pages_and_quality(tmp_path):
    import fitz

    path = tmp_path / "contract.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "This contract contains enough embedded text for direct extraction and validation.",
    )
    document.save(path)
    document.close()

    extracted = extract_pdf_text("file-1", "contract.pdf", path)

    assert extracted.file_id == "file-1"
    assert extracted.filename == "contract.pdf"
    assert extracted.method == "pymupdf"
    assert extracted.page_count == 1
    assert extracted.pages[0].page_number == 1
    assert "contract contains enough" in extracted.pages[0].text
    assert extracted.quality.level == "good"
    assert extracted.quality.needs_ocr_fallback is False


def test_extract_pdf_text_marks_weak_extraction_for_ocr_fallback(tmp_path):
    import fitz

    path = tmp_path / "scan.pdf"
    document = fitz.open()
    document.new_page()
    document.save(path)
    document.close()

    extracted = extract_pdf_text("file-2", "scan.pdf", path)

    assert extracted.quality.level == "empty"
    assert extracted.quality.needs_ocr_fallback is True
    assert extracted.quality.empty_pages == 1
