"""Dataset adapters. Each dataset keeps its own adapter; datasets are never merged automatically."""
from abc import ABC, abstractmethod
import os
import json
from typing import Iterator, Sequence
import pandas as pd

class DatasetAdapter(ABC):
    name: str
    def __init__(self, root: str):
        self.root = root

    @abstractmethod
    def class_names(self) -> Sequence[str]:
        ...

    @abstractmethod
    def iter_samples(self) -> Iterator[tuple[str, str]]:
        """Yield (image_path, label)."""
        ...

    def get_all_samples(self) -> list[tuple[str, str]]:
        return list(self.iter_samples())


class RealWasteAdapter(DatasetAdapter):
    name = "realwaste"
    CLASSES = [
        "Cardboard", "Food Organics", "Glass", "Metal",
        "Miscellaneous Trash", "Paper", "Plastic",
        "Textile Trash", "Vegetation"
    ]

    def class_names(self) -> Sequence[str]:
        return self.CLASSES

    def iter_samples(self) -> Iterator[tuple[str, str]]:
        for cls in self.CLASSES:
            cls_dir = os.path.join(self.root, cls)
            if not os.path.isdir(cls_dir):
                continue
            for fname in os.listdir(cls_dir):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    yield (os.path.join(cls_dir, fname), cls)


class TrashNetAdapter(DatasetAdapter):
    name = "trashnet"
    CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

    def class_names(self) -> Sequence[str]:
        return self.CLASSES

    def iter_samples(self) -> Iterator[tuple[str, str]]:
        for cls in self.CLASSES:
            cls_dir = os.path.join(self.root, cls)
            if not os.path.isdir(cls_dir):
                continue
            for fname in os.listdir(cls_dir):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    yield (os.path.join(cls_dir, fname), cls)


class TacoAdapter(DatasetAdapter):
    name = "taco"

    def __init__(self, root: str, annotations_file: str | None = None):
        super().__init__(root)
        if annotations_file is None:
            annotations_file = os.path.join(root, "data", "annotations.json")
        self.annotations_file = annotations_file
        self._data = None

    def _load_annotations(self):
        if self._data is None:
            with open(self.annotations_file, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        return self._data

    def class_names(self) -> Sequence[str]:
        data = self._load_annotations()
        return [c["name"] for c in data.get("categories", [])]

    def iter_samples(self) -> Iterator[tuple[str, str]]:
        """
        Yields (image_path, primary_category_name) for images that have annotations.
        For images with multiple annotations, yields the first/dominant object annotation.
        """
        data = self._load_annotations()
        cat_id_to_name = {c["id"]: c["name"] for c in data.get("categories", [])}
        img_id_to_file = {img["id"]: img["file_name"] for img in data.get("images", [])}

        seen_images = set()
        for ann in data.get("annotations", []):
            img_id = ann["image_id"]
            if img_id not in seen_images:
                seen_images.add(img_id)
                rel_path = img_id_to_file.get(img_id)
                if rel_path:
                    full_path = os.path.join(self.root, "data", rel_path)
                    cat_name = cat_id_to_name.get(ann["category_id"], "Unknown")
                    yield (full_path, cat_name)


class RegionalWasteLoader:
    """Loads and standardizes regional_waste_by_year.csv."""
    def __init__(self, path: str):
        self.path = path

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.path)
        # Standardize report_year to calendar year integer
        year_mapping = {
            "2016-17": 2016,
            "2017-18": 2017,
            "2018": 2018,
            "2019": 2019,
            "2020": 2020,
            "2021": 2021,
            "2022": 2022,
            "2023": 2023
        }
        df["year"] = df["report_year"].astype(str).map(year_mapping)
        if df["year"].isnull().any():
            df["year"] = df["report_year"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
        df["year"] = df["year"].astype(int)
        return df
