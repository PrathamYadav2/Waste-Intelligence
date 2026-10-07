"""Loads configs/label_mapping.yaml and provides mapping utilities."""
import os
import yaml

def load_mapping_config(path: str = "configs/label_mapping.yaml") -> dict:
    if not os.path.exists(path):
        # Fallback if working from subfolder
        path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "label_mapping.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_mapping(source: str, target: str) -> dict:
    """Returns mapping from source dataset to target dataset classes."""
    cfg = load_mapping_config()
    key = f"{source}_to_{target}"
    if key in cfg:
        return cfg[key]
    raise KeyError(f"Mapping configuration for '{key}' not found in configs/label_mapping.yaml")

def map_label(source_label: str, source: str, target: str) -> str | None:
    mapping = load_mapping(source, target)
    if source == "realwaste" and target == "trashnet":
        entry = mapping.get(source_label)
        if entry and entry.get("status") == "VERIFIED":
            return entry.get("target")
        return None
    elif source == "realwaste" and target == "taco":
        return None
    return None
