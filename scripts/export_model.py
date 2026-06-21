from __future__ import annotations

import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Export trained YOLO weights.")
    parser.add_argument("--weights", default="models/best.pt")
    parser.add_argument("--format", default="onnx", choices=["onnx", "torchscript", "openvino"])
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--opset", type=int, default=20)
    args = parser.parse_args()

    model = YOLO(args.weights)
    export_args = {"format": args.format, "imgsz": args.imgsz}
    if args.format == "onnx":
        export_args["opset"] = args.opset
    model.export(**export_args)


if __name__ == "__main__":
    main()
