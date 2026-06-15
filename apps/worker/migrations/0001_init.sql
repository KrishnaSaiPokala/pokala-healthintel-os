DROP TABLE IF EXISTS investigations;
DROP TABLE IF EXISTS evidence_items;
DROP TABLE IF EXISTS model_runs;
DROP TABLE IF EXISTS signal_timeseries;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS data_health;

CREATE TABLE investigations (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  region TEXT,
  specialty TEXT,
  thesis TEXT,
  status TEXT,
  market_score REAL,
  safety_score REAL,
  reimbursement_score REAL,
  provider_score REAL,
  transformer_momentum TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX idx_investigations_region_specialty ON investigations(region, specialty);

CREATE TABLE evidence_items (
  id TEXT PRIMARY KEY,
  investigation_id TEXT,
  source_name TEXT,
  source_url TEXT,
  claim TEXT,
  metric_name TEXT,
  metric_value TEXT,
  confidence REAL,
  rows_examined INTEGER,
  generated_at TEXT
);
CREATE INDEX idx_evidence_investigation ON evidence_items(investigation_id);

CREATE TABLE model_runs (
  id TEXT PRIMARY KEY,
  model_name TEXT,
  model_type TEXT,
  baseline_name TEXT,
  accuracy REAL,
  f1 REAL,
  mae REAL,
  momentum_class TEXT,
  notes TEXT,
  attention_json TEXT,
  created_at TEXT
);

CREATE TABLE signal_timeseries (
  id TEXT PRIMARY KEY,
  entity_key TEXT,
  region TEXT,
  specialty TEXT,
  signal_name TEXT,
  period TEXT,
  value REAL,
  source_name TEXT
);
CREATE INDEX idx_signal_lookup ON signal_timeseries(region, specialty, signal_name, period);

CREATE TABLE reports (
  id TEXT PRIMARY KEY,
  investigation_id TEXT,
  report_markdown TEXT,
  report_json TEXT,
  created_at TEXT
);
CREATE INDEX idx_reports_investigation ON reports(investigation_id);

CREATE TABLE data_health (
  id TEXT PRIMARY KEY,
  dataset_name TEXT,
  rows_loaded INTEGER,
  freshness TEXT,
  status TEXT,
  caveat TEXT,
  updated_at TEXT
);
