import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Bot, FileCheck, ShieldAlert, Zap, X } from 'lucide-react';
import { floatingToolbarVariants } from '@/lib/motion-config';

interface FloatingAIToolbarProps {
  isVisible: boolean;
  selectedText?: string;
  onActionClick: (action: string) => void;
  onClose: () => void;
}

export const FloatingAIToolbar: React.FC<FloatingAIToolbarProps> = ({
  isVisible,
  selectedText,
  onActionClick,
  onClose,
}) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          variants={floatingToolbarVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 glass-floating-bar rounded-2xl p-2 px-3 flex items-center gap-2 shadow-2xl border border-white/60 dark:border-white/10"
        >
          {/* AI Magic Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-500 text-white font-bold text-xs shadow-md animate-pulse">
            <Sparkles className="w-3.5 h-3.5 fill-white" />
            <span>AI X-Ray</span>
          </div>

          <div className="h-5 w-px bg-slate-200 dark:bg-slate-700 my-auto" />

          {/* Quick Action Buttons */}
          <button
            onClick={() => onActionClick('Process Audit')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-800 hover:text-indigo-600 transition-colors"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />
            <span>Scan Shadow Risk</span>
          </button>

          <button
            onClick={() => onActionClick('GSTIN Verification')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-800 hover:text-indigo-600 transition-colors"
          >
            <FileCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Validate GST & Math</span>
          </button>

          <button
            onClick={() => onActionClick('Asset Reallocation')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-800 hover:text-indigo-600 transition-colors"
          >
            <Zap className="w-3.5 h-3.5 text-indigo-500" />
            <span>Match Dormant Asset</span>
          </button>

          {/* AI Assistant Chat Launcher */}
          <button
            onClick={() => onActionClick('Open AI Assistant')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition-all shadow-sm hover:shadow-indigo-500/25"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Ask Assistant</span>
          </button>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ml-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
