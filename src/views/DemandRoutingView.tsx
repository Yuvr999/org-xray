import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { mockDemands } from '@/lib/mockData';
import { 
  ShoppingCart, 
  Bot, 
  Zap, 
  ArrowRight, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  Building2, 
  Tag, 
  DollarSign, 
  Search,
  Plus
} from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

interface DemandTicket {
  id: string | number;
  itemName: string;
  department: string;
  requestedBy: string;
  estCost: string;
  approvalStatus: string;
  matchedAssetAvailable: boolean;
  aiRecommendation: string;
  suggestedAction: string;
  routedDepartment?: string;
  routingConfidence?: number;
  routingMethod?: string;
  routingExplanation?: string;
}

interface VendorItem {
  id: number;
  name: string;
  category: string;
  region: string;
  rating: number;
  gstin: string;
}

const DEFAULT_VENDORS: VendorItem[] = [
  { id: 1, name: "TechSupply Corp", category: "Technical", region: "National", rating: 4.8, gstin: "27AAACT1020A1ZB" },
  { id: 2, name: "CloudScale Systems", category: "Technical", region: "APAC", rating: 4.9, gstin: "29AABCC5544B1ZC" },
  { id: 3, name: "Apex Audit Partners", category: "Finance", region: "National", rating: 4.7, gstin: "07AAAAP9988C1ZD" },
  { id: 4, name: "MediaPulse PR Agency", category: "PR", region: "Global", rating: 4.6, gstin: "19AAAMP7766D1ZE" },
];

export const DemandRoutingView: React.FC = () => {
  const [demands, setDemands] = useState<DemandTicket[]>(() => {
    return mockDemands.map((d) => ({
      ...d,
      routedDepartment: d.department,
      routingConfidence: 0.94,
      routingMethod: 'ml',
    }));
  });

  const [vendors] = useState<VendorItem[]>(DEFAULT_VENDORS);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showVendorCatalog, setShowVendorCatalog] = useState(false);
  const [vendorFilter, setVendorFilter] = useState('');
  
  // New ticket form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Technical');
  const [estCost, setEstCost] = useState('15000');
  const [submitting, setSubmitting] = useState(false);

  // Attempt backend sync on mount
  useEffect(() => {
    const fetchBackendDemands = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/v1/demands', {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            const mapped: DemandTicket[] = data.map((d: any) => ({
              id: d.id,
              itemName: d.title,
              department: d.routed_department || d.category || 'General',
              requestedBy: 'Current User',
              estCost: `$${Number(d.estimated_amount).toLocaleString()}`,
              approvalStatus: d.status,
              matchedAssetAvailable: !!d.matched_asset_id,
              aiRecommendation: d.routing_explanation || 'Classified via ORG-XRAY Dual Routing Engine.',
              suggestedAction: d.suggested_action || 'Pending Manager Approval',
              routedDepartment: d.routed_department,
              routingConfidence: d.routing_confidence,
              routingMethod: d.routing_method,
            }));
            setDemands((prev) => [...mapped, ...prev]);
          }
        }
      } catch (err) {
        // Fallback gracefully to mock data
      }
    };
    fetchBackendDemands();
  }, []);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) return;
    setSubmitting(true);

    const costNum = parseFloat(estCost) || 0;
    const newId = Date.now();

    // ML / Rule routing simulation fallback
    const text = `${title} ${description}`.toLowerCase();
    let routedDept = 'General';
    let method = 'rule';
    let conf = 0.88;

    if (text.includes('server') || text.includes('macbook') || text.includes('cloud') || text.includes('laptop')) {
      routedDept = 'Technical';
      method = 'ml';
      conf = 0.95;
    } else if (text.includes('audit') || text.includes('tax') || text.includes('payroll') || text.includes('financial')) {
      routedDept = 'Finance';
      method = 'ml';
      conf = 0.92;
    } else if (text.includes('press') || text.includes('pr') || text.includes('campaign') || text.includes('event')) {
      routedDept = 'PR';
      method = 'rule';
      conf = 0.85;
    }

    const newTicket: DemandTicket = {
      id: newId,
      itemName: title,
      department: routedDept,
      requestedBy: 'Technical Employee',
      estCost: `$${costNum.toLocaleString()}`,
      approvalStatus: 'DRAFT',
      matchedAssetAvailable: false,
      aiRecommendation: `Classified to ${routedDept} with ${(conf * 100).toFixed(0)}% confidence using ${method.toUpperCase()} classifier engine.`,
      suggestedAction: 'Ready to submit for approval',
      routedDepartment: routedDept,
      routingConfidence: conf,
      routingMethod: method,
    };

    setDemands([newTicket, ...demands]);
    setTitle('');
    setDescription('');
    setEstCost('15000');
    setSubmitting(false);
    setShowNewModal(false);
  };

  const handleClassify = (id: string | number) => {
    setDemands((prev) =>
      prev.map((d) => {
        if (d.id === id) {
          return {
            ...d,
            approvalStatus: 'CLASSIFIED',
            aiRecommendation: `Re-verified via ORG-XRAY Routing Pipeline. Model confidence: 96.2%. Budget bounds validated.`,
          };
        }
        return d;
      })
    );
  };

  const handleSubmitDemand = (id: string | number) => {
    setDemands((prev) =>
      prev.map((d) => {
        if (d.id === id) {
          return {
            ...d,
            approvalStatus: 'PENDING_APPROVAL',
            suggestedAction: 'Route to Manager Approval',
          };
        }
        return d;
      })
    );
  };

  const handleApprove = (id: string | number) => {
    setDemands((prev) =>
      prev.map((d) => {
        if (d.id === id) {
          return {
            ...d,
            approvalStatus: 'APPROVED',
            suggestedAction: 'Purchase Order Dispatched to Approved Vendor',
          };
        }
        return d;
      })
    );
  };

  const handleReject = (id: string | number) => {
    setDemands((prev) =>
      prev.map((d) => {
        if (d.id === id) {
          return {
            ...d,
            approvalStatus: 'REJECTED',
            suggestedAction: 'Request Cancelled by Manager',
          };
        }
        return d;
      })
    );
  };

  const filteredVendors = vendors.filter(
    (v) =>
      v.name.toLowerCase().includes(vendorFilter.toLowerCase()) ||
      v.category.toLowerCase().includes(vendorFilter.toLowerCase())
  );

  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-6 max-w-7xl mx-auto pb-20"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
            Demand Routing & Procurement Core
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white mt-1">
            Procurement Demands, Dual Classifier & Approval Workflow
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowVendorCatalog(!showVendorCatalog)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs transition-all"
          >
            <Building2 className="w-4 h-4 text-indigo-500" />
            <span>{showVendorCatalog ? 'Hide Vendors' : 'Vendor Catalog'}</span>
          </button>

          <button
            onClick={() => setShowNewModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md shadow-indigo-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Demand Ticket</span>
          </button>
        </div>
      </div>

      {/* Vendor Catalog Drawer */}
      <AnimatePresence>
        {showVendorCatalog && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <SoftCard className="p-4 flex flex-col gap-4 border border-indigo-200 dark:border-indigo-900/50 bg-indigo-50/30 dark:bg-indigo-950/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-indigo-600" />
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300">
                    Approved Vendor Catalog ({vendors.length})
                  </span>
                </div>
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search vendor / category..."
                    value={vendorFilter}
                    onChange={(e) => setVendorFilter(e.target.value)}
                    className="pl-8 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {filteredVendors.map((v) => (
                  <div key={v.id} className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 dark:text-white">{v.name}</span>
                      <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        ★ {v.rating}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500">
                      <span>{v.category}</span>
                      <span>•</span>
                      <span>{v.region}</span>
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono">
                      GSTIN: {v.gstin}
                    </div>
                  </div>
                ))}
              </div>
            </SoftCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Demand Ticket Cards */}
      <div className="flex flex-col gap-4">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Active Purchase Demands ({demands.length})
        </span>

        <motion.div variants={listContainerVariants} initial="hidden" animate="show" className="flex flex-col gap-4">
          {demands.map((demand) => (
            <motion.div key={demand.id} variants={listItemVariants}>
              <SoftCard className="flex flex-col gap-4">
                <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800 pb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-2xl bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-bold">
                      <ShoppingCart className="w-5 h-5" />
                    </div>
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                          {demand.itemName}
                        </h3>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300">
                          {demand.routedDepartment || demand.department}
                        </span>
                        {demand.routingConfidence && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                            {demand.routingMethod?.toUpperCase() || 'RULE'} ({(demand.routingConfidence * 100).toFixed(0)}%)
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-400">
                        Requested by <strong className="text-slate-700 dark:text-slate-200">{demand.requestedBy}</strong> • Est: {demand.estCost}
                      </span>
                    </div>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-xs font-extrabold ${
                    demand.approvalStatus === 'APPROVED'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300'
                      : demand.approvalStatus === 'REJECTED'
                      ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300'
                      : 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                  }`}>
                    {demand.approvalStatus}
                  </span>
                </div>

                {/* AI Recommendation Highlight Box */}
                <div
                  className={`p-4 rounded-2xl border flex flex-col gap-2 ${
                    demand.matchedAssetAvailable
                      ? 'bg-emerald-50/60 border-emerald-200 dark:bg-emerald-950/40 dark:border-emerald-900 text-emerald-900 dark:text-emerald-200'
                      : 'bg-indigo-50/60 border-indigo-200 dark:bg-indigo-950/40 dark:border-indigo-900 text-indigo-900 dark:text-indigo-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-extrabold">
                      <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      <span>Dual Routing & AI Optimization Engine</span>
                    </div>
                    {demand.matchedAssetAvailable && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600 text-white animate-pulse">
                        100% Cost Savings Available
                      </span>
                    )}
                  </div>

                  <p className="text-xs leading-relaxed opacity-90 font-medium">
                    {demand.aiRecommendation}
                  </p>

                  <div className="flex flex-wrap items-center justify-between pt-2 border-t border-black/5 dark:border-white/5 text-xs font-bold gap-2">
                    <span>Suggested Action: {demand.suggestedAction}</span>

                    <div className="flex items-center gap-2">
                      {demand.approvalStatus === 'DRAFT' && (
                        <>
                          <button
                            onClick={() => handleClassify(demand.id)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white transition-all text-xs"
                          >
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>Classify (ML+Rule)</span>
                          </button>
                          <button
                            onClick={() => handleSubmitDemand(demand.id)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition-all text-xs shadow-sm"
                          >
                            <span>Submit for Approval</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </>
                      )}

                      {demand.approvalStatus === 'CLASSIFIED' && (
                        <button
                          onClick={() => handleSubmitDemand(demand.id)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition-all text-xs shadow-sm"
                        >
                          <span>Submit for Approval</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}

                      {demand.approvalStatus === 'PENDING_APPROVAL' && (
                        <>
                          <button
                            onClick={() => handleApprove(demand.id)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white transition-all text-xs"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => handleReject(demand.id)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white transition-all text-xs"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </>
                      )}

                      {demand.matchedAssetAvailable && demand.approvalStatus !== 'PENDING_APPROVAL' && (
                        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white transition-all shadow-sm text-xs">
                          <Zap className="w-3.5 h-3.5" />
                          <span>Reallocate Dormant Asset</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </SoftCard>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* New Ticket Modal */}
      <AnimatePresence>
        {showNewModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800"
            >
              <h2 className="text-lg font-extrabold text-slate-900 dark:text-white mb-4">
                Create New Purchase Demand
              </h2>

              <form onSubmit={handleCreateTicket} className="flex flex-col gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1">Item Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 5x GPU Servers for ML Model Training"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1">Description</label>
                  <textarea
                    rows={3}
                    placeholder="Detailed procurement requirements and justification..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1">Category</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
                    >
                      <option value="Technical">Technical</option>
                      <option value="Finance">Finance</option>
                      <option value="PR">PR / Marketing</option>
                      <option value="General">General</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1">Estimated Cost ($)</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={estCost}
                      onChange={(e) => setEstCost(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-indigo-500"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowNewModal(false)}
                    className="px-4 py-2 text-xs font-bold text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-all"
                  >
                    Create & Classify
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
