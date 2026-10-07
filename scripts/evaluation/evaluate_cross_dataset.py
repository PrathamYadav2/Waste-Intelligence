"""Cross-dataset evaluation: RealWaste (train) -> TrashNet (secondary) -> TACO (external)."""
import os
import json
from src.config import get_settings
from src.vision.classifier import ClassifierFactory
from src.vision.evaluation import evaluate_samples
from src.data.adapters import TrashNetAdapter, TacoAdapter
from src.data.label_mapping import load_mapping_config

def evaluate_trashnet(classifier, trashnet_path: str) -> dict:
    print("\n=== Evaluating on Secondary Dataset: TrashNet ===")
    tn_adapter = TrashNetAdapter(trashnet_path)
    samples = tn_adapter.get_all_samples()
    
    # Mapping RealWaste -> TrashNet:
    # TrashNet labels are: ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
    # RealWaste classes are: ['Cardboard', 'Food Organics', 'Glass', 'Metal', 'Miscellaneous Trash', 'Paper', 'Plastic', 'Textile Trash', 'Vegetation']
    # Mapped correspondence:
    trashnet_to_realwaste = {
        "cardboard": "Cardboard",
        "glass": "Glass",
        "metal": "Metal",
        "paper": "Paper",
        "plastic": "Plastic",
        "trash": "Miscellaneous Trash"
    }

    mapped_samples = []
    unmapped_count = 0
    for img_path, tn_label in samples:
        rw_label = trashnet_to_realwaste.get(tn_label)
        if rw_label:
            mapped_samples.append((img_path, rw_label))
        else:
            unmapped_count += 1

    print(f"TrashNet samples: total={len(samples)}, mapped={len(mapped_samples)}, unmapped={unmapped_count}")
    metrics = evaluate_samples(classifier, mapped_samples, target_classes=list(trashnet_to_realwaste.values()))
    
    metrics["dataset"] = "TrashNet"
    metrics["role"] = "secondary_cross_dataset_evaluation"
    metrics["domain_shift_notes"] = "TrashNet consists of single items on white backgrounds, introducing domain shift relative to RealWaste outdoor/real-world scenes."
    metrics["mapped_classes"] = list(trashnet_to_realwaste.values())
    metrics["unmapped_realwaste_classes"] = ["Food Organics", "Textile Trash", "Vegetation"]
    return metrics

def evaluate_taco(classifier, taco_path: str) -> dict:
    print("\n=== Evaluating on External Generalization Dataset: TACO ===")
    taco_adapter = TacoAdapter(taco_path)
    
    mapping_cfg = load_mapping_config()
    rw_to_taco = mapping_cfg.get("realwaste_to_taco", {}).get("mapping", {})
    # Invert mapping: taco_cat -> realwaste_class
    taco_to_rw = {}
    for rw_cls, taco_list in rw_to_taco.items():
        for t_cat in taco_list:
            taco_to_rw[t_cat] = rw_cls

    all_taco_samples = taco_adapter.get_all_samples()
    mapped_samples = []
    unmapped_count = 0
    
    for img_path, taco_cat in all_taco_samples:
        if not os.path.exists(img_path):
            continue
        rw_cls = taco_to_rw.get(taco_cat)
        if rw_cls:
            mapped_samples.append((img_path, rw_cls))
        else:
            unmapped_count += 1

    print(f"TACO dominant-object samples: evaluated={len(mapped_samples)}, unmapped={unmapped_count}")
    
    if mapped_samples:
        metrics = evaluate_samples(classifier, mapped_samples)
    else:
        metrics = {"error": "No mapped samples found"}

    metrics["dataset"] = "TACO"
    metrics["role"] = "external_generalization_testing"
    metrics["domain_shift_notes"] = "TACO is an in-the-wild litter detection dataset (bounding boxes/segmentations). Evaluating on dominant annotated objects tests realistic domain shift."
    metrics["limitations"] = "TACO images often contain complex multiple litter items and cluttered background; single-label classification on full images exhibits lower precision due to scene complexity without bounding box localization."
    return metrics

def main():
    settings = get_settings()
    trashnet_path = settings.trashnet_path or "Project Data/Image Data/dataset-resized"
    taco_path = settings.taco_path or "Project Data/Image Data/TACO"
    model_path = "models/image_classifier/realwaste_mobilenet_v3.pth"

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Train classifier first.")
        return

    classifier = ClassifierFactory.create("mobilenet_v3_small")
    classifier.load(model_path)
    print("Loaded trained RealWaste classifier.")

    tn_metrics = evaluate_trashnet(classifier, trashnet_path)
    taco_metrics = evaluate_taco(classifier, taco_path)

    os.makedirs("reports/model_evaluation", exist_ok=True)
    out_file = "reports/model_evaluation/cross_dataset_evaluation_report.json"
    with open(out_file, "w") as f:
        json.dump({
            "trashnet": tn_metrics,
            "taco": taco_metrics
        }, f, indent=2)
    print(f"\nCross-dataset evaluation complete! Report saved to {out_file}")

if __name__ == "__main__":
    main()
