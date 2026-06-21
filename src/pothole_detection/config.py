from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT_DIR / "pothole-detection-2-6"
DATA_YAML = DATASET_DIR / "data.yaml"
MODELS_DIR = ROOT_DIR / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "best.pt"
OUTPUTS_DIR = ROOT_DIR / "outputs"
RUN_HISTORY_DB = OUTPUTS_DIR / "runs.sqlite3"


CLASS_NAMES = [
    "0",
    "1",
    "2",
    "Manhole",
    "Pothole",
    "Pothole - v1 raw",
    "Pothole_Segmentation_YOLOv8 - v1 2023-10-20 10-09pm",
    "Unmarked Bump",
    "crack",
    "damage",
    "medium-pothole",
    "object",
    "pothole",
    "pothole_water",
    "pothole_water_m",
    "risk-pothole",
]
