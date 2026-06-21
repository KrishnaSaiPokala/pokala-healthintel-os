import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle2,
  Clipboard,
  Database,
  FileSearch,
  Filter,
  LockKeyhole,
  ShieldAlert,
  ShieldCheck
} from 'lucide-react';
import { Panel } from '../../components/Panel';
import type { IntelligenceSnapshot } from '../../types/intelligence';

type SourceGroup = 'Provider' | 'Payment' | 'Safety' | 'Research' | 'Governance';

type EvidenceClaim = {
  id: string;
  title: string;
  source: SourceGroup;
  mart: string;
  supports: string;
  doesNotProve: string;
  boundary: string;
  confidence: 'High' | 'Medium' | 'Exploratory';
  rows: string;
};

const claims: EvidenceClaim[] = [
  {
    id: 'provider-density',
    title: 'Texas radiology diligence is supported by provider/entity context.',
    source: 'Provider',
    mart: 'provider_core + temporal feature matrix',
    supports: 'Market structure and entity-density context for prioritizing outreach.',
    doesNotProve: 'Buyer intent, adoption probability, revenue, or patient-level demand.',
    boundary: 'Public NPI/entity context only. No PHI.',
    confidence: 'Medium',
    rows: '41k+ provider-context rows'
  },
  {
    id: 'cms-pressure',
    title: 'CMS utilization/payment signals provide reimbursement context.',
    source: 'Payment',
    mart: 'cms_physician_supplier_utilization_mart',
    supports: 'Aggregate service/payment pressure useful for market diligence framing.',
    doesNotProve: 'Provider profitability, negotiated rates, patient economics, or individual claims.',
    boundary: 'Aggregate public CMS context only.',
    confidence: 'Medium',
    rows: 'CMS utilization mart'
  },
  {
    id: 'maude-safety',
    title: 'openFDA/MAUDE signals are treated as safety-pressure context.',
    source: 'Safety',
    mart: 'device_event_monthly',
    supports: 'Passive reporting pressure and category-level safety posture.',
    doesNotProve: 'Incidence, causality, comparative safety, or clinical risk rate.',
    boundary: 'Passive adverse-event reports are not causal evidence.',
    confidence: 'High',
    rows: 'openFDA device-event mart'
  },
  {
    id: 'trial-momentum',
    title: 'ClinicalTrials.gov activity contributes research momentum context.',
    source: 'Research',
    mart: 'trial_density',
    supports: 'Public research activity and category momentum.',
    doesNotProve: 'Commercial adoption, clinical efficacy, or purchasing readiness.',
    boundary: 'Trial registry activity is a market signal, not outcome proof.',
    confidence: 'Medium',
    rows: 'trial-density mart'
  },
  {
    id: 'model-caveat',
    title: 'V4 model evidence is a benchmark artifact, not validated forecasting.',
    source: 'Governance',
    mart: 'enterprise_model_card + run_history_v4',
    supports: 'Transparent weak/moderate signal testing and reproducibility.',
    doesNotProve: 'Production-grade predictive validity or clinical utility.',
    boundary: 'Benchmark Lab is experimental public-source benchmarking.',
    confidence: 'Exploratory',
    rows: '2,388 model windows'
  }
];

const filters: Array<SourceGroup | 'All'> = ['All', 'Provider', 'Payment', 'Safety', 'Research', 'Governance'];

const cardMotion = {
  initial: { opacity: 0, y: 14, scale: 0.985 },
  animate: { opacity: 1, y: 0, scale: 1 },
  transition: { duration: 0.34 }
};

export function EvidenceLedger({ snapshot }: { snapshot?: IntelligenceSnapshot }) {
  const [filter, setFilter] = useState<SourceGroup | 'All'>('All');
  const [openId, setOpenId] = useState<string>('provider-density');

  const visibleClaims = useMemo(() => {
    return filter === 'All' ? claims : claims.filter((claim) => claim.source === filter);
  }, [filter]);

  const copyClaim = async (claim: EvidenceClaim) => {
    const text = [
      `Claim: ${claim.title}`,
      `Source family: ${claim.source}`,
      `Mart: ${claim.mart}`,
      `Supports: ${claim.supports}`,
      `Does not prove: ${claim.doesNotProve}`,
      `Boundary: ${claim.boundary}`
    ].join('\n');

    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Clipboard may be blocked in some browser contexts.
    }
  };

  return (
    <motion.section className="gridPage evidenceConsole" initial="initial" animate="animate">
      <Panel span={12} title="Evidence Governance" eyebrow="Trust spine" icon={ShieldCheck}>
        <motion.div className="evidenceHero" {...cardMotion}>
          <div>
            <span className="sectionKicker">Claim-to-source discipline</span>
            <h2>Every serious claim needs a source, a boundary, and a ?does not prove.?</h2>
            <p>
              The ledger turns the product from a dashboard into a defensible intelligence artifact. It separates public-data support
              from clinical, causal, patient-level, or incidence claims.
            </p>
          </div>

          <div className="evidenceTrustCard">
            <span>Evidence posture</span>
            <strong>Bounded public-source</strong>
            <small>No PHI ? No CDS ? No causality ? No incidence claims</small>
          </div>
        </motion.div>
      </Panel>

      <Panel span={12} title="Source filters" eyebrow="Evidence families" icon={Filter}>
        <div className="evidenceFilters">
          {filters.map((item) => (
            <button
              key={item}
              type="button"
              className={filter === item ? 'active' : ''}
              onClick={() => setFilter(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </Panel>

      <div className="evidenceClaimGrid">
        {visibleClaims.map((claim, index) => {
          const isOpen = openId === claim.id;

          return (
            <motion.article
              key={claim.id}
              className={`evidenceClaimCard ${isOpen ? 'open' : ''}`}
              initial={cardMotion.initial}
              animate={cardMotion.animate}
              transition={{ duration: 0.32, delay: index * 0.04 }}
              onClick={() => setOpenId(isOpen ? '' : claim.id)}
            >
              <div className="claimTopline">
                <span>{claim.source}</span>
                <strong>{claim.confidence}</strong>
              </div>

              <h3>{claim.title}</h3>

              <div className="claimMeta">
                <span><Database size={13} /> {claim.mart}</span>
                <span><FileSearch size={13} /> {claim.rows}</span>
              </div>

              {isOpen && (
                <motion.div
                  className="claimDetails"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.22 }}
                >
                  <section>
                    <CheckCircle2 size={15} />
                    <div>
                      <strong>Supports</strong>
                      <p>{claim.supports}</p>
                    </div>
                  </section>

                  <section>
                    <ShieldAlert size={15} />
                    <div>
                      <strong>Does not prove</strong>
                      <p>{claim.doesNotProve}</p>
                    </div>
                  </section>

                  <section>
                    <LockKeyhole size={15} />
                    <div>
                      <strong>Boundary</strong>
                      <p>{claim.boundary}</p>
                    </div>
                  </section>

                  <button type="button" onClick={(event) => { event.stopPropagation(); copyClaim(claim); }}>
                    <Clipboard size={14} />
                    Copy evidence note
                  </button>
                </motion.div>
              )}
            </motion.article>
          );
        })}
      </div>
    </motion.section>
  );
}

