# Model Evaluation
**Classifier:** train RealWaste -> test on held-out RealWaste; secondary on TrashNet **mapped subset only** (RealWaste's Food Organics, Textile Trash, Vegetation have no TrashNet equivalent); external on TACO (mapping TO_BE_VERIFIED_DURING_IMPLEMENTATION).
Metrics: accuracy, per-class precision/recall/F1, macro/weighted F1, confusion matrix. Report the unmapped classes and domain shift explicitly. Adapters and preprocessing are per dataset.
**Forecaster:** MAE, RMSE, R2, MAPE vs naive baseline, time-aware validation. A model that does not beat the baseline is reported as such.
Results are written only by real runs to `reports/model_evaluation/` and `reports/forecasting/`. No numbers appear in this repo until then.
