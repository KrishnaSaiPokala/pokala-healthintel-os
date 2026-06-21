from pathlib import Path

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
app = repo / "apps" / "web" / "src" / "app" / "App.tsx"
text = app.read_text(encoding="utf-8")

if "deep_benchmark_leakage_clean.json" not in text:
    text = text.replace(
        "import modelLeakageAudit from '../data/model_leakage_audit.json';",
        "import modelLeakageAudit from '../data/model_leakage_audit.json';\nimport cleanBenchmarkRaw from '../data/deep_benchmark_leakage_clean.json';\nimport cleanLeakageAuditRaw from '../data/model_leakage_audit_clean.json';"
    )

if "const cleanBenchmark = cleanBenchmarkRaw as any;" not in text:
    text = text.replace(
        "const modelAudit = modelLeakageAudit as any;",
        "const modelAudit = modelLeakageAudit as any;\nconst cleanBenchmark = cleanBenchmarkRaw as any;\nconst cleanAudit = cleanLeakageAuditRaw as any;"
    )

helper = """
function cleanAuditLevel() {
  return cleanAudit?.warning_level ?? 'pending';
}

function cleanBestModel() {
  return cleanBenchmark?.best_model ?? {};
}
"""

if "function cleanAuditLevel()" not in text:
    marker = "function bestOvernightModel() {"
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("Could not find helper insertion point.")
    text = text[:idx] + helper + "\\n" + text[idx:]

panel = r'''
      <section className="benchmarkPanel cleanAuditPanel">
        <div className="benchmarkHeader">
          <div>
            <span className="eyebrow"><ShieldCheck size={15} /> Leakage-Clean Audit</span>
            <h2>Green audit benchmark v2</h2>
            <p>
              Clean benchmark excludes target, future, next, lead, lookahead, outcome, and near-target proxy features before rerunning the model suite.
            </p>
          </div>
          <aside>
            <span>Audit level</span>
            <strong>{cleanAuditLevel()}</strong>
          </aside>
        </div>

        <section className="modelGrid">
          <article className="modelCard">
            <span>Clean seed runs</span>
            <strong>{cleanBenchmark?.completed_seed_runs ?? '-'}</strong>
            <p>Completed after leakage-style feature removal.</p>
          </article>
          <article className="modelCard">
            <span>Failed runs</span>
            <strong>{cleanBenchmark?.failed_seed_runs ?? '-'}</strong>
            <p>Seed failures in the clean benchmark.</p>
          </article>
          <article className="modelCard">
            <span>Clean feature count</span>
            <strong>{cleanBenchmark?.cleaning?.clean_feature_count ?? '-'}</strong>
            <p>Features retained after name and correlation filtering.</p>
          </article>
          <article className="modelCard">
            <span>Best clean model</span>
            <strong>{cleanBestModel()?.model_id ?? '-'}</strong>
            <p>Best clean model by mean ROC-AUC.</p>
          </article>
        </section>

        <div className="leaderboardNote">
          Green audit means the current tabular benchmark surface removed obvious target/future/next leakage names and near-target proxy features.
          It does not claim clinical utility; the next summit layer is walk-forward validation over true temporal tensors.
        </div>
      </section>

'''

if "Green audit benchmark v2" not in text:
    anchor = "      <section className=\"benchmarkPanel legacyBenchmarkPanel\">"
    idx = text.find(anchor)
    if idx == -1:
        anchor = "      <section className=\"benchmarkPanel\">"
        idx = text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find panel anchor for green audit.")
    text = text[:idx] + panel + text[idx:]

app.write_text(text, encoding="utf-8", newline="\n")
print("Surfaced leakage-clean green audit in App.tsx")