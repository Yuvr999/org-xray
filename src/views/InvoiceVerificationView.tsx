import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { mockInvoices, InvoiceItem } from '@/lib/mockData';
import { FileUp, CheckCircle, AlertTriangle, Copy, FileText, Check, ShieldCheck } from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

export const InvoiceVerificationView: React.FC = () => {
  const [selectedInvoice, setSelectedInvoice] = useState<InvoiceItem>(mockInvoices[0]);

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
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
            GSTIN & Tax Compliance Engine
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white mt-1">
            Smart Invoice Verification & GST Checksum
          </h1>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md shadow-indigo-500/20 transition-all">
          <FileUp className="w-4 h-4" />
          <span>Upload Vendor PDF Invoice</span>
        </button>
      </div>

      {/* Drag & Drop Glass Dropzone Card */}
      <SoftCard className="border-2 border-dashed border-indigo-300 dark:border-indigo-800 bg-indigo-50/30 dark:bg-indigo-950/20 flex flex-col items-center justify-center py-8 cursor-pointer hover:border-indigo-500 transition-colors">
        <div className="w-12 h-12 rounded-2xl bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-3">
          <FileUp className="w-6 h-6" />
        </div>
        <p className="text-sm font-bold text-slate-800 dark:text-slate-100">
          Drop vendor PDF invoice here or click to browse
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Automated 18% GST arithmetic verification + Duplicate hash check enabled
        </p>
      </SoftCard>

      {/* Main Dual-Pane Invoice Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Invoice List (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Ingested Vendor Invoices ({mockInvoices.length})
          </span>

          <motion.div variants={listContainerVariants} initial="hidden" animate="show" className="flex flex-col gap-3">
            {mockInvoices.map((inv) => {
              const isSelected = selectedInvoice.id === inv.id;

              return (
                <motion.div key={inv.id} variants={listItemVariants}>
                  <SoftCard
                    onClick={() => setSelectedInvoice(inv)}
                    className={`cursor-pointer transition-all ${
                      isSelected
                        ? 'border-2 border-indigo-500 bg-white/95 dark:bg-slate-800/95 shadow-lg'
                        : 'hover:border-indigo-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 font-mono">
                        {inv.invoiceNumber}
                      </span>
                      {inv.isDuplicate ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-100 text-rose-700 flex items-center gap-1">
                          <Copy className="w-3 h-3" /> Duplicate Alert
                        </span>
                      ) : !inv.isArithmeticValid ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-700 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" /> Invalid Math
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-700 flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> 18% GST Verified
                        </span>
                      )}
                    </div>

                    <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                      {inv.vendorName}
                    </h4>

                    <div className="flex items-center justify-between mt-3 text-xs">
                      <span className="text-slate-400">{inv.date}</span>
                      <span className="font-extrabold text-slate-900 dark:text-white">
                        ₹{inv.amount.toLocaleString()}
                      </span>
                    </div>
                  </SoftCard>
                </motion.div>
              );
            })}
          </motion.div>
        </div>

        {/* Right Side: Detailed Verification Breakdown (7 cols) */}
        <div className="lg:col-span-7">
          <SoftCard className="flex flex-col gap-6">
            <div className="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-800 pb-4">
              <div className="flex flex-col">
                <span className="text-xs text-slate-400">Invoice Inspection View</span>
                <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">
                  {selectedInvoice.vendorName}
                </h3>
              </div>
              <span className="text-xl font-extrabold text-indigo-600 dark:text-indigo-400">
                ₹{selectedInvoice.amount.toLocaleString()}
              </span>
            </div>

            {/* Compliance Status Banners */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* GST Arithmetic Status Card */}
              <div
                className={`p-4 rounded-2xl border flex flex-col gap-1 ${
                  selectedInvoice.isArithmeticValid
                    ? 'bg-emerald-50/50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-900 dark:text-emerald-200'
                    : 'bg-amber-50/50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-200'
                }`}
              >
                <div className="flex items-center gap-2 font-bold text-xs">
                  {selectedInvoice.isArithmeticValid ? (
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                  )}
                  <span>18% GST Arithmetic Check</span>
                </div>
                <p className="text-xs opacity-80 mt-1">
                  {selectedInvoice.isArithmeticValid
                    ? 'Tax calculation matches exact 18% statutory formula.'
                    : 'Tax mismatch detected! 18% of base does not equal claimed GST.'}
                </p>
              </div>

              {/* GSTIN Checksum Card */}
              <div className="p-4 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900 text-indigo-900 dark:text-indigo-200 flex flex-col gap-1">
                <div className="flex items-center gap-2 font-bold text-xs">
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <span>GSTIN Format & Checksum</span>
                </div>
                <p className="text-xs opacity-80 font-mono mt-1">
                  {selectedInvoice.gstin} (Valid Active Vendor)
                </p>
              </div>
            </div>

            {/* Extracted Line Items */}
            <div className="flex flex-col gap-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Extracted PDF Line Items
              </span>
              <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800 overflow-hidden">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100/60 dark:bg-slate-800/60 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200/60 dark:border-slate-800">
                    <tr>
                      <th className="p-3">Description</th>
                      <th className="p-3">Qty</th>
                      <th className="p-3">Unit Price</th>
                      <th className="p-3 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200/50 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                    {selectedInvoice.items.map((item, i) => (
                      <tr key={i}>
                        <td className="p-3 font-medium">{item.description}</td>
                        <td className="p-3">{item.qty}</td>
                        <td className="p-3">₹{item.unitPrice.toLocaleString()}</td>
                        <td className="p-3 text-right font-bold">₹{item.total.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-xs hover:bg-slate-200 transition-colors">
                Reject Invoice
              </button>
              <button className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-500/20 transition-all">
                Approve Tax Sign-off
              </button>
            </div>
          </SoftCard>
        </div>
      </div>
    </motion.div>
  );
};
