from pydantic import BaseModel


class ImagePreprocessingResult(BaseModel):
    original_path: str
    processed_path: str
    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    operations: list[str]
