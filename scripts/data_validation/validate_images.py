"""validate_images script: runs validation on image datasets and outputs reports."""
import json
import os
from src.config import get_settings
from src.data.adapters import RealWasteAdapter, TrashNetAdapter
from src.data.validation import validate_image_dataset

def main():
    settings = get_settings()
    realwaste_path = settings.realwaste_path or "Project Data/Image Data/RealWaste"
    trashnet_path = settings.trashnet_path or "Project Data/Image Data/dataset-resized"

    print("--- Validating RealWaste ---")
    rw_adapter = RealWasteAdapter(realwaste_path)
    rw_report = validate_image_dataset(rw_adapter)
    print(f"RealWaste valid: {rw_report.valid_samples}/{rw_report.total_samples}, passed: {rw_report.passed}")

    print("--- Validating TrashNet ---")
    tn_adapter = TrashNetAdapter(trashnet_path)
    tn_report = validate_image_dataset(tn_adapter)
    print(f"TrashNet valid: {tn_report.valid_samples}/{tn_report.total_samples}, passed: {tn_report.passed}")

    os.makedirs("reports/documentation", exist_ok=True)
    out_file = "reports/documentation/image_validation_report.json"
    with open(out_file, "w") as f:
        json.dump({
            "realwaste": {
                "dataset": rw_report.dataset,
                "passed": rw_report.passed,
                "total_samples": rw_report.total_samples,
                "valid_samples": rw_report.valid_samples,
                "invalid_samples": rw_report.invalid_samples,
                "class_distribution": rw_report.class_distribution,
                "issues": rw_report.issues
            },
            "trashnet": {
                "dataset": tn_report.dataset,
                "passed": tn_report.passed,
                "total_samples": tn_report.total_samples,
                "valid_samples": tn_report.valid_samples,
                "invalid_samples": tn_report.invalid_samples,
                "class_distribution": tn_report.class_distribution,
                "issues": tn_report.issues
            }
        }, f, indent=2)
    print(f"Image validation report written to {out_file}")

if __name__ == "__main__":
    main()
