from pathlib import Path
import json

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
app = repo / "apps" / "web" / "src" / "app" / "App.tsx"
css = repo / "apps" / "web" / "src" / "styles" / "global.css"

text = app.read_text(encoding="utf-8")

# Fix bad literal inserted by prior patch.
text = text.replace("\\nfunction bestOvernightModel() {", "\nfunction bestOvernightModel() {")

# Do not call a red audit green.
text = text.replace("Green audit benchmark v2", "Leakage-clean audit benchmark v2")
text = text.replace(
    "Green audit means the current tabular benchmark surface removed obvious target/future/next leakage names and near-target proxy features.",
    "Leakage-clean audit removed obvious target/future/next leakage names and near-target proxy features, but the clean benchmark still requires caution because performance remains near-perfect."
)

text = text.replace(
    "It does not claim clinical utility; the next summit layer is walk-forward validation over true temporal tensors.",
    "It does not claim clinical utility. The next summit layer is walk-forward validation over true temporal tensors before treating this as clean predictive proof."
)

text = text.replace(
    '<section className="benchmarkPanel cleanAuditPanel">',
    '<section className="benchmarkPanel cleanAuditPanel cautionAuditPanel">'
)

app.write_text(text, encoding="utf-8", newline="\n")

css_text = css.read_text(encoding="utf-8", errors="ignore")
marker = "/* === Leakage Clean Audit Caution Repair === */"
if marker in css_text:
    css_text = css_text[:css_text.index(marker)].rstrip()

css_text += r"""

/* === Leakage Clean Audit Caution Repair === */

.cautionAuditPanel {
  border: 1px solid rgba(245, 158, 11, 0.28);
  background:
    radial-gradient(circle at top left, rgba(245, 158, 11, 0.13), transparent 24rem),
    rgba(255, 255, 255, 0.97);
}

.cautionAuditPanel .benchmarkHeader aside strong {
  color: #b45309;
  text-transform: uppercase;
}

.cautionAuditPanel .leaderboardNote {
  background: rgba(245, 158, 11, 0.10);
  color: #92400e;
}
"""

css.write_text(css_text, encoding="utf-8", newline="\n")

audit_path = repo / "apps" / "web" / "src" / "data" / "model_leakage_audit_clean.json"
if audit_path.exists():
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    print("clean audit level:", audit.get("warning_level"))
    print("completed:", audit.get("benchmark_summary", {}).get("completed_seed_runs"))
    print("failed:", audit.get("benchmark_summary", {}).get("failed_seed_runs"))
    print("best:", audit.get("benchmark_summary", {}).get("best_model", {}))

print("Repaired App.tsx and audit wording.")