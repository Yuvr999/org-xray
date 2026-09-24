import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Bot, FileCheck, ShieldAlert, Zap, X, Plus, RotateCcw } from 'lucide-react';
import { floatingToolbarVariants } from '@/lib/motion-config';

interface FloatingAIToolbarProps {
  isVisible: boolean;
  selectedText?: string;
  onActionClick: (action: string) => void;
  onClose: () => void;
  onOpenFeatureModal?: (tab?: 'add' | 'reset') => void;
}

export const FloatingAIToolbar: React.FC<FloatingAIToolbarProps> = ({
  isVisible,
  selectedText,
  onActionClick,
  onClose,
  onOpenFeatureModal,
}) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          variants={floatingToolbarVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 glass-floating-bar rounded-2xl p-2 px-3 flex items-center gap-2 shadow-2xl border border-slate-200 bg-white/95 backdrop-blur-xl"
        >
          {/* AI Magic Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-xs shadow-md shadow-blue-500/30">
            <Sparkles className="w-3.5 h-3.5 fill-white" />
            <span>AI X-Ray</span>
          </div>

          <div className="h-5 w-px bg-slate-200 my-auto" />

          {/* Quick Action Buttons */}
          <button
            onClick={() => onActionClick('Process Audit')}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-blue-600" />
            <span>Scan Shadow Risk</span>
          </button>

          <button
            onClick={() => onActionClick('GSTIN Verification')}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <FileCheck className="w-3.5 h-3.5 text-blue-600" />
            <span>Validate GST & Math</span>
          </button>

          <button
            onClick={() => onActionClick('Asset Reallocation')}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 hover:text-blue-600 transition-colors cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5 text-blue-600" />
            <span>Match Dormant Asset</span>
          </button>

          {/* Add Feature Trigger */}
          {onOpenFeatureModal && (
            <button
              onClick={() => onOpenFeatureModal('add')}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-colors cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5 text-blue-600" />
              <span>Add Feature</span>
            </button>
          )}

          {/* Reset Action Trigger */}
          {onOpenFeatureModal && (
            <button
              onClick={() => onOpenFeatureModal('reset')}
              title="Reset or Clear Canvas"
              className="p-1.5 rounded-xl text-slate-500 hover:text-rose-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}

          {/* AI Assistant Chat Launcher */}
          <button
            onClick={() => onActionClick('Open AI Assistant')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-sm shadow-blue-500/25 cursor-pointer ml-1"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Ask Assistant</span>
          </button>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors ml-1 cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
