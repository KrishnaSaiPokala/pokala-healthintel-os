import staticIntel from '../data/intelligence.json';

const apiBase = (import.meta as any).env?.VITE_API_BASE || '';

export async function fetchCommandCenter() {
  if (!apiBase) return { product: 'Pokala HealthIntel OS', staticMode: true, intelligence: staticIntel };
  const res = await fetch(`${apiBase}/api/command-center`);
  if (!res.ok) throw new Error(`API command-center failed: ${res.status}`);
  return res.json();
}

export async function fetchApiHealth() {
  if (!apiBase) return { status: 'static-fallback', product: 'Pokala HealthIntel OS' };
  const res = await fetch(`${apiBase}/api/health`);
  if (!res.ok) throw new Error(`API health failed: ${res.status}`);
  return res.json();
}

export async function createInvestigation(input: { title?: string; region?: string; specialty?: string; thesis?: string }) {
  if (!apiBase) return null;
  const res = await fetch(`${apiBase}/api/investigations`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(input)
  });
  if (!res.ok) throw new Error(`Create investigation failed: ${res.status}`);
  return res.json();
}

