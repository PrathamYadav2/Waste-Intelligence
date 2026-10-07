"""Validate all image datasets: RealWaste, TrashNet, TACO."""
import os
import json
from PIL import Image

def validate_image_dir(name, root_dir):
    print(f"Validating {name} at {root_dir}...")
    class_counts = {}
    valid_count = 0
    corrupt_count = 0
    formats = set()
    dimensions = set()

    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.startswith('.'):
                continue
            if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                continue
            
            # Determine class from folder
            rel = os.path.relpath(dirpath, root_dir)
            cls_name = rel.split(os.sep)[0] if rel != '.' else "root"
            class_counts[cls_name] = class_counts.get(cls_name, 0) + 1
            
            fp = os.path.join(dirpath, f)
            try:
                with Image.open(fp) as img:
                    img.verify()
                with Image.open(fp) as img:
                    formats.add(img.format)
                    dimensions.add(img.size)
                valid_count += 1
            except Exception as e:
                corrupt_count += 1

    return {
        "dataset": name,
        "total_images": valid_count + corrupt_count,
        "valid_images": valid_count,
        "corrupt_images": corrupt_count,
        "classes_count": len(class_counts),
        "class_distribution": class_counts,
        "formats_detected": list(formats),
        "unique_resolutions_count": len(dimensions),
        "passed": (corrupt_count == 0 and valid_count > 0)
    }

def main():
    rw_res = validate_image_dir("RealWaste", "Project Data/Image Data/RealWaste")
    tn_res = validate_image_dir("TrashNet", "Project Data/Image Data/dataset-resized")

    # TACO inspection
    taco_ann = "Project Data/Image Data/TACO/data/annotations.json"
    taco_info = {"exists": os.path.exists(taco_ann)}
    if taco_info["exists"]:
        with open(taco_ann, "r", encoding="utf-8") as f:
            t_data = json.load(f)
        taco_info["images_in_coco"] = len(t_data.get("images", []))
        taco_info["annotations_count"] = len(t_data.get("annotations", []))
        taco_info["categories_count"] = len(t_data.get("categories", []))

    out = {
        "RealWaste": rw_res,
        "TrashNet": tn_res,
        "TACO": taco_info
    }
    
    os.makedirs("reports/data_validation", exist_ok=True)
    report_file = "reports/data_validation/image_datasets_validation.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\n[DONE] Image dataset validation completed:")
    print(f"  RealWaste: {rw_res['valid_images']} valid, {rw_res['corrupt_images']} corrupt (Passed: {rw_res['passed']})")
    print(f"  TrashNet:  {tn_res['valid_images']} valid, {tn_res['corrupt_images']} corrupt (Passed: {tn_res['passed']})")
    print(f"  Report: {report_file}")

if __name__ == "__main__":
    main()
