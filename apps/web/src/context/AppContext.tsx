import React, { createContext, useContext, useState } from 'react';
import { 
  InvoiceItem, 
  DemandItem, 
  PhysicalAsset, 
  ShadowAlert, 
  mockInvoices, 
  mockDemands, 
  mockAssets, 
  mockShadowAlerts 
} from '@/lib/mockData';

export interface CustomFeature {
  id: string;
  name: string;
  category: string;
  description: string;
  metric: string;
  metricLabel: string;
  badge: string;
  iconName: string;
  status: 'Active' | 'Beta' | 'Automated';
  createdAt: string;
}

export interface GovernancePolicyItem {
  id: string;
  title: string;
  subtitle: string;
  badge: string;
  limit: string;
  avgTurnaround: string;
  description: string;
  tags: string[];
  rules: string[];
  authorizer: string;
  auditFrequency: string;
}

export const DEFAULT_GOVERNANCE_POLICIES: GovernancePolicyItem[] = [
  {
    id: 'manager',
    title: 'Manager Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 1 Approval',
    limit: 'Up to $5,000',
    avgTurnaround: '1.2 hours',
    description:
      'Requires direct department manager approval. AI rule engine performs instant compliance check, budget reservation, and automated duplicate prevention.',
    tags: ['LOGISTICS', 'OPEX BUDGET', 'INSTANT AI', 'TIER 1'],
    rules: [
      'Line-manager electronic signature verification',
      'Automated check against remaining quarterly departmental budget',
      'Zero shadow IT anomaly match required prior to release',
    ],
    authorizer: 'Direct Department Lead / Engineering Manager',
    auditFrequency: 'Continuous Real-time AI Stream',
  },
  {
    id: 'finance',
    title: 'Finance & Tax Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 2 Approval',
    limit: '$5,000 – $25,000',
    avgTurnaround: '4.5 hours',
    description:
      'Requires Finance Director sign-off + GSTIN verification audit before budget commitment. Cross-verifies vendor tax ledgers and 18% statutory IGST/CGST rates.',
    tags: ['TAX AUDIT', '18% GSTIN', 'FINANCE DIR', 'TIER 2'],
    rules: [
      'Automated GSTIN format and checksum algorithmic validation',
      'PO creation and 3-way match against vendor invoice pro-forma',
      'Secondary audit trail logged to immutable event store',
    ],
    authorizer: 'Finance Director / Corporate Controller',
    auditFrequency: 'Daily Ledger Reconciliation',
  },
  {
    id: 'executive',
    title: 'Executive & Procurement Board',
    subtitle: 'Sign-off',
    badge: 'Tier 3 Approval',
    limit: '$25,000+',
    avgTurnaround: '24 hours',
    description:
      'Full governance review with vendor MSA negotiation check, shadow risk assessment, multi-year commitment terms, and physical asset reallocation sweep.',
    tags: ['BOARD REVIEW', 'MSA CONTRACT', 'CAPEX', 'TIER 3'],
    rules: [
      'Master Services Agreement (MSA) legal and security sign-off',
      'Mandatory dormant asset telemetry sweep before new purchase order',
      'C-Suite / Procurement Committee unanimous sign-off',
    ],
    authorizer: 'Chief Financial Officer & VP of Procurement',
    auditFrequency: 'Bi-weekly Executive Governance Committee',
  },
  {
    id: 'legal',
    title: 'Legal & Security Sign-off',
    subtitle: 'Sign-off',
    badge: 'Tier 4 Governance',
    limit: 'Enterprise & SaaS',
    avgTurnaround: '48 hours',
    description:
      'Enterprise SLA review, SOC2 Type II compliance audit, data security protocols, cross-border IP governance, and mutual NDA verification.',
    tags: ['COMPLIANCE', 'SOC2 / GDPR', 'LEGAL COUNSEL', 'TIER 4'],
    rules: [
      'Data Privacy Addendum (DPA) and GDPR/HIPAA compliance validation',
      'Third-party cloud vendor vulnerability and penetration test review',
      'General Counsel approval for custom contract liability limits',
    ],
    authorizer: 'General Counsel & Chief Information Security Officer',
    auditFrequency: 'Quarterly Risk Review',
  },
];

interface AppContextType {
  invoices: InvoiceItem[];
  demands: DemandItem[];
  assets: PhysicalAsset[];
  shadowAlerts: ShadowAlert[];
  governancePolicies: GovernancePolicyItem[];
  customFeatures: CustomFeature[];
  
  // Actions
  clearAllData: () => void;
  resetToDefaults: () => void;
  addInvoice: (invoice: InvoiceItem) => void;
  addDemand: (demand: DemandItem) => void;
  addAsset: (asset: PhysicalAsset) => void;
  addShadowAlert: (alert: ShadowAlert) => void;
  addGovernancePolicy: (policy: GovernancePolicyItem) => void;
  addCustomFeature: (feature: CustomFeature) => void;
  removeCustomFeature: (id: string) => void;
  deleteInvoice: (id: string) => void;
  deleteAsset: (id: string) => void;
  deleteDemand: (id: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [invoices, setInvoices] = useState<InvoiceItem[]>(mockInvoices);
  const [demands, setDemands] = useState<DemandItem[]>(mockDemands);
  const [assets, setAssets] = useState<PhysicalAsset[]>(mockAssets);
  const [shadowAlerts, setShadowAlerts] = useState<ShadowAlert[]>(mockShadowAlerts);
  const [governancePolicies, setGovernancePolicies] = useState<GovernancePolicyItem[]>(DEFAULT_GOVERNANCE_POLICIES);
  const [customFeatures, setCustomFeatures] = useState<CustomFeature[]>([]);

  // Clear everything to a clean blank state
  const clearAllData = () => {
    setInvoices([]);
    setDemands([]);
    setAssets([]);
    setShadowAlerts([]);
    setGovernancePolicies([]);
    setCustomFeatures([]);
  };

  // Restore demo defaults
  const resetToDefaults = () => {
    setInvoices(mockInvoices);
    setDemands(mockDemands);
    setAssets(mockAssets);
    setShadowAlerts(mockShadowAlerts);
    setGovernancePolicies(DEFAULT_GOVERNANCE_POLICIES);
    setCustomFeatures([]);
  };

  const addInvoice = (invoice: InvoiceItem) => {
    setInvoices((prev) => [invoice, ...prev]);
  };

  const addDemand = (demand: DemandItem) => {
    setDemands((prev) => [demand, ...prev]);
  };

  const addAsset = (asset: PhysicalAsset) => {
    setAssets((prev) => [asset, ...prev]);
  };

  const addShadowAlert = (alert: ShadowAlert) => {
    setShadowAlerts((prev) => [alert, ...prev]);
  };

  const addGovernancePolicy = (policy: GovernancePolicyItem) => {
    setGovernancePolicies((prev) => [...prev, policy]);
  };

  const addCustomFeature = (feature: CustomFeature) => {
    setCustomFeatures((prev) => [feature, ...prev]);
  };

  const removeCustomFeature = (id: string) => {
    setCustomFeatures((prev) => prev.filter((f) => f.id !== id));
  };

  const deleteInvoice = (id: string) => {
    setInvoices((prev) => prev.filter((inv) => inv.id !== id));
  };

  const deleteAsset = (id: string) => {
    setAssets((prev) => prev.filter((a) => a.id !== id));
  };

  const deleteDemand = (id: string) => {
    setDemands((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <AppContext.Provider
      value={{
        invoices,
        demands,
        assets,
        shadowAlerts,
        governancePolicies,
        customFeatures,
        clearAllData,
        resetToDefaults,
        addInvoice,
        addDemand,
        addAsset,
        addShadowAlert,
        addGovernancePolicy,
        addCustomFeature,
        removeCustomFeature,
        deleteInvoice,
        deleteAsset,
        deleteDemand,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
