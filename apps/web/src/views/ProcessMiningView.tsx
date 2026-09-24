import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { useApp } from '@/context/AppContext';
import { 
  ShieldAlert, 
  AlertCircle, 
  Sparkles, 
  Activity, 
  CheckCircle2, 
  ShieldCheck, 
  Key, 
  Zap, 
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Check,
  TrendingDown,
  ExternalLink,
  Lock,
  ArrowRight
} from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

interface AnomalySolution {
  id: string;
  title: string;
  badge: string;
  impact: string;
  description: string;
}

interface EnrichedAnomaly {
  id: string;
  department: string;
  processName: string;
  riskScore: number;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  estimatedLeakage: string;
  unapprovedTool: string;
  detectedAt: string;
  status: 'Flagged' | 'Investigating' | 'Resolved';
  selectedSolutionId?: string;
  resolvedSolutionText?: string;
  solutions: AnomalySolution[];
}

const INITIAL_ANOMALIES: EnrichedAnomaly[] = [
  {
    id: 'SHD-9021',
    department: 'Marketing & Growth',
    processName: 'Unsanctioned Cloud Analytics Subscription',
    riskScore: 88,
    severity: 'Critical',
    estimatedLeakage: '$14,200 / yr',
    unapprovedTool: 'Mixpanel (Personal Credit Card Claim)',
    detectedAt: '12 mins ago',
    status: 'Flagged',
    solutions: [
      {
        id: 'sso-migrate',
        title: 'Migrate to Enterprise SSO & Consolidate',
        badge: 'Recommended (AI)',
        impact: 'Saves $14,200/yr • Zero Downtime',
        description: 'Enforce Google/Okta Single Sign-On and merge personal seats into Corporate Master Agreement.',
      },
      {
        id: 'block-gateway',
        title: 'Block Endpoint & Revoke Expensing',
        badge: 'Strict Security',
        impact: 'Immediate Risk Halt',
        description: 'Deactivate reimbursement code and redirect analytics events to approved in-house data lake.',
      },
      {
        id: 'manager-waiver',
        title: 'Issue 30-Day Manager Compliance Waiver',
        badge: 'Opex Routing',
        impact: 'Delegates Review',
        description: 'Send one-time budget authorization ticket to VP of Marketing with automatic expiry.',
      },
    ],
  },
  {
    id: 'SHD-9022',
    department: 'Engineering',
    processName: 'Bypassed Security Gateway for External API',
    riskScore: 76,
    severity: 'High',
    estimatedLeakage: '$8,500 / mo',
    unapprovedTool: 'Unverified LLM Proxy Service',
    detectedAt: '45 mins ago',
    status: 'Flagged',
    solutions: [
      {
        id: 'gemini-gateway',
        title: 'Route to Enterprise Gemini Private Gateway',
        badge: 'Recommended (AI)',
        impact: '100% Data Confidentiality',
        description: 'Auto-provision secure Google Cloud Vertex API keys with DLP filtering and audit logs.',
      },
      {
        id: 'quarantine-token',
        title: 'Revoke API Tokens & Quarantine Endpoint',
        badge: 'Security Lock',
        impact: 'Eliminates Data Leakage',
        description: 'Instantly block unverified outbound IP requests and notify repository owners.',
      },
      {
        id: 'dev-sandbox',
        title: 'Provision Isolated R&D Sandbox',
        badge: 'Dev Flexibility',
        impact: 'Zero Production Exposure',
        description: 'Isolate team traffic into non-confidential ephemeral test cluster with budget cap.',
      },
    ],
  },
  {
    id: 'SHD-9023',
    department: 'Operations',
    processName: 'Duplicate Freight Forwarder Vendor Creation',
    riskScore: 64,
    severity: 'Medium',
    estimatedLeakage: '$22,000 one-time',
    unapprovedTool: 'Direct Vendor Invoice Submission',
    detectedAt: '3 hours ago',
    status: 'Flagged',
    solutions: [
      {
        id: 'vendor-merge',
        title: 'Reconcile & Merge into Master Vendor Ledger',
        badge: 'Recommended (AI)',
        impact: 'Recovers $22,000 Duplicate',
        description: 'Cancel duplicate PO creation and apply contractual 15% freight discount code.',
      },
      {
        id: 'gstin-revalidation',
        title: 'Run 18% GST Verification & Reject Draft',
        badge: 'Tax Compliance',
        impact: 'Prevents Penalty',
        description: 'Reject unapproved vendor draft and require approved carrier GSTIN documentation.',
      },
    ],
  },
  {
    id: 'SHD-9024',
    department: 'Product Design',
    processName: 'Personal Figma Team Account Expensing',
    riskScore: 42,
    severity: 'Low',
    estimatedLeakage: '$1,800 / yr',
    unapprovedTool: 'Figma Organization Bypass',
    detectedAt: 'Yesterday',
    status: 'Resolved',
    selectedSolutionId: 'figma-org',
    resolvedSolutionText: 'Transferred 6 designers to Enterprise Figma Org with SSO provisioned.',
    solutions: [
      {
        id: 'figma-org',
        title: 'Transfer Seats to Corporate Organization',
        badge: 'Auto-Resolved',
        impact: 'Centralized Assets',
        description: 'Add users to main Figma Enterprise team and cancel personal invoice claims.',
      },
    ],
  },
];

export const ProcessMiningView: React.FC = () => {
  const { shadowAlerts } = useApp();
  const [anomalies, setAnomalies] = useState<EnrichedAnomaly[]>(INITIAL_ANOMALIES);
  const [selectedAnomalyId, setSelectedAnomalyId] = useState<string | null>(null);
  const [chosenSolutions, setChosenSolutions] = useState<Record<string, string>>({
    'SHD-9021': 'sso-migrate',
    'SHD-9022': 'gemini-gateway',
    'SHD-9023': 'vendor-merge',
    'SHD-9024': 'figma-org',
  });
  const [filterCategory, setFilterCategory] = useState<'all' | 'flagged' | 'resolved'>('all');
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [isSweeping, setIsSweeping] = useState(false);

  // Toggle single expanded anomaly row
  const toggleRow = (id: string) => {
    setSelectedAnomalyId((prev) => (prev === id ? null : id));
  };

  const handleSelectSolution = (anomalyId: string, solutionId: string) => {
    setChosenSolutions((prev) => ({
      ...prev,
      [anomalyId]: solutionId,
    }));
  };

  const handleApplySolution = (anomaly: EnrichedAnomaly) => {
    const selectedSolId = chosenSolutions[anomaly.id] || anomaly.solutions[0]?.id;
    const sol = anomaly.solutions.find((s) => s.id === selectedSolId) || anomaly.solutions[0];

    setAnomalies((prev) =>
      prev.map((item) =>
        item.id === anomaly.id
          ? {
              ...item,
              status: 'Resolved',
              resolvedSolutionText: sol.title,
            }
          : item
      )
    );

    setActionFeedback(`✅ Applied Solution: "${sol.title}" for ${anomaly.processName}. Impact resolved!`);
    setSelectedAnomalyId(null);
    setTimeout(() => setActionFeedback(null), 4000);
  };

  const handleSweep = () => {
    setIsSweeping(true);
    setActionFeedback('🔍 Scanning system event streams for unapproved SaaS and shadow processes...');
    setTimeout(() => {
      setIsSweeping(false);
      setActionFeedback('✨ AI Scan complete. All active shadow vectors categorized with solution options.');
      setTimeout(() => setActionFeedback(null), 4000);
    }, 1200);
  };

  // Filtered list
  const filteredAnomalies = anomalies.filter((a) => {
    if (filterCategory === 'flagged') return a.status !== 'Resolved';
    if (filterCategory === 'resolved') return a.status === 'Resolved';
    return true;
  });

  const activeCount = anomalies.filter((a) => a.status !== 'Resolved').length;
  const resolvedCount = anomalies.filter((a) => a.status === 'Resolved').length;

  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-6 max-w-6xl mx-auto pb-24 text-slate-900"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
            <span className="text-sm font-black text-white uppercase tracking-wider">
              Shadow Intelligence & Remediation Studio
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight mt-1">
            Detected Process Workarounds
          </h1>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSweep}
            disabled={isSweeping}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-100 disabled:opacity-50 text-blue-700 font-extrabold text-sm shadow-lg shadow-black/15 transition-all hover:scale-105 active:scale-95 cursor-pointer"
          >
            <Sparkles className={`w-4 h-4 text-blue-600 ${isSweeping ? 'animate-spin' : ''}`} />
            <span>{isSweeping ? 'Scanning...' : 'Scan Now'}</span>
          </button>
        </div>
      </div>

      {/* Feedback Toast */}
      <AnimatePresence>
        {actionFeedback && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="p-4 rounded-2xl bg-white text-slate-900 text-sm font-bold border border-slate-200 shadow-xl flex items-center gap-3"
          >
            <Activity className="w-5 h-5 text-blue-600 flex-shrink-0 animate-pulse" />
            <span>{actionFeedback}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stat Boxes (White Boxes with Black Fonts) */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-lg shadow-blue-950/10 flex items-center justify-between">
          <div>
            <span className="text-xs font-black text-slate-500 uppercase tracking-wider">Active Bypasses</span>
            <span className="block text-3xl font-black text-slate-900 mt-1">{activeCount}</span>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-lg shadow-blue-950/10 flex items-center justify-between">
          <div>
            <span className="text-xs font-black text-slate-500 uppercase tracking-wider">Resolved Cases</span>
            <span className="block text-3xl font-black text-blue-600 mt-1">{resolvedCount}</span>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-lg shadow-blue-950/10 flex items-center justify-between">
          <div>
            <span className="text-xs font-black text-slate-500 uppercase tracking-wider">Est. Annual Leakage</span>
            <span className="block text-3xl font-black text-slate-900 mt-1">$46,500</span>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
            <TrendingDown className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between border-b border-white/20 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterCategory('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filterCategory === 'all'
                ? 'bg-white text-blue-700 shadow-md shadow-black/10'
                : 'text-white hover:bg-white/15 bg-white/10 border border-white/20'
            }`}
          >
            All Workarounds ({anomalies.length})
          </button>
          <button
            onClick={() => setFilterCategory('flagged')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filterCategory === 'flagged'
                ? 'bg-white text-blue-700 shadow-md shadow-black/10'
                : 'text-white hover:bg-white/15 bg-white/10 border border-white/20'
            }`}
          >
            Pending Solutions ({activeCount})
          </button>
          <button
            onClick={() => setFilterCategory('resolved')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filterCategory === 'resolved'
                ? 'bg-white text-blue-700 shadow-md shadow-black/10'
                : 'text-white hover:bg-white/15 bg-white/10 border border-white/20'
            }`}
          >
            Resolved ({resolvedCount})
          </button>
        </div>

        <span className="text-xs text-blue-100 font-semibold hidden sm:inline">
          Click any row to choose & apply a solution
        </span>
      </div>

      {/* Anomaly Accordion List (White Boxes with Black Fonts) */}
      <motion.div variants={listContainerVariants} initial="hidden" animate="show" className="flex flex-col gap-3">
        {filteredAnomalies.map((alert) => {
          const isExpanded = selectedAnomalyId === alert.id;
          const isResolved = alert.status === 'Resolved';
          const currentSolutionId = chosenSolutions[alert.id] || alert.solutions[0]?.id;

          return (
            <motion.div
              key={alert.id}
              variants={listItemVariants}
              layout
              className={`rounded-2xl transition-all duration-200 overflow-hidden bg-white border ${
                isExpanded
                  ? 'border-blue-500 shadow-2xl ring-2 ring-blue-500/20'
                  : 'border-slate-200 hover:border-blue-400 shadow-lg shadow-blue-950/10'
              }`}
            >
              {/* Row Summary Header */}
              <div
                onClick={() => toggleRow(alert.id)}
                className="p-4 sm:p-5 flex items-center justify-between gap-4 cursor-pointer select-none"
              >
                {/* Left: Risk Score & Details */}
                <div className="flex items-center gap-3.5 min-w-0">
                  <div
                    className={`w-10 h-10 rounded-xl font-black text-xs flex items-center justify-center flex-shrink-0 shadow-sm ${
                      isResolved
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : alert.riskScore > 80
                        ? 'bg-blue-600 text-white shadow-blue-600/30'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {isResolved ? <Check className="w-5 h-5" /> : alert.riskScore}
                  </div>

                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-extrabold text-slate-900 truncate">
                        {alert.processName}
                      </span>
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {alert.department}
                      </span>
                      {isResolved && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-sky-50 text-sky-700 border border-sky-200 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Resolved
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5 truncate">
                      Tool: <strong className="text-slate-800">{alert.unapprovedTool}</strong> • {alert.detectedAt}
                    </p>
                  </div>
                </div>

                {/* Right: Impact & Action Trigger */}
                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="text-right hidden sm:block">
                    <span className="text-xs font-black text-blue-600 block">
                      {alert.estimatedLeakage}
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase font-bold">Est. Impact</span>
                  </div>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleRow(alert.id);
                    }}
                    className={`px-3.5 py-1.5 rounded-xl font-bold text-xs transition-all flex items-center gap-1.5 cursor-pointer border ${
                      isExpanded
                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                        : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
                    }`}
                  >
                    <span>{isExpanded ? 'Hide Options' : isResolved ? 'View Solution' : 'Select Solution'}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Expandable Solutions Panel (White Box with Black Fonts) */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden border-t border-slate-200 bg-slate-50/80 p-4 sm:p-5"
                  >
                    <div className="flex flex-col gap-4">
                      {/* Section Title */}
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                          <Zap className="w-3.5 h-3.5 text-blue-600" />
                          <span>Choose a Remediation Solution:</span>
                        </span>
                        <span className="text-[11px] text-slate-500 font-semibold">
                          {alert.solutions.length} verified resolution paths
                        </span>
                      </div>

                      {/* Solution Options Selector (White cards with Black Fonts) */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {alert.solutions.map((sol) => {
                          const isSelected = currentSolutionId === sol.id;

                          return (
                            <div
                              key={sol.id}
                              onClick={() => handleSelectSolution(alert.id, sol.id)}
                              className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between relative ${
                                isSelected
                                  ? 'bg-blue-50/90 border-blue-600 shadow-md ring-1 ring-blue-500/30'
                                  : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                              }`}
                            >
                              <div>
                                <div className="flex items-center justify-between gap-2 mb-2">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                      isSelected
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-slate-100 text-slate-700'
                                    }`}
                                  >
                                    {sol.badge}
                                  </span>
                                  <span className="text-[10px] font-bold text-blue-600">{sol.impact}</span>
                                </div>

                                <h4 className="text-xs font-bold text-slate-900 mb-1 leading-snug">
                                  {sol.title}
                                </h4>
                                <p className="text-[11px] text-slate-600 leading-relaxed">
                                  {sol.description}
                                </p>
                              </div>

                              <div className="pt-3 mt-3 border-t border-slate-200 flex items-center justify-between text-[11px]">
                                <span className={isSelected ? 'text-blue-700 font-bold' : 'text-slate-500'}>
                                  {isSelected ? '✓ Selected Option' : 'Click to Select'}
                                </span>
                                <div
                                  className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                                    isSelected
                                      ? 'border-blue-600 bg-blue-600 text-white'
                                      : 'border-slate-300 bg-white'
                                  }`}
                                >
                                  {isSelected && <Check className="w-3 h-3" />}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      {/* Execute Solution Action Footer */}
                      <div className="pt-3 border-t border-slate-200 flex items-center justify-between gap-4">
                        <div className="text-xs text-slate-600">
                          {isResolved ? (
                            <span className="text-blue-700 font-semibold">
                              Resolution Status: {alert.resolvedSolutionText}
                            </span>
                          ) : (
                            <span>Selected action will execute automated rule & update audit trail.</span>
                          )}
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => toggleRow(alert.id)}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 transition-colors cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => handleApplySolution(alert)}
                            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 active:bg-blue-700 shadow-md shadow-blue-600/25 transition-all flex items-center gap-1.5 cursor-pointer"
                          >
                            <span>Apply Selected Solution</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </motion.div>
    </motion.div>
  );
};
