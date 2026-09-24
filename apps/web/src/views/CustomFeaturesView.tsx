import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Plus, Trash2, Cpu, CheckCircle2, Activity, Layers, ArrowUpRight } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { pageFadeVariants } from '@/lib/motion-config';

interface CustomFeaturesViewProps {
  onOpenAddModal: () => void;
}

export const CustomFeaturesView: React.FC<CustomFeaturesViewProps> = ({ onOpenAddModal }) => {
  const { customFeatures, removeCustomFeature } = useApp();

  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-8 max-w-7xl mx-auto pb-24"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col">
          <span className="text-sm font-black text-white flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-white" />
            Dynamic Enterprise Modules
          </span>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white mt-1">
            Custom Features & Process Extensions
          </h1>
          <p className="text-sm text-blue-100 mt-1 font-medium">
            Manage custom intelligence features, AI workflows, and telemetry modules created dynamically.
          </p>
        </div>

        <button
          onClick={onOpenAddModal}
          className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-105 active:scale-95 cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add New Feature</span>
        </button>
      </div>

      {/* Empty State when no custom features have been added */}
      {customFeatures.length === 0 && (
        <div className="p-12 rounded-3xl bg-white border border-slate-200 text-center flex flex-col items-center justify-center gap-4 shadow-xl">
          <div className="w-14 h-14 rounded-2xl bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-600">
            <Layers className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">No Custom Features Added Yet</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
              Use the "+ Add New Feature" button to build custom intelligence widgets, metrics, and automation modules.
            </p>
          </div>
          <button
            onClick={onOpenAddModal}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition-all cursor-pointer flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Your First Feature</span>
          </button>
        </div>
      )}

      {/* Grid of Dynamic User Features */}
      {customFeatures.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {customFeatures.map((feat) => (
            <motion.div
              key={feat.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-3xl bg-white border border-slate-200 hover:border-blue-400 transition-all shadow-xl flex flex-col justify-between group relative overflow-hidden"
            >
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800 border border-blue-200 uppercase">
                    {feat.badge}
                  </span>
                  <button
                    onClick={() => removeCustomFeature(feat.id)}
                    title="Delete Feature"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div>
                  <h3 className="text-lg font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {feat.name}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {feat.description}
                  </p>
                </div>

                {/* Metric Display */}
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-500 font-bold uppercase">
                      {feat.metricLabel}
                    </span>
                    <span className="text-xl font-black text-slate-900 mt-0.5">
                      {feat.metric}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-bold text-blue-600">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{feat.status}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>Created {feat.createdAt}</span>
                <span className="text-blue-600 font-bold flex items-center gap-1 group-hover:underline">
                  Telemetry Active <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};
