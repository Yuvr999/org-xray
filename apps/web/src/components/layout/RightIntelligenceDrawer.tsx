import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  AlertCircle,
  X,
  PanelRightClose
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
      const apiUrl = getApiUrl('/api/v1/assistant/query');
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: `⚠️ Could not reach the AI API. This may be because the server is waking up (free tier — wait ~30s and try again).\n\nEndpoint tried: ${apiUrl}\n\nIf this persists, the API service may be restarting. Please try again in 30 seconds.`,
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
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ width: 0, opacity: 0, x: 20 }}
          animate={{ width: 340, opacity: 1, x: 0 }}
          exit={{ width: 0, opacity: 0, x: 20 }}
          transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
          className="flex-shrink-0 glass-panel h-screen flex flex-col justify-between border-l border-slate-200 z-30 overflow-hidden relative shadow-2xl bg-white/95 backdrop-blur-xl"
        >
          {/* Drawer Top Header: Tabs and Top-Right Close Button */}
          <div className="p-3.5 border-b border-slate-200 flex items-center justify-between gap-2">
            <div className="flex-1 flex items-center p-1 rounded-xl bg-slate-100 border border-slate-200">
              <button
                onClick={() => setActiveTab('assistant')}
                className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                  activeTab === 'assistant'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-blue-600'
                }`}
              >
                <Bot className="w-3.5 h-3.5" />
                <span>AI Copilot</span>
              </button>

              <button
                onClick={() => setActiveTab('audit')}
                className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                  activeTab === 'audit'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-blue-600'
                }`}
              >
                <History className="w-3.5 h-3.5" />
                <span>Audit Trail</span>
              </button>
            </div>

            {/* Top Right Close Button */}
            <button
              onClick={onClose}
              title="Close Sidebar"
              className="p-1.5 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <PanelRightClose className="w-4 h-4" />
            </button>
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
                        className={`max-w-[92%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                          m.sender === 'user'
                            ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                            : 'bg-white text-slate-900 rounded-bl-none border border-slate-200 shadow-md'
                        }`}
                      >
                        {m.sender === 'ai' && (
                          <div className="flex items-center justify-between font-bold text-[10px] text-blue-600 mb-1.5 pb-1 border-b border-slate-100">
                            <div className="flex items-center gap-1">
                              <Sparkles className="w-3 h-3 fill-current" />
                              <span>ORG-XRAY Gemini AI</span>
                            </div>
                            {m.model && (
                              <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 border border-blue-200">
                                {m.model}
                              </span>
                            )}
                          </div>
                        )}
                        
                        <div className="whitespace-pre-wrap font-medium text-slate-800">
                          {m.text}
                        </div>

                        {/* Tool Badges */}
                        {m.toolCalls && m.toolCalls.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2 pt-1 border-t border-slate-100">
                            {m.toolCalls.map((t, tidx) => (
                              <span key={tidx} className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-blue-50 text-blue-700 flex items-center gap-1 border border-blue-200">
                                <CheckCircle2 className="w-2.5 h-2.5 text-blue-600" />
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
                    <div className="flex items-center gap-2 text-xs text-blue-600 p-2.5 bg-white rounded-2xl w-fit border border-slate-200 shadow-sm">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      <span className="font-semibold text-[11px]">Gemini reasoning...</span>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Quick Suggested Prompts */}
                <div className="flex flex-col gap-2 pt-2 border-t border-slate-200">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Quick Inquiries
                  </span>
                  <button
                    onClick={() => sendQuery('What is the single transaction purchase limit for an employee vs manager?')}
                    className="text-left p-2.5 rounded-xl bg-white hover:bg-blue-50 text-[11px] font-medium text-slate-800 transition-colors border border-slate-200 shadow-xs"
                  >
                    💳 What are employee purchase limits?
                  </button>
                  <button
                    onClick={() => sendQuery('Which approved vendors provide IT servers and laptops?')}
                    className="text-left p-2.5 rounded-xl bg-white hover:bg-blue-50 text-[11px] font-medium text-slate-800 transition-colors border border-slate-200 shadow-xs"
                  >
                    🏢 Search approved IT vendors
                  </button>
                  <button
                    onClick={() => sendQuery('How does the dual classifier route hardware demands to avoid shadow IT?')}
                    className="text-left p-2.5 rounded-xl bg-white hover:bg-blue-50 text-[11px] font-medium text-slate-800 transition-colors border border-slate-200 shadow-xs"
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
                  <div key={log.id} className="bg-white rounded-xl p-3 flex flex-col gap-1 border border-slate-200 shadow-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900">{log.action}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{log.timestamp}</span>
                    </div>
                    <p className="text-[11px] text-slate-600">Target: {log.target}</p>
                    <div className="flex items-center justify-between mt-1 text-[10px]">
                      <span className="text-blue-600 font-semibold">{log.actor}</span>
                      {log.confidenceScore && (
                        <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-bold border border-blue-200">
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
            <div className="p-3 border-t border-slate-200">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-2 bg-slate-50 rounded-xl p-1.5 border border-slate-200"
              >
                <input
                  type="text"
                  value={inputVal}
                  disabled={loading}
                  onChange={(e) => setInputVal(e.target.value)}
                  placeholder="Ask Gemini copilot..."
                  className="flex-1 bg-transparent text-xs text-slate-800 placeholder-slate-400 focus:outline-none px-2"
                />
                <button
                  type="submit"
                  disabled={loading || !inputVal.trim()}
                  className="p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition-all shadow-sm cursor-pointer"
                >
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                </button>
              </form>
            </div>
          )}

          {/* External Integration Bar */}
          <div className="p-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-around text-slate-700 text-xs">
            <span className="text-[10px] font-bold text-slate-400">Sync:</span>
            <span className="font-bold flex items-center gap-1 cursor-pointer hover:text-blue-600">
              Notion
            </span>
            <span className="font-bold flex items-center gap-1 cursor-pointer hover:text-blue-600">
              Slack
            </span>
            <span className="font-bold flex items-center gap-1 cursor-pointer hover:text-blue-600">
              Drive
            </span>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

