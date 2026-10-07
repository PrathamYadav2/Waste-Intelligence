CREATE TABLE regional_waste_data (
  regional_id BIGSERIAL PRIMARY KEY,
  region TEXT NOT NULL,
  year SMALLINT NOT NULL,
  latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
  gen_total_ulb_tpd NUMERIC(12,2),     -- forecasting target
  source_report TEXT,
  extra_attributes JSONB,              -- other CSV columns: TO_BE_VERIFIED_DURING_IMPLEMENTATION
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ingest_batch TEXT,
  UNIQUE (region, year)
);
CREATE INDEX ix_regional_region ON regional_waste_data(region);
CREATE TABLE forecasts (
  forecast_id BIGSERIAL PRIMARY KEY,
  model_version_id BIGINT NOT NULL REFERENCES model_versions(model_version_id),
  region TEXT NOT NULL,
  target_year SMALLINT NOT NULL,
  predicted_tpd NUMERIC(12,2) NOT NULL,
  lower_tpd NUMERIC(12,2), upper_tpd NUMERIC(12,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (model_version_id, region, target_year)
);
CREATE TABLE capacity_analysis (
  capacity_id BIGSERIAL PRIMARY KEY,
  forecast_id BIGINT NOT NULL REFERENCES forecasts(forecast_id) ON DELETE CASCADE,
  capacity_tpd NUMERIC(12,2),          -- source TO_BE_VERIFIED_DURING_IMPLEMENTATION
  capacity_source TEXT,
  gap_tpd NUMERIC(12,2),
  pressure_index NUMERIC(6,3),
  priority_rank SMALLINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
