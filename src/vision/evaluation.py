"""Evaluation utilities for calculating accuracy, precision, recall, F1 and confusion matrix."""
import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from PIL import Image
from tqdm import tqdm

def evaluate_samples(classifier, samples: list[tuple[str, str]], target_classes: list[str] | None = None) -> dict:
    """
    Evaluates classifier on a list of (image_path, true_label) tuples.
    Computes real metrics using scikit-learn.
    """
    y_true = []
    y_pred = []
    
    class_names = classifier.class_names
    
    for img_path, true_label in tqdm(samples, desc="Evaluating"):
        try:
            with Image.open(img_path) as img:
                pred = classifier.predict(img)
                y_true.append(true_label)
                y_pred.append(pred.label)
        except Exception as e:
            continue

    if not y_true:
        return {"error": "No valid samples evaluated"}

    labels_to_eval = target_classes if target_classes is not None else sorted(list(set(y_true).union(set(y_pred))))

    acc = float(accuracy_score(y_true, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_weight, r_weight, f1_weight, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    p_per, r_per, f1_per, sup_per = precision_recall_fscore_support(y_true, y_pred, labels=labels_to_eval, zero_division=0)
    
    per_class = {}
    for i, label in enumerate(labels_to_eval):
        per_class[label] = {
            "precision": float(p_per[i]),
            "recall": float(r_per[i]),
            "f1": float(f1_per[i]),
            "support": int(sup_per[i])
        }

    cm = confusion_matrix(y_true, y_pred, labels=labels_to_eval).tolist()

    return {
        "total_samples": len(y_true),
        "accuracy": acc,
        "macro_precision": float(p_macro),
        "macro_recall": float(r_macro),
        "macro_f1": float(f1_macro),
        "weighted_f1": float(f1_weight),
        "per_class": per_class,
        "labels": labels_to_eval,
        "confusion_matrix": cm
    }

def evaluate(model, adapter, mapping=None) -> dict:
    samples = adapter.get_all_samples()
    if mapping:
        # Filter and map labels
        mapped_samples = []
        for img_path, original_label in samples:
            mapped_lbl = mapping.get(original_label)
            if mapped_lbl:
                mapped_samples.append((img_path, mapped_lbl))
        samples = mapped_samples
    return evaluate_samples(model, samples)
