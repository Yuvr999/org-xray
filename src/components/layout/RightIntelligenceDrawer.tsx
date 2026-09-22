import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Bot, 
  Send, 
  Sparkles, 
  ShieldCheck, 
  Clock, 
  ChevronRight, 
  ExternalLink,
  MessageSquare,
  History
} from 'lucide-react';
import { mockAuditLogs } from '@/lib/mockData';

interface RightIntelligenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RightIntelligenceDrawer: React.FC<RightIntelligenceDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'assistant' | 'audit'>('assistant');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Hello Sarah! I scanned the latest invoice from Apex Cloud (APX-99412). The 18% GST calculation is verified, but I flagged a potential duplicate claim under INV-2026-083. How would you like to proceed?',
      timestamp: '11:42 AM',
    },
  ]);
  const [inputVal, setInputVal] = useState('');

  const handleSend = () => {
    if (!inputVal.trim()) return;
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: inputVal, timestamp: 'Just now' },
      {
        sender: 'ai',
        text: `Understood. Analyzing "${inputVal}" against enterprise policy #POL-881... Recommendation generated.`,
        timestamp: 'Just now',
      },
    ]);
    setInputVal('');
  };

  return (
    <aside className="w-80 flex-shrink-0 glass-panel h-screen flex flex-col justify-between border-l border-white/50 dark:border-white/5 z-20 overflow-hidden">
      {/* Drawer Header Tabs */}
      <div className="p-4 border-b border-slate-200/60 dark:border-slate-800">
        <div className="flex items-center justify-between p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80">
          <button
            onClick={() => setActiveTab('assistant')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'assistant'
                ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>AI Assistant</span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'audit'
                ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Audit Trail</span>
          </button>
        </div>
      </div>

      {/* Drawer Content */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {activeTab === 'assistant' ? (
          <>
            {/* Conversation Messages */}
            <div className="flex-1 flex flex-col gap-3">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col gap-1 ${
                    m.sender === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div
                    className={`max-w-[88%] rounded-2xl p-3 text-xs leading-relaxed ${
                      m.sender === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none shadow-sm'
                        : 'glass-card text-slate-700 dark:text-slate-200 rounded-bl-none'
                    }`}
                  >
                    {m.sender === 'ai' && (
                      <div className="flex items-center gap-1 font-bold text-[10px] text-indigo-600 dark:text-indigo-400 mb-1">
                        <Sparkles className="w-3 h-3 fill-current" />
                        <span>Org X-Ray Copilot</span>
                      </div>
                    )}
                    {m.text}
                  </div>
                  <span className="text-[10px] text-slate-400 px-1">{m.timestamp}</span>
                </div>
              ))}
            </div>

            {/* Quick Suggested Prompts (Matching Reference Screenshot 3!) */}
            <div className="flex flex-col gap-2 pt-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Suggested Actions
              </span>
              <button
                onClick={() => setInputVal('Check GSTIN checksum for 27AAACA12341Z5')}
                className="text-left p-2 rounded-xl glass-card hover:bg-indigo-50 dark:hover:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-200 transition-colors"
              >
                🔍 Check GSTIN Checksum
              </button>
              <button
                onClick={() => setInputVal('Scan for dormant laptops in IT depot')}
                className="text-left p-2 rounded-xl glass-card hover:bg-indigo-50 dark:hover:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-200 transition-colors"
              >
                📦 Match Dormant IT Hardware
              </button>
            </div>
          </>
        ) : (
          /* Audit Logs View */
          <div className="flex flex-col gap-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Immutable System Audit Logs
            </span>
            {mockAuditLogs.map((log) => (
              <div key={log.id} className="glass-card rounded-xl p-3 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{log.action}</span>
                  <span className="text-[10px] text-slate-400 font-mono">{log.timestamp}</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">Target: {log.target}</p>
                <div className="flex items-center justify-between mt-1 text-[10px]">
                  <span className="text-indigo-600 dark:text-indigo-400 font-semibold">{log.actor}</span>
                  {log.confidenceScore && (
                    <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 font-bold">
                      {(log.confidenceScore * 100).toFixed(0)}% confidence
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Footer for Assistant */}
      {activeTab === 'assistant' && (
        <div className="p-3 border-t border-slate-200/60 dark:border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2 bg-white/60 dark:bg-slate-800/60 rounded-xl p-1.5 border border-white/80 dark:border-slate-700"
          >
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask copilot about governance..."
              className="flex-1 bg-transparent text-xs text-slate-700 dark:text-slate-200 placeholder-slate-400 focus:outline-none px-2"
            />
            <button
              type="submit"
              className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-all shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}

      {/* External Integration Bar (Matching Notion/Slack/Drive in Screenshot 3!) */}
      <div className="p-3 bg-slate-50/50 dark:bg-slate-900/50 border-t border-slate-200/60 dark:border-slate-800 flex items-center justify-around">
        <span className="text-[10px] font-bold text-slate-400">Sync:</span>
        <span className="text-xs font-bold text-slate-600 dark:text-slate-300 flex items-center gap-1 cursor-pointer hover:text-indigo-600">
          N Notion
        </span>
        <span className="text-xs font-bold text-slate-600 dark:text-slate-300 flex items-center gap-1 cursor-pointer hover:text-indigo-600">
          # Slack
        </span>
        <span className="text-xs font-bold text-slate-600 dark:text-slate-300 flex items-center gap-1 cursor-pointer hover:text-indigo-600">
          ▲ Drive
        </span>
      </div>
    </aside>
  );
};
