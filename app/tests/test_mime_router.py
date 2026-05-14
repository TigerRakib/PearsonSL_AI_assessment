from app.ingestion.mime_router import route_mime


def test_routes_pdf(tmp_path):
    path = tmp_path / "contract.pdf"
    path.write_bytes(b"%PDF-1.7\n")

    route = route_mime(path, "application/pdf")

    assert route.route == "pdf"
    assert route.is_supported is True


def test_routes_image_to_ocr(tmp_path):
    path = tmp_path / "scan.png"
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    )

    route = route_mime(path, "image/png")

    assert route.route == "image_ocr"
    assert route.is_supported is True


def test_marks_unknown_files_unsupported(tmp_path):
    path = tmp_path / "archive.bin"
    path.write_bytes(b"\x00\x01\x02\x03")

    route = route_mime(path, "application/octet-stream")

    assert route.route == "unsupported"
    assert route.is_supported is False
