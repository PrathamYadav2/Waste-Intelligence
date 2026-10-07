"""Training pipeline for RealWaste classifier using PyTorch Transfer Learning."""
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from PIL import Image
from tqdm import tqdm

from ..preprocessing.images import build_train_transform, build_eval_transform, stratified_split
from ..data.adapters import RealWasteAdapter
from .registry import register

class ImagePathDataset(Dataset):
    def __init__(self, samples: list[tuple[str, str]], class_to_idx: dict[str, int], transform=None):
        self.samples = samples
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        target = self.class_to_idx[label]
        return image, target

def train(cfg: dict) -> dict:
    realwaste_path = cfg.get("realwaste_path", "Project Data/Image Data/RealWaste")
    output_dir = cfg.get("output_dir", "models/image_classifier")
    os.makedirs(output_dir, exist_ok=True)

    adapter = RealWasteAdapter(realwaste_path)
    samples = adapter.get_all_samples()
    class_names = adapter.class_names()
    class_to_idx = {c: i for i, c in enumerate(class_names)}

    print(f"Total RealWaste samples: {len(samples)}, classes: {len(class_names)}")
    train_samples, val_samples, test_samples = stratified_split(samples, seed=cfg.get("seed", 42))

    train_ds = ImagePathDataset(train_samples, class_to_idx, transform=build_train_transform())
    val_ds = ImagePathDataset(val_samples, class_to_idx, transform=build_eval_transform())
    test_ds = ImagePathDataset(test_samples, class_to_idx, transform=build_eval_transform())

    batch_size = cfg.get("batch_size", 32)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Transfer learning: Pretrained MobileNetV3 Small
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, len(class_names))
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.get("learning_rate", 0.001), weight_decay=1e-4)

    epochs = cfg.get("num_epochs", 3)
    best_val_acc = 0.0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, targets in tqdm(train_loader, desc=f"Epoch {epoch}/{epochs} [Train]"):
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)

        train_loss = running_loss / total
        train_acc = correct / total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, targets in tqdm(val_loader, desc=f"Epoch {epoch}/{epochs} [Val]"):
                images, targets = images.to(device), targets.to(device)
                outputs = model(images)
                loss = criterion(outputs, targets)

                val_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1)
                val_correct += (preds == targets).sum().item()
                val_total += targets.size(0)

        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        print(f"Epoch {epoch}: Train Loss={train_loss:.4f}, Train Acc={train_acc:.4f} | Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}")
        
        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc
        })

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            artifact_path = os.path.join(output_dir, "realwaste_mobilenet_v3.pth")
            torch.save({
                "version": "1.0.0",
                "backbone": "mobilenet_v3_small",
                "class_names": class_names,
                "state_dict": model.state_dict(),
                "val_accuracy": val_acc
            }, artifact_path)

    # Save test set for formal evaluation
    torch.save(test_samples, os.path.join(output_dir, "test_samples.pt"))

    # Register model
    artifact_uri = os.path.join(output_dir, "realwaste_mobilenet_v3.pth")
    register(
        kind="image_classifier",
        name="RealWaste-MobileNetV3",
        version="1.0.0",
        artifact_uri=artifact_uri,
        metrics={"best_val_accuracy": best_val_acc, "history": history},
        metadata={"backbone": "mobilenet_v3_small", "num_classes": len(class_names), "class_names": class_names}
    )

    return {"artifact_path": artifact_uri, "val_accuracy": best_val_acc, "history": history}
