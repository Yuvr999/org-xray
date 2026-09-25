import React, { useState } from 'react';
import { AppProvider } from './context/AppContext';
import { AppShell } from './components/layout/AppShell';
import { ActiveTab } from './components/layout/IconRail';
import { AuthFlow, UserSession } from './components/auth/AuthFlow';
import { ProcessMiningView } from './views/ProcessMiningView';
import { InvoiceVerificationView } from './views/InvoiceVerificationView';
import { DemandRoutingView } from './views/DemandRoutingView';
import { AssetRecoveryView } from './views/AssetRecoveryView';
import { GovernanceView } from './views/GovernanceView';
import { CustomFeaturesView } from './views/CustomFeaturesView';
import { FeatureManagerModal } from './components/modals/FeatureManagerModal';
import { AnimatePresence } from 'framer-motion';

function DashboardContent() {
  const [userSession, setUserSession] = useState<UserSession | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('process');
  const [isFeatureModalOpen, setIsFeatureModalOpen] = useState(false);
  const [featureModalTab, setFeatureModalTab] = useState<'add' | 'reset'>('add');

  const handleLoginSuccess = (session: UserSession) => {
    setUserSession(session);
    if (session.role === 'admin') {
      setActiveTab('process');
    } else if (session.role === 'manager') {
      setActiveTab('invoices');
    } else if (session.role === 'employee') {
      setActiveTab('invoices');
    }
  };

  const handleLogout = () => {
    setUserSession(null);
  };

  const openFeatureModal = (tab: 'add' | 'reset' = 'add') => {
    setFeatureModalTab(tab);
    setIsFeatureModalOpen(true);
  };

  // If unauthenticated, show the 2-step Auth Flow (1st page role selection, 2nd page credentials login)
  if (!userSession) {
    return <AuthFlow onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <>
      <AppShell
        activeTab={activeTab}
        onTabChange={setActiveTab}
        userSession={userSession}
        onLogout={handleLogout}
        onOpenFeatureModal={openFeatureModal}
        onTriggerAIAction={(action) => {
          if (action === 'Process Audit' || action === 'Mine Bottlenecks') setActiveTab('process');
          if (action === 'GSTIN Verification' || action === 'Audit Invoices') setActiveTab('invoices');
          if (action === 'Asset Reallocation' || action === 'Match Demands') setActiveTab('demand');
          if (action === 'Telemetry Scan') setActiveTab('assets');
          if (action === 'Compliance Review') setActiveTab('governance');
        }}
      >
        <AnimatePresence mode="wait">
          {activeTab === 'process' && <ProcessMiningView key="process" />}
          {activeTab === 'invoices' && <InvoiceVerificationView key="invoices" userSession={userSession} />}
          {activeTab === 'demand' && <DemandRoutingView key="demand" />}
          {activeTab === 'assets' && <AssetRecoveryView key="assets" />}
          {activeTab === 'governance' && <GovernanceView key="governance" />}
          {activeTab === 'custom' && (
            <CustomFeaturesView
              key="custom"
              onOpenAddModal={() => openFeatureModal('add')}
            />
          )}
        </AnimatePresence>
      </AppShell>

      {/* Feature Builder & Reset State Modal */}
      <FeatureManagerModal
        isOpen={isFeatureModalOpen}
        defaultTab={featureModalTab}
        onClose={() => setIsFeatureModalOpen(false)}
      />
    </>
  );
}

export function App() {
  return (
    <AppProvider>
      <DashboardContent />
    </AppProvider>
  );
}

export default App;
