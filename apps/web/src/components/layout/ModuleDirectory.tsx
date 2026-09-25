import React from 'react';
import { motion } from 'framer-motion';
import { 
  Folder, 
  ChevronDown, 
  Plus, 
  RotateCcw,
  Sparkles, 
  Search, 
  Building2, 
  Users,
  Layers,
  FileText,
  Box,
  ShoppingCart,
  ShieldCheck,
  Activity
} from 'lucide-react';
import { ActiveTab } from './IconRail';
import { useApp } from '@/context/AppContext';
import { mockCollaborators } from '@/lib/mockData';

interface ModuleDirectoryProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  onOpenFeatureModal?: (tab?: 'add' | 'reset') => void;
  userSession?: import('@/components/auth/AuthFlow').UserSession | null;
}

export const ModuleDirectory: React.FC<ModuleDirectoryProps> = ({
  activeTab,
  onTabChange,
  onOpenFeatureModal,
  userSession,
}) => {
  const { invoices, demands, assets, shadowAlerts, customFeatures } = useApp();
  const role = userSession?.role || 'admin';

  return (
    <aside className="w-80 flex-shrink-0 glass-panel h-screen flex flex-col justify-between p-4 z-20 border-r border-slate-200 overflow-y-auto bg-white/95 backdrop-blur-xl">
      <div className="flex flex-col gap-5">
        {/* Workspace Selector */}
        <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-sm border border-blue-200">
              <Building2 className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-black text-slate-900">Enterprise HQ</span>
              <span className="text-xs font-bold text-slate-500">Org X-Ray v2.4</span>
            </div>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-500" />
        </div>

        {/* Quick Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search processes, invoices..."
            className="w-full pl-10 pr-3.5 py-2.5 rounded-xl text-sm font-medium bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500/40 transition-all"
          />
        </div>

        {/* Module Tree Directory */}
        <div className="flex flex-col gap-1.5">
          <span className="text-xs font-black tracking-widest text-slate-500 uppercase px-2 mb-1">
            {role === 'employee' ? 'Staff Portal' : role === 'manager' ? 'Management Modules' : 'Governance Modules'}
          </span>

          {role === 'admin' && (
            <button
              onClick={() => onTabChange('process')}
              className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                activeTab === 'process'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-800 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <Activity className={`w-5 h-5 ${activeTab === 'process' ? 'text-white' : 'text-blue-600'}`} />
                <span className="font-extrabold">Shadow Process Mining</span>
              </div>
              {shadowAlerts.length > 0 && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-black ${
                  activeTab === 'process' ? 'bg-white text-blue-800' : 'bg-blue-600 text-white'
                }`}>
                  {shadowAlerts.length}
                </span>
              )}
            </button>
          )}

          <button
            onClick={() => onTabChange('invoices')}
            className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer ${
              activeTab === 'invoices'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-800 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <FileText className={`w-5 h-5 ${activeTab === 'invoices' ? 'text-white' : 'text-blue-600'}`} />
              <span className="font-extrabold">
                {role === 'employee' ? 'Upload Invoice & GST' : role === 'manager' ? 'Invoice Audits & Approvals' : 'Invoices & GSTIN Ledger'}
              </span>
            </div>
            <span className={`text-xs font-bold ${activeTab === 'invoices' ? 'text-blue-100' : 'text-slate-500'}`}>
              {invoices.length} docs
            </span>
          </button>

          <button
            onClick={() => onTabChange('demand')}
            className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer ${
              activeTab === 'demand'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-800 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <ShoppingCart className={`w-5 h-5 ${activeTab === 'demand' ? 'text-white' : 'text-blue-600'}`} />
              <span className="font-extrabold">
                {role === 'employee' ? 'Purchase Requisitions' : role === 'manager' ? 'Department Requisitions' : 'Demand Routing Flow'}
              </span>
            </div>
            <span className={`text-xs font-bold ${activeTab === 'demand' ? 'text-blue-100' : 'text-slate-500'}`}>
              {demands.length} items
            </span>
          </button>

          <button
            onClick={() => onTabChange('assets')}
            className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer ${
              activeTab === 'assets'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-800 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <Box className={`w-5 h-5 ${activeTab === 'assets' ? 'text-white' : 'text-blue-600'}`} />
              <span className="font-extrabold">
                {role === 'employee' ? 'My Assigned Assets' : role === 'manager' ? 'Department Asset Pool' : 'IoT & Asset Recovery'}
              </span>
            </div>
            <span className={`text-xs font-bold ${activeTab === 'assets' ? 'text-blue-100' : 'text-blue-600'}`}>
              {assets.length} devices
            </span>
          </button>

          <button
            onClick={() => onTabChange('governance')}
            className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer ${
              activeTab === 'governance'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-800 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <ShieldCheck className={`w-5 h-5 ${activeTab === 'governance' ? 'text-white' : 'text-blue-600'}`} />
              <span className="font-extrabold">
                {role === 'employee' ? 'Policy Handbook' : role === 'manager' ? 'Team Policies & Matrix' : 'Governance & Audits'}
              </span>
            </div>
          </button>

          {/* Dynamic Custom Features Studio Tab (Admin Only) */}
          {role === 'admin' && (
            <button
              onClick={() => onTabChange('custom')}
              className={`flex items-center justify-between p-3 rounded-xl text-sm font-bold transition-all cursor-pointer mt-1 border border-blue-200 ${
                activeTab === 'custom'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-blue-700 bg-blue-50/80 hover:bg-blue-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <Layers className={`w-5 h-5 ${activeTab === 'custom' ? 'text-white' : 'text-blue-600'}`} />
                <span className="font-extrabold">Feature Studio</span>
              </div>
              <span className="px-2 py-0.5 rounded-full text-xs font-black bg-blue-100 text-blue-800 border border-blue-200">
                {customFeatures.length}
              </span>
            </button>
          )}
        </div>

        {/* Action Buttons: Add Feature & Reset (Admin & Manager) */}
        {role === 'admin' && (
          <div className="flex flex-col gap-2.5 pt-1">
            <button
              onClick={() => onOpenFeatureModal && onOpenFeatureModal('add')}
              className="w-full py-3 px-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-600/25 transition-all hover:scale-[1.02] cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>+ Add Feature / Data</span>
            </button>

            <button
              onClick={() => onOpenFeatureModal && onOpenFeatureModal('reset')}
              className="w-full py-2.5 px-3.5 rounded-xl bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-600 border border-slate-200 text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset Workspace Data</span>
            </button>
          </div>
        )}
      </div>

      {/* Active Collaborators Section */}
      <div className="flex flex-col gap-3 pt-4 border-t border-slate-200">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-black text-slate-600 uppercase flex items-center gap-1.5">
            <Users className="w-4 h-4 text-blue-600" />
            <span>Active Governance Team</span>
          </span>
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping" />
        </div>

        <div className="flex flex-col gap-2">
          {mockCollaborators.map((c, i) => (
            <div key={i} className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-100 transition-colors">
              <div className="flex items-center gap-2.5">
                <div className="relative">
                  <img src={c.avatar} alt={c.name} className="w-8 h-8 rounded-full object-cover border border-slate-300" />
                  <span className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white ${c.status === 'online' ? 'bg-emerald-500' : 'bg-blue-500'}`} />
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-900">{c.name}</span>
                  <span className="text-xs font-semibold text-slate-500">{c.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
