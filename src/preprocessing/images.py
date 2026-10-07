from torchvision import transforms
from sklearn.model_selection import train_test_split
from PIL import Image

def pad_to_square(image: Image.Image, fill=(128, 128, 128)) -> Image.Image:
    """Preserves natural geometry of waste items (bottles, cans, boxes) without squashing."""
    w, h = image.size
    if w == h:
        return image
    max_side = max(w, h)
    new_img = Image.new("RGB", (max_side, max_side), fill)
    left = (max_side - w) // 2
    top = (max_side - h) // 2
    new_img.paste(image, (left, top))
    return new_img

def build_train_transform(input_size=(224, 224)):
    return transforms.Compose([
        transforms.Resize(input_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def build_eval_transform(input_size=(224, 224)):
    return transforms.Compose([
        transforms.Resize(input_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def stratified_split(samples: list[tuple[str, str]], seed: int = 42, train_size=0.70, val_size=0.15, test_size=0.15):
    """
    Split samples into train, val, and test partitions using stratified sampling.
    """
    labels = [s[1] for s in samples]
    train_samples, temp_samples, train_labels, temp_labels = train_test_split(
        samples, labels, train_size=train_size, stratify=labels, random_state=seed
    )
    
    val_ratio = val_size / (val_size + test_size)
    val_samples, test_samples = train_test_split(
        temp_samples, train_size=val_ratio, stratify=temp_labels, random_state=seed
    )
    
    return train_samples, val_samples, test_samples
