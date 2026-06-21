from pathlib import Path

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
app = repo / "apps" / "web" / "src" / "app" / "App.tsx"
text = app.read_text(encoding="utf-8")

# Ensure imports exist.
if "deep_benchmark_leakage_clean.json" not in text:
    if "import modelLeakageAudit from '../data/model_leakage_audit.json';" in text:
        text = text.replace(
            "import modelLeakageAudit from '../data/model_leakage_audit.json';",
            "import modelLeakageAudit from '../data/model_leakage_audit.json';\n"
            "import cleanBenchmarkRaw from '../data/deep_benchmark_leakage_clean.json';\n"
            "import cleanLeakageAuditRaw from '../data/model_leakage_audit_clean.json';"
        )
    else:
        # Fallback near other data imports.
        text = text.replace(
            "import modelBenchmark from '../data/model_benchmark.json';",
            "import modelBenchmark from '../data/model_benchmark.json';\n"
            "import cleanBenchmarkRaw from '../data/deep_benchmark_leakage_clean.json';\n"
            "import cleanLeakageAuditRaw from '../data/model_leakage_audit_clean.json';"
        )

# Ensure constants exist.
if "const cleanBenchmark = cleanBenchmarkRaw as any;" not in text:
    if "const modelAudit = modelLeakageAudit as any;" in text:
        text = text.replace(
            "const modelAudit = modelLeakageAudit as any;",
            "const modelAudit = modelLeakageAudit as any;\n"
            "const cleanBenchmark = cleanBenchmarkRaw as any;\n"
            "const cleanAudit = cleanLeakageAuditRaw as any;"
        )
    else:
        text = text.replace(
            "const snapshot = rawSnapshot as any;",
            "const snapshot = rawSnapshot as any;\n"
            "const cleanBenchmark = cleanBenchmarkRaw as any;\n"
            "const cleanAudit = cleanLeakageAuditRaw as any;"
        )

# Ensure no literal escaped newline remains.
text = text.replace("\\nfunction", "\nfunction")

# Honest wording: not green if audit is red.
text = text.replace("Green audit benchmark v2", "Leakage-clean audit benchmark v2")
text = text.replace("green audit", "leakage-clean audit")
text = text.replace("Green audit", "Leakage-clean audit")

app.write_text(text, encoding="utf-8", newline="\n")
print("Fixed clean benchmark imports/constants and honest audit wording.")