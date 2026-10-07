# Database Schema
PostgreSQL dialect in `sql/001_core.sql`, `002_regional.sql`, `003_actions.sql`. Apply in order. No seed data.
| Table | PK | FKs |
|---|---|---|
| users | user_id | - |
| model_versions | model_version_id | created_by -> users |
| waste_observations | observation_id | user_id -> users |
| predictions | prediction_id | observation_id, model_version_id |
| classification_results | result_id | prediction_id |
| recovery_scores | score_id | result_id |
| recovery_decisions | decision_id | score_id |
| regional_waste_data | regional_id | UNIQUE(region, year) |
| forecasts | forecast_id | model_version_id |
| capacity_analysis | capacity_id | forecast_id |
| recommendations | recommendation_id | observation_id, decision_id, capacity_id |
| community_actions | action_id | recommendation_id, user_id |
| prediction_logs | log_id | user_id, model_version_id |

Audit: `created_at`/`updated_at` on mutable tables, `created_by`, soft delete on observations. Indexes on region/time, user, route, request_id. Regional extra CSV columns go to `extra_attributes` until verified.
