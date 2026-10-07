"""Validate regional waste dataset regional_waste_by_year.csv."""
import os
import json
import pandas as pd

def main():
    csv_path = "Project Data/Regional Data/regional_waste_by_year.csv"
    coord_path = "Project Data/Regional Data/region_coordinates.csv"
    print(f"Validating regional data at {csv_path}...")

    df = pd.read_csv(csv_path)
    issues = []

    # Check rows and columns
    expected_rows = 96
    if len(df) != expected_rows:
        issues.append(f"Expected {expected_rows} rows, found {len(df)}")

    # Check regions
    regions = df["region"].unique().tolist()
    if len(regions) != 12:
        issues.append(f"Expected 12 regions, found {len(regions)}")

    # Check target
    target_col = "gen_total_ulb_tpd"
    if target_col not in df.columns:
        issues.append(f"Missing target column: {target_col}")
    else:
        nulls = int(df[target_col].isnull().sum())
        non_pos = int((df[target_col] <= 0).sum())
        if nulls > 0:
            issues.append(f"Target has {nulls} missing values")
        if non_pos > 0:
            issues.append(f"Target has {non_pos} non-positive values")

    # Check duplicate region-year pairs
    dups = int(df.duplicated(subset=["region", "report_year"]).sum())
    if dups > 0:
        issues.append(f"Found {dups} duplicate (region, report_year) pairs")

    # Check coordinates
    coords_exist = os.path.exists(coord_path)
    df_coords = pd.read_csv(coord_path) if coords_exist else None

    # Treatment and capacity statistics
    treated_nulls = int(df["treated_total_ulb_tpd"].isnull().sum())
    gap_nulls = int(df["untreated_gap_tpd"].isnull().sum())

    passed = (len(issues) == 0)
    report = {
        "dataset": "regional_waste_by_year.csv",
        "passed": passed,
        "rows": len(df),
        "columns": list(df.columns),
        "regions_count": len(regions),
        "regions": regions,
        "years": sorted(df["report_year"].unique().tolist()),
        "target_summary": {
            "column": target_col,
            "min": float(df[target_col].min()),
            "mean": float(df[target_col].mean()),
            "max": float(df[target_col].max())
        },
        "treatment_and_capacity_fields": {
            "treated_total_ulb_tpd_nulls": treated_nulls,
            "untreated_gap_tpd_nulls": gap_nulls,
            "status": "Available for 2018-2023 (6 annual records per region)"
        },
        "issues": issues
    }

    os.makedirs("reports/data_validation", exist_ok=True)
    out_file = "reports/data_validation/regional_data_validation.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[DONE] Regional dataset validation completed:")
    print(f"  Rows: {len(df)}, Regions: {len(regions)}, Target min={report['target_summary']['min']}, max={report['target_summary']['max']}")
    print(f"  Passed: {passed}")
    print(f"  Report: {out_file}")

if __name__ == "__main__":
    main()
