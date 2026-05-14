from app.ingestion.router import route_mime


def test_routes_digital_pdf_to_direct_extraction(tmp_path):
    import fitz

    path = tmp_path / "contract.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "This contract contains enough embedded text for direct extraction.")
    document.save(path)
    document.close()

    route = route_mime(path, "application/pdf")

    assert route.route == "pdf"
    assert route.document_type == "digital_pdf"
    assert route.strategy == "direct_extraction"
    assert route.needs_ocr is False
    assert route.pdf_classification.page_count == 1
    assert route.is_supported is True


def test_routes_scanned_pdf_to_ocr(tmp_path):
    import fitz

    path = tmp_path / "scan.pdf"
    document = fitz.open()
    page = document.new_page()
    page.draw_rect(fitz.Rect(72, 72, 200, 200), color=(0, 0, 0), fill=(0, 0, 0))
    document.save(path)
    document.close()

    route = route_mime(path, "application/pdf")

    assert route.route == "pdf"
    assert route.document_type == "scanned_pdf"
    assert route.strategy == "ocr"
    assert route.needs_ocr is True


def test_routes_hybrid_pdf_to_extraction_with_ocr_fallback(tmp_path):
    import fitz

    path = tmp_path / "hybrid.pdf"
    document = fitz.open()
    text_page = document.new_page()
    text_page.insert_text((72, 72), "This page has enough embedded text for direct extraction.")
    image_page = document.new_page()
    image_page.draw_rect(fitz.Rect(72, 72, 200, 200), color=(0, 0, 0), fill=(0, 0, 0))
    document.save(path)
    document.close()

    route = route_mime(path, "application/pdf")

    assert route.route == "pdf"
    assert route.document_type == "hybrid_pdf"
    assert route.strategy == "extraction_with_ocr_fallback"
    assert route.needs_ocr is True


def test_routes_image_to_ocr(tmp_path):
    path = tmp_path / "scan.png"
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    )

    route = route_mime(path, "image/png")

    assert route.route == "image_ocr"
    assert route.document_type == "image"
    assert route.strategy == "ocr"
    assert route.needs_ocr is True
    assert route.is_supported is True


def test_marks_unknown_files_unsupported(tmp_path):
    path = tmp_path / "archive.bin"
    path.write_bytes(b"\x00\x01\x02\x03")

    route = route_mime(path, "application/octet-stream")

    assert route.route == "unsupported"
    assert route.is_supported is False
