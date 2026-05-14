from pathlib import Path

from app.api.schemas.preprocessing import ImagePreprocessingResult


def preprocess_image_for_ocr(
    source_path: Path,
    output_path: Path,
    resize_scale: float = 2.0,
) -> ImagePreprocessingResult:
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        raise RuntimeError("OpenCV and NumPy are required for image preprocessing.") from exc

    image = cv2.imread(str(source_path))
    if image is None:
        raise ValueError(f"Unable to read image: {source_path}")

    operations = []
    original_height, original_width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    operations.append("grayscale")

    denoised = cv2.fastNlMeansDenoising(gray, h=30)
    operations.append("denoise")

    if resize_scale > 1:
        denoised = cv2.resize(
            denoised,
            None,
            fx=resize_scale,
            fy=resize_scale,
            interpolation=cv2.INTER_CUBIC,
        )
        operations.append("resize")

    thresholded = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    operations.append("adaptive_threshold")

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(thresholded, -1, kernel)
    operations.append("sharpen")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), sharpened):
        raise ValueError(f"Unable to write preprocessed image: {output_path}")

    processed_height, processed_width = sharpened.shape[:2]
    return ImagePreprocessingResult(
        original_path=str(source_path),
        processed_path=str(output_path),
        original_width=original_width,
        original_height=original_height,
        processed_width=processed_width,
        processed_height=processed_height,
        operations=operations,
    )
