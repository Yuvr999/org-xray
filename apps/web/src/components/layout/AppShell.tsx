import React, { useState } from 'react';
import { IconRail, ActiveTab } from './IconRail';
import { ModuleDirectory } from './ModuleDirectory';
import { RightIntelligenceDrawer } from './RightIntelligenceDrawer';
import { FloatingAIToolbar } from '@/components/ui/FloatingAIToolbar';
import { mockShadowAlerts } from '@/lib/mockData';

interface AppShellProps {
  children: React.ReactNode;
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  onTriggerAIAction?: (action: string) => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeTab,
  onTabChange,
  isDarkMode,
  onToggleDarkMode,
  onTriggerAIAction,
}) => {
  const [isFloatingToolbarVisible, setIsFloatingToolbarVisible] = useState(true);

  return (
    <div className={`min-h-screen flex ${isDarkMode ? 'dark bg-ambient-mesh-dark text-slate-100' : 'bg-ambient-mesh-light text-slate-800'}`}>
      {/* Pane 1: Leftmost Icon Rail */}
      <IconRail
        activeTab={activeTab}
        onTabChange={onTabChange}
        isDarkMode={isDarkMode}
        onToggleDarkMode={onToggleDarkMode}
      />

      {/* Pane 2: Collapsible Directory Tree */}
      <ModuleDirectory
        activeTab={activeTab}
        onTabChange={onTabChange}
        shadowAlertCount={mockShadowAlerts.length}
      />

      {/* Pane 3: Main Canvas Viewport */}
      <main className="flex-1 h-screen overflow-y-auto p-6 relative">
        {children}
      </main>

      {/* Pane 4: Right Intelligence & Audit Drawer */}
      <RightIntelligenceDrawer
        isOpen={true}
        onClose={() => {}}
      />

      {/* Contextual Floating AI Toolbar */}
      <FloatingAIToolbar
        isVisible={isFloatingToolbarVisible}
        onActionClick={(action) => {
          if (onTriggerAIAction) onTriggerAIAction(action);
        }}
        onClose={() => setIsFloatingToolbarVisible(false)}
      />
    </div>
  );
};
