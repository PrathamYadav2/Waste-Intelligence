"""Model registry / versioning. Stores and queries registered models."""
import os
import json
from datetime import datetime, timezone

REGISTRY_FILE = "models/registry.json"

def get_registry() -> dict:
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"models": []}

def save_registry(data: dict) -> None:
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def register(kind: str, name: str, version: str, artifact_uri: str, metrics: dict | None = None, metadata: dict | None = None) -> dict:
    reg = get_registry()
    entry = {
        "model_kind": kind,
        "name": name,
        "version": version,
        "artifact_uri": artifact_uri,
        "metrics": metrics or {},
        "metadata": metadata or {},
        "status": "production",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    # Update if exists, else append
    existing = [m for m in reg["models"] if m["name"] == name and m["version"] == version]
    if existing:
        existing[0].update(entry)
    else:
        reg["models"].append(entry)
    save_registry(reg)
    return entry

def get_active(kind: str) -> dict | None:
    reg = get_registry()
    matches = [m for m in reg["models"] if m["model_kind"] == kind and m.get("status") == "production"]
    if matches:
        return matches[-1]
    return None

def list_models() -> list[dict]:
    reg = get_registry()
    return reg.get("models", [])
