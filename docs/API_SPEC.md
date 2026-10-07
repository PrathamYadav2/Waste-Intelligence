# API Spec (v1, prefix `/api/v1`)
Status: contracts defined; unbuilt endpoints return 501 `NOT_IMPLEMENTED_YET`. `/health` is live.
| Method | Path | Request | Response |
|---|---|---|---|
| GET | /health | - | HealthResponse |
| POST | /api/v1/waste/classify | multipart: image | ClassifyResponse |
| POST | /api/v1/waste/analyze | multipart: image, region?, condition? | classification + recovery + recommendation |
| POST | /api/v1/recovery/recommend | RecoveryRequest | RecoveryResponse |
| GET | /api/v1/regional/overview | - | list of regions + pressure |
| GET | /api/v1/regional/{region} | - | trend + stats |
| GET | /api/v1/forecast | region?, horizon? | forecast + model version |
| GET | /api/v1/map | layer? | GeoJSON-style features |
| GET | /api/v1/recommendations | region?, priority?, page, page_size | Page of RecommendationItem |
| GET | /api/v1/models | - | model versions + metrics |

Schemas: `src/api/schemas.py`. **Errors:** `{"error": {"code","message","details","request_id"}}`; codes: VALIDATION_ERROR (422), NOT_IMPLEMENTED_YET (501), UNAUTHORIZED (401), NOT_FOUND (404), MODEL_NOT_LOADED (503). **Validation:** image MIME/size limits TBD; lat/lon ranges enforced. **Auth:** placeholder. **Logging:** JSON logs, `X-Request-ID`, per-call rows in `prediction_logs`.
