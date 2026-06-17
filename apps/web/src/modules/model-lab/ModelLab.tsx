import modelCard from "../../data/enterprise_model_card.json";
import featureManifest from "../../data/enterprise_temporal_manifest.json";

type Metric = {
  mae: number;
  rmse: number;
  directional_accuracy: number;
};

type ModelCard = {
  model_family: string;
  generated_at: string;
  training_rows: number;
  windows: number;
  entities: number;
  periods: number;
  feature_columns: string[];
  target: string;
  models_compared: string[];
  best_model_by_rmse: string;
  metrics: Record<string, Metric>;
  artifacts: Record<string, string>;
  claim_boundary: string[];
};

type FeatureManifest = {
  status: string;
  boundary: string;
  rows: number;
  entities: number;
  periods: number;
  feature_columns: string[];
  source_boundary: string;
};

const card = modelCard as ModelCard;
const manifest = featureManifest as FeatureManifest;

const labels: Record<string, string> = {
  persistence_last_value: "Persistence baseline",
  rolling_window_mean: "Rolling mean",
  ridge: "Ridge regression",
  random_forest: "Random forest",
  gru: "GRU sequence model",
  temporal_transformer: "Temporal Transformer v2"
};

const formatMetric = (value: number) => value.toFixed(4);
const pct = (value: number) => `${(value * 100).toFixed(1)}%`;

const rows = Object.entries(card.metrics).sort((a, b) => a[1].rmse - b[1].rmse);
const best = labels[card.best_model_by_rmse] ?? card.best_model_by_rmse;
const transformer = card.metrics.temporal_transformer;
const persistence = card.metrics.persistence_last_value;

export function ModelLab() {
  return (
    <section className="page-shell model-lab-page">
      <div className="section-kicker">Model Lab</div>
      <div className="hero-panel">
        <div>
          <h1>Enterprise temporal intelligence model lab</h1>
          <p>
            This lab compares classical baselines, a GRU sequence model, and a Temporal Transformer on the public-source HealthIntel feature matrix.
          </p>
        </div>
        <div className="status-card">
          <span>Best model by RMSE</span>
          <strong>{best}</strong>
          <small>Current run favors the simplest temporal baseline.</small>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <span>Training rows</span>
          <strong>{card.training_rows.toLocaleString()}</strong>
          <small>Feature-matrix rows</small>
        </div>
        <div className="metric-card">
          <span>Temporal windows</span>
          <strong>{card.windows.toLocaleString()}</strong>
          <small>12-period sequences</small>
        </div>
        <div className="metric-card">
          <span>Entities</span>
          <strong>{card.entities}</strong>
          <small>Texas radiology city cohorts</small>
        </div>
        <div className="metric-card">
          <span>Periods</span>
          <strong>{card.periods}</strong>
          <small>Monthly signal periods</small>
        </div>
      </div>

      <div className="casefile-grid">
        <article className="case-panel wide">
          <div className="panel-header">
            <div>
              <span className="section-kicker">Evaluation</span>
              <h2>Baseline comparison</h2>
            </div>
            <span className="pill">time-based holdout</span>
          </div>
          <div className="model-table">
            <div className="model-table-row header">
              <span>Model</span>
              <span>MAE</span>
              <span>RMSE</span>
              <span>Direction</span>
            </div>
            {rows.map(([key, metric]) => (
              <div className={key === card.best_model_by_rmse ? "model-table-row winner" : "model-table-row"} key={key}>
                <span>{labels[key] ?? key}</span>
                <span>{formatMetric(metric.mae)}</span>
                <span>{formatMetric(metric.rmse)}</span>
                <span>{pct(metric.directional_accuracy)}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="case-panel">
          <span className="section-kicker">Transformer readout</span>
          <h2>Sequence model status</h2>
          <p>
            The transformer trained successfully on the real-source feature matrix, but it does not beat the persistence baseline in this run.
          </p>
          <div className="mini-stack">
            <div><span>Transformer RMSE</span><strong>{formatMetric(transformer.rmse)}</strong></div>
            <div><span>Persistence RMSE</span><strong>{formatMetric(persistence.rmse)}</strong></div>
            <div><span>Transformer direction</span><strong>{pct(transformer.directional_accuracy)}</strong></div>
          </div>
        </article>

        <article className="case-panel">
          <span className="section-kicker">Feature matrix</span>
          <h2>{manifest.status}</h2>
          <p>{manifest.boundary}</p>
          <div className="mini-stack">
            <div><span>Rows</span><strong>{manifest.rows.toLocaleString()}</strong></div>
            <div><span>Features</span><strong>{manifest.feature_columns.length}</strong></div>
            <div><span>Target</span><strong>{card.target}</strong></div>
          </div>
        </article>

        <article className="case-panel wide">
          <span className="section-kicker">Claim boundary</span>
          <h2>What this model can and cannot claim</h2>
          <div className="claim-list">
            {card.claim_boundary.map((claim) => (
              <div key={claim}>{claim}</div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

export default ModelLab;
