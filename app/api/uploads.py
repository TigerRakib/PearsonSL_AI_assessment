from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse

from app.config import settings
from app.models.mime import MimeRoute
from app.models.uploads import DeleteResponse, UploadedFile, UploadList
from app.utils.file_storage import FileStorage

router = APIRouter(prefix="/files", tags=["files"])


def get_storage() -> FileStorage:
    return FileStorage(settings.upload_dir, settings.max_file_size_mb)


@router.post(
    "",
    response_model=UploadedFile,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
)
async def upload_file(
    file: UploadFile,
    storage: FileStorage = Depends(get_storage),
) -> UploadedFile:
    return await storage.save(file)


@router.get("", response_model=UploadList, summary="List uploaded files")
async def list_files(storage: FileStorage = Depends(get_storage)) -> UploadList:
    return UploadList(files=storage.list())


@router.get("/{file_id}/download", summary="Download an uploaded file")
async def download_file(
    file_id: str,
    storage: FileStorage = Depends(get_storage),
) -> FileResponse:
    uploaded_file = storage.get(file_id)
    path = storage.get_download_path(file_id)
    return FileResponse(
        path,
        media_type=uploaded_file.content_type,
        filename=uploaded_file.original_filename,
    )


@router.get("/{file_id}/route", response_model=MimeRoute, summary="Get MIME route")
async def get_file_route(
    file_id: str,
    storage: FileStorage = Depends(get_storage),
) -> MimeRoute:
    return storage.get(file_id).mime_route


@router.delete(
    "/{file_id}",
    response_model=DeleteResponse,
    summary="Delete an uploaded file",
)
async def delete_file(
    file_id: str,
    storage: FileStorage = Depends(get_storage),
) -> DeleteResponse:
    storage.delete(file_id)
    return DeleteResponse(id=file_id, deleted=True)
