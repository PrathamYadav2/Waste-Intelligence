"""Pipeline orchestrator implementing all system stages."""
import argparse
import os

from src.config import get_settings
from src.data.validation import validate_regional_csv, validate_image_dataset
from src.data.adapters import RealWasteAdapter, TrashNetAdapter, RegionalWasteLoader
from src.vision.classifier import ClassifierFactory
from src.explainability.gradcam import explain
from src.recovery.scoring import RecoveryInput, score_recovery
from src.recommendations.engine import recommend
from src.analytics.capacity import analyze_all_regions
from PIL import Image

STAGES = [
    "validate_data", "train_classifier", "evaluate_cross_dataset", "explain",
    "train_forecaster", "forecast", "capacity_analysis", "recommend"
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", choices=STAGES, required=True)
    a = p.parse_args()

    settings = get_settings()

    if a.stage == "validate_data":
        print("Executing validate_data stage...")
        import scripts.data_validation.validate_regional as vr
        import scripts.data_validation.validate_images as vi
        vr.main()
        vi.main()
        print("Data validation stage completed.")

    elif a.stage == "train_classifier":
        print("Executing train_classifier stage...")
        import scripts.training.train_classifier as tc
        tc.main()
        print("Train classifier stage completed.")

    elif a.stage == "evaluate_cross_dataset":
        print("Executing evaluate_cross_dataset stage...")
        import scripts.evaluation.evaluate_cross_dataset as ecd
        ecd.main()
        print("Cross-dataset evaluation stage completed.")

    elif a.stage == "explain":
        print("Executing explain (Grad-CAM) stage...")
        clf = ClassifierFactory.create("mobilenet_v3_small")
        clf.load("models/image_classifier/realwaste_mobilenet_v3.pth")
        sample_img = "reports/figures/sample_gradcam_overlay.jpg"
        if not os.path.exists(sample_img):
            test_path = "Project Data/Image Data/RealWaste/Cardboard/Cardboard_1.jpg"
            img = Image.open(test_path)
            _, overlay = explain(clf, img)
            Image.fromarray(overlay).save(sample_img)
        print(f"Grad-CAM overlay available at {sample_img}")

    elif a.stage in ["train_forecaster", "forecast"]:
        print("Executing forecasting stage...")
        import scripts.forecasting.run_forecast as rf
        rf.main()
        print("Forecasting stage completed.")

    elif a.stage == "capacity_analysis":
        print("Executing capacity_analysis stage...")
        loader = RegionalWasteLoader("Project Data/Regional Data/regional_waste_by_year.csv")
        df = loader.load()
        res = analyze_all_regions(df)
        print(f"Capacity and pressure analyzed for {len(res)} regions.")

    elif a.stage == "recommend":
        print("Executing recommend stage...")
        rec_res = score_recovery(RecoveryInput(waste_class="Plastic", condition="clean"))
        reco = recommend("Plastic", 0.85, rec_res, {"pressure_index": 70.8, "category": "High"})
        print(f"Action: {reco.action}")
        print(f"Explanation: {reco.explanation}")

if __name__ == "__main__":
    main()
