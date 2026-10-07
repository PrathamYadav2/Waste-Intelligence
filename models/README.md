# 🤖 Machine Learning Model Registry & Artifacts

This directory contains the serialized model artifacts, weights, and performance registries for the Waste Intelligence platform.

---

## 📂 Model Inventory

```
models/
├── image_classifier/
│   ├── realwaste_mobilenet_v3.pth   # PyTorch Vision Model weights (MobileNetV3-Small)
│   ├── test_samples.pt              # Holdout benchmark evaluation tensors
│   └── README.md                    # Detailed Vision Model guide & Python usage
├── forecasting/                     # Regional forecasting configuration & cache
├── explainability/                  # Grad-CAM heatmap visualization hooks
├── registry.json                    # Central model registry with verified metrics
└── README.md                        # This document
```

---

## 🔍 Model Overview

### 1. Computer Vision: `RealWaste-MobileNetV3`
- **Location:** [`models/image_classifier/realwaste_mobilenet_v3.pth`](file:///c:/Users/pratham/Desktop/Waste%20Project/models/image_classifier/realwaste_mobilenet_v3.pth)
- **Architecture:** PyTorch `MobileNetV3-Small`
- **Classes (9):** Cardboard, Food Organics, Glass, Metal, Miscellaneous Trash, Paper, Plastic, Textile Trash, Vegetation.
- **Test Accuracy:** **78.26%** | **Macro F1:** **79.26%**
- **Documentation & Code:** See [`models/image_classifier/README.md`](file:///c:/Users/pratham/Desktop/Waste%20Project/models/image_classifier/README.md).

### 2. Time-Series Forecaster: `Damped Linear Trend Forecaster`
- **Location:** [`data/processed/forecasts_2024_2027.csv`](file:///c:/Users/pratham/Desktop/Waste%20Project/data/processed/forecasts_2024_2027.csv)
- **Scope:** 12 Urban Local Bodies across Maharashtra (2024–2027 horizon).
- **Validation Backtest (2020–2023):**
  - **MAE:** `72.07 TPD` (Best among ARIMA, Holt-Winters, Naive, Linear)
  - **MAPE:** `3.17%`
  - **R² Score:** `0.9944`

---

## ⚠️ Note on Opening Model Files
File extensions like `.pth` are binary serialized PyTorch models. They cannot be opened directly by double-clicking in Windows Explorer.

- **To run visually:** Use the Web Dashboard via **`start.bat`** or browse to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.
- **To test from CLI:** Run `python predict.py "path/to/image.jpg"`.
