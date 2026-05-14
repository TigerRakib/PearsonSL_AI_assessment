from app.ingestion.image_processor import preprocess_image_for_ocr


def test_preprocess_image_for_ocr(tmp_path):
    import cv2
    import numpy as np

    source = tmp_path / "source.png"
    output = tmp_path / "processed.png"
    image = np.full((20, 40, 3), 255, dtype=np.uint8)
    cv2.putText(image, "A", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.imwrite(str(source), image)

    result = preprocess_image_for_ocr(source, output)

    assert output.exists()
    assert result.processed_width == 80
    assert result.processed_height == 40
    assert result.operations == [
        "grayscale",
        "denoise",
        "resize",
        "adaptive_threshold",
        "sharpen",
    ]
