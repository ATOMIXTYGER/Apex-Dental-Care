import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Stethoscope, Lock, Mail, ArrowRight, ShieldCheck, Sparkles, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!usernameOrEmail || !password) {
      setError('Please provide your username/email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await login(usernameOrEmail, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (email: string) => {
    setUsernameOrEmail(email);
    setPassword('Dental@123');
  };

  return (
    <div className="min-h-screen w-full flex bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950 text-slate-100">
      {/* Left Feature Showcase */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 relative overflow-hidden border-r border-slate-700/50">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-teal-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 rounded-full bg-teal-600/10 blur-3xl pointer-events-none" />

        {/* Branding */}
        <div className="flex items-center gap-3 z-10">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-teal-500 to-teal-400 flex items-center justify-center text-white shadow-xl shadow-teal-500/30">
            <Stethoscope className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Apex Dental Care</h1>
            <p className="text-xs text-teal-400 font-semibold tracking-wider uppercase">
              Clinical Management & Patient Records
            </p>
          </div>
        </div>

        {/* Value Proposition */}
        <div className="space-y-6 z-10 my-auto py-12 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Modern Clinical Operating Platform</span>
          </div>

          <h2 className="text-3xl font-extrabold text-white leading-tight">
            Precision dental care workflows from intake to recovery.
          </h2>

          <p className="text-sm text-slate-400 leading-relaxed">
            Interactive FDI 32-tooth notation chart, real-time conflict-free appointments, digital prescriptions with PDF generation, and automated billing.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4">
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <p className="text-2xl font-bold text-white">32 Teeth</p>
              <p className="text-xs text-slate-400 mt-1">Full FDI permanent chart with 5-surface anatomy</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <p className="text-2xl font-bold text-teal-400">100% RBAC</p>
              <p className="text-xs text-slate-400 mt-1">Role separation for Admins, Dentists, and Receptionists</p>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="flex items-center gap-2 text-xs text-slate-500 z-10">
          <ShieldCheck className="w-4 h-4 text-teal-500" />
          <span>Encrypted Clinical Storage • HIPAA & GDPR Aligned Architecture</span>
        </div>
      </div>

      {/* Right Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md space-y-8 bg-slate-900/80 p-8 sm:p-10 rounded-3xl border border-slate-700/60 shadow-2xl backdrop-blur-xl">
          <div>
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <div className="w-9 h-9 rounded-xl bg-teal-500 flex items-center justify-center text-white">
                <Stethoscope className="w-5 h-5" />
              </div>
              <span className="font-bold text-white">Apex Dental Care</span>
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight text-white">Sign In to Clinic Portal</h2>
            <p className="text-xs text-slate-400 mt-1">
              Enter your credentials or click any demo role below for 1-click login.
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-950/60 border border-red-800 rounded-xl text-xs text-red-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Email or Username
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  required
                  value={usernameOrEmail}
                  onChange={(e) => setUsernameOrEmail(e.target.value)}
                  placeholder="name@clinic.com or username"
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white rounded-xl text-xs font-bold tracking-wide transition-all shadow-lg shadow-teal-500/20 flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
            >
              {isLoading ? 'Verifying...' : 'Sign In to Workspace'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* 1-Click Demo Profiles */}
          <div className="pt-4 border-t border-slate-800">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center mb-3">
              1-Click Demo Personas
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@clinic.com')}
                className="p-2.5 rounded-xl bg-purple-950/40 hover:bg-purple-900/60 border border-purple-800/50 text-left transition-all"
              >
                <span className="block text-[10px] font-bold text-purple-300 uppercase">Admin</span>
                <span className="block text-[11px] text-white font-medium truncate">Sarah J.</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('dr.chen@clinic.com')}
                className="p-2.5 rounded-xl bg-teal-950/40 hover:bg-teal-900/60 border border-teal-800/50 text-left transition-all"
              >
                <span className="block text-[10px] font-bold text-teal-300 uppercase">Dentist</span>
                <span className="block text-[11px] text-white font-medium truncate">Dr. Chen</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('reception1@clinic.com')}
                className="p-2.5 rounded-xl bg-blue-950/40 hover:bg-blue-900/60 border border-blue-800/50 text-left transition-all"
              >
                <span className="block text-[10px] font-bold text-blue-300 uppercase">Reception</span>
                <span className="block text-[11px] text-white font-medium truncate">Jessica M.</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
