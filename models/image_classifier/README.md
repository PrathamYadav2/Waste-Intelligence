# 🧠 RealWaste MobileNetV3 Image Classifier

> **File:** `realwaste_mobilenet_v3.pth` (6.24 MB)  
> **Architecture:** PyTorch `mobilenet_v3_small`  
> **Status:** Production Ready & Verified

---

## ⚠️ Important Note: Why clicking on `.pth` doesn't open it

Agar aapne `realwaste_mobilenet_v3.pth` file par double click kiya hai aur Windows ne error diya ya poochha *"How do you want to open this file?"*, toh dhyan dein:

- **`.pth` file koi executable software (`.exe`) ya document nahi hai.**
- Yeh ek **PyTorch Binary Checkpoint (State Dictionary)** hai, jisme model ke deep neural network ke trained weights (numbers/floating point tensors) store hote hain.
- Isko direct double-click karke nahi khola jata, balki **Python / Web Dashboard** ke through load karke chalaya jata hai.

---

## 🚀 Model ko Run aur Test Kaise Karein?

### Tarika 1: Web Dashboard (Sabse Aasan Visual Interface)
1. Project root folder me **`start.bat`** par double click karein.
2. Browser me automatically **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** khul jayega.
3. **"AI Vision Classifier & Scanner"** section me koi bhi image drag-and-drop ya upload karein.
4. Model turant:
   - Waste category classify karega
   - Confidence score batayega
   - **Grad-CAM visual heatmap** show karega
   - Recycling Potential aur Market scrap rate (Rs./kg) calculate karega.

---

### Tarika 2: Command Line se Kisi Photo ko Test Karna
Root folder me command prompt ya terminal kholiye aur run karein:
```bash
python predict.py "path/to/your/image.jpg"
```
*(Example: `python predict.py "Project Data/Image Data/RealWaste/Cardboard/Cardboard_1.jpg"`)*

---

### Tarika 3: Python Code me Model Load Karna

Agar aap Python code ke zariye model load karke predict karna chahte hain:

```python
import torch
from torchvision import models
import torch.nn as nn
from PIL import Image
from torchvision import transforms

# 1. 9 RealWaste Classes
CLASSES = [
    "Cardboard", "Food Organics", "Glass", "Metal",
    "Miscellaneous Trash", "Paper", "Plastic", "Textile Trash", "Vegetation"
]

# 2. Backbone Architecture initialize karein
model = models.mobilenet_v3_small(weights=None)
in_features = model.classifier[3].in_features
model.classifier[3] = nn.Linear(in_features, len(CLASSES))

# 3. Trained Weights (.pth) load karein
weights_path = "models/image_classifier/realwaste_mobilenet_v3.pth"
checkpoint = torch.load(weights_path, map_location="cpu", weights_only=False)

if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
    model.load_state_dict(checkpoint["state_dict"])
elif isinstance(checkpoint, dict):
    model.load_state_dict(checkpoint)
else:
    model = checkpoint

model.eval()
print("✅ Model successfully loaded in memory!")

# 4. Image Preprocessing & Inference
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

img = Image.open("your_waste_image.jpg").convert("RGB")
tensor = transform(img).unsqueeze(0)

with torch.no_grad():
    outputs = model(tensor)
    probs = torch.softmax(outputs, dim=1)[0]
    conf, pred_idx = torch.max(probs, dim=0)

print(f"Predicted Class: {CLASSES[pred_idx]} ({conf.item()*100:.2f}% confidence)")
```

---

## 📊 Model Training & Benchmark Specifications

| Metric / Parameter | Value |
| :--- | :--- |
| **Model Architecture** | `MobileNetV3-Small` (Transfer Learning from ImageNet) |
| **Training Dataset** | RealWaste (4,752 curated real-world waste images) |
| **Total Classes** | 9 Mutual Exclusive Waste Streams |
| **Test Accuracy** | **78.26%** (Evaluated on 713 holdout samples) |
| **Validation Macro F1** | **79.26%** |
| **Peak Validation Acc** | **81.63%** |
| **Inference Enhancements** | Square-pad preservation + 3-view Test-Time Augmentation (TTA) |
| **File Size** | 6,242,301 bytes (~6.24 MB) |

---

## 🏷️ Supported 9 Waste Categories

1. **Cardboard** (Corrugated boxes, packaging cartons) -> Blue Bin
2. **Food Organics** (Kitchen waste, leftovers, peels) -> Green Bin
3. **Glass** (Bottles, broken glassware, cullet) -> Blue Bin
4. **Metal** (Aluminium cans, tinplate, scrap alloy) -> Blue Bin
5. **Miscellaneous Trash** (Sanitary waste, composite packaging, inerts) -> Black Bin
6. **Paper** (Newspaper, office shred, envelopes) -> Blue Bin
7. **Plastic** (PET bottles, HDPE containers, LDPE films) -> Blue Bin
8. **Textile Trash** (Cotton rags, worn garments, upholstery felt) -> Special Recovery
9. **Vegetation** (Garden clippings, pruning waste, leaves) -> Green Bin
