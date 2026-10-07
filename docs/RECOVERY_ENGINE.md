# Recovery Engine
Routes: reuse, recycle, compost, material recovery, authorized e-waste collection, safe disposal.
**Waste Recovery Score** - a project-specific, explainable 0-100 score. Not an official environmental metric; always labelled as such in UI and API (`score_version`).
Factors: detected material, waste category, condition (manual/unavailable), route feasibility, recoverability rules, local handling constraints. Weights: TBD, to be justified and versioned.
Rules: `configs/recovery_rules.yaml` (all PLACEHOLDER). Condition is never inferred without labels; missing condition lowers certainty, shown as "condition unavailable".
Output: `{score, route, factor_breakdown, rationale}` stored in `recovery_scores` / `recovery_decisions` with `decided_by` in (rule, scoring, ml).
