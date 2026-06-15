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
