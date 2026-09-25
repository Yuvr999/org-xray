import React, { useState } from 'react';
import { IconRail, ActiveTab } from './IconRail';
import { ModuleDirectory } from './ModuleDirectory';
import { RightIntelligenceDrawer } from './RightIntelligenceDrawer';
import { FloatingAIToolbar } from '@/components/ui/FloatingAIToolbar';
import { Bot, PanelRightClose, PanelRightOpen, Sparkles } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { UserSession } from '../auth/AuthFlow';

interface AppShellProps {
  children: React.ReactNode;
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  userSession?: UserSession | null;
  onLogout?: () => void;
  onTriggerAIAction?: (action: string) => void;
  onOpenFeatureModal?: (tab?: 'add' | 'reset') => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeTab,
  onTabChange,
  userSession,
  onLogout,
  onTriggerAIAction,
  onOpenFeatureModal,
}) => {
  const [isFloatingToolbarVisible, setIsFloatingToolbarVisible] = useState(true);
  const [isRightDrawerOpen, setIsRightDrawerOpen] = useState(true);

  return (
    <div className="min-h-screen flex bg-ambient-mesh-dark text-slate-900 overflow-hidden">
      {/* Pane 1: Leftmost Icon Rail */}
      <IconRail
        activeTab={activeTab}
        onTabChange={onTabChange}
        userSession={userSession}
        onLogout={onLogout}
      />

      {/* Pane 2: Collapsible Directory Tree */}
      <ModuleDirectory
        activeTab={activeTab}
        onTabChange={onTabChange}
        onOpenFeatureModal={onOpenFeatureModal}
        userSession={userSession}
      />

      {/* Pane 3: Main Canvas Viewport */}
      <main className="flex-1 h-screen overflow-y-auto p-6 relative transition-all duration-300">
        {/* Top-Right Sidebar Re-open Floating Action when drawer is closed */}
        <AnimatePresence>
          {!isRightDrawerOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, x: 20 }}
              animate={{ opacity: 1, scale: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.9, x: 20 }}
              className="fixed top-5 right-6 z-40"
            >
              <button
                onClick={() => setIsRightDrawerOpen(true)}
                title="Open AI Copilot & Audit Drawer"
                className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-500/25 border border-blue-400/30 transition-all hover:scale-105 active:scale-95 cursor-pointer backdrop-blur-md"
              >
                <Sparkles className="w-3.5 h-3.5 fill-current text-sky-200" />
                <span>AI Copilot & Audit</span>
                <PanelRightOpen className="w-4 h-4 ml-0.5 text-blue-200" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {children}
      </main>

      {/* Pane 4: Right Intelligence & Audit Drawer with Closing Animation */}
      <RightIntelligenceDrawer
        isOpen={isRightDrawerOpen}
        onClose={() => setIsRightDrawerOpen(false)}
      />

      {/* Contextual Floating AI Toolbar */}
      <FloatingAIToolbar
        isVisible={isFloatingToolbarVisible}
        onOpenFeatureModal={onOpenFeatureModal}
        onActionClick={(action) => {
          if (action === 'Open AI Assistant') {
            setIsRightDrawerOpen(true);
          }
          if (onTriggerAIAction) onTriggerAIAction(action);
        }}
        onClose={() => setIsFloatingToolbarVisible(false)}
      />
    </div>
  );
};
