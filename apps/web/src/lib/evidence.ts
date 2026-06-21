import type { EvidenceItem, IntelligenceSnapshot } from '../types/intelligence';

export function evidenceRows(snapshot: IntelligenceSnapshot): number {
  return snapshot.evidence.reduce((total, item) => total + item.rows, 0);
}

export function sourceCount(snapshot: IntelligenceSnapshot): number {
  return new Set(snapshot.evidence.map((item) => item.source)).size;
}

export function evidenceCoverage(snapshot: IntelligenceSnapshot): string {
  const sources = sourceCount(snapshot);
  const rows = evidenceRows(snapshot);
  return `${sources} sources / ${rows.toLocaleString()} evidence rows`;
}

export function summarizeEvidence(item: EvidenceItem): string {
  return `${item.source} Â· ${item.freshness} Â· ${item.rows.toLocaleString()} rows`;
}

export function exportEvidenceMarkdown(snapshot: IntelligenceSnapshot): string {
  const lines = [
    '# Pokala HealthIntel OS Evidence Export',
    '',
    `Run: ${snapshot.meta.runId}`,
    `Status: ${snapshot.meta.status}`,
    `Refresh: ${snapshot.meta.refresh}`,
    '',
    '## Evidence Claims',
    ...snapshot.evidence.map((item) => `- **${item.claim}** â€” ${summarizeEvidence(item)}`),
    '',
    '## Claim Boundary',
    'This export is for public-data market, safety, reimbursement, and strategy intelligence. It is not clinical decision support, diagnosis, treatment guidance, HIPAA certification, or production EHR integration evidence.'
  ];

  return lines.join('\n');
}

