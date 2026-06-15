
export interface Env {
  DB: D1Database;
  APP_NAME: string;
  APP_MODE: string;
}

type JsonValue = Record<string, unknown> | Array<unknown> | string | number | boolean | null;

const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,OPTIONS",
  "access-control-allow-headers": "content-type"
};

function json(payload: JsonValue, status = 200) {
  return new Response(JSON.stringify(payload, null, 2), { status, headers: jsonHeaders });
}

function html(payload: string, status = 200) {
  return new Response(payload, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store"
    }
  });
}

function esc(v: unknown) {
  return String(v ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[c] || c));
}

function num(v: unknown) {
  const n = Number(v ?? 0);
  return Number.isFinite(n) ? n : 0;
}

function pct(v: unknown) {
  return `${Math.round(num(v) * 100) / 100}`;
}

function safeJson(value: string | null | undefined) {
  if (!value) return null;
  try { return JSON.parse(value); } catch { return null; }
}

function notFound(path: string) {
  return html(shell("Not Found", "none", `
    <section class="panel heroPanel">
      <div class="eyebrow">404 / Route not found</div>
      <h1>Route unavailable</h1>
      <p class="muted">The route <code>${esc(path)}</code> is not registered in Pokala HealthIntel OS.</p>
      <div class="actions">
        <a href="/" class="btn">Open Command Center</a>
        <a href="/api" class="btn ghost">View API index</a>
      </div>
    </section>
  `), 404);
}

async function readBody<T>(request: Request): Promise<T> {
  try { return await request.json() as T; } catch { return {} as T; }
}

async function getCommandCenter(env: Env) {
  const inv = await env.DB.prepare(`SELECT * FROM investigations ORDER BY updated_at DESC LIMIT 12`).all();
  const models = await env.DB.prepare(`SELECT * FROM model_runs ORDER BY created_at DESC LIMIT 3`).all();
  const health = await env.DB.prepare(`SELECT * FROM data_health ORDER BY dataset_name ASC`).all();
  const top = await env.DB.prepare(`SELECT region, specialty, signal_name, period, value FROM signal_timeseries ORDER BY value DESC LIMIT 16`).all();
  return {
    product: env.APP_NAME,
    mode: env.APP_MODE,
    investigations: inv.results,
    model_runs: models.results,
    data_health: health.results,
    top_signals: top.results
  };
}

async function getInvestigation(env: Env, id: string) {
  const inv = await env.DB.prepare(`SELECT * FROM investigations WHERE id = ?`).bind(id).first();
  if (!inv) return null;
  const evidence = await env.DB.prepare(`SELECT * FROM evidence_items WHERE investigation_id = ? ORDER BY confidence DESC`).bind(id).all();
  const reports = await env.DB.prepare(`SELECT * FROM reports WHERE investigation_id = ? ORDER BY created_at DESC`).bind(id).all();
  return { investigation: inv, evidence: evidence.results, reports: reports.results };
}

async function createInvestigation(env: Env, request: Request) {
  const body = await readBody<{ title?: string; region?: string; specialty?: string; thesis?: string }>(request);
  const now = new Date().toISOString();
  const id = `inv_${crypto.randomUUID().slice(0, 8)}`;
  const title = body.title || `${body.region || "US"} ${body.specialty || "Healthcare"} AI market investigation`;
  const region = body.region || "Texas";
  const specialty = body.specialty || "Radiology";
  const thesis = body.thesis || "AI imaging workflow automation";
  await env.DB.prepare(`INSERT INTO investigations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).bind(
    id, title, region, specialty, thesis, "draft", 72, 48, 69, 81, "pending", now, now
  ).run();
  return await getInvestigation(env, id);
}

async function generateMemo(env: Env, id: string) {
  const data = await getInvestigation(env, id);
  if (!data) return null;
  const inv = data.investigation as Record<string, any>;
  const evidence = data.evidence as Array<Record<string, any>>;
  const bullets = evidence.slice(0, 5).map(e => `- ${e.claim} (${e.source_name}; confidence ${e.confidence})`).join("\n");
  const markdown = `# ${inv.title}

## Recommendation
Proceed with focused ${inv.region} ${inv.specialty} exploration if the commercial story is framed around workflow intelligence, evidence traceability, and human-governed AI.

## Signal Summary
- Market score: ${inv.market_score}
- Safety risk score: ${inv.safety_score}
- Reimbursement signal: ${inv.reimbursement_score}
- Transformer momentum: ${inv.transformer_momentum}

## Evidence
${bullets || "- Evidence pack pending."}

## Next Motion
Position as an executive-grade health intelligence layer: reimbursement leverage, safety monitoring, provider concentration, and model-governed signal acceleration.`;
  const reportId = `rep_${crypto.randomUUID().slice(0, 8)}`;
  await env.DB.prepare(`INSERT INTO reports VALUES (?, ?, ?, ?, ?)`).bind(
    reportId,
    id,
    markdown,
    JSON.stringify({ id: reportId, investigation_id: id, generated_by: "worker" }),
    new Date().toISOString()
  ).run();
  return { id: reportId, investigation_id: id, report_markdown: markdown };
}

async function searchEntities(env: Env, q: string) {
  const like = `%${q.toLowerCase()}%`;
  const rows = await env.DB.prepare(`
    SELECT DISTINCT entity_key as id, region, specialty, signal_name, source_name
    FROM signal_timeseries
    WHERE lower(entity_key) LIKE ? OR lower(region) LIKE ? OR lower(specialty) LIKE ? OR lower(signal_name) LIKE ?
    LIMIT 30
  `).bind(like, like, like, like).all();
  return rows.results;
}

function shell(title: string, active: string, body: string) {
  const nav = [
    ["/", "Command Center", "command"],
    ["/model-lab", "Model Lab", "model"],
    ["/data-health", "Data Health", "data"],
    ["/api", "API Index", "api"]
  ];
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${esc(title)} | Pokala HealthIntel OS</title>
  <style>
    :root{
      --bg:#030712; --bg2:#07111f; --panel:#0b1220; --panel2:#101827; --panel3:#111c31;
      --line:rgba(148,163,184,.18); --line2:rgba(103,232,249,.26);
      --text:#e5f0ff; --muted:#94a3b8; --faint:#64748b;
      --cyan:#67e8f9; --blue:#60a5fa; --violet:#a78bfa; --green:#34d399; --amber:#fbbf24; --red:#fb7185;
      --shadow:0 24px 80px rgba(0,0,0,.40);
    }
    *{box-sizing:border-box}
    body{
      margin:0; color:var(--text); font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;
      background:
        radial-gradient(circle at 15% -10%,rgba(103,232,249,.22),transparent 30%),
        radial-gradient(circle at 80% 0%,rgba(167,139,250,.17),transparent 28%),
        linear-gradient(180deg,var(--bg),#050915 55%,#030712);
      min-height:100vh;
    }
    a{color:inherit}
    .app{display:grid;grid-template-columns:260px 1fr;min-height:100vh}
    .rail{border-right:1px solid var(--line);background:rgba(3,7,18,.72);backdrop-filter:blur(18px);padding:22px;position:sticky;top:0;height:100vh}
    .brand{display:flex;align-items:center;gap:12px;margin-bottom:28px}
    .mark{width:42px;height:42px;border-radius:15px;background:linear-gradient(135deg,var(--cyan),var(--violet));box-shadow:0 0 38px rgba(103,232,249,.22)}
    .brand b{display:block;letter-spacing:-.03em}.brand span{display:block;color:var(--muted);font-size:12px;margin-top:2px}
    .nav{display:grid;gap:8px}
    .nav a{text-decoration:none;color:var(--muted);padding:12px 13px;border-radius:14px;border:1px solid transparent;font-weight:700;font-size:14px}
    .nav a.active,.nav a:hover{color:var(--text);background:rgba(255,255,255,.055);border-color:var(--line)}
    .railFoot{position:absolute;left:22px;right:22px;bottom:22px;border:1px solid var(--line);border-radius:18px;padding:14px;background:rgba(16,24,39,.62)}
    .railFoot .dot{width:8px;height:8px;background:var(--green);border-radius:99px;display:inline-block;margin-right:8px;box-shadow:0 0 16px var(--green)}
    .main{padding:24px 28px 44px;min-width:0}
    .top{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:22px}
    .kicker{color:var(--cyan);font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:900}
    h1{font-size:clamp(34px,5vw,64px);line-height:.96;letter-spacing:-.06em;margin:8px 0 0}
    .muted{color:var(--muted);line-height:1.55}.faint{color:var(--faint)}
    .statusbar{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
    .chip{border:1px solid var(--line);border-radius:999px;padding:8px 11px;background:rgba(15,23,42,.72);font-size:12px;color:var(--muted)}
    .chip strong{color:var(--text)}
    .grid{display:grid;gap:16px}.g4{grid-template-columns:repeat(4,minmax(0,1fr))}.g3{grid-template-columns:repeat(3,minmax(0,1fr))}.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
    .panel{border:1px solid var(--line);background:linear-gradient(180deg,rgba(15,23,42,.86),rgba(8,13,25,.86));border-radius:24px;box-shadow:var(--shadow);padding:20px;min-width:0}
    .panel.soft{box-shadow:none;background:rgba(15,23,42,.54)}
    .heroPanel{padding:26px}
    .metric{font-size:40px;font-weight:950;letter-spacing:-.06em;margin:4px 0}
    .label{font-size:13px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.09em}
    .good{color:var(--green)}.warn{color:var(--amber)}.hot{color:var(--red)}.accent{color:var(--cyan)}.violet{color:var(--violet)}
    table{width:100%;border-collapse:collapse}
    th,td{padding:12px 10px;border-bottom:1px solid var(--line);text-align:left;font-size:13px;vertical-align:top}
    th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.12em}
    td{color:#dbeafe}
    .bar{height:10px;background:rgba(148,163,184,.18);border-radius:99px;overflow:hidden}
    .bar span{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),var(--violet));border-radius:99px}
    .matrix{display:grid;grid-template-columns:160px repeat(8,1fr);gap:6px;align-items:center;font-size:11px}
    .cell{border:1px solid var(--line);border-radius:10px;padding:8px;background:rgba(15,23,42,.82);text-align:center;color:var(--muted)}
    .cell.hotcell{background:linear-gradient(180deg,rgba(103,232,249,.18),rgba(167,139,250,.10));border-color:var(--line2);color:var(--text)}
    .btn{display:inline-flex;align-items:center;gap:8px;text-decoration:none;border:1px solid var(--line);border-radius:14px;padding:11px 13px;background:rgba(255,255,255,.055);font-weight:900}
    .btn.primary{background:linear-gradient(135deg,var(--cyan),var(--violet));color:#061018;border:0}
    code{background:rgba(0,0,0,.3);border:1px solid var(--line);border-radius:8px;padding:2px 6px}
    .timeline{display:grid;gap:10px}.timelineItem{display:grid;grid-template-columns:110px 1fr;gap:12px;align-items:center}
    .spark{height:64px;border:1px solid var(--line);border-radius:16px;background:rgba(2,6,23,.35);padding:10px;display:flex;align-items:end;gap:8px}
    .spark i{flex:1;border-radius:7px 7px 0 0;background:linear-gradient(180deg,var(--cyan),rgba(103,232,249,.18));min-height:6px}
    @media(max-width:980px){.app{grid-template-columns:1fr}.rail{position:relative;height:auto}.railFoot{position:relative;left:auto;right:auto;bottom:auto;margin-top:18px}.g4,.g3,.g2{grid-template-columns:1fr}.top{display:block}.statusbar{justify-content:flex-start;margin-top:12px}}
  </style>
</head>
<body>
  <div class="app">
    <aside class="rail">
      <div class="brand"><div class="mark"></div><div><b>Pokala HealthIntel OS</b><span>Worker + D1 SaaS Console</span></div></div>
      <nav class="nav">
        ${nav.map(([href,label,key]) => `<a class="${active===key ? "active" : ""}" href="${href}">${label}</a>`).join("")}
      </nav>
      <div class="railFoot"><span class="dot"></span><b>Live on Workers</b><div class="muted" style="font-size:12px;margin-top:6px">D1-backed healthcare intelligence MVP</div></div>
    </aside>
    <main class="main">${body}</main>
  </div>
</body>
</html>`;
}

function scoreCard(label: string, value: unknown, tone = "accent") {
  return `<div class="panel soft"><div class="label">${esc(label)}</div><div class="metric ${tone}">${pct(value)}</div><div class="bar"><span style="width:${Math.max(0,Math.min(100,num(value)))}%"></span></div></div>`;
}

function bars(values: Array<{ label: string; value: number }>) {
  const max = Math.max(...values.map(v => v.value), 1);
  return `<div class="timeline">${values.map(v => `
    <div class="timelineItem">
      <div class="muted">${esc(v.label)}</div>
      <div class="bar"><span style="width:${Math.round((v.value/max)*100)}%"></span></div>
    </div>`).join("")}</div>`;
}

function commandCenterPage(data: any) {
  const inv = data.investigations?.[0] || {};
  const model = data.model_runs?.[0] || {};
  const health = data.data_health || [];
  const totalRows = health.reduce((a: number, r: any) => a + num(r.rows_loaded), 0);
  const topSignals = (data.top_signals || []).slice(0, 10);

  return shell("Command Center", "command", `
    <div class="top">
      <div>
        <div class="kicker">Executive Intelligence Workspace</div>
        <h1>AI Radiology Market + Safety Command Center</h1>
        <p class="muted">Live D1-backed view of the Texas radiology AI market-entry case file, overnight intelligence artifacts, and temporal momentum model output.</p>
      </div>
      <div class="statusbar">
        <span class="chip"><strong>Mode</strong> ${esc(data.mode)}</span>
        <span class="chip"><strong>D1</strong> connected</span>
        <span class="chip"><strong>Rows</strong> ${totalRows.toLocaleString()}</span>
      </div>
    </div>

    <section class="grid g4">
      ${scoreCard("Market Score", inv.market_score, "good")}
      ${scoreCard("Safety Score", inv.safety_score, "warn")}
      ${scoreCard("Reimbursement", inv.reimbursement_score, "accent")}
      ${scoreCard("Provider Density", inv.provider_score, "violet")}
    </section>

    <section class="grid g2" style="margin-top:16px">
      <div class="panel">
        <div class="kicker">Case File</div>
        <h2 style="margin:8px 0 10px">${esc(inv.title || "Investigation")}</h2>
        <p class="muted">${esc(inv.thesis || "")}</p>
        <table>
          <tr><th>Region</th><td>${esc(inv.region)}</td></tr>
          <tr><th>Specialty</th><td>${esc(inv.specialty)}</td></tr>
          <tr><th>Status</th><td><span class="good">${esc(inv.status)}</span></td></tr>
          <tr><th>Transformer Momentum</th><td>${esc(inv.transformer_momentum)}</td></tr>
          <tr><th>Updated</th><td>${esc(inv.updated_at)}</td></tr>
        </table>
      </div>

      <div class="panel">
        <div class="kicker">Temporal Model</div>
        <h2 style="margin:8px 0 10px">${esc(model.model_name || "Model")}</h2>
        <p class="muted">${esc(model.notes || "")}</p>
        <section class="grid g3">
          ${scoreCard("Accuracy", num(model.accuracy)*100, "good")}
          ${scoreCard("F1", num(model.f1)*100, "accent")}
          ${scoreCard("MAE Risk", num(model.mae)*100, "warn")}
        </section>
        <div style="margin-top:14px"><a class="btn primary" href="/model-lab">Open Model Lab</a></div>
      </div>
    </section>

    <section class="grid g2" style="margin-top:16px">
      <div class="panel">
        <div class="kicker">Dataset Health</div>
        <h2>Loaded public-source marts</h2>
        ${bars(health.map((r:any) => ({label:r.dataset_name, value:num(r.rows_loaded)})))}
        <div style="margin-top:14px"><a class="btn" href="/data-health">Open Data Health</a></div>
      </div>
      <div class="panel">
        <div class="kicker">Top Signals</div>
        <h2>D1 signal leaderboard</h2>
        <table>
          <thead><tr><th>Signal</th><th>Period</th><th>Value</th></tr></thead>
          <tbody>${topSignals.map((s:any) => `<tr><td>${esc(s.signal_name)}</td><td>${esc(s.period)}</td><td>${pct(s.value)}</td></tr>`).join("")}</tbody>
        </table>
      </div>
    </section>
  `);
}

function modelLabPage(rows: any[]) {
  const model = rows?.[0] || {};
  const attention = safeJson(model.attention_json) || model.attention || {};
  const keys = Object.keys(attention);
  const columns = keys.length ? Object.keys(attention[keys[0]] || {}) : [];
  const flat = keys.flatMap(k => columns.map(c => ({ from:k, to:c, v:num(attention[k]?.[c]) }))).sort((a,b)=>b.v-a.v).slice(0,10);

  return shell("Model Lab", "model", `
    <div class="top">
      <div>
        <div class="kicker">Temporal Transformer Lab</div>
        <h1>Model Lab</h1>
        <p class="muted">Readable model page for the temporal self-attention run. The raw JSON remains available at <code>/api/model-lab</code>.</p>
      </div>
      <div class="statusbar">
        <span class="chip"><strong>Model</strong> ${esc(model.model_type || "temporal")}</span>
        <span class="chip"><strong>Baseline</strong> ${esc(model.baseline_name || "baseline")}</span>
      </div>
    </div>

    <section class="grid g4">
      ${scoreCard("Accuracy", num(model.accuracy)*100, "good")}
      ${scoreCard("F1", num(model.f1)*100, "accent")}
      ${scoreCard("MAE", num(model.mae)*100, "warn")}
      <div class="panel soft"><div class="label">Momentum Class</div><div style="font-size:22px;font-weight:950;line-height:1.1;margin-top:12px">${esc(model.momentum_class)}</div></div>
    </section>

    <section class="grid g2" style="margin-top:16px">
      <div class="panel">
        <div class="kicker">Run Card</div>
        <h2>${esc(model.model_name || "Temporal Signal Transformer")}</h2>
        <table>
          <tr><th>ID</th><td>${esc(model.id)}</td></tr>
          <tr><th>Type</th><td>${esc(model.model_type)}</td></tr>
          <tr><th>Baseline</th><td>${esc(model.baseline_name)}</td></tr>
          <tr><th>Created</th><td>${esc(model.created_at)}</td></tr>
          <tr><th>Notes</th><td>${esc(model.notes)}</td></tr>
        </table>
      </div>

      <div class="panel">
        <div class="kicker">Top Attention Links</div>
        <h2>Signal influence ranking</h2>
        ${bars(flat.map(x => ({label:`${x.from} -> ${x.to}`, value:Math.round(x.v*10000)})))}
      </div>
    </section>

    <section class="panel" style="margin-top:16px">
      <div class="kicker">Attention Matrix</div>
      <h2>Temporal self-attention signal map</h2>
      <div class="matrix" style="margin-top:12px">
        <div class="cell"></div>
        ${columns.map(c => `<div class="cell">${esc(c)}</div>`).join("")}
        ${keys.map(k => `
          <div class="cell">${esc(k)}</div>
          ${columns.map(c => {
            const v = num(attention[k]?.[c]);
            return `<div class="cell ${v >= .126 ? "hotcell" : ""}">${v.toFixed(4)}</div>`;
          }).join("")}
        `).join("")}
      </div>
    </section>

    <section class="panel soft" style="margin-top:16px">
      <div class="kicker">Honest Model Status</div>
      <p class="muted">This is the MVP temporal self-attention artifact page. Next upgrade should train/evaluate the PyTorch transformer and make attention separation stronger. The page is now a real web view; <code>/api/model-lab</code> remains raw backend JSON.</p>
    </section>
  `);
}

function dataHealthPage(rows: any[]) {
  const total = rows.reduce((a:any,r:any)=>a+num(r.rows_loaded),0);
  const loaded = rows.filter((r:any)=>String(r.status).toLowerCase()==="loaded").length;

  return shell("Data Health", "data", `
    <div class="top">
      <div>
        <div class="kicker">Public Data Observability</div>
        <h1>Data Health</h1>
        <p class="muted">Human-readable data-source status. The raw machine endpoint remains at <code>/api/data-health</code>.</p>
      </div>
      <div class="statusbar">
        <span class="chip"><strong>Datasets</strong> ${rows.length}</span>
        <span class="chip"><strong>Loaded</strong> ${loaded}</span>
        <span class="chip"><strong>Total rows</strong> ${total.toLocaleString()}</span>
      </div>
    </div>

    <section class="grid g3">
      <div class="panel soft"><div class="label">Total Rows</div><div class="metric good">${total.toLocaleString()}</div></div>
      <div class="panel soft"><div class="label">Loaded Sources</div><div class="metric accent">${loaded}/${rows.length}</div></div>
      <div class="panel soft"><div class="label">PHI Policy</div><div class="metric violet">0</div><div class="muted">No patient data / no PHI</div></div>
    </section>

    <section class="panel" style="margin-top:16px">
      <div class="kicker">Dataset Registry</div>
      <h2>Overnight-loaded public marts</h2>
      <table>
        <thead><tr><th>Dataset</th><th>Status</th><th>Rows</th><th>Freshness</th><th>Caveat</th><th>Updated</th></tr></thead>
        <tbody>
          ${rows.map((r:any)=>`
            <tr>
              <td><strong>${esc(r.dataset_name)}</strong></td>
              <td><span class="${String(r.status).toLowerCase()==="loaded" ? "good" : "warn"}">${esc(r.status)}</span></td>
              <td>${num(r.rows_loaded).toLocaleString()}</td>
              <td>${esc(r.freshness)}</td>
              <td class="muted">${esc(r.caveat)}</td>
              <td>${esc(r.updated_at)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>

    <section class="panel" style="margin-top:16px">
      <div class="kicker">Volume Map</div>
      <h2>Rows by source</h2>
      ${bars(rows.map((r:any)=>({label:r.dataset_name, value:num(r.rows_loaded)})))}
    </section>
  `);
}

function apiIndex(env: Env) {
  return json({
    product: env.APP_NAME,
    web_pages: ["/", "/command-center", "/model-lab", "/data-health"],
    api_routes: ["/api/health", "/api/command-center", "/api/model-lab", "/api/data-health", "/api/investigations", "/api/entities/search", "/api/signals"]
  });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { headers: jsonHeaders });
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (path === "/" || path === "/app" || path === "/command-center") {
      return html(commandCenterPage(await getCommandCenter(env)));
    }

    if (path === "/model-lab") {
      const rows = await env.DB.prepare(`SELECT * FROM model_runs ORDER BY created_at DESC`).all();
      return html(modelLabPage(rows.results as any[]));
    }

    if (path === "/data-health") {
      const rows = await env.DB.prepare(`SELECT * FROM data_health ORDER BY rows_loaded DESC`).all();
      return html(dataHealthPage(rows.results as any[]));
    }

    if (path === "/api") return apiIndex(env);
    if (path === "/api/health") return json({ status: "ok", product: env.APP_NAME, mode: env.APP_MODE, time: new Date().toISOString() });
    if (path === "/api/command-center") return json(await getCommandCenter(env));

    if (path === "/api/data-health") {
      const rows = await env.DB.prepare(`SELECT * FROM data_health ORDER BY dataset_name ASC`).all();
      return json({ rows: rows.results });
    }

    if (path === "/api/model-lab") {
      const rows = await env.DB.prepare(`SELECT * FROM model_runs ORDER BY created_at DESC`).all();
      return json({ rows: rows.results.map((r: any) => ({ ...r, attention: safeJson(r.attention_json) })) });
    }

    if (path === "/api/investigations" && request.method === "GET") {
      const rows = await env.DB.prepare(`SELECT * FROM investigations ORDER BY updated_at DESC`).all();
      return json({ rows: rows.results });
    }

    if (path === "/api/investigations" && request.method === "POST") {
      return json(await createInvestigation(env, request), 201);
    }

    const invMatch = path.match(/^\/api\/investigations\/([^\/]+)$/);
    if (invMatch && request.method === "GET") {
      const data = await getInvestigation(env, invMatch[1]);
      return data ? json(data) : notFound(path);
    }

    const memoMatch = path.match(/^\/api\/investigations\/([^\/]+)\/memo$/);
    if (memoMatch && request.method === "POST") {
      const memo = await generateMemo(env, memoMatch[1]);
      return memo ? json(memo, 201) : notFound(path);
    }

    if (path === "/api/entities/search") {
      return json({ rows: await searchEntities(env, url.searchParams.get("q") || "") });
    }

    if (path === "/api/signals") {
      const region = url.searchParams.get("region") || "Texas";
      const specialty = url.searchParams.get("specialty") || "Radiology";
      const rows = await env.DB.prepare(`SELECT * FROM signal_timeseries WHERE region = ? AND specialty = ? ORDER BY period ASC`).bind(region, specialty).all();
      return json({ rows: rows.results });
    }

    return notFound(path);
  }
};
