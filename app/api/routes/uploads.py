from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies.storage import get_storage
from app.api.schemas.mime import MimeRoute
from app.api.schemas.preprocessing import ImagePreprocessingResult
from app.api.schemas.uploads import DeleteResponse, UploadedFile, UploadList
from app.models.document import ExtractedDocument
from app.storage.file_store import FileStorage

router = APIRouter(prefix="/files", tags=["files"])


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


@router.post(
    "/{file_id}/preprocess",
    response_model=ImagePreprocessingResult,
    summary="Preprocess an image upload for OCR",
)
async def preprocess_file_for_ocr(
    file_id: str,
    storage: FileStorage = Depends(get_storage),
) -> ImagePreprocessingResult:
    return storage.preprocess_for_ocr(file_id)


@router.post(
    "/{file_id}/extract",
    response_model=ExtractedDocument,
    summary="Extract text from an uploaded PDF",
)
async def extract_file(
    file_id: str,
    storage: FileStorage = Depends(get_storage),
) -> ExtractedDocument:
    return storage.extract(file_id)


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
