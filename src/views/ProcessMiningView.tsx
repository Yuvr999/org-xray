import React from 'react';
import { motion } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { ScoreGaugeMeter } from '@/components/ui/ScoreGaugeMeter';
import { mockShadowAlerts, mockShadowScore } from '@/lib/mockData';
import { ShieldAlert, AlertCircle, ArrowUpRight, TrendingUp, Zap, Sparkles } from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

export const ProcessMiningView: React.FC = () => {
  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-6 max-w-7xl mx-auto pb-20"
    >
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300">
              Live Monitoring
            </span>
            <span className="text-xs text-slate-400">Process Mining & Shadow Intelligence</span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white mt-1">
            Shadow Process Intelligence & Leakage Radar
          </h1>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-500 text-white font-bold text-xs shadow-lg shadow-rose-500/20 hover:scale-[1.02] transition-transform">
          <Sparkles className="w-4 h-4" />
          <span>Run AI Anomaly Sweep</span>
        </button>
      </div>

      {/* Top Metric Cards & Risk Gauge Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Composite Score Semi-Circle Gauge (Reference Image 4) */}
        <SoftCard className="flex flex-col items-center justify-center">
          <ScoreGaugeMeter
            score={mockShadowScore}
            title="Composite Shadow Risk Index"
            subtitle="Calculated from 14 organizational audit logs"
          />
        </SoftCard>

        {/* Card 2: Financial Leakage Impact */}
        <SoftCard className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Est. Annual Leakage
            </span>
            <div className="p-2 rounded-xl bg-rose-100 dark:bg-rose-950 text-rose-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>

          <div className="my-4">
            <span className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              $46,500
            </span>
            <p className="text-xs font-medium text-rose-500 mt-1 flex items-center gap-1">
              <span>+18.4% vs last month</span>
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/50 text-xs text-slate-600 dark:text-slate-300">
            Unsanctioned SaaS subscriptions account for 62% of financial leakage.
          </div>
        </SoftCard>

        {/* Card 3: Active Bypasses Alert */}
        <SoftCard className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Flagged Bypasses
            </span>
            <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-950 text-amber-600">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>

          <div className="my-4">
            <span className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              4 Critical
            </span>
            <p className="text-xs text-slate-400 mt-1">
              Requires immediate governance sign-off
            </p>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-200/50 dark:border-slate-800 text-xs">
            <span className="text-indigo-600 dark:text-indigo-400 font-bold cursor-pointer hover:underline flex items-center gap-1">
              <span>Auto-Remediate Bypasses</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </span>
          </div>
        </SoftCard>
      </div>

      {/* Shadow Anomaly Breakdown List */}
      <div className="flex flex-col gap-3 mt-2">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-500" />
            <span>Detected Shadow Process Workarounds</span>
          </h3>
          <span className="text-xs text-slate-400 font-medium">Sorted by Risk Score</span>
        </div>

        <motion.div
          variants={listContainerVariants}
          initial="hidden"
          animate="show"
          className="flex flex-col gap-3"
        >
          {mockShadowAlerts.map((alert) => (
            <motion.div key={alert.id} variants={listItemVariants}>
              <SoftCard className="flex items-center justify-between p-4">
                <div className="flex items-center gap-4">
                  {/* Risk Badge */}
                  <div
                    className={`w-12 h-12 rounded-2xl font-extrabold text-sm flex items-center justify-center shadow-sm ${
                      alert.severity === 'Critical'
                        ? 'bg-rose-500 text-white'
                        : alert.severity === 'High'
                        ? 'bg-amber-500 text-white'
                        : 'bg-indigo-500 text-white'
                    }`}
                  >
                    {alert.riskScore}
                  </div>

                  <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-slate-900 dark:text-white">
                        {alert.processName}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {alert.department}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Unapproved Tool: <strong className="text-slate-700 dark:text-slate-200">{alert.unapprovedTool}</strong> • {alert.detectedAt}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-bold text-rose-600 dark:text-rose-400">
                      {alert.estimatedLeakage}
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">
                      Est. Impact
                    </span>
                  </div>

                  <button className="px-3.5 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-600 hover:text-white text-indigo-600 dark:text-indigo-400 font-bold text-xs transition-all shadow-sm">
                    Investigate
                  </button>
                </div>
              </SoftCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
};
