from datetime import datetime

from pydantic import BaseModel, Field


class UploadedFile(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    content_type: str | None = None
    size_bytes: int = Field(ge=0)
    uploaded_at: datetime
    download_url: str


class UploadList(BaseModel):
    files: list[UploadedFile]


class DeleteResponse(BaseModel):
    id: str
    deleted: bool
