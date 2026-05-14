from app.storage.file_store import FileStorage
from app.utils.config import settings


def get_storage() -> FileStorage:
    return FileStorage(settings.upload_dir, settings.max_file_size_mb)
