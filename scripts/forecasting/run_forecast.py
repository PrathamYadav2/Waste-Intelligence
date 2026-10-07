"""scripts/forecasting/run_forecast.py: Time-aware evaluation, model selection and 2024-2027 forecasts."""
import os
import json
import pandas as pd
from src.config import get_settings
from src.data.adapters import RegionalWasteLoader
from src.forecasting.pipeline import rolling_origin_backtesting, train_and_forecast_all_regions
from src.vision.registry import register

def main():
    settings = get_settings()
    regional_path = settings.regional_data_path or "Project Data/Regional Data/regional_waste_by_year.csv"
    
    loader = RegionalWasteLoader(regional_path)
    df = loader.load()
    print(f"Loaded {len(df)} rows across {df['region'].nunique()} regions, years: {sorted(df['year'].unique())}")

    print("--- Running Rolling-Origin Backtesting (2020-2023) ---")
    backtest_metrics = rolling_origin_backtesting(df, val_years=(2020, 2021, 2022, 2023))
    print("Backtesting Results:")
    for model_name, m in backtest_metrics.items():
        print(f"  {model_name:20s}: MAE={m['MAE']:8.2f}, RMSE={m['RMSE']:8.2f}, MAPE={m['MAPE']:5.2f}%, R2={m['R2']:6.3f}")

    # Select best model based on MAE (or RMSE)
    best_model_name = min(backtest_metrics, key=lambda k: backtest_metrics[k]["MAE"])
    print(f"\n--> Selected Best Model: {best_model_name} (lowest MAE: {backtest_metrics[best_model_name]['MAE']:.2f})")

    # Generate forecasts for 2024, 2025, 2026, 2027
    print("\n--- Generating 2024-2027 Forecasts on Historical Data through 2023 ---")
    forecast_results = train_and_forecast_all_regions(df, best_model_name, horizon_years=(2024, 2025, 2026, 2027))
    
    # Save forecasts to JSON and CSV
    os.makedirs("reports/forecasting", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    fc_df = pd.DataFrame(forecast_results["forecasts"])
    fc_df.to_csv("data/processed/forecasts_2024_2027.csv", index=False)
    
    # Save complete evaluation & forecast report
    full_report = {
        "historical_period": "2016-2023",
        "target": "gen_total_ulb_tpd",
        "regions": sorted(df["region"].unique().tolist()),
        "validation_strategy": "rolling_origin_expanding_window",
        "candidate_models": backtest_metrics,
        "selected_model": best_model_name,
        "selected_model_metrics": backtest_metrics[best_model_name],
        "horizon_years": [2024, 2025, 2026, 2027],
        "forecasts": forecast_results["forecasts"]
    }
    with open("reports/forecasting/forecasting_evaluation_report.json", "w") as f:
        json.dump(full_report, f, indent=2)

    # Register forecaster model
    register(
        kind="forecaster",
        name=best_model_name,
        version="1.0.0",
        artifact_uri="data/processed/forecasts_2024_2027.csv",
        metrics=backtest_metrics[best_model_name],
        metadata={"horizon_years": [2024, 2025, 2026, 2027], "regions_count": len(full_report["regions"])}
    )

    print("Forecasting run complete! Report written to reports/forecasting/forecasting_evaluation_report.json")

if __name__ == "__main__":
    main()
