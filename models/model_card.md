# Model Card

Current production artifact: `models/best.pt`.

The service automatically loads this file with Ultralytics YOLO. If the file is absent, the API uses a deterministic OpenCV fallback so that `/health`, `/predict`, history logging and smoke tests remain runnable.

Selected model: YOLOv8n quick fine-tuned for 3 CPU epochs on the Roboflow pothole dataset at 416 px.

Validation summary:

- `mAP@0.5`: 0.12392
- `mAP@0.5:0.95`: 0.06245
- precision: 0.33921
- recall: 0.17314
- inference: 51.0 ms/image on CPU
- weights: 5.9 MB

Deployment artifact: `models/best.onnx`, exported with ONNX opset 20 for ONNX Runtime compatibility. A smoke inference on one test image took 11.0 ms/image on CPU.

YOLOv8n was selected over YOLO11n quick because it had slightly better `mAP@0.5:0.95` and lower latency in this CPU run. For production-quality accuracy, run the full GPU configs and review false positives on road texture plus missed small potholes.
