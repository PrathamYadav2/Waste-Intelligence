# ♻️ AI-Based Waste Segregation, Recycling Analytics & Regional Decision Intelligence System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Pytest-14%20Passing-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Verified-success.svg)]()

> **An End-to-End Decision Intelligence Platform** combining deep-learning computer vision, explainable AI (Grad-CAM), material recyclability analytics, and empirical regional time-series forecasting across 12 major Maharashtra municipal urban clusters.

---

## 🌟 Core System Innovation

This is not a standalone toy waste classifier. It solves the complete circular waste lifecycle:

$$\text{Image} \longrightarrow \text{AI Vision} \longrightarrow \text{Material} \longrightarrow \text{Recycling Potential} \longrightarrow \text{AI Recommendation} \longrightarrow \text{Regional Forecast} \longrightarrow \text{Decision Action}$$

1. **AI Computer Vision (MobileNetV3):** Classifies waste items across 9 RealWaste categories with multi-view Test-Time Augmentation (TTA) and aspect-ratio preservation.
2. **Explainable AI (Grad-CAM):** Generates backpropagated gradient heatmaps showing the visual features that drove the prediction.
3. **Deep Recycling Potential Engine:** Evaluates recyclability indices (0–100%), Indian secondary scrap market rates (₹/kg), material degradation limits, downcycling risks, and industrial processing pathways.
4. **Multi-Tier AI Recommendation Engine:** Formulates tailored directives across three distinct stakeholders:
   - 🏠 **Citizen Protocol:** At-source segregation, pre-cleaning, and bin assignment (Green/Blue/Black).
   - 🏭 **Municipal MRF Directives:** Material Recovery Facility processing, optical sorting, and baling.
   - 🔄 **Circular Economy Offtake:** Industrial buyer linkages, EPR credit eligibility, and carbon offset ($CO_2$ & water conserved).
5. **Regional Municipal Waste Forecasting (2024–2027):** Trend-aware regression projections across 12 Maharashtra urban local bodies (ULBs) with $\pm 1.96\sigma$ prediction intervals.
6. **Interactive Geographic Map:** Geospatial visualization of municipal waste load, treatment capacity deficits, and district action plans.

---

## 🚀 Quick Start & How to Run

### Method 1: Windows One-Click (Easiest)
Simply double-click on either of these files inside the folder:
- **`start.bat`** (or **`Launch_Waste_AI.bat`**)

*The script starts the FastAPI uvicorn server and **automatically opens your web browser** to `http://127.0.0.1:8000/`.*

---

### Method 2: Git Bash / Linux / macOS / WSL
Open your terminal in the project directory and execute:
```bash
./run.sh
```
*To run the automated test suite:*
```bash
./run.sh test
```

---

### Method 3: Manual Python Execution
```bash
# 1. Activate environment / set PYTHONPATH
set PYTHONPATH=.        # On Windows CMD
$env:PYTHONPATH="."     # On Windows PowerShell
export PYTHONPATH="."   # On Linux / macOS

# 2. Run the server
python app.py
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in Google Chrome or any modern browser.

---

## 🧠 Machine Learning & Analytical Models

### 1. Primary Vision Classifier (`MobileNetV3-Small`)
- **Dataset:** RealWaste (4,752 real-world images across 9 classes).
- **Architecture:** PyTorch `MobileNetV3-Small` transfer learning backbone with custom linear classification head.
- **Artifact:** `models/image_classifier/realwaste_mobilenet_v3.pth` (6.24 MB).
- **Holdout Test Accuracy:** **78.26%** | **Macro F1:** **79.26%** (evaluated on 713 independent samples).
- **Inference Enhancements:**
  - **Aspect-Ratio Preserving Pad:** Uses `pad_to_square` with neutral padding to prevent bottle/carton squashing.
  - **Multi-View TTA:** Ensembles natural padded, horizontal flipped, and center-cropped views for high real-world stability.

#### Per-Class Performance:
| Waste Class | F1-Score | Stream Nature | Recommended Bin |
| :--- | :---: | :--- | :--- |
| **Vegetation** | `0.939` | Organic Biodegradable | 🟢 Green Bin |
| **Food Organics** | `0.860` | Organic Wet Waste | 🟢 Green Bin |
| **Cardboard** | `0.857` | Dry Recyclable Fibre | 🔵 Blue Bin |
| **Textile Trash** | `0.804` | Secondary Recovery / Felt | ⚪ Special Segregation |
| **Metal** | `0.779` | High-Value Recyclable Alloy | 🔵 Blue Bin |
| **Glass** | `0.767` | Infinite Recyclable Cullet | 🔵 Blue Bin |
| **Paper** | `0.766` | Cellulose Pulp | 🔵 Blue Bin |
| **Plastic** | `0.750` | Polymer Resins (PET/HDPE) | 🔵 Blue Bin |
| **Misc Trash** | `0.612` | Non-recyclable / Inerts | ⚫ Black Bin (RDF) |

---

### 2. Explainable AI (`Grad-CAM`)
- Uses gradient-weighted class activation mapping backpropagated from the final convolutional feature layer (`model.features[12]`).
- Visualizes spatial saliency heatmaps overlaid on the uploaded photo to explain which pixels triggered the classification.

---

### 3. Regional Waste Forecasting Pipeline (2024–2027)
- **Target Variable:** `gen_total_ulb_tpd` (Municipal Solid Waste generation in Metric Tonnes Per Day).
- **Historical Data:** Audited annual observations (2016–2023) across 12 Maharashtra regions sourced from official CPCB / MPCB State SWM Annual Reports.
- **Model Selected via Rolling-Origin Backtesting:** Damped Linear Trend Forecaster (prevents runaway extrapolation on short 8-year series while capturing actual CAGR).
- **Evaluated Horizon:** Projections for 2024, 2025, 2026, and 2027 with empirical $\pm 1.96\sigma$ uncertainty intervals.
- **Validation Backtest Benchmark (2020–2023 Holdouts):**
  - **MAE:** `72.07 TPD` (Champion)
  - **MAPE:** `3.17%`
  - **R² Score:** `0.9944`

#### 2023 Baseline vs 2027 Net Projected Waste:
| Region | 2023 Baseline (TPD) | 2024 Forecast | 2027 Forecast | Net Change by 2027 | Annual Growth |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pune** | 4,439.9 | 4,510.7 | **4,723.2** | `+283.2 TPD (+6.4%) ↗` | `+70.8 TPD/yr` |
| **Nashik** | 2,245.1 | 2,277.7 | **2,375.7** | `+130.6 TPD (+5.8%) ↗` | `+32.7 TPD/yr` |
| **Thane** | 2,148.9 | 2,178.3 | **2,266.5** | `+117.6 TPD (+5.5%) ↗` | `+29.4 TPD/yr` |
| **Nagpur** | 1,688.0 | 1,710.6 | **1,778.3** | `+90.3 TPD (+5.3%) ↗` | `+22.6 TPD/yr` |
| **Aurangabad** | 1,858.6 | 1,878.9 | **1,939.8** | `+81.3 TPD (+4.4%) ↗` | `+20.3 TPD/yr` |
| **Chandrapur** | 503.5 | 514.9 | **549.3** | `+45.8 TPD (+9.1%) ↗` | `+11.5 TPD/yr` |
| **Amravati** | 809.9 | 818.2 | **843.2** | `+33.2 TPD (+4.1%) ↗` | `+8.3 TPD/yr` |
| **Kolhapur** | 823.1 | 828.8 | **845.8** | `+22.6 TPD (+2.7%) ↗` | `+5.7 TPD/yr` |
| **Raigad** | 593.4 | 630.8 | **743.2** | `+149.8 TPD (+25.2%) ↗`| `+37.5 TPD/yr` |
| **Navi Mumbai** | 743.0 | 741.2 | **735.9** | `-7.1 TPD (-1.0%) ↘` | `-1.8 TPD/yr` |
| **Kalyan** | 1,606.0 | 1,589.6 | **1,540.5** | `-65.5 TPD (-4.1%) ↘` | `-16.4 TPD/yr` |
| **Mumbai** | 6,690.0 | 6,509.3 | **5,967.0** | `-723.0 TPD (-10.8%) ↘`| `-180.8 TPD/yr`|

---

## 🔬 In-Depth Recycling Potential Metrics

For every detected waste item, the system calculates granular economic and circular metrics:
- **Recyclability Index:** Scaled percentage based on polymer/material purity.
- **Scrap Market Benchmark:** Indian secondary raw material market rates (e.g. Aluminium scrap at `Rs. 125-155/kg`, PET bottles at `Rs. 26-38/kg`, Corrugated Cardboard at `Rs. 11-15/kg`).
- **Lifecycle Loops:** Physical recycling degradation count (e.g. Aluminium & Glass = Infinite closed loops; Cardboard = 5-7 cycles; Plastic = 2-3 mechanical cycles).
- **Industrial Processing SOP:** Step-by-step industrial transformation (e.g., Hydrapulping, Caustic Flake Washing at 85°C, Induction Smelting at 660°C).
- **Target Buyer Industries:** Direct commercial off-takers (Foundries, Paper Mills, Textile Converters, Bio-CNG plants).

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Live health probe of PyTorch model, SQLite DB, and forecasting |
| `POST`| `/api/v1/waste/analyze` | Full multi-modal analysis (Vision + Grad-CAM + Recycling + AI Recommendation) |
| `GET` | `/api/v1/recommendations/simulate` | Interactive AI simulator for any waste category & batch weight (KG) |
| `GET` | `/api/v1/regional/overview` | Audited 2023 metrics, treatment shares, and pressure ranks for all 12 regions |
| `GET` | `/api/v1/regional/{region}` | Full historical timeline (2016–2023) and 2024–2027 forecasts for a region |
| `GET` | `/api/v1/forecast` | Programmatic forecast ledger for all 12 regions (48 records) |
| `GET` | `/api/v1/map` | Geospatial coordinates, generation, and risk markers for Leaflet map |

---

## 🧪 Automated Test Suite

All 14 unit and integration tests are verified passing:
```bash
python -m pytest tests/ -v
```

```
tests/integration/test_api_contract.py::test_health PASSED               [  7%]
tests/integration/test_api_contract.py::test_request_id_header PASSED    [ 14%]
tests/integration/test_api_contract.py::test_models_endpoint_implemented PASSED [ 21%]
tests/integration/test_api_contract.py::test_regional_overview_endpoint PASSED [ 28%]
tests/integration/test_api_contract.py::test_forecast_endpoint PASSED    [ 35%]
tests/unit/test_forecast_horizon.py::test_forecast_file_exists PASSED    [ 42%]
tests/unit/test_forecast_horizon.py::test_forecast_horizon_and_regions PASSED [ 50%]
tests/unit/test_forecast_requirements.py::test_forecast_years_exact PASSED [ 57%]
tests/unit/test_forecast_requirements.py::test_rolling_origin_validation PASSED [ 64%]
tests/unit/test_label_mapping_config.py::test_unmapped_classes_flagged PASSED [ 71%]
tests/unit/test_scaffold_contracts.py::test_routes_defined PASSED        [ 78%]
tests/unit/test_scaffold_contracts.py::test_candidates_exclude_lstm PASSED [ 85%]
tests/unit/test_scaffold_contracts.py::test_recovery_scoring_real PASSED [ 92%]
tests/unit/test_scaffold_contracts.py::test_classifier_factory_unsupported PASSED [100%]
======================= 14 passed in 13.52s =======================
```

---

## 📁 Repository Structure

```
Waste Project/
├── app.py                           # Server entrypoint (serves API & single unified UI)
├── app/
│   ├── index.html                   # High-aesthetic interactive Single-Page Dashboard
│   └── styles/                      # Design system tokens and styles
├── data/
│   └── processed/                   # Generated forecast CSVs (2024-2027)
├── models/
│   └── image_classifier/            # PyTorch MobileNetV3 weights (.pth) & test samples
├── Project Data/
│   ├── Image Data/                  # RealWaste, dataset-resized (TrashNet), TACO
│   ├── Recycling/                   # Statutory recycling material guidance
│   └── Regional Data/               # Official Maharashtra annual waste CSV (2016-2023)
├── reports/                         # Backtesting comparison reports, metrics, plots
├── scripts/
│   ├── forecasting/                 # ML backtesting & regional forecast scripts
│   └── training/                    # Vision model fine-tuning pipeline
├── src/
│   ├── api/                         # FastAPI routes, schemas, middleware
│   ├── explainability/              # PyTorch Grad-CAM visual heatmaps
│   ├── forecasting/                 # Time-series regression & backtesting
│   ├── recovery/                    # Material recoverability & recycling potential engine
│   ├── recommendations/             # Multi-tier AI recommendation engine
│   └── vision/                      # MobileNetV3 classifier & TTA pipeline
├── tests/                           # Unit and integration test suite
├── run.sh                           # Unified runner script (Bash / Linux / Git Bash)
├── start.bat                        # One-click Windows launcher (auto-opens browser)
└── waste_intelligence.db            # SQLite persistence database
```

---

## 📜 Regulatory Standards & Statutory Compliance
- **Solid Waste Management (SWM) Rules 2016** (Ministry of Environment, Forest and Climate Change, Govt. of India).
- **Plastic Waste Management (PWM) Rules 2022** (Extended Producer Responsibility - EPR framework).
- **Central Pollution Control Board (CPCB)** Municipal Solid Waste Characterization Guidelines.
