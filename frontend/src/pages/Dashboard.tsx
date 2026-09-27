import React, { useState, useEffect } from 'react';
import {
  Users,
  Calendar,
  Activity,
  DollarSign,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  CalendarCheck,
  RefreshCw
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { DashboardSummary, DashboardAnalytics } from '../types';
import { dashboardApi } from '../api/dashboard';

const STATUS_COLORS: Record<string, string> = {
  scheduled: '#3b82f6',
  confirmed: '#06b6d4',
  in_progress: '#f59e0b',
  completed: '#10b981',
  cancelled: '#ef4444',
  no_show: '#94a3b8',
};

export const Dashboard: React.FC = () => {
  const [period, setPeriod] = useState<'today' | '7d' | '30d'>('30d');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumRes, anaRes] = await Promise.all([
        dashboardApi.getSummary(period),
        dashboardApi.getAnalytics(period === 'today' ? 7 : period === '7d' ? 14 : 30),
      ]);
      setSummary(sumRes);
      setAnalytics(anaRes);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [period]);

  return (
    <div className="space-y-6">
      {/* Top Welcome & Period Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Clinic Performance Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time database aggregated clinical indicators, appointments, and financial records.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Period Toggle */}
          <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold">
            {(['today', '7d', '30d'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-lg transition-all capitalize ${
                  period === p ? 'bg-white text-teal-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {p === 'today' ? 'Today' : p === '7d' ? 'Last 7 Days' : 'Last 30 Days'}
              </button>
            ))}
          </div>

          <button
            onClick={loadDashboardData}
            title="Refresh statistics"
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-xl transition-colors border border-slate-200"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-teal-600' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 6 Key Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Patients */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Patients</span>
            <Users className="w-4 h-4 text-teal-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {isLoading ? '...' : summary?.total_patients ?? 0}
          </div>
          <div className="text-[10px] text-teal-700 font-semibold mt-1">
            +{summary?.new_patients_period ?? 0} new in period
          </div>
        </div>

        {/* Today's Appointments */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Today's Appts</span>
            <CalendarCheck className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {isLoading ? '...' : summary?.today_appointments ?? 0}
          </div>
          <div className="text-[10px] text-blue-700 font-semibold mt-1">
            {summary?.upcoming_appointments ?? 0} upcoming days
          </div>
        </div>

        {/* Pending Treatments */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Pending Tx</span>
            <Activity className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {isLoading ? '...' : summary?.pending_treatments ?? 0}
          </div>
          <div className="text-[10px] text-amber-700 font-semibold mt-1">
            {summary?.completed_treatments ?? 0} completed
          </div>
        </div>

        {/* Follow-ups Due */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Follow-ups Due</span>
            <Clock className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {isLoading ? '...' : summary?.followups_due ?? 0}
          </div>
          <div className="text-[10px] text-purple-700 font-semibold mt-1">
            Requires clinical review
          </div>
        </div>

        {/* Total Revenue */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Revenue</span>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-emerald-600">
            ${isLoading ? '...' : Number(summary?.total_revenue ?? 0).toFixed(0)}
          </div>
          <div className="text-[10px] text-emerald-700 font-semibold mt-1">
            Realized cash inflow
          </div>
        </div>

        {/* Outstanding Balance */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Outstanding</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-black text-rose-600">
            ${isLoading ? '...' : Number(summary?.outstanding_payments ?? 0).toFixed(0)}
          </div>
          <div className="text-[10px] text-rose-700 font-semibold mt-1">
            Unpaid receivables
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend Area Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Daily Revenue & Invoicing Trend</h3>
              <p className="text-xs text-slate-400">Payments collected vs invoiced charges</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {analytics?.revenue_trend && analytics.revenue_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics.revenue_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0d9488" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorInv" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '11px' }}
                    formatter={(val: any) => [`$${Number(val).toFixed(2)}`, '']}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Area type="monotone" dataKey="revenue" name="Collected Revenue ($)" stroke="#0d9488" fillOpacity={1} fill="url(#colorRev)" />
                  <Area type="monotone" dataKey="invoiced" name="Invoiced Amount ($)" stroke="#3b82f6" fillOpacity={1} fill="url(#colorInv)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading charts...</div>
            )}
          </div>
        </div>

        {/* Appointment Status Distribution (Pie / Bar) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Appointments by Operational Status</h3>
              <p className="text-xs text-slate-400">Distribution across scheduled, confirmed, completed, cancelled</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {analytics?.appointments_by_status && analytics.appointments_by_status.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.appointments_by_status} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="status" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '11px' }}
                  />
                  <Bar dataKey="count" name="Appointments" radius={[6, 6, 0, 0]}>
                    {analytics.appointments_by_status.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.status] || '#14b8a6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading charts...</div>
            )}
          </div>
        </div>

        {/* Treatments by Procedure Bar Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Treatments by Procedure Type</h3>
              <p className="text-xs text-slate-400">Frequency of restorative, endodontic, and preventive procedures</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {analytics?.treatments_by_procedure && analytics.treatments_by_procedure.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={analytics.treatments_by_procedure} margin={{ top: 10, right: 20, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                  <YAxis type="category" dataKey="procedure_name" tick={{ fontSize: 9, fill: '#64748b' }} width={120} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '11px' }}
                  />
                  <Bar dataKey="count" name="Procedures Performed" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">No procedures recorded yet</div>
            )}
          </div>
        </div>

        {/* New Patients Registration Trend */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Patient Intake Trend</h3>
              <p className="text-xs text-slate-400">Newly registered patients over time</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {analytics?.patients_trend && analytics.patients_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics.patients_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '11px' }}
                  />
                  <Area type="monotone" dataKey="new_patients" name="New Patients" stroke="#10b981" fill="#ecfdf5" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading charts...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
