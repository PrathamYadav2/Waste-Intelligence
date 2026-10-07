# Architecture
## Layers
1. **Presentation** (`app/`): static HTML/CSS design system, 11 pages. Framework-agnostic; may be ported to React later.
2. **API** (`src/api/`): FastAPI, versioned `/api/v1`, structured errors, request IDs, placeholder auth.
3. **Domain engines**: `vision`, `forecasting`, `recovery`, `analytics`, `recommendations`, `explainability`.
4. **Data**: `src/data` adapters (one per dataset), validation, label mapping. `src/database` + `sql/`.
5. **Config**: env vars + `configs/*.yaml`. No hard-coded paths.

## Component taxonomy (must stay visible in code, DB and UI)
| Kind | Components |
|---|---|
| ML-based | Image classifier, forecaster, Grad-CAM (model-derived) |
| Scoring | Waste Recovery Score (project-specific, explainable, not an official metric) |
| Rule-based | Recoverability/handling rules, route constraints (configs/recovery_rules.yaml) |
| Analytics | Regional aggregation, pressure index, capacity gap, priority ranking |

Static if/else logic is labelled **Rule**, never "AI". Each recommendation stores a `component_trace`.

## Data flow
```
Upload -> /waste/analyze -> classifier(ML) -> material mapping(Rule) -> recovery score(Scoring) -> route(Rule+Scoring)
Regional CSV -> validation -> features -> forecaster(ML) -> capacity gap(Analytics) -> priority
(classification, route, pressure, forecast, gap) -> recommendation engine -> community action -> DB
```
## Principles
No fake data; datasets connected via env vars only; datasets never auto-merged; time-aware validation; every model version registered.
