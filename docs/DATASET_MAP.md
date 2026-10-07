# Dataset Map (Verified Post-Implementation)

| Dataset | Location / Env Var | Role | Verified Count | Classes / Schema | Status |
|---|---|---|---|---|---|
| **RealWaste** | `Project Data/Image Data/RealWaste` | Primary Vision Classifier Training & Eval | 4,752 images | 9 classes (Cardboard, Food Organics, Glass, Metal, Miscellaneous Trash, Paper, Plastic, Textile Trash, Vegetation) | **Trained & Evaluated (Test Acc: 78.26%, Macro F1: 79.26%)** |
| **TrashNet** | `Project Data/Image Data/dataset-resized` | Secondary Cross-Dataset Evaluation | 2,527 images | 6 classes (cardboard, glass, metal, paper, plastic, trash) | **Evaluated on 6 mapped classes (Acc: 32.01%, Macro F1: 16.70%)** |
| **TACO** | `Project Data/Image Data/TACO` | External In-The-Wild Generalization | 1,500 images | 60 categories, COCO format | **Evaluated on 1,475 dominant objects (Acc: 7.39%, Macro F1: 7.73%)** |
| **Regional Waste Data** | `Project Data/Regional Data/regional_waste_by_year.csv` | Regional Intelligence, Pressure Index & 2024–2027 Forecasting | 96 rows | 12 regions, 8 annual observations (2016–2023), target `gen_total_ulb_tpd` | **Backtested & Forecasted (2024–2027 generated for all 12 regions)** |
| **Material Guidance** | `Project Data/Recycling/material_guidance` | Recovery Scoring & Statutory Rules | 9 categories | Statutory pathways, bin colors, community actions | **Connected to Recovery Scoring Engine** |
