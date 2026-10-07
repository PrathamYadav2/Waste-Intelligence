-- PostgreSQL dialect. Schema only: NO seed data, NO fake results.
CREATE TABLE users (
  user_id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  role TEXT NOT NULL DEFAULT 'citizen' CHECK (role IN ('citizen','volunteer','analyst','admin')),
  region TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by BIGINT, updated_by BIGINT
);
CREATE TABLE model_versions (
  model_version_id BIGSERIAL PRIMARY KEY,
  model_kind TEXT NOT NULL CHECK (model_kind IN ('image_classifier','forecaster','explainer')),
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  artifact_uri TEXT,
  training_dataset TEXT,
  config_hash TEXT,
  metrics JSONB,                       -- filled only from real evaluation runs
  status TEXT NOT NULL DEFAULT 'registered' CHECK (status IN ('registered','staging','production','retired')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by BIGINT REFERENCES users(user_id),
  UNIQUE (model_kind, name, version)
);
CREATE TABLE waste_observations (
  observation_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(user_id),
  image_uri TEXT NOT NULL,
  image_sha256 TEXT,
  region TEXT,
  latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
  user_condition_input TEXT,           -- manual condition, if provided
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ix_obs_user ON waste_observations(user_id);
CREATE INDEX ix_obs_region_time ON waste_observations(region, observed_at);
CREATE TABLE predictions (
  prediction_id BIGSERIAL PRIMARY KEY,
  observation_id BIGINT NOT NULL REFERENCES waste_observations(observation_id) ON DELETE CASCADE,
  model_version_id BIGINT NOT NULL REFERENCES model_versions(model_version_id),
  latency_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_pred_obs ON predictions(observation_id);
CREATE TABLE classification_results (
  result_id BIGSERIAL PRIMARY KEY,
  prediction_id BIGINT NOT NULL REFERENCES predictions(prediction_id) ON DELETE CASCADE,
  rank SMALLINT NOT NULL DEFAULT 1,
  waste_class TEXT NOT NULL,
  material TEXT,
  confidence NUMERIC(5,4) CHECK (confidence BETWEEN 0 AND 1),
  gradcam_uri TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (prediction_id, rank)
);
CREATE TABLE recovery_scores (
  score_id BIGSERIAL PRIMARY KEY,
  result_id BIGINT NOT NULL REFERENCES classification_results(result_id) ON DELETE CASCADE,
  score NUMERIC(5,2) CHECK (score BETWEEN 0 AND 100),
  score_version TEXT NOT NULL,         -- project-specific explainable score, not an official metric
  factor_breakdown JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE recovery_decisions (
  decision_id BIGSERIAL PRIMARY KEY,
  score_id BIGINT NOT NULL REFERENCES recovery_scores(score_id) ON DELETE CASCADE,
  route TEXT NOT NULL CHECK (route IN ('reuse','recycle','compost','material_recovery','authorized_ewaste_collection','safe_disposal')),
  rationale TEXT,
  decided_by TEXT NOT NULL CHECK (decided_by IN ('rule','scoring','ml')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_dec_route ON recovery_decisions(route);
