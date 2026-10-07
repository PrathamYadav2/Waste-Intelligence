import pytest
import pandas as pd
from src.forecasting.pipeline import rolling_origin_backtesting, train_and_forecast_all_regions
from src.data.adapters import RegionalWasteLoader

@pytest.fixture
def regional_df():
    loader = RegionalWasteLoader("Project Data/Regional Data/regional_waste_by_year.csv")
    return loader.load()

def test_forecast_years_exact(regional_df):
    """
    CRITICAL REQUIREMENT TEST:
    Verifies that forecast_years == [2024, 2025, 2026, 2027]
    and that every valid region has four forecast records.
    """
    results = train_and_forecast_all_regions(regional_df, "naive_previous_year", horizon_years=(2024, 2025, 2026, 2027))
    forecast_df = pd.DataFrame(results["forecasts"])
    
    unique_years = sorted(forecast_df["forecast_year"].unique().tolist())
    assert unique_years == [2024, 2025, 2026, 2027], f"Expected [2024, 2025, 2026, 2027], got {unique_years}"
    
    regions = regional_df["region"].unique()
    assert len(regions) == 12
    
    for reg in regions:
        reg_records = forecast_df[forecast_df["region"] == reg]
        assert len(reg_records) == 4, f"Region {reg} expected 4 forecast records, got {len(reg_records)}"
        years_for_reg = sorted(reg_records["forecast_year"].tolist())
        assert years_for_reg == [2024, 2025, 2026, 2027], f"Region {reg} missing forecast years: {years_for_reg}"
        
        # Verify predictions are positive numbers
        for _, row in reg_records.iterrows():
            assert row["predicted_gen_total_ulb_tpd"] > 0
            assert row["lower_bound"] >= 0
            assert row["upper_bound"] >= row["predicted_gen_total_ulb_tpd"]

def test_rolling_origin_validation(regional_df):
    """
    Verifies time-aware expanding window validation runs and returns valid metrics.
    """
    metrics = rolling_origin_backtesting(regional_df, val_years=(2022, 2023))
    assert "naive_previous_year" in metrics
    for model_name, m in metrics.items():
        assert m["MAE"] > 0
        assert m["RMSE"] > 0
        assert m["MAPE"] > 0
