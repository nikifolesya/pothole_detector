from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import yaml

from pothole_detection.config import DATASET_DIR, OUTPUTS_DIR


def main() -> None:
    names = yaml.safe_load((DATASET_DIR / "data.yaml").read_text())["names"]
    rows = []
    for split in ["train", "valid", "test"]:
        images = list((DATASET_DIR / split / "images").glob("*"))
        labels = list((DATASET_DIR / split / "labels").glob("*.txt"))
        counter: Counter[str] = Counter()
        empty = 0
        for label in labels:
            lines = [line.strip() for line in label.read_text().splitlines() if line.strip()]
            if not lines:
                empty += 1
            for line in lines:
                counter[line.split()[0]] += 1
        for class_id, count in sorted(counter.items(), key=lambda item: int(item[0])):
            rows.append(
                {
                    "split": split,
                    "images": len(images),
                    "labels": len(labels),
                    "empty_labels": empty,
                    "class_id": class_id,
                    "class_name": names[int(class_id)],
                    "objects": count,
                }
            )

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUTS_DIR / "dataset_summary.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(out)


if __name__ == "__main__":
    main()
