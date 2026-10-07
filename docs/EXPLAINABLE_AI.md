# Explainable AI
Method: **Grad-CAM**. Flow: image -> preprocess -> CNN -> prediction -> Grad-CAM (target = predicted class) -> heatmap -> overlay -> user text.
Rules: heatmaps only from real forward/backward passes; no placeholders presented as results; target layer selection per backbone (TO_BE_VERIFIED_DURING_IMPLEMENTATION). Explanation text states that highlights show influence, not proof of correctness. Include failure examples in reports.
