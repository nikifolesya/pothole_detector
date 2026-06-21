from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from ultralytics import YOLO, RTDETR


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a detector from a YAML config.")
    parser.add_argument("--config", required=True, help="Path to config YAML.")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = yaml.safe_load(config_path.read_text())
    model_name = cfg.pop("model")
    model = RTDETR(model_name) if "rtdetr" in model_name.lower() else YOLO(model_name)
    model.train(**cfg)


if __name__ == "__main__":
    main()
