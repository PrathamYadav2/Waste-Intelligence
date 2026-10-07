"""Grad-CAM implementation for PyTorch vision models."""
import numpy as np
import torch
import cv2
from PIL import Image
from ..preprocessing.images import build_eval_transform

class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._hook_handles = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0]

        h1 = self.target_layer.register_forward_hook(forward_hook)
        h2 = self.target_layer.register_full_backward_hook(backward_hook)
        self._hook_handles.extend([h1, h2])

    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        self.model.eval()
        output = self.model(input_tensor)
        
        self.model.zero_grad()
        loss = output[0, class_idx]
        loss.backward()

        gradients = self.gradients.data.cpu().numpy()[0]
        activations = self.activations.data.cpu().numpy()[0]

        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(activations.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            cam += w * activations[i]

        cam = np.maximum(cam, 0)
        if np.max(cam) > 0:
            cam = cam / np.max(cam)
        else:
            cam = np.zeros_like(cam)

        cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))
        return cam

    def remove_hooks(self):
        for h in self._hook_handles:
            h.remove()


def explain(classifier, image: Image.Image, target_class: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes real Grad-CAM heatmap and overlay from classifier and image.
    Returns: (heatmap_normalized, overlay_image_rgb_uint8)
    """
    model = classifier.model
    # For MobileNetV3, the last convolutional layer is model.features[-1]
    target_layer = model.features[-1]
    grad_cam = GradCAM(model, target_layer)

    if image.mode != "RGB":
        image = image.convert("RGB")
    
    transform = build_eval_transform()
    tensor = transform(image).unsqueeze(0).to(classifier.device)

    if target_class is None:
        with torch.no_grad():
            output = model(tensor)
            target_class = int(torch.argmax(output, dim=1).item())

    heatmap = grad_cam.generate_heatmap(tensor, target_class)
    grad_cam.remove_hooks()

    # Create overlay
    orig_np = np.array(image.resize((224, 224)))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    overlay = np.uint8(0.6 * orig_np + 0.4 * heatmap_colored)
    return heatmap, overlay
