# Regional Solid Waste Forecasting Report (2024–2027)

## 1. Executive Summary & Verification
- **Historical Data:** 2016 through 2023 (8 annual observations per region across 12 Maharashtra ULB clusters).
- **Target Metric:** `gen_total_ulb_tpd` (Municipal Solid Waste Generation in Tonnes Per Day).
- **Zero Future Data Leakage:** Cutoff year was 2023. No actual 2024–2027 records were used.
- **Validation Methodology:** Expanding-window / rolling-origin backtesting across origins 2020, 2021, 2022, and 2023.

## 2. Model Comparison Metrics
| Model | MAE (TPD) | RMSE (TPD) | MAPE (%) | R² Score | Selected |
|---|---|---|---|---|---|
| naive_previous_year | 72.07 | 127.18 | 3.17% | 0.9944 | **YES (Champion)** |
| linear_regression | 132.40 | 232.12 | 7.19% | 0.9813 | No |
| random_forest | 81.44 | 133.96 | 3.81% | 0.9938 | No |
| gradient_boosting | 73.52 | 123.44 | 3.40% | 0.9947 | No |

## 3. Champion Model Rationale
The **naive_previous_year** achieved the lowest MAE (72.07 TPD) and lowest MAPE (3.17%). On an 8-year annual municipal series, parametric and polynomial models exhibit high sensitivity and overfitting risk. The baseline provides high stability without linear extrapolation distortion.

## 4. Regional Forecast Table (2024–2027)
| Region | 2024 (TPD) | 2025 (TPD) | 2026 (TPD) | 2027 (TPD) | Model Used |
|---|---|---|---|---|---|
| **Amravati** | 809.92 | 809.92 | 809.92 | 809.92 | naive_previous_year v1.0.0 |
| **Aurangabad** | 1858.55 | 1858.55 | 1858.55 | 1858.55 | naive_previous_year v1.0.0 |
| **Chandrapur** | 503.46 | 503.46 | 503.46 | 503.46 | naive_previous_year v1.0.0 |
| **Kalyan** | 1606.00 | 1606.00 | 1606.00 | 1606.00 | naive_previous_year v1.0.0 |
| **Kolhapur** | 823.14 | 823.14 | 823.14 | 823.14 | naive_previous_year v1.0.0 |
| **Mumbai** | 6690.00 | 6690.00 | 6690.00 | 6690.00 | naive_previous_year v1.0.0 |
| **Nagpur** | 1688.01 | 1688.01 | 1688.01 | 1688.01 | naive_previous_year v1.0.0 |
| **Nashik** | 2245.07 | 2245.07 | 2245.07 | 2245.07 | naive_previous_year v1.0.0 |
| **Navi Mumbai** | 743.00 | 743.00 | 743.00 | 743.00 | naive_previous_year v1.0.0 |
| **Pune** | 4439.90 | 4439.90 | 4439.90 | 4439.90 | naive_previous_year v1.0.0 |
| **Raigad** | 593.36 | 593.36 | 593.36 | 593.36 | naive_previous_year v1.0.0 |
| **Thane** | 2148.90 | 2148.90 | 2148.90 | 2148.90 | naive_previous_year v1.0.0 |

## 5. Limitations
1. Small sample size (8 observations per region) limits high-degree parametric modeling.
2. Unforeseen policy changes (e.g. municipal boundary expansions or single-use plastic bans) may cause non-linear trajectory shifts.
