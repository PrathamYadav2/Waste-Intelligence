# ML (Vision) Architecture
**Flow:** ingest -> validate (readable, type, size) -> resize -> normalize -> augment (train only) -> stratified train/val/test split -> train -> evaluate -> register -> infer (+confidence).
- **Model-agnostic:** `ImageClassifier` interface + `ClassifierFactory`; supports custom CNN, transfer learning, ResNet/EfficientNet-style backbones. Backbone and input size are config values (TO_BE_VERIFIED_DURING_IMPLEMENTATION).
- **Primary training:** RealWaste only. TrashNet and TACO are never used to train the primary model without an explicit, documented experiment.
- **Confidence:** softmax probability; calibration and a low-confidence threshold to be evaluated before use (TBD).
- **Material:** derived from class via a documented mapping (Rule) unless a material-level model is later justified.
- **Condition:** not predicted. Manual input or "unavailable" unless condition labels exist.
- **Leakage controls:** split before augmentation; duplicate check across splits (see DATA_VALIDATION.md).
- **Outputs:** versioned artifacts + metrics JSON in `models/` and `reports/`; metadata in `model_versions`.
