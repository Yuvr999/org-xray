import React, { useState } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { ActiveTab } from '@/components/layout/IconRail';
import { ProcessMiningView } from '@/views/ProcessMiningView';
import { InvoiceVerificationView } from '@/views/InvoiceVerificationView';
import { DemandRoutingView } from '@/views/DemandRoutingView';
import { AssetRecoveryView } from '@/views/AssetRecoveryView';
import { GovernanceView } from '@/views/GovernanceView';
import { AnimatePresence } from 'framer-motion';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('process');
  const [isDarkMode, setIsDarkMode] = useState(false);

  return (
    <AppShell
      activeTab={activeTab}
      onTabChange={setActiveTab}
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode((prev) => !prev)}
      onTriggerAIAction={(action) => {
        if (action === 'Process Audit') setActiveTab('process');
        if (action === 'GSTIN Verification') setActiveTab('invoices');
        if (action === 'Asset Reallocation') setActiveTab('demand');
      }}
    >
      <AnimatePresence mode="wait">
        {activeTab === 'process' && <ProcessMiningView key="process" />}
        {activeTab === 'invoices' && <InvoiceVerificationView key="invoices" />}
        {activeTab === 'demand' && <DemandRoutingView key="demand" />}
        {activeTab === 'assets' && <AssetRecoveryView key="assets" />}
        {activeTab === 'governance' && <GovernanceView key="governance" />}
      </AnimatePresence>
    </AppShell>
  );
};

export default App;
