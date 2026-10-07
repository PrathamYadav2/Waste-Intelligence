"""Validation interfaces and functions for datasets."""
import os
from dataclasses import dataclass, field
import pandas as pd
from PIL import Image

@dataclass
class ValidationReport:
    dataset: str
    passed: bool
    total_samples: int = 0
    valid_samples: int = 0
    invalid_samples: int = 0
    class_distribution: dict = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

def validate_image_dataset(adapter) -> ValidationReport:
    issues = []
    class_counts = {}
    valid = 0
    invalid = 0

    samples = adapter.get_all_samples()
    for img_path, label in samples:
        class_counts[label] = class_counts.get(label, 0) + 1
        if not os.path.exists(img_path):
            issues.append(f"Missing file: {img_path}")
            invalid += 1
            continue
        try:
            with Image.open(img_path) as img:
                img.verify()
            with Image.open(img_path) as img:
                if img.size[0] <= 0 or img.size[1] <= 0:
                    issues.append(f"Invalid dimensions: {img_path}")
                    invalid += 1
                else:
                    valid += 1
        except Exception as e:
            issues.append(f"Corrupted image {img_path}: {e}")
            invalid += 1

    passed = (invalid == 0) and (valid > 0)
    return ValidationReport(
        dataset=adapter.name,
        passed=passed,
        total_samples=len(samples),
        valid_samples=valid,
        invalid_samples=invalid,
        class_distribution=class_counts,
        issues=issues
    )

def validate_regional_csv(path: str) -> ValidationReport:
    issues = []
    if not os.path.exists(path):
        return ValidationReport(dataset="regional", passed=False, issues=[f"File not found: {path}"])

    df = pd.read_csv(path)
    total_rows = len(df)
    
    # Required columns
    required_cols = ["report_year", "region", "gen_total_ulb_tpd", "latitude", "longitude"]
    for col in required_cols:
        if col not in df.columns:
            issues.append(f"Missing column: {col}")

    # Check nulls in target
    if "gen_total_ulb_tpd" in df.columns:
        null_target = df["gen_total_ulb_tpd"].isnull().sum()
        if null_target > 0:
            issues.append(f"Target 'gen_total_ulb_tpd' has {null_target} missing values")
        neg_target = (df["gen_total_ulb_tpd"] <= 0).sum()
        if neg_target > 0:
            issues.append(f"Target 'gen_total_ulb_tpd' has {neg_target} non-positive values")

    # Check region count
    regions = df["region"].unique() if "region" in df.columns else []
    if len(regions) != 12:
        issues.append(f"Expected 12 regions, found {len(regions)}")

    # Check duplicate (region, report_year)
    if "region" in df.columns and "report_year" in df.columns:
        dups = df.duplicated(subset=["region", "report_year"]).sum()
        if dups > 0:
            issues.append(f"Found {dups} duplicate (region, report_year) pairs")

    passed = (len(issues) == 0)
    return ValidationReport(
        dataset="regional_waste",
        passed=passed,
        total_samples=total_rows,
        valid_samples=total_rows if passed else total_rows - len(issues),
        invalid_samples=0 if passed else len(issues),
        class_distribution={"regions": len(regions), "rows": total_rows},
        issues=issues
    )
