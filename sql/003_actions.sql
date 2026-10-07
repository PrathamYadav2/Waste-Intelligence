CREATE TABLE recommendations (
  recommendation_id BIGSERIAL PRIMARY KEY,
  observation_id BIGINT REFERENCES waste_observations(observation_id) ON DELETE SET NULL,
  decision_id BIGINT REFERENCES recovery_decisions(decision_id),
  capacity_id BIGINT REFERENCES capacity_analysis(capacity_id),
  region TEXT,
  recommended_action TEXT NOT NULL,
  priority TEXT NOT NULL CHECK (priority IN ('low','medium','high')),
  explanation TEXT NOT NULL,
  component_trace JSONB NOT NULL,      -- which ml / rule / scoring / analytics parts contributed
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_reco_region ON recommendations(region, priority);
CREATE TABLE community_actions (
  action_id BIGSERIAL PRIMARY KEY,
  recommendation_id BIGINT NOT NULL REFERENCES recommendations(recommendation_id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(user_id),
  action_type TEXT NOT NULL CHECK (action_type IN ('segregation_awareness','recycling','composting','ewaste_collection','region_awareness','cleanup_campaign','waste_reduction')),
  status TEXT NOT NULL DEFAULT 'suggested' CHECK (status IN ('suggested','accepted','completed','dismissed')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_action_user ON community_actions(user_id, status);
CREATE TABLE prediction_logs (
  log_id BIGSERIAL PRIMARY KEY,
  request_id TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  user_id BIGINT REFERENCES users(user_id),
  model_version_id BIGINT REFERENCES model_versions(model_version_id),
  status_code SMALLINT,
  latency_ms INTEGER,
  error_code TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_log_req ON prediction_logs(request_id);
CREATE INDEX ix_log_time ON prediction_logs(created_at);
