import pathlib, yaml
def test_unmapped_classes_flagged():
    cfg = yaml.safe_load(pathlib.Path("configs/label_mapping.yaml").read_text())
    m = cfg["realwaste_to_trashnet"]
    assert all(m[k]["status"] == "UNMAPPED" for k in ["Food Organics", "Textile Trash", "Vegetation"])
