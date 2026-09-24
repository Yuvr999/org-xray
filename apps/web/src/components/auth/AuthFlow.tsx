import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, UserCheck, Users, Lock, Mail, ArrowLeft, Sparkles, CheckCircle2, ChevronRight, KeyRound } from 'lucide-react';

export type UserRole = 'admin' | 'manager' | 'employee';

export interface UserSession {
  role: UserRole;
  name: string;
  email: string;
  avatar: string;
  department: string;
}

interface AuthFlowProps {
  onLoginSuccess: (session: UserSession) => void;
}

export const AuthFlow: React.FC<AuthFlowProps> = ({ onLoginSuccess }) => {
  // Step 1 = Role Selection, Step 2 = Credentials Login Form
  const [step, setStep] = useState<1 | 2>(1);
  const [selectedRole, setSelectedRole] = useState<UserRole>('admin');
  const [email, setEmail] = useState('admin@org-xray.internal');
  const [password, setPassword] = useState('••••••••••••');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showForgotModal, setShowForgotModal] = useState(false);

  const roleDetails: Record<
    UserRole,
    {
      title: string;
      defaultEmail: string;
      defaultName: string;
      department: string;
      avatar: string;
      icon: React.ElementType;
    }
  > = {
    admin: {
      title: 'Admin',
      defaultEmail: 'admin@org-xray.internal',
      defaultName: 'Devon Vance (Admin)',
      department: 'Enterprise Security & IT Ops',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=faces',
      icon: Shield,
    },
    manager: {
      title: 'Manager',
      defaultEmail: 'manager.sarah@org-xray.internal',
      defaultName: 'Sarah Jenkins (Manager)',
      department: 'Engineering & Procurement',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=faces',
      icon: UserCheck,
    },
    employee: {
      title: 'Employee',
      defaultEmail: 'alex.morgan@org-xray.internal',
      defaultName: 'Alex Morgan (Staff)',
      department: 'Product Development',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces',
      icon: Users,
    },
  };

  const handleSelectRole = (role: UserRole) => {
    setSelectedRole(role);
    setEmail(roleDetails[role].defaultEmail);
    setPassword('password123');
    setStep(2);
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrorMessage('Please enter your Email or User ID');
      return;
    }
    setErrorMessage('');
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      const details = roleDetails[selectedRole];
      onLoginSuccess({
        role: selectedRole,
        name: details.defaultName,
        email: email,
        avatar: details.avatar,
        department: details.department,
      });
    }, 500);
  };

  return (
    <div className="min-h-screen bg-[#0055fe] text-slate-100 flex flex-col justify-between items-center p-4 sm:p-8 selection:bg-blue-600 selection:text-white bg-ambient-mesh-dark">
      {/* Top Brand Bar */}
      <header className="w-full max-w-5xl flex items-center justify-between py-4">
        <div className="flex items-center gap-3.5">
          <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center text-blue-600 shadow-xl shadow-black/15 border-2 border-white/80">
            <Sparkles className="w-7 h-7 fill-blue-600 text-blue-600" />
          </div>
          <div>
            <span className="text-2xl sm:text-3xl font-black tracking-tight text-white leading-none block">
              ORG<span className="text-blue-200">-XRAY</span>
            </span>
            <span className="block text-xs font-black tracking-widest uppercase text-blue-100 mt-0.5">
              Enterprise Intelligence
            </span>
          </div>
        </div>

        <div className="text-xs sm:text-sm font-extrabold text-white flex items-center gap-2 bg-white/10 px-3.5 py-1.5 rounded-full border border-white/20">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400"></span>
          <span>System Online • 99.98% SLA</span>
        </div>
      </header>

      {/* Main Container */}
      <div className="w-full max-w-4xl my-auto py-8">
        <AnimatePresence mode="wait">
          {/* ============================================================ */}
          {/* STEP 1: PORTAL & ROLE SELECTION (1st Page - Clean White Boxes) */}
          {/* ============================================================ */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
              className="flex flex-col items-center text-center max-w-md mx-auto"
            >
              {/* Ultra-Clean "Sign In" Header */}
              <div className="mb-8">
                <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight">
                  Sign In
                </h1>
              </div>

              {/* 3 Clean White Role Boxes with Bold Black Letters */}
              <div className="flex flex-col gap-4 w-full">
                {[
                  { key: 'admin' as UserRole, title: 'Admin', icon: Shield },
                  { key: 'manager' as UserRole, title: 'Manager', icon: UserCheck },
                  { key: 'employee' as UserRole, title: 'Employee', icon: Users },
                ].map((item) => {
                  const Icon = item.icon;

                  return (
                    <motion.button
                      key={item.key}
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSelectRole(item.key)}
                      className="w-full bg-white hover:border-blue-500 hover:shadow-2xl border-2 border-slate-200 rounded-2xl p-4.5 sm:p-5 flex items-center justify-between transition-all duration-200 cursor-pointer group shadow-xl"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-xs">
                          <Icon className="w-6 h-6" />
                        </div>
                        <span className="text-lg font-black text-slate-900 group-hover:text-blue-600 transition-colors">
                          Sign in as {item.title}
                        </span>
                      </div>

                      <ChevronRight className="w-6 h-6 text-slate-800 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* ============================================================ */}
          {/* STEP 2: CREDENTIALS LOGIN SCREEN (White Card & Black Letters) */}
          {/* ============================================================ */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center max-w-lg mx-auto"
            >
              {/* Back to Step 1 Switcher */}
              <button
                type="button"
                onClick={() => setStep(1)}
                className="self-start mb-6 inline-flex items-center gap-2 text-xs font-black text-slate-900 hover:text-blue-600 transition-colors cursor-pointer bg-white px-4 py-2 rounded-xl border border-slate-200 shadow-md"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Role Selection</span>
              </button>

              {/* Login Card Container (Crisp White Card with Black Font) */}
              <div className="w-full bg-white rounded-3xl border border-slate-200 shadow-2xl p-8 sm:p-10 text-center">
                {/* Company Logo Header */}
                <div className="flex flex-col items-center justify-center mb-8">
                  <div className="flex items-center justify-center gap-3.5">
                    <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
                      <Sparkles className="w-7 h-7 fill-white" />
                    </div>
                    <div className="text-left">
                      <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 leading-none">
                        ORG<span className="text-blue-600">-XRAY</span>
                      </h2>
                      <span className="text-xs font-black tracking-widest uppercase text-blue-600 mt-1 block">
                        Intelligence Hub
                      </span>
                    </div>
                  </div>

                  {/* Active Portal Indicator Pill */}
                  <div className="mt-4 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-black">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse"></span>
                    <span>Portal: {roleDetails[selectedRole].title} Login</span>
                  </div>
                </div>

                {/* Form Elements */}
                <form onSubmit={handleLoginSubmit} className="space-y-4 text-left">
                  {/* EMAIL / USER ID Input */}
                  <div>
                    <label className="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1.5">
                      Email / User ID
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="ENTER EMAIL OR USER ID"
                        className="w-full h-12 px-4 rounded-xl bg-slate-50 border-2 border-slate-200 text-slate-900 placeholder:text-slate-400 placeholder:font-bold placeholder:text-xs text-sm font-black focus:bg-white focus:outline-hidden focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 transition-all uppercase tracking-wide"
                        required
                      />
                    </div>
                  </div>

                  {/* PASSWORD Input */}
                  <div>
                    <label className="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1.5">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="ENTER PASSWORD"
                        className="w-full h-12 px-4 rounded-xl bg-slate-50 border-2 border-slate-200 text-slate-900 placeholder:text-slate-400 placeholder:font-bold placeholder:text-xs text-sm font-black focus:bg-white focus:outline-hidden focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 transition-all uppercase tracking-wide"
                        required
                      />
                    </div>
                  </div>

                  {errorMessage && (
                    <p className="text-xs font-bold text-rose-800 bg-rose-50 p-3 rounded-xl border border-rose-200">
                      {errorMessage}
                    </p>
                  )}

                  {/* LOGIN Button */}
                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full h-12 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-black text-sm tracking-wider uppercase shadow-lg shadow-blue-600/30 transition-all cursor-pointer flex items-center justify-center gap-2"
                    >
                      {isLoading ? (
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        <span>LOGIN</span>
                      )}
                    </button>
                  </div>

                  {/* Forgot Password Link */}
                  <div className="text-center pt-2">
                    <button
                      type="button"
                      onClick={() => setShowForgotModal(true)}
                      className="text-xs font-black text-blue-600 hover:text-blue-700 hover:underline transition-colors cursor-pointer"
                    >
                      Forgot your password?
                    </button>
                  </div>
                </form>

                {/* Demo Quick Role Switcher */}
                <div className="mt-8 pt-5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <span className="font-bold text-slate-700">Demo Quick Switch:</span>
                  <div className="flex items-center gap-1.5">
                    {(['admin', 'manager', 'employee'] as UserRole[]).map((r) => (
                      <button
                        key={r}
                        type="button"
                        onClick={() => handleSelectRole(r)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-black capitalize transition-all cursor-pointer border ${
                          selectedRole === r
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'bg-slate-100 text-slate-800 border-slate-200 hover:bg-slate-200'
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Forgot Password Modal */}
      <AnimatePresence>
        {showForgotModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-md flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-slate-900 rounded-2xl p-6 max-w-sm w-full border border-blue-900/40 shadow-2xl text-center text-slate-100"
            >
              <div className="w-12 h-12 rounded-full bg-blue-950 text-blue-400 flex items-center justify-center mx-auto mb-3 border border-blue-800/40">
                <KeyRound className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white">Reset Portal Password</h3>
              <p className="text-xs text-slate-400 mt-1 mb-4">
                Enter your registered ID to receive a secure login token.
              </p>
              <input
                type="email"
                defaultValue={email}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white mb-4 focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-hidden"
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowForgotModal(false)}
                  className="flex-1 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    alert('Password reset link sent to registered email address!');
                    setShowForgotModal(false);
                  }}
                  className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-bold text-white cursor-pointer"
                >
                  Send Link
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="w-full max-w-5xl py-4 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
        <span>&copy; 2026 ORG-XRAY Technologies Inc. All rights reserved.</span>
        <div className="flex items-center gap-4 text-slate-400 font-semibold">
          <a href="#privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</a>
          <span>•</span>
          <a href="#terms" className="hover:text-blue-400 transition-colors">Terms of Service</a>
          <span>•</span>
          <a href="#security" className="hover:text-blue-400 transition-colors">Security Whitepaper</a>
        </div>
      </footer>
    </div>
  );
};
