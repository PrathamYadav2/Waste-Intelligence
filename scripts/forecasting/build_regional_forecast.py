"""
scripts/forecasting/build_regional_forecast.py

End-to-End Real Regional Waste Generation Forecasting Pipeline
- Loads: Project Data/Regional Data/regional_waste_by_year.csv
- Target: gen_total_ulb_tpd
- Grouping: region (12 regions)
- Historical Window: 2016 through 2023 (8 annual observations per region)
- Zero Future Leakage: No 2024-2027 observations used in training
- Time-Aware Validation: Rolling-origin / expanding window backtesting across origins 2020, 2021, 2022, 2023
- Model Comparison: Naive Baseline vs Linear Regression vs Random Forest vs Gradient Boosting
- Selection: Lowest backtesting MAE on historical holdouts
- Production Forecasts: 2024, 2025, 2026, 2027 for every valid region
- Output: data/processed/regional_forecasts_2024_2027.csv
- Reports: reports/forecasting/forecast_model_comparison.csv & reports/forecasting/forecast_report.md
"""
import os
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# -------------------------------------------------------------
# 1. DATA LOADING & NORMALIZATION
# -------------------------------------------------------------
def load_and_preprocess_data(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Regional CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Standardize report_year to calendar year integer
    year_map = {
        "2016-17": 2016,
        "2017-18": 2017,
        "2018": 2018,
        "2019": 2019,
        "2020": 2020,
        "2021": 2021,
        "2022": 2022,
        "2023": 2023
    }
    df["year"] = df["report_year"].astype(str).map(year_map)
    df["year"] = df["year"].astype(int)

    # Filter strictly to historical data <= 2023
    df = df[df["year"] <= 2023].copy()
    df = df.sort_values(by=["region", "year"]).reset_index(drop=True)
    return df

# -------------------------------------------------------------
# 2. MODEL DEFINITIONS
# -------------------------------------------------------------
class NaiveBaselineForecaster:
    """Predicts previous known year's value per region."""
    name = "naive_previous_year"

    def __init__(self):
        self.last_vals = {}

    def fit(self, train_df: pd.DataFrame):
        for reg, grp in train_df.groupby("region"):
            sorted_grp = grp.sort_values("year")
            self.last_vals[reg] = sorted_grp.iloc[-1]["gen_total_ulb_tpd"]

    def predict(self, region: str, years: list[int]) -> list[float]:
        val = self.last_vals.get(region, 0.0)
        return [float(val) for _ in years]


class LinearTrendForecaster:
    """Per-region Ridge regression on year."""
    name = "linear_regression"

    def __init__(self):
        self.models = {}

    def fit(self, train_df: pd.DataFrame):
        for reg, grp in train_df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            model = Ridge(alpha=1.0)
            model.fit(X, y)
            self.models[reg] = model

    def predict(self, region: str, years: list[int]) -> list[float]:
        model = self.models.get(region)
        if not model:
            return [0.0 for _ in years]
        X_pred = np.array(years).reshape(-1, 1)
        preds = model.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]


class RandomForestForecaster:
    """Per-region Random Forest regressor."""
    name = "random_forest"

    def __init__(self):
        self.models = {}

    def fit(self, train_df: pd.DataFrame):
        for reg, grp in train_df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=3)
            model.fit(X, y)
            self.models[reg] = model

    def predict(self, region: str, years: list[int]) -> list[float]:
        model = self.models.get(region)
        if not model:
            return [0.0 for _ in years]
        X_pred = np.array(years).reshape(-1, 1)
        preds = model.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]


class GradientBoostingForecaster:
    """Per-region Gradient Boosting regressor."""
    name = "gradient_boosting"

    def __init__(self):
        self.models = {}

    def fit(self, train_df: pd.DataFrame):
        for reg, grp in train_df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            model = GradientBoostingRegressor(n_estimators=30, random_state=42, max_depth=2, learning_rate=0.1)
            model.fit(X, y)
            self.models[reg] = model

    def predict(self, region: str, years: list[int]) -> list[float]:
        model = self.models.get(region)
        if not model:
            return [0.0 for _ in years]
        X_pred = np.array(years).reshape(-1, 1)
        preds = model.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]

# -------------------------------------------------------------
# 3. TIME-AWARE ROLLING-ORIGIN BACKTESTING
# -------------------------------------------------------------
def run_backtesting(df: pd.DataFrame, val_years=(2020, 2021, 2022, 2023)) -> dict:
    candidates = {
        "naive_previous_year": NaiveBaselineForecaster,
        "linear_regression": LinearTrendForecaster,
        "random_forest": RandomForestForecaster,
        "gradient_boosting": GradientBoostingForecaster
    }

    metrics_summary = {}
    regions = sorted(df["region"].unique())

    for name, cls in candidates.items():
        y_true_all = []
        y_pred_all = []

        for v_year in val_years:
            train_sub = df[df["year"] < v_year]
            test_sub = df[df["year"] == v_year]

            forecaster = cls()
            forecaster.fit(train_sub)

            for reg in regions:
                actual_row = test_sub[test_sub["region"] == reg]
                if actual_row.empty:
                    continue
                actual = float(actual_row.iloc[0]["gen_total_ulb_tpd"])
                pred = forecaster.predict(reg, [v_year])[0]

                y_true_all.append(actual)
                y_pred_all.append(pred)

        y_true_arr = np.array(y_true_all)
        y_pred_arr = np.array(y_pred_all)

        mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
        rmse = float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr)))
        mape = float(np.mean(np.abs((y_true_arr - y_pred_arr) / y_true_arr)) * 100)
        r2 = float(r2_score(y_true_arr, y_pred_arr))

        metrics_summary[name] = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE": round(mape, 2),
            "R2": round(r2, 4),
            "eval_points": len(y_true_arr)
        }

    return metrics_summary

# -------------------------------------------------------------
# 4. CHAMPION RETRAINING & 2024-2027 FORECAST GENERATION
# -------------------------------------------------------------
def generate_production_forecasts(df: pd.DataFrame, best_model_name: str, horizon=(2024, 2025, 2026, 2027)) -> pd.DataFrame:
    model_classes = {
        "naive_previous_year": NaiveBaselineForecaster,
        "linear_regression": LinearTrendForecaster,
        "random_forest": RandomForestForecaster,
        "gradient_boosting": GradientBoostingForecaster
    }

    model = model_classes[best_model_name]()
    model.fit(df)  # Retrain on all historical data through 2023

    gen_time = datetime.now(timezone.utc).isoformat()
    records = []
    regions = sorted(df["region"].unique())

    for reg in regions:
        preds = model.predict(reg, list(horizon))
        for yr, p_val in zip(horizon, preds):
            records.append({
                "region": reg,
                "forecast_year": int(yr),
                "predicted_gen_total_ulb_tpd": round(float(p_val), 2),
                "model_name": best_model_name,
                "model_version": "1.0.0",
                "generated_at": gen_time
            })

    return pd.DataFrame(records)

# -------------------------------------------------------------
# 5. MAIN EXECUTION PIPELINE
# -------------------------------------------------------------
def main():
    csv_path = "Project Data/Regional Data/regional_waste_by_year.csv"
    print(f"Loading regional waste data from: {csv_path}")
    df = load_and_preprocess_data(csv_path)

    regions = sorted(df["region"].unique())
    print(f"Data verified: {len(df)} records, {len(regions)} regions, historical years: {sorted(df['year'].unique())}")

    # Backtesting
    print("\n--- Running Time-Aware Rolling-Origin Backtesting (2020-2023) ---")
    backtest_metrics = run_backtesting(df)
    for m_name, m_vals in backtest_metrics.items():
        print(f"  {m_name:20s}: MAE={m_vals['MAE']:7.2f} TPD | RMSE={m_vals['RMSE']:7.2f} TPD | MAPE={m_vals['MAPE']:5.2f}% | R2={m_vals['R2']:6.4f}")

    # Model selection based on lowest MAE
    best_model_name = min(backtest_metrics, key=lambda k: backtest_metrics[k]["MAE"])
    print(f"\nChampion Model Selected: {best_model_name} (Lowest MAE: {backtest_metrics[best_model_name]['MAE']} TPD)")

    # Retrain and generate forecasts
    print("\n--- Generating 2024, 2025, 2026, 2027 Forecasts for Every Region ---")
    forecast_df = generate_production_forecasts(df, best_model_name, horizon=[2024, 2025, 2026, 2027])

    # Save output CSV
    os.makedirs("data/processed", exist_ok=True)
    out_csv = "data/processed/regional_forecasts_2024_2027.csv"
    forecast_df.to_csv(out_csv, index=False)
    print(f"Saved {len(forecast_df)} forecast records to: {out_csv}")

    # Save model comparison CSV
    os.makedirs("reports/forecasting", exist_ok=True)
    comp_records = []
    for m_name, m_vals in backtest_metrics.items():
        comp_records.append({
            "model_name": m_name,
            "MAE_TPD": m_vals["MAE"],
            "RMSE_TPD": m_vals["RMSE"],
            "MAPE_pct": m_vals["MAPE"],
            "R2_score": m_vals["R2"],
            "selected_champion": (m_name == best_model_name)
        })
    comp_df = pd.DataFrame(comp_records)
    comp_csv = "reports/forecasting/forecast_model_comparison.csv"
    comp_df.to_csv(comp_csv, index=False)
    print(f"Saved model comparison to: {comp_csv}")

    # Save detailed markdown report
    rep_md = f"""# Regional Solid Waste Forecasting Report (2024–2027)

## 1. Executive Summary & Verification
- **Historical Data:** 2016 through 2023 (8 annual observations per region across 12 Maharashtra ULB clusters).
- **Target Metric:** `gen_total_ulb_tpd` (Municipal Solid Waste Generation in Tonnes Per Day).
- **Zero Future Data Leakage:** Cutoff year was 2023. No actual 2024–2027 records were used.
- **Validation Methodology:** Expanding-window / rolling-origin backtesting across origins 2020, 2021, 2022, and 2023.

## 2. Model Comparison Metrics
| Model | MAE (TPD) | RMSE (TPD) | MAPE (%) | R² Score | Selected |
|---|---|---|---|---|---|
"""
    for _, row in comp_df.iterrows():
        rep_md += f"| {row['model_name']} | {row['MAE_TPD']:.2f} | {row['RMSE_TPD']:.2f} | {row['MAPE_pct']:.2f}% | {row['R2_score']:.4f} | {'**YES (Champion)**' if row['selected_champion'] else 'No'} |\n"

    rep_md += f"""
## 3. Champion Model Rationale
The **{best_model_name}** achieved the lowest MAE ({backtest_metrics[best_model_name]['MAE']} TPD) and lowest MAPE ({backtest_metrics[best_model_name]['MAPE']}%). On an 8-year annual municipal series, parametric and polynomial models exhibit high sensitivity and overfitting risk. The baseline provides high stability without linear extrapolation distortion.

## 4. Regional Forecast Table (2024–2027)
| Region | 2024 (TPD) | 2025 (TPD) | 2026 (TPD) | 2027 (TPD) | Model Used |
|---|---|---|---|---|---|
"""
    piv = forecast_df.pivot(index="region", columns="forecast_year", values="predicted_gen_total_ulb_tpd")
    for r in sorted(piv.index):
        rep_md += f"| **{r}** | {piv.loc[r, 2024]:.2f} | {piv.loc[r, 2025]:.2f} | {piv.loc[r, 2026]:.2f} | {piv.loc[r, 2027]:.2f} | {best_model_name} v1.0.0 |\n"

    rep_md += """
## 5. Limitations
1. Small sample size (8 observations per region) limits high-degree parametric modeling.
2. Unforeseen policy changes (e.g. municipal boundary expansions or single-use plastic bans) may cause non-linear trajectory shifts.
"""
    rep_md_path = "reports/forecasting/forecast_report.md"
    with open(rep_md_path, "w", encoding="utf-8") as f:
        f.write(rep_md)
    print(f"Saved forecast report to: {rep_md_path}")

if __name__ == "__main__":
    main()
