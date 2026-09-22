import React from 'react';
import { motion } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { ShieldCheck, UserCheck, CheckCircle2, Clock, Lock, Key } from 'lucide-react';
import { pageFadeVariants } from '@/lib/motion-config';

export const GovernanceView: React.FC = () => {
  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-6 max-w-7xl mx-auto pb-20"
    >
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-xs font-bold text-purple-600 dark:text-purple-400">
            Governance & Approval Architecture
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white mt-1">
            Multi-Tiered Sign-off Policies & Purchase Limits
          </h1>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4" />
          <span>RBAC Enforcement Active</span>
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SoftCard className="flex flex-col gap-3 border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Tier 1 Approval</span>
            <span className="text-xs font-extrabold text-emerald-600">Up to $5,000</span>
          </div>
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">Manager Sign-off</h3>
          <p className="text-xs text-slate-500">Requires direct department manager approval. AI rule engine performs instant compliance check.</p>
          <div className="pt-2 border-t border-slate-200/50 dark:border-slate-800 text-[11px] font-bold text-slate-400">
            Avg turn-around: 1.2 hours
          </div>
        </SoftCard>

        <SoftCard className="flex flex-col gap-3 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Tier 2 Approval</span>
            <span className="text-xs font-extrabold text-amber-600">$5,000 – $25,000</span>
          </div>
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">Finance & Tax Sign-off</h3>
          <p className="text-xs text-slate-500">Requires Finance Director sign-off + GSTIN verification audit before budget commitment.</p>
          <div className="pt-2 border-t border-slate-200/50 dark:border-slate-800 text-[11px] font-bold text-slate-400">
            Avg turn-around: 4.5 hours
          </div>
        </SoftCard>

        <SoftCard className="flex flex-col gap-3 border-l-4 border-l-indigo-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Tier 3 Approval</span>
            <span className="text-xs font-extrabold text-indigo-600">$25,000+</span>
          </div>
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">Executive & Procurement Board</h3>
          <p className="text-xs text-slate-500">Full governance review with vendor MSA negotiation check and shadow risk assessment.</p>
          <div className="pt-2 border-t border-slate-200/50 dark:border-slate-800 text-[11px] font-bold text-slate-400">
            Avg turn-around: 24 hours
          </div>
        </SoftCard>
      </div>
    </motion.div>
  );
};
