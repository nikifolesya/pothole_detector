from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile

from pothole_detection.config import DEFAULT_MODEL_PATH, OUTPUTS_DIR, RUN_HISTORY_DB
from pothole_detection.detector import PotholeDetector
from service.history import RunHistory


UPLOAD_DIR = OUTPUTS_DIR / "uploads"
ANNOTATION_DIR = OUTPUTS_DIR / "annotated"

app = FastAPI(title="Pothole Detection API", version="1.0.0")
detector = PotholeDetector(DEFAULT_MODEL_PATH)
history = RunHistory(RUN_HISTORY_DB)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "backend": detector.backend,
        "model_path": str(detector.model_path),
        "model_exists": detector.model_path.exists(),
    }


@app.post("/predict")
def predict(file: UploadFile = File(...)) -> dict[str, object]:
    image_path = _save_upload(file)
    output_path = ANNOTATION_DIR / f"{image_path.stem}_annotated.jpg"
    result = detector.annotate(image_path, output_path)
    result["run_id"] = history.add(result)
    return result


@app.post("/batch_predict")
def batch_predict(files: list[UploadFile] = File(...)) -> dict[str, object]:
    results = []
    for file in files:
        image_path = _save_upload(file)
        output_path = ANNOTATION_DIR / f"{image_path.stem}_annotated.jpg"
        result = detector.annotate(image_path, output_path)
        result["run_id"] = history.add(result)
        results.append(result)
    return {"items": results, "count": len(results)}


@app.get("/stats")
@app.get("/metrics")
def stats() -> dict[str, object]:
    return history.stats()


def _save_upload(file: UploadFile) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    image_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    with image_path.open("wb") as dst:
        shutil.copyfileobj(file.file, dst)
    return image_path
