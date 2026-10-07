# Recommendation Engine
**Inputs:** classification, material, condition, recovery score, route, regional pressure, forecast, capacity gap.
**Outputs:** recommended action, route, priority (low/medium/high), explanation, community action, component_trace.
| Stage | Kind |
|---|---|
| Classification | ML |
| Recovery score | Scoring |
| Route constraints | Rule |
| Regional pressure, capacity gap | Analytics |
| Forecast | ML |
| Priority/action selection | Rule or Scoring at v1 (labelled honestly). An ML ranker is considered only if outcome data exists. |

The engine is called "AI-assisted" because ML outputs feed it; static rules are never presented as AI.
