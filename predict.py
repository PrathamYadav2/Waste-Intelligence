"""Standalone CLI prediction and model inspector script."""
import sys
import os
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.vision.classifier import ClassifierFactory
from src.recovery.scoring import compute_recovery_score, get_recycling_potential
from src.recommendations.engine import recommend

def main():
    print("=" * 65)
    print("♻️  WASTE INTELLIGENCE - MODEL INFERENCE & INSPECTOR")
    print("=" * 65)

    weights_path = PROJECT_ROOT / "models" / "image_classifier" / "realwaste_mobilenet_v3.pth"
    if not weights_path.exists():
        print(f"❌ Error: Model weights not found at: {weights_path}")
        return 1

    print(f"📦 Loading Model: MobileNetV3-Small")
    print(f"📍 Artifact: {weights_path.relative_to(PROJECT_ROOT)} ({weights_path.stat().st_size / (1024*1024):.2f} MB)")
    
    classifier = ClassifierFactory.create("mobilenet_v3_small")
    classifier.load(str(weights_path))
    print("✅ Model successfully loaded into memory!")
    print(f"🏷️  Supported Categories ({len(classifier.class_names)}):")
    for idx, c in enumerate(classifier.class_names, 1):
        print(f"   {idx}. {c}")
    print("-" * 65)

    # Determine image path
    if len(sys.argv) > 1:
        img_path = Path(sys.argv[1])
    else:
        # Default sample image
        img_path = PROJECT_ROOT / "Project Data" / "Image Data" / "RealWaste" / "Cardboard" / "Cardboard_1.jpg"
        print(f"ℹ️  No image path specified. Using default sample image:")
        print(f"   {img_path.relative_to(PROJECT_ROOT)}")

    if not img_path.exists():
        print(f"❌ Image not found: {img_path}")
        return 1

    print(f"🖼️  Evaluating: {img_path.name}...")
    img = Image.open(img_path)
    pred = classifier.predict(img)

    print("\n🎯 PREDICTION RESULTS:")
    print(f"   ► Category:   {pred.label.upper()}")
    print(f"   ► Confidence: {pred.confidence * 100:.2f}%\n")

    print("📊 Top Probabilities:")
    for label, conf in pred.top_k[:4]:
        bar = "█" * int(conf * 25)
        print(f"   - {label:<20} {conf*100:5.1f}%  |{bar}")

    # Circular Economy & Recycling Potential
    rec = get_recycling_potential(pred.label)
    print("\n🔬 RECYCLING POTENTIAL & MARKET BENCHMARK:")
    print(f"   ► Recyclability Index: {rec.recyclability_index}% ({rec.feasibility})")
    print(f"   ► Scrap Benchmark:     Rs. {rec.market_value_inr_per_kg['min_inr']} - {rec.market_value_inr_per_kg['max_inr']} / kg")
    print(f"   ► Lifecycle Loops:     {rec.lifecycle_loops}")
    print(f"   ► Buyer Industries:    {', '.join(rec.target_buyer_industries)}")
    print(f"   ► Industrial SOP:      {rec.industrial_processing_sop}")

    # AI Recommendation
    recovery = compute_recovery_score(pred.label, condition="clean")
    directives = recommend(pred.label, pred.confidence, recovery)
    print("\n💡 AI RECOMMENDATIONS (CITIZEN & FACILITY):")
    print(f"   ► Statutory Route:    {directives.route}")
    print(f"   ► Primary Action:     {directives.action}")
    print(f"   ► Facility Action:    {directives.mrf_facility_action}")
    if directives.citizen_protocol:
        print(f"   ► Citizen Directives: {', '.join(directives.citizen_protocol[:2])}")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())
