# Pothole Detection Practice

Практическая работа по теме: сравнение архитектур для детекции дефектов дорожного покрытия на изображениях и видео.

Проект покрывает полный цикл: описание данных, план экспериментов, обучение детекторов, API для инференса, историю запусков, Docker-запуск, smoke-test и отчет.

## Данные

Используется датасет Roboflow `pothole-detection-2-zvaru`, version 6, license CC BY 4.0.

Разбиение:

| split | images | labels | objects |
| --- | ---: | ---: | ---: |
| train | 5325 | 5325 | 13022 |
| valid | 4943 | 4943 | 12042 |
| test | 4070 | 4070 | 10329 |

Основной прикладной класс: `Pothole`. В исходном датасете также есть близкие классы: `medium-pothole`, `risk-pothole`, `pothole_water`, `crack`, `damage`, `Manhole`, `Unmarked Bump`.

## Структура

```text
configs/                 конфиги экспериментов
pothole-detection-2-6/   датасет в YOLO-формате
src/pothole_detection/   общий код инференса
service/                 FastAPI-сервис и SQLite-история
scripts/                 обучение, экспорт, отчет по данным, smoke-test
tests/                   базовые проверки
models/                  место для best.pt и описания модели
outputs/                 метрики, разметки, история запусков
reports/                 итоговый отчет
```

## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PWD/src
```

## Smoke-test

```bash
PYTHONPATH=$PWD/src ./venv/bin/python scripts/smoke_test.py
```

В текущей версии `models/best.pt` уже содержит дообученный YOLOv8n quick. Если файл удалить, сервис переключится на OpenCV fallback только для проверки API и пайплайна.

## Обучение

Примеры запусков:

```bash
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/yolov8n.yaml
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/yolo11n.yaml
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/yolo11n_960.yaml
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/rtdetr_l.yaml
```

Для быстрых CPU-прогонов использовались:

```bash
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/yolov8n_quick.yaml
PYTHONPATH=$PWD/src ./venv/bin/python scripts/train_ultralytics.py --config configs/yolo11n_quick.yaml
```

Лучшие веса текущего прогона уже скопированы в `models/best.pt`.

Экспорт:

```bash
PYTHONPATH=$PWD/src ./venv/bin/python scripts/export_model.py --weights models/best.pt --format onnx
```

## API

Локальный запуск:

```bash
PYTHONPATH=$PWD/src uvicorn service.app:app --host 0.0.0.0 --port 8000
```

Docker:

```bash
docker compose up --build
```

Endpoints:

| endpoint | method | назначение |
| --- | --- | --- |
| `/health` | GET | состояние сервиса и backend |
| `/predict` | POST | инференс одного изображения |
| `/batch_predict` | POST | пакетный инференс |
| `/stats` | GET | агрегированная история запусков |
| `/metrics` | GET | alias для `/stats` |

Пример:

```bash
curl -F "file=@pothole-detection-2-6/test/images/your_image.jpg" http://localhost:8000/predict
```

## Эксперименты

Фактические и плановые прогоны лежат в `outputs/experiments.csv`.

Выполнено на CPU:

| run | model | mAP50 | mAP50-95 | precision | recall | latency |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| E1 | YOLOv8n quick | 0.12392 | 0.06245 | 0.33921 | 0.17314 | 51.0 ms |
| E2 | YOLO11n quick | 0.11990 | 0.06000 | 0.41832 | 0.17996 | 55.7 ms |
| E5 | YOLOv8n ONNX | inherited | inherited | inherited | inherited | 11.0 ms |

ONNX artifact: `models/best.onnx` exported from `models/best.pt` with opset 20.

План для GPU: YOLO11n 960 px и RT-DETR-L.

## Итоговые материалы

Основной отчет: `reports/practice_report.md`.

Для расширенной финальной сдачи можно добавить:

1. 5 удачных и 5 ошибочных примеров в `outputs/annotated/`.
2. Скриншоты запуска API, `/predict` и `/stats`.
3. Полные GPU-прогоны E3-E4.
