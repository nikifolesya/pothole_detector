from __future__ import annotations

import json
from pathlib import Path

from pothole_detection.config import DATASET_DIR, OUTPUTS_DIR
from pothole_detection.detector import PotholeDetector


def main() -> None:
    sample = next((DATASET_DIR / "test" / "images").glob("*"))
    output = OUTPUTS_DIR / "smoke_test_annotated.jpg"
    detector = PotholeDetector()
    result = detector.annotate(sample, output)
    assert Path(result["annotated_image"]).exists()
    assert result["latency_ms"] >= 0
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
