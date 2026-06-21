from pathlib import Path

from pothole_detection.config import DATASET_DIR, OUTPUTS_DIR
from pothole_detection.detector import PotholeDetector


def test_detector_returns_result_for_sample_image() -> None:
    sample = next((DATASET_DIR / "test" / "images").glob("*"))
    output_path = OUTPUTS_DIR / "pytest_annotated.jpg"
    result = PotholeDetector().annotate(sample, output_path)

    assert Path(result["annotated_image"]).exists()
    assert result["backend"] in {"opencv-fallback", "ultralytics-yolo"}
    assert isinstance(result["detections"], list)
    assert result["latency_ms"] >= 0


if __name__ == "__main__":
    test_detector_returns_result_for_sample_image()
    print("smoke test passed")
