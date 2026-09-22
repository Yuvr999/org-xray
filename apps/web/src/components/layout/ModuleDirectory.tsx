import React from 'react';
import { motion } from 'framer-motion';
import { 
  Folder, 
  ChevronDown, 
  Plus, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Search,
  Building2,
  Users
} from 'lucide-react';
import { ActiveTab } from './IconRail';
import { mockCollaborators } from '@/lib/mockData';

interface ModuleDirectoryProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  shadowAlertCount: number;
}

export const ModuleDirectory: React.FC<ModuleDirectoryProps> = ({
  activeTab,
  onTabChange,
  shadowAlertCount,
}) => {
  return (
    <aside className="w-72 flex-shrink-0 glass-panel h-screen flex flex-col justify-between p-4 z-20 border-r border-white/50 dark:border-white/5 overflow-y-auto">
      <div className="flex flex-col gap-5">
        {/* Workspace Selector */}
        <div className="flex items-center justify-between p-2 rounded-2xl bg-white/60 dark:bg-slate-800/60 border border-white/80 dark:border-slate-700/50 shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 flex items-center justify-center font-bold text-xs">
              <Building2 className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-slate-800 dark:text-slate-100">Enterprise HQ</span>
              <span className="text-[10px] text-slate-400">Org X-Ray v2.4</span>
            </div>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </div>

        {/* Quick Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search processes, invoices..."
            className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-white/40 dark:bg-slate-900/40 border border-slate-200/60 dark:border-slate-800 text-slate-700 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
          />
        </div>

        {/* Module Tree Directory */}
        <div className="flex flex-col gap-1">
          <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase px-2 mb-1">
            Governance Modules
          </span>

          <button
            onClick={() => onTabChange('process')}
            className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'process'
                ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Folder className="w-4 h-4 text-amber-500" />
              <span>Process Mining</span>
            </div>
            {shadowAlertCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-500 text-white animate-pulse">
                {shadowAlertCount} alerts
              </span>
            )}
          </button>

          <button
            onClick={() => onTabChange('invoices')}
            className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'invoices'
                ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Folder className="w-4 h-4 text-emerald-500" />
              <span>Invoice & GSTIN Hub</span>
            </div>
            <span className="text-[10px] text-slate-400 font-bold">3 docs</span>
          </button>

          <button
            onClick={() => onTabChange('demand')}
            className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'demand'
                ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Folder className="w-4 h-4 text-indigo-500" />
              <span>Demand Routing</span>
            </div>
            <span className="text-[10px] text-slate-400 font-bold">2 pending</span>
          </button>

          <button
            onClick={() => onTabChange('assets')}
            className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'assets'
                ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Folder className="w-4 h-4 text-blue-500" />
              <span>IoT Assets & Recovery</span>
            </div>
            <span className="text-[10px] text-emerald-500 font-bold">1 dormant</span>
          </button>

          <button
            onClick={() => onTabChange('governance')}
            className={`flex items-center justify-between p-2.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'governance'
                ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Folder className="w-4 h-4 text-purple-500" />
              <span>Approval Policies</span>
            </div>
          </button>
        </div>

        {/* Quick New Action Button */}
        <button className="w-full py-2.5 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-indigo-500/20 transition-all hover:scale-[1.02]">
          <Plus className="w-4 h-4" />
          <span>New Procurement Demand</span>
        </button>
      </div>

      {/* Active Collaborators Section */}
      <div className="flex flex-col gap-3 pt-4 border-t border-slate-200/60 dark:border-slate-800">
        <div className="flex items-center justify-between px-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5" />
            <span>Active Governance Team</span>
          </span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
        </div>

        <div className="flex flex-col gap-2">
          {mockCollaborators.map((c, i) => (
            <div key={i} className="flex items-center justify-between p-1.5 rounded-xl hover:bg-white/40 dark:hover:bg-slate-800/40 transition-colors">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <img src={c.avatar} alt={c.name} className="w-7 h-7 rounded-full object-cover border border-white dark:border-slate-800" />
                  <span className={`absolute bottom-0 right-0 w-2 h-2 rounded-full border border-white ${c.status === 'online' ? 'bg-emerald-500' : 'bg-amber-400'}`} />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">{c.name}</span>
                  <span className="text-[10px] text-slate-400">{c.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
