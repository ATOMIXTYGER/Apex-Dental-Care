import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  Download, 
  Calendar, 
  IndianRupee, 
  FileSpreadsheet, 
  AlertCircle, 
  CreditCard, 
  Filter,
  CheckCircle,
  Receipt
} from 'lucide-react';
import { reportsApi } from '../api/reports';
import { useAuth } from '../context/AuthContext';
import { formatINR, formatDateIN, formatDateTimeIN } from '../utils/formatters';

export default function Reports() {
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<'revenue' | 'outstanding'>('revenue');
  
  // 30 days default date range
  const todayStr = new Date().toISOString().split('T')[0];
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const thirtyDaysAgoStr = thirtyDaysAgo.toISOString().split('T')[0];

  const [startDate, setStartDate] = useState<string>(thirtyDaysAgoStr);
  const [endDate, setEndDate] = useState<string>(todayStr);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Fetch Revenue Report
  const { data: revenueData = [], isLoading: isRevLoading } = useQuery({
    queryKey: ['reportRevenue', startDate, endDate],
    queryFn: () => reportsApi.getRevenue(startDate || undefined, endDate || undefined),
    enabled: activeTab === 'revenue',
  });

  // Fetch Outstanding Report
  const { data: outstandingData = [], isLoading: isOutLoading } = useQuery({
    queryKey: ['reportOutstanding'],
    queryFn: reportsApi.getOutstanding,
    enabled: activeTab === 'outstanding',
  });

  const handleExportCsv = async () => {
    try {
      setIsExporting(true);
      await reportsApi.exportRevenueCsv(startDate, endDate);
    } catch (err) {
      console.error('Export error:', err);
      alert('Could not export CSV file.');
    } finally {
      setIsExporting(false);
    }
  };

  // Summaries
  const totalRevenueCollected = revenueData.reduce((acc, row) => acc + Number(row.amount || 0), 0);
  const totalOutstandingBalance = outstandingData.reduce((acc, row) => acc + Number(row.balance_due || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Clinical & Financial Reports</h1>
          <p className="text-sm text-slate-500 mt-1">Review clinic payment streams, cashflow ledger, and outstanding balances.</p>
        </div>
        {activeTab === 'revenue' && (
          <button
            onClick={handleExportCsv}
            disabled={isExporting}
            className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-emerald-600 rounded-lg shadow-sm hover:bg-emerald-700 transition disabled:opacity-50"
          >
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            {isExporting ? 'Exporting...' : 'Export to CSV'}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('revenue')}
          className={`py-3 px-6 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'revenue'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <IndianRupee className="w-4 h-4" />
          Revenue Collections ({revenueData.length})
        </button>
        <button
          onClick={() => setActiveTab('outstanding')}
          className={`py-3 px-6 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'outstanding'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <AlertCircle className="w-4 h-4" />
          Outstanding Receivables ({outstandingData.length})
        </button>
      </div>

      {activeTab === 'revenue' && (
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Revenue Collected</div>
                <div className="text-2xl font-bold text-emerald-600 mt-1">{formatINR(totalRevenueCollected)}</div>
                <div className="text-xs text-slate-400 mt-0.5">{revenueData.length} transactions in period</div>
              </div>
              <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                <IndianRupee className="w-6 h-6" />
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Avg Transaction Size</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {formatINR(revenueData.length > 0 ? (totalRevenueCollected / revenueData.length) : 0)}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Per receipt average</div>
              </div>
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <Receipt className="w-6 h-6" />
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Date Period</div>
                <div className="text-sm font-semibold text-slate-800 mt-1">{formatDateIN(startDate)} to {formatDateIN(endDate)}</div>
                <div className="text-xs text-slate-400 mt-0.5">Filter applied below</div>
              </div>
              <div className="p-3 bg-slate-50 text-slate-600 rounded-xl">
                <Calendar className="w-6 h-6" />
              </div>
            </div>
          </div>

          {/* Date Filter Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-2">
                <label className="text-xs font-medium text-slate-500">From:</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center space-x-2">
                <label className="text-xs font-medium text-slate-500">To:</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={() => {
                  setStartDate(thirtyDaysAgoStr);
                  setEndDate(todayStr);
                }}
                className="px-3 py-1.5 text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
              >
                Last 30 Days
              </button>
            </div>

            <div className="text-xs text-slate-500 font-medium">
              Showing {revenueData.length} records
            </div>
          </div>

          {/* Revenue Ledger Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            {isRevLoading ? (
              <div className="py-16 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
                <p className="text-sm text-slate-500 mt-3 font-medium">Loading financial ledger...</p>
              </div>
            ) : revenueData.length === 0 ? (
              <div className="py-16 text-center">
                <IndianRupee className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="text-base font-semibold text-slate-700">No payment receipts in selected range</p>
                <p className="text-xs text-slate-500 mt-1">Adjust dates to inspect other periods.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      <th className="py-3 px-4">Payment ID</th>
                      <th className="py-3 px-4">Invoice #</th>
                      <th className="py-3 px-4">Patient Name</th>
                      <th className="py-3 px-4">Payment Method</th>
                      <th className="py-3 px-4">Transaction Ref</th>
                      <th className="py-3 px-4">Date & Time</th>
                      <th className="py-3 px-4 text-right">Amount (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-xs">
                    {revenueData.map((row) => (
                      <tr key={row.payment_id} className="hover:bg-slate-50/70">
                        <td className="py-3 px-4 font-mono font-medium text-slate-700">TXN-{row.payment_id}</td>
                        <td className="py-3 px-4 font-mono text-blue-600 font-medium">{row.invoice_number}</td>
                        <td className="py-3 px-4 font-semibold text-slate-900">{row.patient_name}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800 capitalize">
                            {row.method?.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-500">{row.reference || '-'}</td>
                        <td className="py-3 px-4 text-slate-600">{formatDateTimeIN(row.date)}</td>
                        <td className="py-3 px-4 text-right font-bold text-emerald-600">+{formatINR(row.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'outstanding' && (
        <div className="space-y-6">
          {/* Outstanding KPI */}
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-rose-700 uppercase tracking-wider">Total Outstanding Patient Accounts</div>
              <div className="text-3xl font-extrabold text-rose-800 mt-1">{formatINR(totalOutstandingBalance)}</div>
              <p className="text-xs text-rose-600 mt-1">Requires accounts follow-up and patient collection reminders.</p>
            </div>
            <div className="p-3 bg-white text-rose-600 rounded-xl shadow-sm">
              <AlertCircle className="w-8 h-8" />
            </div>
          </div>

          {/* Outstanding Receivables Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            {isOutLoading ? (
              <div className="py-16 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
                <p className="text-sm text-slate-500 mt-3 font-medium">Loading receivables ledger...</p>
              </div>
            ) : outstandingData.length === 0 ? (
              <div className="py-16 text-center">
                <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                <p className="text-base font-semibold text-slate-700">No outstanding invoices</p>
                <p className="text-xs text-slate-500 mt-1">All invoices are settled in full!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      <th className="py-3 px-4">Invoice #</th>
                      <th className="py-3 px-4">Patient Name</th>
                      <th className="py-3 px-4">Phone</th>
                      <th className="py-3 px-4">Created Date</th>
                      <th className="py-3 px-4">Due Date</th>
                      <th className="py-3 px-4 text-right">Total (₹)</th>
                      <th className="py-3 px-4 text-right">Paid (₹)</th>
                      <th className="py-3 px-4 text-right">Balance Due (₹)</th>
                      <th className="py-3 px-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-xs">
                    {outstandingData.map((inv) => (
                      <tr key={inv.id} className="hover:bg-slate-50/70">
                        <td className="py-3 px-4 font-mono font-medium text-blue-600">{inv.invoice_number}</td>
                        <td className="py-3 px-4 font-semibold text-slate-900">
                          <Link to={`/patients/${inv.patient_id}`} className="hover:underline text-blue-600">
                            {inv.patient_name}
                          </Link>
                        </td>
                        <td className="py-3 px-4 text-slate-600">{inv.phone || '-'}</td>
                        <td className="py-3 px-4 text-slate-600">{formatDateIN(inv.created_at)}</td>
                        <td className="py-3 px-4 text-slate-600">{formatDateIN(inv.due_date) || '-'}</td>
                        <td className="py-3 px-4 text-right text-slate-700">{formatINR(inv.total_amount)}</td>
                        <td className="py-3 px-4 text-right text-emerald-600">{formatINR(inv.paid_amount)}</td>
                        <td className="py-3 px-4 text-right font-bold text-rose-600">{formatINR(inv.balance_due)}</td>
                        <td className="py-3 px-4 text-center">
                          <Link
                            to="/billing"
                            className="inline-flex items-center px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded"
                          >
                            Open Invoice
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
