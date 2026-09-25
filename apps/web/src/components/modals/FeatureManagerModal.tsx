import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Trash2, 
  RotateCcw, 
  Plus, 
  Sparkles, 
  Layers, 
  FileText, 
  Box, 
  ShoppingCart, 
  ShieldCheck, 
  CheckCircle2, 
  Sliders, 
  Cpu, 
  AlertTriangle 
} from 'lucide-react';
import { useApp, CustomFeature } from '@/context/AppContext';

interface FeatureManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: 'add' | 'reset';
}

export const FeatureManagerModal: React.FC<FeatureManagerModalProps> = ({
  isOpen,
  onClose,
  defaultTab = 'add',
}) => {
  const { 
    clearAllData, 
    resetToDefaults, 
    addCustomFeature, 
    addInvoice, 
    addAsset, 
    addDemand, 
    addGovernancePolicy,
    customFeatures,
    invoices,
    assets,
    demands,
    shadowAlerts 
  } = useApp();

  const [activeTab, setActiveTab] = useState<'add' | 'reset'>(defaultTab);
  const [featureCategory, setFeatureCategory] = useState<'custom' | 'invoice' | 'asset' | 'demand' | 'policy'>('custom');
  
  // Custom Feature Form States
  const [featureName, setFeatureName] = useState('');
  const [featureDesc, setFeatureDesc] = useState('');
  const [featureMetric, setFeatureMetric] = useState('');
  const [featureMetricLabel, setFeatureMetricLabel] = useState('');
  const [featureBadge, setFeatureBadge] = useState('AI Powered');
  const [featureStatus, setFeatureStatus] = useState<'Active' | 'Beta' | 'Automated'>('Active');
  
  // Quick Feedback
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Simple quick invoice form
  const [vendorName, setVendorName] = useState('');
  const [invoiceAmount, setInvoiceAmount] = useState('');
  const [invoiceGstin, setInvoiceGstin] = useState('27AAACA99991Z1');

  // Simple quick asset form
  const [assetName, setAssetName] = useState('');
  const [assetLocation, setAssetLocation] = useState('Building A - Desk 101');
  const [assetUser, setAssetUser] = useState('New Assignee');

  const handleCreateCustomFeature = (e: React.FormEvent) => {
    e.preventDefault();
    if (!featureName.trim()) return;

    const newFeature: CustomFeature = {
      id: `feat-${Date.now()}`,
      name: featureName.trim(),
      category: 'Enterprise Module',
      description: featureDesc.trim() || 'Dynamic custom process intelligence module generated via feature builder.',
      metric: featureMetric.trim() || '100% Operational',
      metricLabel: featureMetricLabel.trim() || 'Telemetry SLA',
      badge: featureBadge.trim() || 'Custom Module',
      iconName: 'Sparkles',
      status: featureStatus,
      createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    addCustomFeature(newFeature);
    setSuccessNotice(`✨ Feature "${featureName}" added successfully to the dashboard!`);
    setFeatureName('');
    setFeatureDesc('');
    setFeatureMetric('');
    setFeatureMetricLabel('');
    setTimeout(() => setSuccessNotice(null), 3000);
  };

  const handleCreateInvoice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!vendorName.trim() || !invoiceAmount) return;

    const parsedAmount = parseFloat(invoiceAmount) || 50000;
    const gstCalc = Math.round(parsedAmount * 0.18);

    addInvoice({
      id: `INV-2026-${Date.now().toString().slice(-4)}`,
      vendorName: vendorName.trim(),
      gstin: invoiceGstin.trim(),
      invoiceNumber: `VND-${Math.floor(10000 + Math.random() * 90000)}`,
      amount: parsedAmount + gstCalc,
      gstAmount: gstCalc,
      isArithmeticValid: true,
      isDuplicate: false,
      date: new Date().toISOString().split('T')[0],
      status: 'Verified',
      items: [
        {
          description: `${vendorName} Enterprise Service Provisioning`,
          qty: 1,
          unitPrice: parsedAmount,
          total: parsedAmount,
        },
        {
          description: 'GST @ 18%',
          qty: 1,
          unitPrice: gstCalc,
          total: gstCalc,
        },
      ],
    });

    setSuccessNotice(`📄 Ingested new invoice from ${vendorName} for ₹${(parsedAmount + gstCalc).toLocaleString()}!`);
    setVendorName('');
    setInvoiceAmount('');
    setTimeout(() => setSuccessNotice(null), 3000);
  };

  const handleCreateAsset = (e: React.FormEvent) => {
    e.preventDefault();
    if (!assetName.trim()) return;

    addAsset({
      id: `AST-${Date.now().toString().slice(-4)}`,
      assetTag: `ORG-HW-${Math.floor(10000 + Math.random() * 90000)}`,
      name: assetName.trim(),
      category: 'Hardware Workstation',
      location: assetLocation.trim(),
      assignedUser: assetUser.trim(),
      status: 'Active',
      telemetry: {
        batteryPct: 98,
        tempCelsius: 28,
        lastPing: 'Just now',
        signalStrength: 'Strong (5G Mesh)',
      },
    });

    setSuccessNotice(`🖥️ Registered IoT Asset "${assetName}" with active telemetry!`);
    setAssetName('');
    setTimeout(() => setSuccessNotice(null), 3000);
  };

  const handleWipeClean = () => {
    clearAllData();
    setSuccessNotice('🧹 Canvas cleared! All datasets and items have been reset to 0.');
    setTimeout(() => setSuccessNotice(null), 3500);
  };

  const handleRestoreDefaults = () => {
    resetToDefaults();
    setSuccessNotice('🔄 Restored default demo data for all modules.');
    setTimeout(() => setSuccessNotice(null), 3500);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-md">
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 15 }}
            transition={{ duration: 0.25 }}
            className="w-full max-w-2xl bg-white border border-slate-200 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
          >
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
                  <Sparkles className="w-5 h-5 fill-white" />
                </div>
                <div>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight">
                    Workspace Controls & Feature Studio
                  </h2>
                  <p className="text-xs font-semibold text-slate-500">
                    Add new custom features, ingest assets & invoices, or reset workspace state.
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="px-6 pt-4 flex gap-2 border-b border-slate-200 bg-slate-50">
              <button
                onClick={() => setActiveTab('add')}
                className={`pb-3 px-4 text-xs font-black transition-all border-b-2 flex items-center gap-2 cursor-pointer ${
                  activeTab === 'add'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Plus className="w-4 h-4" />
                <span>+ Add New Feature / Data</span>
              </button>

              <button
                onClick={() => setActiveTab('reset')}
                className={`pb-3 px-4 text-xs font-black transition-all border-b-2 flex items-center gap-2 cursor-pointer ${
                  activeTab === 'reset'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset & Wipe Data</span>
              </button>
            </div>

            {/* Notification Banner */}
            {successNotice && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="px-6 py-2.5 bg-blue-50 border-b border-blue-200 text-blue-900 text-xs font-bold flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>{successNotice}</span>
              </motion.div>
            )}

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-6">
              {/* ======================================================= */}
              {/* TAB 1: ADD NEW FEATURE OR DATA */}
              {/* ======================================================= */}
              {activeTab === 'add' && (
                <div className="flex flex-col gap-5">
                  {/* Category Selector */}
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setFeatureCategory('custom')}
                      className={`p-3 rounded-xl border text-xs font-bold transition-all flex flex-col items-center gap-1.5 cursor-pointer ${
                        featureCategory === 'custom'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-600/30'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>Custom Feature</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setFeatureCategory('invoice')}
                      className={`p-3 rounded-xl border text-xs font-bold transition-all flex flex-col items-center gap-1.5 cursor-pointer ${
                        featureCategory === 'invoice'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-600/30'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <FileText className="w-4 h-4" />
                      <span>New Invoice</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setFeatureCategory('asset')}
                      className={`p-3 rounded-xl border text-xs font-bold transition-all flex flex-col items-center gap-1.5 cursor-pointer ${
                        featureCategory === 'asset'
                          ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-600/30'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <Box className="w-4 h-4" />
                      <span>New IoT Asset</span>
                    </button>
                  </div>

                  {/* FORM 1: CUSTOM FEATURE BUILDER */}
                  {featureCategory === 'custom' && (
                    <form onSubmit={handleCreateCustomFeature} className="flex flex-col gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                          Feature Name
                        </label>
                        <input
                          type="text"
                          required
                          value={featureName}
                          onChange={(e) => setFeatureName(e.target.value)}
                          placeholder="e.g., Cloud Carbon AI Audit, Slack Expense Gateway..."
                          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Key Metric Value
                          </label>
                          <input
                            type="text"
                            value={featureMetric}
                            onChange={(e) => setFeatureMetric(e.target.value)}
                            placeholder="e.g., $18,400 Saved / 99.4%"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                          />
                        </div>

                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Metric Label
                          </label>
                          <input
                            type="text"
                            value={featureMetricLabel}
                            onChange={(e) => setFeatureMetricLabel(e.target.value)}
                            placeholder="e.g., Quarterly Efficiency"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                          />
                        </div>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                          Description & Capabilities
                        </label>
                        <textarea
                          rows={2}
                          value={featureDesc}
                          onChange={(e) => setFeatureDesc(e.target.value)}
                          placeholder="Explain what this new intelligence feature automates..."
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                        />
                      </div>

                      <button
                        type="submit"
                        className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center justify-center gap-2"
                      >
                        <Sparkles className="w-4 h-4 fill-white" />
                        <span>Add Feature to Dashboard</span>
                      </button>
                    </form>
                  )}

                  {/* FORM 2: NEW INVOICE */}
                  {featureCategory === 'invoice' && (
                    <form onSubmit={handleCreateInvoice} className="flex flex-col gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                          Vendor Name
                        </label>
                        <input
                          type="text"
                          required
                          value={vendorName}
                          onChange={(e) => setVendorName(e.target.value)}
                          placeholder="e.g., Salesforce Cloud Technologies India Pvt Ltd"
                          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Base Amount (₹)
                          </label>
                          <input
                            type="number"
                            required
                            value={invoiceAmount}
                            onChange={(e) => setInvoiceAmount(e.target.value)}
                            placeholder="e.g., 75000"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                          />
                        </div>

                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Vendor GSTIN
                          </label>
                          <input
                            type="text"
                            value={invoiceGstin}
                            onChange={(e) => setInvoiceGstin(e.target.value)}
                            placeholder="27AAACA12341Z5"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500 uppercase"
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center justify-center gap-2"
                      >
                        <FileText className="w-4 h-4" />
                        <span>Ingest Vendor Invoice</span>
                      </button>
                    </form>
                  )}

                  {/* FORM 3: NEW IOT ASSET */}
                  {featureCategory === 'asset' && (
                    <form onSubmit={handleCreateAsset} className="flex flex-col gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                          Hardware Name / Model
                        </label>
                        <input
                          type="text"
                          required
                          value={assetName}
                          onChange={(e) => setAssetName(e.target.value)}
                          placeholder="e.g., Apple Mac Studio M2 Ultra (128GB)"
                          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Location / Depot
                          </label>
                          <input
                            type="text"
                            value={assetLocation}
                            onChange={(e) => setAssetLocation(e.target.value)}
                            placeholder="Building B - Server Room"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                          />
                        </div>

                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                            Assignee / User
                          </label>
                          <input
                            type="text"
                            value={assetUser}
                            onChange={(e) => setAssetUser(e.target.value)}
                            placeholder="Alex Morgan"
                            className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center justify-center gap-2"
                      >
                        <Box className="w-4 h-4" />
                        <span>Register IoT Hardware Asset</span>
                      </button>
                    </form>
                  )}
                </div>
              )}

              {/* ======================================================= */}
              {/* TAB 2: RESET & CLEAN SLATE CONTROLS */}
              {/* ======================================================= */}
              {activeTab === 'reset' && (
                <div className="flex flex-col gap-5">
                  <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 flex items-start gap-3.5">
                    <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-black text-slate-900">Resetting Workspace State</h4>
                      <p className="text-xs text-slate-600 font-medium mt-1 leading-relaxed">
                        You can wipe the entire canvas to 0 items to start completely clean, or restore the default demo datasets anytime.
                      </p>
                    </div>
                  </div>

                  {/* Summary of Active Records */}
                  <div className="grid grid-cols-4 gap-2 text-center">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="block text-lg font-black text-slate-900">{invoices.length}</span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Invoices</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="block text-lg font-black text-slate-900">{assets.length}</span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Assets</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="block text-lg font-black text-slate-900">{demands.length}</span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Demands</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="block text-lg font-black text-slate-900">{customFeatures.length}</span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Custom</span>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 pt-2">
                    {/* Wipe Clean Action */}
                    <button
                      type="button"
                      onClick={handleWipeClean}
                      className="flex-1 py-3.5 px-4 rounded-2xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4 text-rose-600" />
                      <span>Remove Everything (Blank Slate)</span>
                    </button>

                    {/* Restore Defaults Action */}
                    <button
                      type="button"
                      onClick={handleRestoreDefaults}
                      className="flex-1 py-3.5 px-4 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <RotateCcw className="w-4 h-4" />
                      <span>Restore Demo Defaults</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
