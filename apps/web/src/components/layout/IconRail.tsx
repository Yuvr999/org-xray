import React from 'react';
import { motion } from 'framer-motion';
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
  Moon
} from 'lucide-react';

export type ActiveTab = 'process' | 'invoices' | 'demand' | 'assets' | 'governance';

interface IconRailProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export const IconRail: React.FC<IconRailProps> = ({
  activeTab,
  onTabChange,
  isDarkMode,
  onToggleDarkMode,
}) => {
  const navItems = [
    { id: 'process', label: 'Shadow Intelligence', icon: Activity, badge: '4' },
    { id: 'invoices', label: 'Invoices & GSTIN', icon: FileText, badge: '1' },
    { id: 'demand', label: 'Demand Routing', icon: ShoppingCart, badge: '' },
    { id: 'assets', label: 'IoT & Asset Recovery', icon: Box, badge: '' },
    { id: 'governance', label: 'Governance & Audits', icon: ShieldCheck, badge: '' },
  ];

  return (
    <aside className="w-18 flex-shrink-0 flex flex-col items-center justify-between py-5 glass-panel h-screen z-30 select-none">
      {/* Brand Icon / Logo */}
      <div className="flex flex-col items-center gap-6">
        <motion.div
          whileHover={{ rotate: 180 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          className="w-11 h-11 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 cursor-pointer"
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
                className="relative p-3 rounded-2xl transition-all duration-200 group flex items-center justify-center"
              >
                {/* Active Pill Spring Animation */}
                {isActive && (
                  <motion.div
                    layoutId="activeRailPill"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                    className="absolute inset-0 bg-indigo-600 rounded-2xl shadow-md shadow-indigo-500/25"
                  />
                )}

                <Icon
                  className={`w-5 h-5 relative z-10 transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'
                  }`}
                />

                {/* Notification Badge */}
                {item.badge && (
                  <span
                    className={`absolute -top-1 -right-1 z-20 w-4 h-4 rounded-full text-[10px] font-extrabold flex items-center justify-center ${
                      isActive
                        ? 'bg-amber-400 text-slate-950'
                        : 'bg-rose-500 text-white'
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

      {/* Theme Switcher & System Settings */}
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={onToggleDarkMode}
          title={isDarkMode ? 'Switch to Light Pastel' : 'Switch to Dark Glass'}
          className="p-3 rounded-2xl text-slate-500 hover:text-indigo-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-indigo-600" />}
        </button>

        <div className="w-9 h-9 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden border-2 border-white dark:border-slate-800 shadow-sm">
          <img
            src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"
            alt="User Avatar"
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </aside>
  );
};
