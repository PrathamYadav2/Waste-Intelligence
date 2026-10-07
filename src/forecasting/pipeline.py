"""Forecasting pipeline interfaces, candidates, time-aware backtesting and forecasting."""
import os
import json
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ..data.adapters import RegionalWasteLoader
from ..vision.registry import register

class Forecaster(ABC):
    name: str
    @abstractmethod
    def fit(self, df: pd.DataFrame): ...
    @abstractmethod
    def predict(self, region: str, years: list[int]) -> list[float]: ...

class NaivePreviousYearForecaster(Forecaster):
    name = "naive_previous_year"
    def __init__(self):
        self.last_known = {}

    def fit(self, df: pd.DataFrame):
        for reg, grp in df.groupby("region"):
            sorted_grp = grp.sort_values("year")
            self.last_known[reg] = sorted_grp.iloc[-1]["gen_total_ulb_tpd"]

    def predict(self, region: str, years: list[int]) -> list[float]:
        val = self.last_known.get(region, 0.0)
        return [float(val) for _ in years]

class LinearTrendForecaster(Forecaster):
    name = "linear_regression"
    def __init__(self):
        self.models = {}

    def fit(self, df: pd.DataFrame):
        for reg, grp in df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            lr = Ridge(alpha=1.0)
            lr.fit(X, y)
            self.models[reg] = lr

    def predict(self, region: str, years: list[int]) -> list[float]:
        lr = self.models.get(region)
        if not lr:
            return [0.0 for _ in years]
        X_pred = np.array(years).reshape(-1, 1)
        preds = lr.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]

class RandomForestTrendForecaster(Forecaster):
    name = "random_forest"
    def __init__(self):
        self.models = {}
        self.last_vals = {}

    def fit(self, df: pd.DataFrame):
        for reg, grp in df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            rf = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=3)
            rf.fit(X, y)
            self.models[reg] = rf
            self.last_vals[reg] = y[-1]

    def predict(self, region: str, years: list[int]) -> list[float]:
        rf = self.models.get(region)
        if not rf:
            return [0.0 for _ in years]
        # RF trees cannot extrapolate linear trends beyond max train year;
        # will predict boundary leaf values.
        X_pred = np.array(years).reshape(-1, 1)
        preds = rf.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]

class GradientBoostingTrendForecaster(Forecaster):
    name = "gradient_boosting"
    def __init__(self):
        self.models = {}

    def fit(self, df: pd.DataFrame):
        for reg, grp in df.groupby("region"):
            X = grp[["year"]].values
            y = grp["gen_total_ulb_tpd"].values
            gb = GradientBoostingRegressor(n_estimators=30, random_state=42, max_depth=2, learning_rate=0.1)
            gb.fit(X, y)
            self.models[reg] = gb

    def predict(self, region: str, years: list[int]) -> list[float]:
        gb = self.models.get(region)
        if not gb:
            return [0.0 for _ in years]
        X_pred = np.array(years).reshape(-1, 1)
        preds = gb.predict(X_pred)
        return [float(max(0.0, p)) for p in preds]


CANDIDATES = {
    "naive_previous_year": NaivePreviousYearForecaster,
    "linear_regression": LinearTrendForecaster,
    "random_forest": RandomForestTrendForecaster,
    "gradient_boosting": GradientBoostingTrendForecaster
}

def rolling_origin_backtesting(df: pd.DataFrame, val_years=(2020, 2021, 2022, 2023)) -> dict:
    """
    Time-aware rolling origin / expanding window validation across all 12 regions.
    For each test year in val_years:
      Train on all years < test_year
      Validate on test_year
    Calculates MAE, RMSE, and MAPE per model.
    """
    results = {}
    regions = df["region"].unique()

    for model_name, model_cls in CANDIDATES.items():
        all_y_true = []
        all_y_pred = []

        for val_year in val_years:
            train_df = df[df["year"] < val_year]
            test_df = df[df["year"] == val_year]

            model = model_cls()
            model.fit(train_df)

            for reg in regions:
                actual_row = test_df[test_df["region"] == reg]
                if actual_row.empty:
                    continue
                actual = float(actual_row.iloc[0]["gen_total_ulb_tpd"])
                pred = model.predict(reg, [val_year])[0]

                all_y_true.append(actual)
                all_y_pred.append(pred)

        all_y_true = np.array(all_y_true)
        all_y_pred = np.array(all_y_pred)

        mae = float(mean_absolute_error(all_y_true, all_y_pred))
        rmse = float(np.sqrt(mean_squared_error(all_y_true, all_y_pred)))
        mape = float(np.mean(np.abs((all_y_true - all_y_pred) / all_y_true)) * 100)
        r2 = float(r2_score(all_y_true, all_y_pred))

        results[model_name] = {
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape,
            "R2": r2,
            "samples_evaluated": len(all_y_true)
        }

    return results

def train_and_forecast_all_regions(df: pd.DataFrame, best_model_name: str, horizon_years=(2024, 2025, 2026, 2027)) -> dict:
    """
    Fits best model on all historical data through 2023.
    Forecasts target years for every valid region.
    Computes statistically defensive prediction intervals based on historical residual standard error.
    """
    model_cls = CANDIDATES[best_model_name]
    model = model_cls()
    model.fit(df)

    # Compute region-specific residual std for prediction interval
    regional_residuals = {}
    for reg, grp in df.groupby("region"):
        preds_hist = model.predict(reg, grp["year"].tolist())
        diffs = grp["gen_total_ulb_tpd"].values - np.array(preds_hist)
        regional_residuals[reg] = float(np.std(diffs)) if len(diffs) > 1 else 10.0

    forecasts = []
    regions = sorted(df["region"].unique())

    for reg in regions:
        preds = model.predict(reg, list(horizon_years))
        std_err = regional_residuals.get(reg, 20.0)

        for step, (yr, pred_val) in enumerate(zip(horizon_years, preds), 1):
            # Interval widens with forecast step sqrt(step)
            margin = 1.96 * std_err * np.sqrt(step)
            lower = max(0.0, float(pred_val - margin))
            upper = float(pred_val + margin)

            forecasts.append({
                "region": reg,
                "forecast_year": yr,
                "predicted_gen_total_ulb_tpd": round(float(pred_val), 2),
                "lower_bound": round(lower, 2),
                "upper_bound": round(upper, 2),
                "model_name": best_model_name,
                "model_version": "1.0.0"
            })

    return {
        "model_name": best_model_name,
        "horizon_years": list(horizon_years),
        "total_forecasts": len(forecasts),
        "forecasts": forecasts
    }
