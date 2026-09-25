import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { 
  ShieldCheck, 
  UserCheck, 
  CheckCircle2, 
  Clock, 
  Lock, 
  Key, 
  ChevronRight, 
  Layers, 
  Sliders, 
  Zap, 
  DollarSign,
  FileCheck2,
  Building2,
  Scale,
  Sparkles
} from 'lucide-react';
import { pageFadeVariants, listItemVariants } from '@/lib/motion-config';

interface SignOffPolicy {
  id: string;
  title: string;
  subtitle: string;
  badge: string;
  limit: string;
  avgTurnaround: string;
  description: string;
  tags: string[];
  rules: string[];
  authorizer: string;
  auditFrequency: string;
}

const SIGN_OFF_POLICIES: SignOffPolicy[] = [
  {
    id: 'manager',
    title: 'Manager Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 1 Approval',
    limit: 'Up to $5,000',
    avgTurnaround: '1.2 hours',
    description:
      'Requires direct department manager approval. AI rule engine performs instant compliance check, budget reservation, and automated duplicate prevention.',
    tags: ['LOGISTICS', 'OPEX BUDGET', 'INSTANT AI', 'TIER 1'],
    rules: [
      'Line-manager electronic signature verification',
      'Automated check against remaining quarterly departmental budget',
      'Zero shadow IT anomaly match required prior to release',
    ],
    authorizer: 'Direct Department Lead / Engineering Manager',
    auditFrequency: 'Continuous Real-time AI Stream',
  },
  {
    id: 'finance',
    title: 'Finance & Tax Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 2 Approval',
    limit: '$5,000 – $25,000',
    avgTurnaround: '4.5 hours',
    description:
      'Requires Finance Director sign-off + GSTIN verification audit before budget commitment. Cross-verifies vendor tax ledgers and 18% statutory IGST/CGST rates.',
    tags: ['TAX AUDIT', '18% GSTIN', 'FINANCE DIR', 'TIER 2'],
    rules: [
      'Automated GSTIN format and checksum algorithmic validation',
      'PO creation and 3-way match against vendor invoice pro-forma',
      'Secondary audit trail logged to immutable event store',
    ],
    authorizer: 'Finance Director / Corporate Controller',
    auditFrequency: 'Daily Ledger Reconciliation',
  },
  {
    id: 'executive',
    title: 'Executive & Procurement Board',
    subtitle: 'Sign-off',
    badge: 'Tier 3 Approval',
    limit: '$25,000+',
    avgTurnaround: '24 hours',
    description:
      'Full governance review with vendor MSA negotiation check, shadow risk assessment, multi-year commitment terms, and physical asset reallocation sweep.',
    tags: ['BOARD REVIEW', 'MSA CONTRACT', 'CAPEX', 'TIER 3'],
    rules: [
      'Master Services Agreement (MSA) legal and security sign-off',
      'Mandatory dormant asset telemetry sweep before new purchase order',
      'C-Suite / Procurement Committee unanimous sign-off',
    ],
    authorizer: 'Chief Financial Officer & VP of Procurement',
    auditFrequency: 'Bi-weekly Executive Governance Committee',
  },
  {
    id: 'legal',
    title: 'Legal & Security Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 4 Governance',
    limit: 'Enterprise & SaaS',
    avgTurnaround: '48 hours',
    description:
      'Enterprise SLA review, SOC2 Type II compliance audit, data security protocols, cross-border IP governance, and mutual NDA verification.',
    tags: ['COMPLIANCE', 'SOC2 / GDPR', 'LEGAL COUNSEL', 'TIER 4'],
    rules: [
      'Data Privacy Addendum (DPA) and GDPR/HIPAA compliance validation',
      'Third-party cloud vendor vulnerability and penetration test review',
      'General Counsel approval for custom contract liability limits',
    ],
    authorizer: 'General Counsel & Chief Information Security Officer',
    auditFrequency: 'Quarterly Risk Review',
  },
];

export const GovernanceView: React.FC = () => {
  const [selectedPolicyId, setSelectedPolicyId] = useState<string>('manager');
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({
    manager: true,
    finance: false,
    executive: false,
    legal: false,
  });

  const selectedPolicy = SIGN_OFF_POLICIES.find((p) => p.id === selectedPolicyId) || SIGN_OFF_POLICIES[0];

  const toggleCard = (id: string) => {
    setSelectedPolicyId(id);
    setExpandedCards((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-8 max-w-7xl mx-auto pb-24"
    >
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col">
          <span className="text-sm font-black text-white flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-white" />
            Governance & Approval Architecture
          </span>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white mt-1">
            Multi-Tiered Sign-off Policies & Purchase Limits
          </h1>
          <p className="text-sm text-blue-100 mt-1 font-medium">
            Click any sign-off box to inspect thresholds, automated AI checks, and SLA governance rules.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="px-4 py-2 rounded-2xl text-sm font-extrabold bg-white text-blue-700 border border-slate-200 flex items-center gap-2 shadow-md">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            <span>RBAC Enforcement Active</span>
          </span>
        </div>
      </div>

      {/* SECTION 1: Interactive Brand-Style Boxes Row (Reference Style from Image 2 & 3) */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-black uppercase tracking-wider text-white">
            Sign-off Matrix Selector (Click a box to reveal information)
          </span>
          <span className="text-xs text-blue-100 font-bold">
            {SIGN_OFF_POLICIES.length} Configured Tiers
          </span>
        </div>

        {/* Minimalist Horizontal Box Rail */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SIGN_OFF_POLICIES.map((policy) => {
            const isSelected = selectedPolicyId === policy.id;

            return (
              <button
                key={policy.id}
                onClick={() => {
                  setSelectedPolicyId(policy.id);
                  setExpandedCards((prev) => ({ ...prev, [policy.id]: true }));
                }}
                className={`group relative p-5 rounded-2xl text-left transition-all duration-300 flex flex-col justify-between h-32 cursor-pointer border ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-500 shadow-xl shadow-blue-600/25 ring-2 ring-white/60'
                    : 'bg-white hover:bg-slate-50 text-slate-900 border-slate-200 shadow-md'
                }`}
              >
                {/* Title */}
                <div className="flex flex-col">
                  <span
                    className={`text-sm font-black tracking-tight transition-colors ${
                      isSelected ? 'text-white' : 'text-slate-900 group-hover:text-blue-600'
                    }`}
                  >
                    {policy.title}
                  </span>
                  <span
                    className={`text-xs font-bold mt-1 tracking-wide ${
                      isSelected ? 'text-blue-100' : 'text-slate-600'
                    }`}
                  >
                    {policy.subtitle}
                  </span>
                </div>

                {/* Bottom Limit Indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-200 text-[11px] font-black">
                  <span className={isSelected ? 'text-sky-200' : 'text-blue-700'}>
                    {policy.limit}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono font-bold ${
                    isSelected ? 'bg-blue-700/80 text-white' : 'bg-blue-100 text-blue-900'
                  }`}>
                    {policy.avgTurnaround}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* SECTION 2: Active Spotlight Card (Crisp White Card with Black Font) */}
      <AnimatePresence mode="wait">
        {selectedPolicy && (
          <motion.div
            key={selectedPolicy.id}
            initial={{ opacity: 0, y: 12, scale: 0.99 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.99 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="rounded-3xl p-6 sm:p-8 bg-white text-slate-900 border border-slate-200 shadow-xl relative overflow-hidden"
          >
            <div className="relative z-10 flex flex-col gap-6">
              {/* Card Top Title & Limit Badge */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-slate-200 pb-6">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-blue-100 text-blue-800 border border-blue-200">
                      {selectedPolicy.badge}
                    </span>
                    <span className="text-xs text-blue-600 font-bold">• Active Policy</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 mt-1">
                    {selectedPolicy.title}
                  </h2>
                  <p className="text-xs text-slate-600 font-semibold">
                    Governed Role: <strong className="text-slate-900">{selectedPolicy.authorizer}</strong>
                  </p>
                </div>

                <div className="flex flex-col sm:items-end gap-1 bg-blue-50 p-3.5 rounded-2xl border border-blue-200">
                  <span className="text-[10px] font-black text-blue-700 uppercase tracking-wider">
                    Sign-off Limit
                  </span>
                  <span className="text-xl font-black text-slate-900">
                    {selectedPolicy.limit}
                  </span>
                  <span className="text-[11px] font-bold text-slate-600">
                    SLA: {selectedPolicy.avgTurnaround}
                  </span>
                </div>
              </div>

              {/* Main Policy Description */}
              <div className="flex flex-col gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-blue-600">
                  Policy Summary & Architectural Scope
                </span>
                <p className="text-sm sm:text-base leading-relaxed text-slate-800 font-medium max-w-4xl">
                  {selectedPolicy.description}
                </p>
              </div>

              {/* Enforcement Rules Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                {selectedPolicy.rules.map((rule, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col gap-2 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-center gap-2 text-xs font-black text-blue-600">
                      <CheckCircle2 className="w-4 h-4 text-blue-500" />
                      <span>Rule 0{idx + 1}</span>
                    </div>
                    <p className="text-xs text-slate-800 leading-normal font-medium">
                      {rule}
                    </p>
                  </div>
                ))}
              </div>

              {/* Bottom Pill Tags */}
              <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
                <div className="flex flex-wrap items-center gap-2">
                  {selectedPolicy.tags.map((tag, tidx) => (
                    <span
                      key={tidx}
                      className="px-3 py-1.5 rounded-xl text-xs font-black tracking-wider bg-slate-100 text-slate-900 border border-slate-200 uppercase"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-600 font-mono font-bold">
                    Audit: {selectedPolicy.auditFrequency}
                  </span>
                  <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black text-xs shadow-lg shadow-blue-600/30 transition-all hover:scale-105 active:scale-95 cursor-pointer">
                    Simulate Sign-off
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* SECTION 3: All Policy Cards with In-Place Click-to-Expand Information */}
      <div className="flex flex-col gap-4">
        <span className="text-xs font-black uppercase tracking-wider text-white">
          Individual Sign-off Boxes (Click any box to expand all details)
        </span>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SIGN_OFF_POLICIES.map((policy) => {
            const isExpanded = expandedCards[policy.id];

            return (
              <motion.div
                key={policy.id}
                layout
                transition={{ duration: 0.2 }}
              >
                <SoftCard
                  onClick={() => toggleCard(policy.id)}
                  className={`flex flex-col justify-between transition-all cursor-pointer border-l-4 bg-white text-slate-900 shadow-md ${
                    selectedPolicyId === policy.id
                      ? 'border-l-blue-600 ring-2 ring-blue-500/40 bg-blue-50/30'
                      : 'border-l-blue-500 hover:border-l-blue-600'
                  }`}
                >
                  {/* Top Bar */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-blue-600">
                        {policy.badge}
                      </span>
                    </div>
                    <span className="text-xs font-black text-blue-700">
                      {policy.limit}
                    </span>
                  </div>

                  {/* Header Title & Subtitle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-black text-slate-900">
                        {policy.title}
                      </h3>
                      <p className="text-xs font-bold text-slate-500">
                        {policy.subtitle}
                      </p>
                    </div>

                    <span className="text-xs text-blue-700 font-bold px-2 py-1 rounded-lg bg-blue-50 border border-blue-200">
                      {isExpanded ? 'Hide Info ▲' : 'View Info ▼'}
                    </span>
                  </div>

                  {/* Expandable Information */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.25 }}
                        className="overflow-hidden flex flex-col gap-3 pt-3 mt-3 border-t border-slate-200"
                      >
                        <p className="text-xs text-slate-800 leading-relaxed font-medium">
                          {policy.description}
                        </p>

                        <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 flex flex-col gap-1.5">
                          <span className="text-[10px] font-black uppercase text-blue-700">
                            Key Approval Requirements:
                          </span>
                          {policy.rules.map((r, ri) => (
                            <div key={ri} className="flex items-start gap-1.5 text-[11px] text-slate-800 font-medium">
                              <span className="text-blue-600 font-black">•</span>
                              <span>{r}</span>
                            </div>
                          ))}
                        </div>

                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          {policy.tags.map((t, ti) => (
                            <span
                              key={ti}
                              className="px-2 py-0.5 rounded-md text-[10px] font-black bg-blue-100 text-blue-900 border border-blue-200"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Card Bottom Meta */}
                  <div className="pt-3 mt-3 border-t border-slate-200 flex items-center justify-between text-[11px] font-bold text-slate-600">
                    <span>Avg turn-around: <strong className="text-slate-900">{policy.avgTurnaround}</strong></span>
                    <span className="font-mono text-slate-700">{policy.authorizer.split('/')[0]}</span>
                  </div>
                </SoftCard>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};
