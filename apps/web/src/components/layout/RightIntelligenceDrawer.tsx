import React, { useState, useRef, useEffect } from 'react';
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
  History,
  Loader2,
  Tag,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { mockAuditLogs } from '@/lib/mockData';

import { getApiUrl } from '@/lib/api';

interface RightIntelligenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ChatMessage {
  id?: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  citations?: string[];
  toolCalls?: Array<{ tool: string; [key: string]: any }>;
  model?: string;
  provider?: string;
}

export const RightIntelligenceDrawer: React.FC<RightIntelligenceDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'assistant' | 'audit'>('assistant');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'ai',
      text: 'Hello Sarah! I am ORG-XRAY Copilot powered by Google Gemini. Ask me about procurement policies, approval limits, vendor ratings, or invoice validation rules.',
      timestamp: '11:42 AM',
      provider: 'gemini',
      model: 'gemini-2.5-flash',
    },
  ]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendQuery = async (queryText: string) => {
    if (!queryText.trim() || loading) return;
    const userMsg = queryText.trim();
    setInputVal('');

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: userMsg, timestamp: now },
    ]);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(getApiUrl('/api/v1/assistant/query'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query: userMsg }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            sender: 'ai',
            text: data.answer || 'Query processed successfully.',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            citations: data.citations || [],
            toolCalls: data.tool_calls || [],
            model: data.model_version || 'gemini-2.5-flash',
            provider: data.provider || 'gemini',
          },
        ]);
      } else {
        const errData = await res.json().catch(() => ({}));
        setMessages((prev) => [
          ...prev,
          {
            sender: 'ai',
            text: `⚠️ Query error (${res.status}): ${errData.detail || 'Failed to reach AI assistant. Ensure backend API is active.'}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: `⚠️ Connection notice: Could not connect to API server at /api/v1/assistant/query. Ensure your FastAPI server is running on port 8000.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = () => {
    sendQuery(inputVal);
  };

  return (
    <aside className="w-84 flex-shrink-0 glass-panel h-screen flex flex-col justify-between border-l border-white/50 dark:border-white/5 z-20 overflow-hidden">
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
            <span>Gemini AI Copilot</span>
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
                    className={`max-w-[92%] rounded-2xl p-3 text-xs leading-relaxed ${
                      m.sender === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none shadow-sm'
                        : 'glass-card text-slate-800 dark:text-slate-200 rounded-bl-none border border-slate-200/60 dark:border-slate-800'
                    }`}
                  >
                    {m.sender === 'ai' && (
                      <div className="flex items-center justify-between font-bold text-[10px] text-indigo-600 dark:text-indigo-400 mb-1.5 pb-1 border-b border-black/5 dark:border-white/5">
                        <div className="flex items-center gap-1">
                          <Sparkles className="w-3 h-3 fill-current" />
                          <span>ORG-XRAY Gemini AI</span>
                        </div>
                        {m.model && (
                          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
                            {m.model}
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div className="whitespace-pre-wrap font-medium">
                      {m.text}
                    </div>

                    {/* Tool Badges */}
                    {m.toolCalls && m.toolCalls.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2 pt-1 border-t border-black/5 dark:border-white/5">
                        {m.toolCalls.map((t, tidx) => (
                          <span key={tidx} className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 flex items-center gap-1">
                            <CheckCircle2 className="w-2.5 h-2.5" />
                            {t.tool}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 px-1">{m.timestamp}</span>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-xs text-indigo-600 dark:text-indigo-400 p-2 glass-card rounded-2xl w-fit">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="font-semibold text-[11px]">Gemini reasoning...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggested Prompts */}
            <div className="flex flex-col gap-2 pt-2 border-t border-slate-200/40 dark:border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Quick Prompts
              </span>
              <button
                onClick={() => sendQuery('What is the single transaction purchase limit for an employee vs manager?')}
                className="text-left p-2 rounded-xl glass-card hover:bg-indigo-50 dark:hover:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-200 transition-colors"
              >
                💳 What are employee purchase limits?
              </button>
              <button
                onClick={() => sendQuery('Which approved vendors provide IT servers and laptops?')}
                className="text-left p-2 rounded-xl glass-card hover:bg-indigo-50 dark:hover:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-200 transition-colors"
              >
                🏢 Search approved IT vendors
              </button>
              <button
                onClick={() => sendQuery('How does the dual classifier route hardware demands to avoid shadow IT?')}
                className="text-left p-2 rounded-xl glass-card hover:bg-indigo-50 dark:hover:bg-slate-800 text-[11px] font-medium text-slate-700 dark:text-slate-200 transition-colors"
              >
                🔍 How does dual routing prevent shadow IT?
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
                    <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-bold">
                      {(log.confidenceScore * 100).toFixed(0)}% confidence
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Footer */}
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
              disabled={loading}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask Gemini copilot about governance..."
              className="flex-1 bg-transparent text-xs text-slate-700 dark:text-slate-200 placeholder-slate-400 focus:outline-none px-2"
            />
            <button
              type="submit"
              disabled={loading || !inputVal.trim()}
              className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white transition-all shadow-sm"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            </button>
          </form>
        </div>
      )}

      {/* External Integration Bar */}
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

