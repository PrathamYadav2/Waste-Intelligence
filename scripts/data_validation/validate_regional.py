"""validate_regional script: runs validation and writes report."""
import json
import os
from src.config import get_settings
from src.data.validation import validate_regional_csv

def main():
    settings = get_settings()
    regional_path = settings.regional_data_path or "Project Data/Regional Data/regional_waste_by_year.csv"
    print(f"Validating regional data: {regional_path}")
    report = validate_regional_csv(regional_path)
    print(f"Passed: {report.passed}")
    print(f"Total samples: {report.total_samples}")
    print(f"Issues: {report.issues}")

    os.makedirs("reports/documentation", exist_ok=True)
    out_file = "reports/documentation/regional_validation_report.json"
    with open(out_file, "w") as f:
        json.dump({
            "dataset": report.dataset,
            "passed": report.passed,
            "total_samples": report.total_samples,
            "issues": report.issues,
            "class_distribution": report.class_distribution
        }, f, indent=2)
    print(f"Report written to {out_file}")

if __name__ == "__main__":
    main()
