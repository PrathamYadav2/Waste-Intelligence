"""Image classifier implementations and registry loading."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image

from ..preprocessing.images import build_eval_transform, pad_to_square

@dataclass
class Prediction:
    label: str
    confidence: float
    top_k: list[tuple[str, float]]

class ImageClassifier(ABC):
    @abstractmethod
    def load(self, artifact_uri: str) -> None:
        ...

    @abstractmethod
    def predict(self, image: Image.Image) -> Prediction:
        ...


class MobileNetV3Classifier(ImageClassifier):
    def __init__(self, class_names: list[str], device: str = "cpu"):
        self.class_names = class_names
        self.device = torch.device(device)
        self.model = models.mobilenet_v3_small(weights=None)
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, len(class_names))
        self.model.to(self.device)
        self.transform = build_eval_transform()
        self.version = "1.0.0"

    def load(self, artifact_uri: str) -> None:
        if not os.path.exists(artifact_uri):
            raise FileNotFoundError(f"Model artifact not found at {artifact_uri}")
        checkpoint = torch.load(artifact_uri, map_location=self.device)
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"])
            if "class_names" in checkpoint:
                self.class_names = checkpoint["class_names"]
            if "version" in checkpoint:
                self.version = checkpoint["version"]
        else:
            self.model.load_state_dict(checkpoint)
        self.model.eval()


    def predict(self, image: Image.Image) -> Prediction:
        self.model.eval()
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Multi-view aspect-ratio preserving inference (TTA)
        # View 1: Geometry-preserved padded square (prevents cylinder/box squashing)
        img_padded = pad_to_square(image)
        t1 = self.transform(img_padded).unsqueeze(0).to(self.device)

        # View 2: Horizontal mirror of padded image
        img_flip = img_padded.transpose(Image.FLIP_LEFT_RIGHT)
        t2 = self.transform(img_flip).unsqueeze(0).to(self.device)

        # View 3: Direct resize
        t3 = self.transform(image).unsqueeze(0).to(self.device)

        batch = torch.cat([t1, t2, t3], dim=0)
        with torch.no_grad():
            logits = self.model(batch)
            probs_batch = torch.softmax(logits, dim=1)
            # Ensemble weights giving higher priority to aspect-ratio preserved views
            w = torch.tensor([[0.45], [0.40], [0.15]], device=self.device)
            probs = (probs_batch * w).sum(dim=0)

        probs_np = probs.cpu().numpy()
        top_indices = probs_np.argsort()[::-1]
        
        top_k = [(self.class_names[idx], float(probs_np[idx])) for idx in top_indices[:5]]
        best_label = self.class_names[top_indices[0]]
        best_conf = float(probs_np[top_indices[0]])
        
        return Prediction(label=best_label, confidence=best_conf, top_k=top_k)


class ClassifierFactory:
    @staticmethod
    def create(backbone: str = "mobilenet_v3_small", class_names: list[str] | None = None) -> ImageClassifier:
        if class_names is None:
            class_names = [
                "Cardboard", "Food Organics", "Glass", "Metal",
                "Miscellaneous Trash", "Paper", "Plastic",
                "Textile Trash", "Vegetation"
            ]
        if backbone == "mobilenet_v3_small":
            return MobileNetV3Classifier(class_names=class_names)
        raise ValueError(f"Unsupported backbone: {backbone}")
