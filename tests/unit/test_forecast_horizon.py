import pytest
import pandas as pd
import os

def test_forecast_file_exists():
    path = "data/processed/regional_forecasts_2024_2027.csv"
    assert os.path.exists(path), f"File {path} does not exist"

def test_forecast_horizon_and_regions():
    df = pd.read_csv("data/processed/regional_forecasts_2024_2027.csv")

    # 1. Verify exact columns specified by user
    expected_cols = [
        "region", "forecast_year", "predicted_gen_total_ulb_tpd",
        "model_name", "model_version", "generated_at"
    ]
    for c in expected_cols:
        assert c in df.columns, f"Expected column {c} not found in CSV"

    # 2. Verify exact forecast years
    expected_years = [2024, 2025, 2026, 2027]
    unique_years = sorted(df["forecast_year"].unique().tolist())
    assert unique_years == expected_years, f"Expected {expected_years}, got {unique_years}"

    # 3. Verify all 12 regions
    regions = df["region"].unique()
    assert len(regions) == 12, f"Expected 12 regions, got {len(regions)}"

    # 4. Total records must equal number of regions * 4
    assert len(df) == 12 * 4, f"Expected 48 records, got {len(df)}"

    # 5. Each region has exactly 4 records with valid positive numbers and no NaNs
    for r in regions:
        r_df = df[df["region"] == r]
        assert len(r_df) == 4, f"Region {r} has {len(r_df)} records instead of 4"
        assert sorted(r_df["forecast_year"].tolist()) == expected_years
        for _, row in r_df.iterrows():
            assert row["predicted_gen_total_ulb_tpd"] > 0
            assert pd.notnull(row["predicted_gen_total_ulb_tpd"])
            assert row["model_name"] in ["naive_previous_year", "damped_trend_forecaster"]
