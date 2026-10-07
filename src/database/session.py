"""Database session and SQLite-compatible schema management using SQLAlchemy."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..config import get_settings

_ENGINE = None
_SESSION_FACTORY = None

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  role TEXT NOT NULL DEFAULT 'citizen',
  region TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_versions (
  model_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_kind TEXT NOT NULL,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  artifact_uri TEXT,
  training_dataset TEXT,
  config_hash TEXT,
  metrics TEXT,
  status TEXT NOT NULL DEFAULT 'production',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (model_kind, name, version)
);

CREATE TABLE IF NOT EXISTS waste_observations (
  observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(user_id),
  image_uri TEXT NOT NULL,
  image_sha256 TEXT,
  region TEXT,
  latitude REAL,
  longitude REAL,
  user_condition_input TEXT,
  observed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_deleted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  observation_id INTEGER NOT NULL REFERENCES waste_observations(observation_id),
  model_version_id INTEGER,
  latency_ms INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classification_results (
  result_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prediction_id INTEGER NOT NULL REFERENCES predictions(prediction_id),
  rank INTEGER NOT NULL DEFAULT 1,
  waste_class TEXT NOT NULL,
  material TEXT,
  confidence REAL,
  gradcam_uri TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_scores (
  score_id INTEGER PRIMARY KEY AUTOINCREMENT,
  result_id INTEGER NOT NULL REFERENCES classification_results(result_id),
  score REAL,
  score_version TEXT NOT NULL,
  factor_breakdown TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_decisions (
  decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
  score_id INTEGER NOT NULL REFERENCES recovery_scores(score_id),
  route TEXT NOT NULL,
  rationale TEXT,
  decided_by TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regional_waste_data (
  regional_id INTEGER PRIMARY KEY AUTOINCREMENT,
  region TEXT NOT NULL,
  year INTEGER NOT NULL,
  latitude REAL,
  longitude REAL,
  gen_total_ulb_tpd REAL,
  treated_total_ulb_tpd REAL,
  untreated_gap_tpd REAL,
  source_report TEXT,
  extra_attributes TEXT,
  ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (region, year)
);

CREATE TABLE IF NOT EXISTS forecasts (
  forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_version_id INTEGER,
  region TEXT NOT NULL,
  target_year INTEGER NOT NULL,
  predicted_tpd REAL NOT NULL,
  lower_tpd REAL,
  upper_tpd REAL,
  model_name TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (region, target_year)
);

CREATE TABLE IF NOT EXISTS capacity_analysis (
  capacity_id INTEGER PRIMARY KEY AUTOINCREMENT,
  region TEXT NOT NULL,
  pressure_index REAL,
  category TEXT,
  latest_generation_tpd REAL,
  untreated_gap_tpd REAL,
  priority_rank INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
  recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  observation_id INTEGER REFERENCES waste_observations(observation_id),
  region TEXT,
  recommended_action TEXT NOT NULL,
  priority TEXT NOT NULL,
  explanation TEXT NOT NULL,
  route TEXT,
  community_action TEXT,
  component_trace TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS community_actions (
  action_id INTEGER PRIMARY KEY AUTOINCREMENT,
  recommendation_id INTEGER REFERENCES recommendations(recommendation_id),
  title TEXT NOT NULL,
  action_type TEXT NOT NULL,
  region TEXT,
  status TEXT NOT NULL DEFAULT 'suggested',
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_logs (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  status_code INTEGER,
  latency_ms INTEGER,
  error_code TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        settings = get_settings()
        db_url = settings.database_url or "sqlite:///waste_intelligence.db"
        connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
        _ENGINE = create_engine(db_url, connect_args=connect_args)
    return _ENGINE

def get_session():
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SESSION_FACTORY()

def apply_schema():
    engine = get_engine()
    with engine.connect() as conn:
        for stmt in SQLITE_SCHEMA.split(";"):
            stmt_clean = stmt.strip()
            if stmt_clean:
                conn.execute(text(stmt_clean))
        conn.commit()
    return True
