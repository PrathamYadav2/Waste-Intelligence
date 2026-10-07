# Testing Strategy
- **Unit** (`tests/unit`): scoring, mapping config, splits (no random time splits), schema validation.
- **Integration** (`tests/integration`): API contract incl. 501 behaviour, request IDs, DB schema apply.
- **Data** (`tests/data`): validators run against tiny synthetic fixtures created for tests, clearly named as fixtures; never project datasets.
- **ML**: determinism with seed, no leakage across splits, evaluation reproduces from stored predictions.
- **Frontend**: keyboard navigation, state rendering, contrast audit.
Run: `pytest`.
