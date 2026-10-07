"""Script to train the primary RealWaste classifier."""
import os
import yaml
import json
from src.config import get_settings
from src.vision.training import train
from src.vision.classifier import ClassifierFactory
from src.vision.evaluation import evaluate_samples
import torch

def main():
    settings = get_settings()
    cfg = {
        "realwaste_path": settings.realwaste_path or "Project Data/Image Data/RealWaste",
        "output_dir": "models/image_classifier",
        "num_epochs": 3,
        "batch_size": 32,
        "learning_rate": 0.001,
        "seed": 42
    }
    print("=== Training RealWaste Classifier ===")
    res = train(cfg)
    print(f"Training complete. Best Val Acc: {res['val_accuracy']:.4f}")
    
    # Run test set evaluation
    test_samples_path = "models/image_classifier/test_samples.pt"
    if os.path.exists(test_samples_path):
        test_samples = torch.load(test_samples_path)
        clf = ClassifierFactory.create("mobilenet_v3_small")
        clf.load(res["artifact_path"])
        test_metrics = evaluate_samples(clf, test_samples)
        print(f"Test Accuracy: {test_metrics['accuracy']:.4f}, Macro F1: {test_metrics['macro_f1']:.4f}")
        
        os.makedirs("reports/model_evaluation", exist_ok=True)
        report_path = "reports/model_evaluation/realwaste_test_metrics.json"
        with open(report_path, "w") as f:
            json.dump(test_metrics, f, indent=2)
        print(f"Test report saved to {report_path}")

if __name__ == "__main__":
    main()
