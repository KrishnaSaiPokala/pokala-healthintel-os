export interface Env {
  DB: D1Database;
  APP_NAME: string;
  APP_MODE: string;
}

type JsonValue = Record<string, unknown> | Array<unknown> | string | number | boolean | null;

const headers = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,OPTIONS",
  "access-control-allow-headers": "content-type"
};

function json(payload: JsonValue, status = 200) {
  return new Response(JSON.stringify(payload, null, 2), { status, headers });
}

function html(payload: string, status = 200) {
  return new Response(payload, {
    status,
    headers: {
      ...headers,
      "content-type": "text/html; charset=utf-8"
    }
  });
}

function landingPage() {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pokala HealthIntel OS</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #05070d;
      --panel: #0b1020;
      --panel2: #10182d;
      --text: #eef4ff;
      --muted: #9aa9c7;
      --line: rgba(255,255,255,.12);
      --accent: #67e8f9;
      --hot: #a78bfa;
      --green: #34d399;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(circle at 20% 0%, rgba(103,232,249,.20), transparent 32%),
        radial-gradient(circle at 80% 10%, rgba(167,139,250,.18), transparent 30%),
        linear-gradient(180deg, #05070d 0%, #070b14 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Arial, sans-serif;
      min-height: 100vh;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 44px 24px; }
    .nav { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 800; letter-spacing: .02em; }
    .mark {
      width: 38px; height: 38px; border-radius: 12px;
      background: linear-gradient(135deg, var(--accent), var(--hot));
      box-shadow: 0 0 35px rgba(103,232,249,.30);
    }
    .pill {
      border: 1px solid var(--line); color: var(--muted); padding: 9px 13px;
      border-radius: 999px; background: rgba(255,255,255,.04); font-size: 13px;
    }
    .hero { padding: 82px 0 46px; display: grid; grid-template-columns: 1.18fr .82fr; gap: 32px; align-items: center; }
    h1 { font-size: clamp(42px, 7vw, 86px); line-height: .92; margin: 0 0 24px; letter-spacing: -.07em; }
    .lead { color: var(--muted); font-size: 20px; line-height: 1.6; max-width: 780px; }
    .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
    a.btn {
      color: #061018; background: var(--accent); text-decoration: none; padding: 13px 18px;
      border-radius: 14px; font-weight: 800;
    }
    a.btn.secondary {
      color: var(--text); background: rgba(255,255,255,.06); border: 1px solid var(--line);
    }
    .terminal {
      border: 1px solid var(--line); border-radius: 24px; background: rgba(11,16,32,.80);
      box-shadow: 0 24px 80px rgba(0,0,0,.38); overflow: hidden;
    }
    .bar { padding: 12px 14px; border-bottom: 1px solid var(--line); color: var(--muted); font-size: 13px; }
    .screen { padding: 22px; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; line-height: 1.8; color: #c7d2fe; }
    .ok { color: var(--green); }
    .accent { color: var(--accent); }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 28px; }
    .card {
      border: 1px solid var(--line); border-radius: 22px; padding: 20px;
      background: linear-gradient(180deg, rgba(16,24,45,.92), rgba(9,13,26,.92));
      min-height: 150px;
    }
    .card h3 { margin: 0 0 10px; font-size: 15px; }
    .card p { margin: 0; color: var(--muted); line-height: 1.55; font-size: 14px; }
    .metric { font-size: 34px; font-weight: 900; margin-bottom: 8px; letter-spacing: -.04em; }
    .footer { color: var(--muted); border-top: 1px solid var(--line); margin-top: 42px; padding-top: 22px; font-size: 13px; }
    @media (max-width: 900px) {
      .hero { grid-template-columns: 1fr; padding-top: 54px; }
      .grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="wrap">
    <nav class="nav">
      <div class="brand"><div class="mark"></div><div>Pokala HealthIntel OS</div></div>
      <div class="pill">Cloudflare Worker + D1 Live MVP</div>
    </nav>

    <section class="hero">
      <div>
        <h1>Healthcare intelligence for market, safety, reimbursement, and AI-risk decisions.</h1>
        <p class="lead">
          A solo-founder HealthTech intelligence OS that converts public healthcare signals into executive-grade investigations,
          temporal momentum scores, evidence packs, and model-lab outputs.
        </p>
        <div class="actions">
          <a class="btn" href="/api/command-center">Open Command Center API</a>
          <a class="btn secondary" href="/api/model-lab">Open Model Lab</a>
          <a class="btn secondary" href="/api/data-health">Data Health</a>
        </div>
      </div>

      <div class="terminal">
        <div class="bar">live worker telemetry</div>
        <div class="screen">
          <div><span class="ok">status</span> = online</div>
          <div><span class="ok">database</span> = Cloudflare D1</div>
          <div><span class="ok">mode</span> = lone-wolf-mvp</div>
          <div><span class="accent">vertical</span> = AI Radiology Market + Safety Intelligence</div>
          <div><span class="accent">model</span> = temporal self-attention signal engine</div>
          <div><span class="accent">evidence</span> = public-source backed intelligence pack</div>
        </div>
      </div>
    </section>

    <section class="grid">
      <div class="card"><div class="metric">01</div><h3>Command Center</h3><p>Market, safety, reimbursement, and top signal summaries from D1.</p></div>
      <div class="card"><div class="metric">02</div><h3>Model Lab</h3><p>Temporal momentum, attention-style signal importance, and baseline-ready outputs.</p></div>
      <div class="card"><div class="metric">03</div><h3>Evidence Pack</h3><p>Every score is designed to connect back to a claim, source, and confidence record.</p></div>
      <div class="card"><div class="metric">04</div><h3>Next Upgrade</h3><p>Real public-source ingestion: NPPES, openFDA, CMS, ClinicalTrials.gov, Open Payments, OCR.</p></div>
    </section>

    <div class="footer">
      Built as a Cloudflare-native healthcare intelligence SaaS MVP. GitHub stores code. Cloudflare Workers serves the app/API. D1 stores investigation intelligence.
    </div>
  </main>
</body>
</html>`;
}

function notFound(path: string) {
  return json({ error: "not_found", path, product: "Pokala HealthIntel OS" }, 404);
}

async function readBody<T>(request: Request): Promise<T> {
  try { return await request.json() as T; } catch { return {} as T; }
}

async function getCommandCenter(env: Env) {
  const inv = await env.DB.prepare(`SELECT * FROM investigations ORDER BY updated_at DESC LIMIT 12`).all();
  const models = await env.DB.prepare(`SELECT * FROM model_runs ORDER BY created_at DESC LIMIT 3`).all();
  const health = await env.DB.prepare(`SELECT * FROM data_health ORDER BY dataset_name ASC`).all();
  const top = await env.DB.prepare(`SELECT region, specialty, signal_name, period, value FROM signal_timeseries ORDER BY value DESC LIMIT 16`).all();
  return { product: env.APP_NAME, mode: env.APP_MODE, investigations: inv.results, model_runs: models.results, data_health: health.results, top_signals: top.results };
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
  const markdown = `# ${inv.title}\n\n## Recommendation\nProceed with focused ${inv.region} ${inv.specialty} exploration if the commercial story is framed around workflow intelligence, evidence traceability, and human-governed AI.\n\n## Signal Summary\n- Market score: ${inv.market_score}\n- Safety risk score: ${inv.safety_score}\n- Reimbursement signal: ${inv.reimbursement_score}\n- Transformer momentum: ${inv.transformer_momentum}\n\n## Evidence\n${bullets || "- Evidence pack pending."}\n\n## Next Motion\nPosition as an executive-grade health intelligence layer: reimbursement leverage, safety monitoring, provider concentration, and model-governed signal acceleration.`;
  const reportId = `rep_${crypto.randomUUID().slice(0, 8)}`;
  await env.DB.prepare(`INSERT INTO reports VALUES (?, ?, ?, ?, ?)`).bind(reportId, id, markdown, JSON.stringify({ id: reportId, investigation_id: id, generated_by: "worker" }), new Date().toISOString()).run();
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

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { headers });
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (path === "/" || path === "/app") return html(landingPage());
    if (path === "/api") return json({ product: env.APP_NAME, routes: ["/api/health", "/api/command-center", "/api/model-lab", "/api/data-health", "/api/investigations", "/api/entities/search", "/api/signals"] });
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
    if (path === "/api/investigations" && request.method === "POST") return json(await createInvestigation(env, request), 201);
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
    if (path === "/api/entities/search") return json({ rows: await searchEntities(env, url.searchParams.get("q") || "") });
    if (path === "/api/signals") {
      const region = url.searchParams.get("region") || "Texas";
      const specialty = url.searchParams.get("specialty") || "Radiology";
      const rows = await env.DB.prepare(`SELECT * FROM signal_timeseries WHERE region = ? AND specialty = ? ORDER BY period ASC`).bind(region, specialty).all();
      return json({ rows: rows.results });
    }
    return notFound(path);
  }
};

function safeJson(value: string | null | undefined) {
  if (!value) return null;
  try { return JSON.parse(value); } catch { return null; }
}
