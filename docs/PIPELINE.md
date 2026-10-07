# Pipeline
Entry point: `python run_pipeline.py --stage <name>` (all `NOT_IMPLEMENTED_YET`).
| # | Stage | Description | Output |
|---|---|---|---|
| 1 | validate_data | Adapters + validators produce reports | reports/documentation |
| 2 | train_classifier | Train on RealWaste only | models/image_classifier |
| 3 | evaluate_cross_dataset | RealWaste test, TrashNet (mapped subset), TACO (generalization) | reports/model_evaluation |
| 4 | explain | Grad-CAM on real model | models/explainability |
| 5 | train_forecaster | Time-split, baseline then candidates | models/forecasting |
| 6 | forecast | Future years per region | DB: forecasts |
| 7 | capacity_analysis | Gap + priority | DB: capacity_analysis |
| 8 | recommend | Combine all signals | DB: recommendations |

Each stage must be idempotent, log to `prediction_logs`/files, and fail loudly when inputs are missing.
