import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  CreditCard, 
  Plus, 
  Search, 
  Download, 
  DollarSign, 
  Calendar, 
  User as UserIcon, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  Receipt,
  ArrowUpRight
} from 'lucide-react';
import { billingApi } from '../api/billing';
import { useAuth } from '../context/AuthContext';
import InvoiceModal from '../components/billing/InvoiceModal';
import PaymentModal from '../components/billing/PaymentModal';
import { Invoice } from '../types';

export default function Billing() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedInvoiceId, setExpandedInvoiceId] = useState<number | null>(null);
  
  // Modals
  const [isInvoiceModalOpen, setIsInvoiceModalOpen] = useState(false);
  const [paymentInvoice, setPaymentInvoice] = useState<Invoice | null>(null);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  // Fetch Invoices
  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ['invoices', statusFilter],
    queryFn: () => billingApi.listInvoices(statusFilter !== 'all' ? { status: statusFilter } : undefined),
  });

  const handleDownloadPdf = async (inv: Invoice, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setDownloadingId(inv.id);
      await billingApi.downloadPdf(inv.id, inv.invoice_number);
    } catch (err) {
      console.error('Failed to download invoice PDF:', err);
      alert('Could not download invoice PDF.');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const invNum = (inv.invoice_number || '').toLowerCase();
    const patient = (inv.patient_name || '').toLowerCase();
    return invNum.includes(q) || patient.includes(q);
  });

  // Calculate Aggregates
  const totalBilled = invoices.reduce((acc, inv) => acc + Number(inv.total || 0), 0);
  const totalPaid = invoices.reduce((acc, inv) => acc + Number(inv.paid_amount || 0), 0);
  const totalOutstanding = invoices.reduce((acc, inv) => acc + Number(inv.balance || 0), 0);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200"><CheckCircle className="w-3 h-3 mr-1" /> Paid</span>;
      case 'partially_paid':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200"><Clock className="w-3 h-3 mr-1" /> Partial</span>;
      case 'voided':
      case 'void':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">Void</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200"><AlertCircle className="w-3 h-3 mr-1" /> Unpaid</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Billing & Invoices</h1>
          <p className="text-sm text-slate-500 mt-1">Manage patient invoices, payment collections, and official printable tax receipts.</p>
        </div>
        <button
          onClick={() => setIsInvoiceModalOpen(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Invoice
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Billed</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">${totalBilled.toFixed(2)}</div>
            <div className="text-xs text-slate-400 mt-0.5">{invoices.length} invoices generated</div>
          </div>
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <Receipt className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Collected</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">${totalPaid.toFixed(2)}</div>
            <div className="text-xs text-emerald-600 font-medium mt-0.5">
              {totalBilled > 0 ? `${((totalPaid / totalBilled) * 100).toFixed(1)}% recovery rate` : '0%'}
            </div>
          </div>
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
            <CheckCircle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Outstanding Balance</div>
            <div className="text-2xl font-bold text-rose-600 mt-1">${totalOutstanding.toFixed(2)}</div>
            <div className="text-xs text-slate-400 mt-0.5">Pending collection</div>
          </div>
          <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
            <AlertCircle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by invoice # or patient..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-slate-500">Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Invoices</option>
              <option value="unpaid">Unpaid</option>
              <option value="partially_paid">Partially Paid</option>
              <option value="paid">Paid</option>
              <option value="void">Void</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing {filteredInvoices.length} invoices
        </div>
      </div>

      {/* Invoices List */}
      {isLoading ? (
        <div className="py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-sm text-slate-500 mt-3 font-medium">Loading invoices...</p>
        </div>
      ) : filteredInvoices.length === 0 ? (
        <div className="bg-white py-16 text-center rounded-xl border border-slate-200">
          <Receipt className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-slate-700">No invoices found</p>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            No invoices match the selected filter criteria.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredInvoices.map((inv) => {
            const isExpanded = expandedInvoiceId === inv.id;
            const balance = Number(inv.balance || 0);

            return (
              <div key={inv.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all">
                {/* Main Row */}
                <div
                  onClick={() => setExpandedInvoiceId(isExpanded ? null : inv.id)}
                  className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer hover:bg-slate-50/60"
                >
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-blue-50 text-blue-600 rounded-xl mt-1">
                      <Receipt className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-900 text-sm">{inv.invoice_number}</span>
                        {getStatusBadge(inv.status)}
                      </div>
                      <div className="text-xs text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                        <span className="flex items-center">
                          <UserIcon className="w-3.5 h-3.5 mr-1 text-slate-400" />
                          Patient: <Link to={`/patients/${inv.patient_id}`} onClick={(e) => e.stopPropagation()} className="ml-1 text-blue-600 hover:underline font-medium">{inv.patient_name || `Patient #${inv.patient_id}`}</Link>
                        </span>
                        <span className="flex items-center">
                          <Calendar className="w-3.5 h-3.5 mr-1 text-slate-400" />
                          Date: {new Date(inv.created_at).toLocaleDateString()}
                        </span>
                        {inv.due_date && (
                          <span>Due: <strong className="text-slate-700">{inv.due_date}</strong></span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Financial Stats & Actions */}
                  <div className="flex items-center justify-between md:justify-end gap-5 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Total</div>
                      <div className="text-sm font-semibold text-slate-900">${Number(inv.total).toFixed(2)}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Paid</div>
                      <div className="text-sm font-semibold text-emerald-600">${Number(inv.paid_amount).toFixed(2)}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Balance</div>
                      <div className={`text-sm font-bold ${balance > 0 ? 'text-rose-600' : 'text-slate-700'}`}>
                        ${balance.toFixed(2)}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* Record Payment Button */}
                      {balance > 0 && inv.status !== 'voided' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setPaymentInvoice(inv);
                          }}
                          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition"
                        >
                          <DollarSign className="w-3.5 h-3.5 mr-1" />
                          Pay
                        </button>
                      )}

                      {/* Download PDF */}
                      <button
                        onClick={(e) => handleDownloadPdf(inv, e)}
                        disabled={downloadingId === inv.id}
                        className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition disabled:opacity-50"
                        title="Download Invoice PDF"
                      >
                        <Download className="w-3.5 h-3.5 mr-1" />
                        {downloadingId === inv.id ? '...' : 'PDF'}
                      </button>

                      <div className="text-slate-400 p-1">
                        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Expanded Items & Payments Details */}
                {isExpanded && (
                  <div className="border-t border-slate-200 bg-slate-50/50 p-4 sm:p-5 space-y-4">
                    {/* Billed Line Items */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Billed Line Items</h4>
                      <div className="overflow-x-auto bg-white rounded-lg border border-slate-200">
                        <table className="w-full text-left text-xs">
                          <thead>
                            <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-600">
                              <th className="py-2 px-3">Description</th>
                              <th className="py-2 px-3 text-center">Qty</th>
                              <th className="py-2 px-3 text-right">Unit Price</th>
                              <th className="py-2 px-3 text-right">Line Total</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {inv.items?.map((item) => (
                              <tr key={item.id} className="hover:bg-slate-50/60">
                                <td className="py-2 px-3 font-medium text-slate-900">{item.description}</td>
                                <td className="py-2 px-3 text-center text-slate-600">{item.quantity}</td>
                                <td className="py-2 px-3 text-right text-slate-700">${Number(item.unit_price).toFixed(2)}</td>
                                <td className="py-2 px-3 text-right font-semibold text-slate-900">${Number(item.total ?? (item.unit_price * item.quantity)).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Payment Transactions History */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Payment Transaction History</h4>
                      {(!inv.payments || inv.payments.length === 0) ? (
                        <p className="text-xs text-slate-500 italic bg-white p-3 rounded-lg border border-slate-200">No payment transactions recorded yet.</p>
                      ) : (
                        <div className="overflow-x-auto bg-white rounded-lg border border-slate-200">
                          <table className="w-full text-left text-xs">
                            <thead>
                              <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-600">
                                <th className="py-2 px-3">Transaction #</th>
                                <th className="py-2 px-3">Date</th>
                                <th className="py-2 px-3">Method</th>
                                <th className="py-2 px-3">Reference</th>
                                <th className="py-2 px-3 text-right">Amount Paid</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {inv.payments.map((p) => (
                                <tr key={p.id} className="hover:bg-slate-50/60">
                                  <td className="py-2 px-3 font-mono text-slate-600">TXN-{p.id}</td>
                                  <td className="py-2 px-3 text-slate-600">{new Date(p.payment_date).toLocaleString()}</td>
                                  <td className="py-2 px-3 capitalize font-medium text-slate-800">{p.payment_method.replace('_', ' ')}</td>
                                  <td className="py-2 px-3 text-slate-500 font-mono">{p.transaction_reference || '-'}</td>
                                  <td className="py-2 px-3 text-right font-bold text-emerald-600">+${Number(p.amount).toFixed(2)}</td>
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
          })}
        </div>
      )}

      {/* Create Invoice Modal */}
      {isInvoiceModalOpen && (
        <InvoiceModal
          isOpen={isInvoiceModalOpen}
          onClose={() => setIsInvoiceModalOpen(false)}
          onSuccess={() => {
            setIsInvoiceModalOpen(false);
            queryClient.invalidateQueries({ queryKey: ['invoices'] });
          }}
        />
      )}

      {/* Record Payment Modal */}
      {paymentInvoice && (
        <PaymentModal
          isOpen={!!paymentInvoice}
          onClose={() => setPaymentInvoice(null)}
          invoice={paymentInvoice}
          onSuccess={() => {
            setPaymentInvoice(null);
            queryClient.invalidateQueries({ queryKey: ['invoices'] });
          }}
        />
      )}
    </div>
  );
}
