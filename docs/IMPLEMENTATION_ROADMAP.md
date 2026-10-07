# Implementation Roadmap
1. **Connect data:** fill `.env`, run `check_env.py`, implement adapters, validators; resolve TO_BE_VERIFIED items; update DATA_DICTIONARY/DATASET_MAP.
2. **Vision baseline:** split, transforms, baseline backbone, evaluate; register model.
3. **Cross-dataset evaluation:** finalize label mapping; TrashNet then TACO; write reports.
4. **Grad-CAM:** target layers, overlays, failure analysis.
5. **Forecasting:** features, time split, baseline -> candidates, select, forecast.
6. **Capacity & analytics:** confirm capacity source, pressure index, priority.
7. **Recovery engine:** populate rules with cited guidance, define weights.
8. **Recommendation engine + DB:** apply SQL, wire persistence.
9. **API wiring + frontend binding:** replace 501s, connect pages, charts, map.
10. **Hardening:** auth, tests, docs, demo.
Each step ends with updated docs and passing tests.
