import React from 'react';
import { motion } from 'framer-motion';
import { UserSession } from '@/components/auth/AuthFlow';
import { 
  Activity, 
  FileText, 
  CheckCircle2, 
  ShoppingCart, 
  Box, 
  ShieldCheck, 
  BarChart3, 
  Settings,
  Sparkles,
  Sun,
  Moon,
  LogOut
} from 'lucide-react';

import { Layers } from 'lucide-react';

export type ActiveTab = 'process' | 'invoices' | 'demand' | 'assets' | 'governance' | 'custom';

interface IconRailProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  userSession?: UserSession | null;
  onLogout?: () => void;
}

export const IconRail: React.FC<IconRailProps> = ({
  activeTab,
  onTabChange,
  userSession,
  onLogout,
}) => {
  const role = userSession?.role || 'admin';

  const allNavItems = [
    { id: 'process', label: role === 'admin' ? 'Shadow Process Mining' : 'Process Workflow', icon: Activity, badge: '', roles: ['admin'] },
    { id: 'invoices', label: role === 'employee' ? 'Upload Invoice & GST' : role === 'manager' ? 'Invoice Audits & Approvals' : 'Invoices & GSTIN Ledger', icon: FileText, badge: '', roles: ['admin', 'manager', 'employee'] },
    { id: 'demand', label: role === 'employee' ? 'Raise Purchase Requisition' : role === 'manager' ? 'Department Requisitions' : 'Demand Routing Flow', icon: ShoppingCart, badge: '', roles: ['admin', 'manager', 'employee'] },
    { id: 'assets', label: role === 'employee' ? 'My Assigned Assets' : role === 'manager' ? 'Department Asset Pool' : 'IoT & Asset Recovery', icon: Box, badge: '', roles: ['admin', 'manager', 'employee'] },
    { id: 'governance', label: role === 'employee' ? 'Employee Policy Handbook' : role === 'manager' ? 'Department Compliance' : 'Governance & Audits', icon: ShieldCheck, badge: '', roles: ['admin', 'manager', 'employee'] },
    { id: 'custom', label: 'Custom Feature Studio', icon: Layers, badge: '✨', roles: ['admin'] },
  ];

  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <aside className="w-18 flex-shrink-0 flex flex-col items-center justify-between py-5 glass-panel h-screen z-30 select-none border-r border-slate-200 bg-white/95 backdrop-blur-xl">
      {/* Brand Icon / Logo */}
      <div className="flex flex-col items-center gap-6">
        <motion.div
          whileHover={{ rotate: 180 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          className="w-11 h-11 rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30 cursor-pointer"
        >
          <Sparkles className="w-6 h-6 fill-white" />
        </motion.div>

        {/* Primary Navigation Rail */}
        <nav className="flex flex-col items-center gap-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id as ActiveTab)}
                title={item.label}
                className="relative p-3 rounded-2xl transition-all duration-200 group flex items-center justify-center cursor-pointer"
              >
                {/* Active Pill Spring Animation */}
                {isActive && (
                  <motion.div
                    layoutId="activeRailPill"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                    className="absolute inset-0 bg-blue-600 rounded-2xl shadow-md shadow-blue-500/30"
                  />
                )}

                <Icon
                  className={`w-5 h-5 relative z-10 transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'text-slate-500 group-hover:text-blue-600'
                  }`}
                />

                {/* Notification Badge */}
                {item.badge && (
                  <span
                    className={`absolute -top-1 -right-1 z-20 w-4 h-4 rounded-full text-[10px] font-extrabold flex items-center justify-center ${
                      isActive
                        ? 'bg-sky-300 text-slate-950'
                        : 'bg-blue-500 text-white'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Session & Logout */}
      <div className="flex flex-col items-center gap-3">
        {/* User Avatar with Role Tooltip */}
        <div 
          title={userSession ? `${userSession.name} (${userSession.role.toUpperCase()})` : 'User Profile'}
          className="relative group cursor-pointer"
        >
          <div className="w-9 h-9 rounded-full bg-blue-100 overflow-hidden border-2 border-blue-500 shadow-sm">
            <img
              src={userSession?.avatar || "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"}
              alt="User Avatar"
              className="w-full h-full object-cover"
            />
          </div>
          <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-blue-600 border-2 border-white rounded-full flex items-center justify-center text-[8px] text-white font-black uppercase">
            {userSession?.role ? userSession.role[0].toUpperCase() : 'U'}
          </span>
        </div>

        {/* Logout Action */}
        {onLogout && (
          <button
            onClick={onLogout}
            title="Log Out & Switch Role Portal"
            className="p-2.5 rounded-xl text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        )}
      </div>
    </aside>
  );
};
