# Data Dictionary (Verified Post-Implementation)

This document contains verified data fields, schemas, and metadata after real dataset inspection and execution.

## 1. Regional Waste Dataset (`regional_waste_by_year.csv`)
- **Row count:** 96 rows
- **Regions:** 12 Urban Local Body (ULB) clusters (Amravati, Aurangabad, Chandrapur, Kalyan, Kolhapur, Mumbai, Nagpur, Nashik, Navi Mumbai, Pune, Raigad, Thane)
- **Time coverage:** 8 annual observations per region (`2016-17`, `2017-18`, `2018`, `2019`, `2020`, `2021`, `2022`, `2023`)
- **Normalized year mapping:** 2016 through 2023 (integer year)
- **Forecasting target:** `gen_total_ulb_tpd` (float, range: 140.26 – 9083.00 TPD, 0 missing values, strictly positive)
- **Coordinate columns:** `latitude` (16.705 to 21.1458 N), `longitude` (72.8722 to 79.2961 E)
- **Capacity & Treatment fields (available 2018–2023):**
  - `treated_total_ulb_tpd`: Total treated municipal waste in tonnes per day
  - `treated_share_pct`: Percentage of generated waste undergoing treatment (mean 70.1%)
  - `untreated_gap_tpd`: Daily capacity processing shortfall in tonnes per day (mean 530.3 TPD)
- **Source reporting:** Maharashtra State Pollution Control Board Annual MSW Implementation Reports

## 2. RealWaste Primary Image Classification Dataset
- **Total images:** 4,752 verified JPEG images (0 corrupted files)
- **Dimensions:** 524 x 524 RGB
- **Classes (9 classes):**
  - Cardboard: 461
  - Food Organics: 411
  - Glass: 420
  - Metal: 790
  - Miscellaneous Trash: 495
  - Paper: 500
  - Plastic: 921
  - Textile Trash: 318
  - Vegetation: 436
- **Splits:** 70% Train (3,326), 15% Validation (713), 15% Test (713), Stratified, Random Seed 42

## 3. TrashNet Secondary Cross-Dataset Evaluation
- **Total images:** 2,527 verified JPEG images (0 corrupted files)
- **Dimensions:** 512 x 384 RGB
- **Classes:** 6 classes (`cardboard`: 403, `glass`: 501, `metal`: 410, `paper`: 594, `plastic`: 482, `trash`: 137)
- **Mapped classes:** All 6 map directly to RealWaste classes (`Cardboard`, `Glass`, `Metal`, `Paper`, `Plastic`, `Miscellaneous Trash`)
- **Unmapped RealWaste classes:** `Food Organics`, `Textile Trash`, `Vegetation`

## 4. TACO External In-The-Wild Generalization Dataset
- **Total images:** 1,500 real-world litter scenes
- **Format:** COCO JSON annotations format (4,784 bounding box / polygon annotations across 60 fine-grained categories)
- **Mapped dominant-object evaluation subset:** 1,475 samples mapped to 7 RealWaste target categories

## 5. Waste Recovery Guidance Reference (`material_guidance`)
- **Format:** JSON structure mapped across all 9 RealWaste categories
- **Attributes:** `stream_type`, `recommended_bin_color`, `source_segregation_guidance`, `recyclability_potential`, `statutory_pathway`, `statutory_reference`, `community_action_tips`
