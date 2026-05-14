import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.api.schemas.uploads import UploadedFile
from app.ingestion.image_processor import preprocess_image_for_ocr
from app.ingestion.router import route_mime

CHUNK_SIZE = 1024 * 1024
SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


class FileStorage:
    def __init__(self, upload_dir: str, max_file_size_mb: int):
        self.upload_dir = Path(upload_dir)
        self.metadata_dir = self.upload_dir / ".metadata"
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile) -> UploadedFile:
        original_filename = _sanitize_filename(file.filename)
        file_id = uuid4().hex
        stored_filename = f"{file_id}{Path(original_filename).suffix.lower()}"
        destination = self._file_path(stored_filename)

        size_bytes = 0
        try:
            with destination.open("wb") as output:
                while chunk := await file.read(CHUNK_SIZE):
                    size_bytes += len(chunk)
                    if size_bytes > self.max_file_size_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=(
                                "File is too large. "
                                f"Maximum size is {self.max_file_size_bytes // (1024 * 1024)} MB."
                            ),
                        )
                    output.write(chunk)
        except HTTPException:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

        if size_bytes == 0:
            destination.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        mime_route = route_mime(destination, file.content_type)
        uploaded_file = UploadedFile(
            id=file_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            mime_route=mime_route,
            size_bytes=size_bytes,
            uploaded_at=datetime.now(timezone.utc),
            download_url=f"/files/{file_id}/download",
        )
        self._write_metadata(uploaded_file)
        return uploaded_file

    def list(self) -> list[UploadedFile]:
        files = []
        for metadata_path in self.metadata_dir.glob("*.json"):
            try:
                files.append(UploadedFile.model_validate_json(metadata_path.read_text()))
            except (OSError, ValueError):
                continue
        return sorted(files, key=lambda file: file.uploaded_at, reverse=True)

    def get(self, file_id: str) -> UploadedFile:
        metadata_path = self._metadata_path(file_id)
        if not metadata_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return UploadedFile.model_validate_json(metadata_path.read_text())

    def get_download_path(self, file_id: str) -> Path:
        uploaded_file = self.get(file_id)
        path = self._file_path(uploaded_file.stored_filename)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return path

    def preprocess_for_ocr(self, file_id: str):
        uploaded_file = self.get(file_id)
        if uploaded_file.mime_route.route != "image_ocr":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image uploads can be preprocessed directly. Scanned PDF preprocessing happens after page rendering.",
            )

        source_path = self.get_download_path(file_id)
        output_path = self.upload_dir / "preprocessed" / f"{file_id}.png"
        return preprocess_image_for_ocr(source_path, output_path)

    def delete(self, file_id: str) -> None:
        uploaded_file = self.get(file_id)
        self._file_path(uploaded_file.stored_filename).unlink(missing_ok=True)
        self._metadata_path(file_id).unlink(missing_ok=True)
        (self.upload_dir / "preprocessed" / f"{file_id}.png").unlink(missing_ok=True)

    def _file_path(self, stored_filename: str) -> Path:
        path = (self.upload_dir / stored_filename).resolve()
        upload_root = self.upload_dir.resolve()
        if upload_root not in path.parents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path.")
        return path

    def _metadata_path(self, file_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{32}", file_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return self.metadata_dir / f"{file_id}.json"

    def _write_metadata(self, uploaded_file: UploadedFile) -> None:
        self._metadata_path(uploaded_file.id).write_text(
            json.dumps(uploaded_file.model_dump(mode="json"), indent=2),
        )


def _sanitize_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    basename = Path(filename).name.strip()
    sanitized = SAFE_FILENAME_PATTERN.sub("_", basename).strip("._")
    if not sanitized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid filename is required.",
        )
    return sanitized
