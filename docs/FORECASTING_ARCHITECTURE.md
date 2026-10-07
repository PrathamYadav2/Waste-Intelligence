# Forecasting & Capacity Planning
**Target:** `gen_total_ulb_tpd`. **Entity:** region. **Known size:** 96 rows = 12 regions x 8 years, so series are short.
## Pipeline
Validate -> clean -> features (lags, growth rates, region encoding; final list TBD) -> **time-based split (never random)** -> baseline -> candidates -> evaluate -> select -> forecast -> capacity gap -> priority -> recommendation.
## Candidates
| Model | Note |
|---|---|
| Naive / previous-year | Mandatory baseline |
| Linear Regression | Simple, interpretable |
| Random Forest | Needs care with 96 rows |
| Gradient Boosting | Same caution |
| ARIMA | Only where per-region length permits; may be inappropriate with ~8 points (decide at implementation) |

No LSTM. Metrics: MAE, RMSE, R2 and MAPE where appropriate (R2/MAPE unstable on tiny holdouts; report with caveats). Prefer expanding-window/rolling-origin validation per region.
## Capacity gap
`gap = forecast - capacity`. Capacity data source is **TO_BE_VERIFIED_DURING_IMPLEMENTATION**; if absent, report pressure relative to historical values and say so. No rankings until implementation.
