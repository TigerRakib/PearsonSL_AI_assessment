from fastapi.testclient import TestClient

from app.api.dependencies.storage import get_storage
from app.main import app
from app.storage.file_store import FileStorage


def test_upload_list_download_and_delete_file(tmp_path):
    app.dependency_overrides[get_storage] = lambda: FileStorage(str(tmp_path), 1)
    client = TestClient(app)

    upload_response = client.post(
        "/files",
        files={"file": ("case notes.txt", b"important evidence", "text/plain")},
    )

    assert upload_response.status_code == 201
    uploaded_file = upload_response.json()
    assert uploaded_file["original_filename"] == "case_notes.txt"
    assert uploaded_file["size_bytes"] == len(b"important evidence")
    assert uploaded_file["mime_route"]["route"] == "text"
    assert uploaded_file["mime_route"]["document_type"] == "text"
    assert uploaded_file["mime_route"]["strategy"] == "text_extraction"
    assert uploaded_file["mime_route"]["needs_ocr"] is False
    assert uploaded_file["mime_route"]["is_supported"] is True

    list_response = client.get("/files")
    assert list_response.status_code == 200
    assert list_response.json()["files"][0]["id"] == uploaded_file["id"]

    route_response = client.get(f"/files/{uploaded_file['id']}/route")
    assert route_response.status_code == 200
    assert route_response.json()["route"] == "text"

    download_response = client.get(uploaded_file["download_url"])
    assert download_response.status_code == 200
    assert download_response.content == b"important evidence"

    delete_response = client.delete(f"/files/{uploaded_file['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"id": uploaded_file["id"], "deleted": True}

    missing_response = client.get(uploaded_file["download_url"])
    assert missing_response.status_code == 404
    app.dependency_overrides.clear()


def test_rejects_empty_file(tmp_path):
    app.dependency_overrides[get_storage] = lambda: FileStorage(str(tmp_path), 1)
    client = TestClient(app)

    response = client.post("/files", files={"file": ("empty.txt", b"", "text/plain")})

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."
    app.dependency_overrides.clear()


def test_rejects_file_over_size_limit(tmp_path):
    app.dependency_overrides[get_storage] = lambda: FileStorage(str(tmp_path), 0)
    client = TestClient(app)

    response = client.post("/files", files={"file": ("large.txt", b"x", "text/plain")})

    assert response.status_code == 413
    app.dependency_overrides.clear()


def test_extract_uploaded_pdf(tmp_path):
    import fitz

    app.dependency_overrides[get_storage] = lambda: FileStorage(str(tmp_path), 1)
    client = TestClient(app)

    pdf_path = tmp_path / "contract.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "This uploaded contract contains enough embedded text for extraction.",
    )
    document.save(pdf_path)
    document.close()

    upload_response = client.post(
        "/files",
        files={"file": ("contract.pdf", pdf_path.read_bytes(), "application/pdf")},
    )
    assert upload_response.status_code == 201

    uploaded_file = upload_response.json()
    extract_response = client.post(f"/files/{uploaded_file['id']}/extract")

    assert extract_response.status_code == 200
    extracted = extract_response.json()
    assert extracted["file_id"] == uploaded_file["id"]
    assert extracted["page_count"] == 1
    assert extracted["quality"]["level"] == "good"
    assert "uploaded contract" in extracted["pages"][0]["text"]
    app.dependency_overrides.clear()
