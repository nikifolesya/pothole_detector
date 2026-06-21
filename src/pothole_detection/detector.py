from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import cv2
import numpy as np

from .config import CLASS_NAMES, DEFAULT_MODEL_PATH


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: list[float]


class PotholeDetector:
    """YOLO-backed detector with a deterministic OpenCV fallback for smoke tests."""

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL_PATH,
        confidence: float = 0.25,
        image_size: int = 640,
    ) -> None:
        self.model_path = Path(model_path)
        self.confidence = confidence
        self.image_size = image_size
        self.model: Any | None = None
        self.backend = "opencv-fallback"

        if self.model_path.exists():
            try:
                from ultralytics import YOLO

                self.model = YOLO(str(self.model_path))
                self.backend = "ultralytics-yolo"
            except Exception:
                self.model = None

    def predict(self, image_path: str | Path) -> dict[str, Any]:
        image_path = Path(image_path)
        started = perf_counter()
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        if self.model is not None:
            detections = self._predict_yolo(image)
        else:
            detections = self._predict_opencv(image)

        latency_ms = (perf_counter() - started) * 1000
        return {
            "image": str(image_path),
            "backend": self.backend,
            "model_path": str(self.model_path),
            "latency_ms": round(latency_ms, 2),
            "detections": [asdict(d) for d in detections],
            "count": len(detections),
        }

    def annotate(self, image_path: str | Path, output_path: str | Path) -> dict[str, Any]:
        result = self.predict(image_path)
        image = cv2.imread(str(image_path))
        for item in result["detections"]:
            x1, y1, x2, y2 = [int(v) for v in item["bbox_xyxy"]]
            label = f"{item['class_name']} {item['confidence']:.2f}"
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 180, 0), 2)
            cv2.putText(image, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 180, 0), 2)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
        result["annotated_image"] = str(output_path)
        return result

    def _predict_yolo(self, image: np.ndarray) -> list[Detection]:
        results = self.model.predict(image, imgsz=self.image_size, conf=self.confidence, verbose=False)
        detections: list[Detection] = []
        for box in results[0].boxes:
            cls = int(box.cls[0].item())
            name = self.model.names.get(cls, CLASS_NAMES[cls] if cls < len(CLASS_NAMES) else str(cls))
            detections.append(
                Detection(
                    class_id=cls,
                    class_name=str(name),
                    confidence=float(box.conf[0].item()),
                    bbox_xyxy=[round(float(v), 2) for v in box.xyxy[0].tolist()],
                )
            )
        return detections

    def _predict_opencv(self, image: np.ndarray) -> list[Detection]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blur, 50, 140)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = gray.shape[:2]
        min_area = max(250, int(0.0015 * h * w))
        candidates: list[tuple[float, Detection]] = []

        for contour in contours:
            x, y, bw, bh = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if area < min_area or bw < 12 or bh < 8:
                continue
            aspect = bw / max(bh, 1)
            if not 0.4 <= aspect <= 5.5:
                continue
            roi = gray[y : y + bh, x : x + bw]
            darkness = 1.0 - float(np.mean(roi) / 255.0)
            fill = min(1.0, area / max(bw * bh, 1))
            score = max(0.05, min(0.92, 0.45 * darkness + 0.55 * fill))
            if score < self.confidence:
                continue
            candidates.append(
                (
                    area,
                    Detection(
                        class_id=4,
                        class_name="Pothole",
                        confidence=round(score, 3),
                        bbox_xyxy=[float(x), float(y), float(x + bw), float(y + bh)],
                    ),
                )
            )

        candidates.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in candidates[:10]]
