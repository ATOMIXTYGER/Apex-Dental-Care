import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ShieldCheck, 
  Search, 
  Filter, 
  Calendar, 
  User as UserIcon, 
  Terminal, 
  ChevronLeft, 
  ChevronRight, 
  Lock, 
  AlertTriangle,
  Info
} from 'lucide-react';
import { auditApi } from '../api/audit';
import { useAuth } from '../context/AuthContext';
import { AuditLogItem } from '../types';

export default function AuditLogs() {
  const { user } = useAuth();

  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(25);
  const [selectedAction, setSelectedAction] = useState<string>('');
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [userEmailSearch, setUserEmailSearch] = useState<string>('');
  const [expandedLogId, setExpandedLogId] = useState<number | null>(null);

  const { data: logData, isLoading, error } = useQuery({
    queryKey: ['auditLogs', page, pageSize, selectedAction, selectedEntity, userEmailSearch],
    queryFn: () => auditApi.list({
      page,
      page_size: pageSize,
      action: selectedAction || undefined,
      entity_name: selectedEntity || undefined,
      user_email: userEmailSearch || undefined,
    }),
  });

  const getActionBadge = (action: string) => {
    if (action.includes('FAILURE') || action.includes('DELETE') || action.includes('REVOKE')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-rose-100 text-rose-800 font-mono">{action}</span>;
    }
    if (action.includes('CREATE') || action.includes('REGISTER')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 font-mono">{action}</span>;
    }
    if (action.includes('UPDATE') || action.includes('MODIFY')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 font-mono">{action}</span>;
    }
    if (action.includes('LOGIN') || action.includes('LOGOUT')) {
      return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 font-mono">{action}</span>;
    }
    return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-800 font-mono">{action}</span>;
  };

  const renderDetails = (details?: string) => {
    if (!details) return <span className="text-slate-400 italic">None</span>;
    try {
      const parsed = JSON.parse(details);
      return (
        <pre className="text-[11px] font-mono bg-slate-900 text-emerald-400 p-2.5 rounded-lg overflow-x-auto max-h-48">
          {JSON.stringify(parsed, null, 2)}
        </pre>
      );
    } catch {
      return <span className="text-xs text-slate-700 font-mono">{details}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Audit & Compliance Log</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
              HIPAA Compliant
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Tamper-resistant append-only operational audit trail for all clinical, financial, and user modifications.
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Action Filter */}
          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-slate-500">Action:</label>
            <select
              value={selectedAction}
              onChange={(e) => {
                setSelectedAction(e.target.value);
                setPage(1);
              }}
              className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Actions</option>
              <option value="LOGIN">LOGIN</option>
              <option value="LOGOUT">LOGOUT</option>
              <option value="LOGIN_FAILURE">LOGIN_FAILURE</option>
              <option value="PATIENT_CREATE">PATIENT_CREATE</option>
              <option value="PATIENT_UPDATE">PATIENT_UPDATE</option>
              <option value="APPOINTMENT_CREATE">APPOINTMENT_CREATE</option>
              <option value="VISIT_CREATE">VISIT_CREATE</option>
              <option value="TOOTH_UPDATE">TOOTH_UPDATE</option>
              <option value="TREATMENT_PLAN_CREATE">TREATMENT_PLAN_CREATE</option>
              <option value="PRESCRIPTION_CREATE">PRESCRIPTION_CREATE</option>
              <option value="INVOICE_CREATE">INVOICE_CREATE</option>
              <option value="PAYMENT_RECORD">PAYMENT_RECORD</option>
              <option value="DOCUMENT_UPLOAD">DOCUMENT_UPLOAD</option>
              <option value="DOCUMENT_DOWNLOAD">DOCUMENT_DOWNLOAD</option>
            </select>
          </div>

          {/* Entity Filter */}
          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-slate-500">Entity:</label>
            <select
              value={selectedEntity}
              onChange={(e) => {
                setSelectedEntity(e.target.value);
                setPage(1);
              }}
              className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Entities</option>
              <option value="User">User</option>
              <option value="Patient">Patient</option>
              <option value="Appointment">Appointment</option>
              <option value="Visit">Visit</option>
              <option value="ToothCondition">ToothCondition</option>
              <option value="TreatmentPlan">TreatmentPlan</option>
              <option value="Prescription">Prescription</option>
              <option value="Invoice">Invoice</option>
              <option value="Payment">Payment</option>
              <option value="Document">Document</option>
            </select>
          </div>

          {/* User Email search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search user email..."
              value={userEmailSearch}
              onChange={(e) => {
                setUserEmailSearch(e.target.value);
                setPage(1);
              }}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-56"
            />
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Total Entries: {logData?.total || 0}
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Retrieving audit ledger...</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-rose-500">
            <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
            <p className="text-sm font-semibold">Failed to load audit logs. Verify administrative privileges.</p>
          </div>
        ) : (!logData?.items || logData.items.length === 0) ? (
          <div className="py-16 text-center">
            <ShieldCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-base font-semibold text-slate-700">No audit log records found</p>
            <p className="text-xs text-slate-500 mt-1">No operations recorded matching current filter options.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-600 uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Target Entity</th>
                  <th className="py-3 px-4">IP / Client</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logData.items.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr className="hover:bg-slate-50/70 transition">
                        {/* Timestamp */}
                        <td className="py-3 px-4 whitespace-nowrap text-slate-600 font-mono">
                          {new Date(log.created_at).toLocaleString()}
                        </td>

                        {/* Action */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          {getActionBadge(log.action)}
                        </td>

                        {/* User */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="font-semibold text-slate-800">{log.user_email || 'System / Anonymous'}</span>
                        </td>

                        {/* Entity */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          {log.entity_name ? (
                            <span className="font-medium text-slate-700">
                              {log.entity_name} {log.entity_id && <span className="font-mono text-slate-400">#{log.entity_id}</span>}
                            </span>
                          ) : (
                            <span className="text-slate-400">-</span>
                          )}
                        </td>

                        {/* IP Address */}
                        <td className="py-3 px-4 whitespace-nowrap text-slate-500 font-mono">
                          {log.ip_address || '127.0.0.1'}
                        </td>

                        {/* Details Toggle */}
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                            className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            {isExpanded ? 'Hide Payload' : 'View Payload'}
                          </button>
                        </td>
                      </tr>

                      {/* Expanded Payload Details */}
                      {isExpanded && (
                        <tr className="bg-slate-50/80">
                          <td colSpan={6} className="p-4 border-t border-slate-200">
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-xs text-slate-600">
                                <span>Event ID: <strong className="font-mono">{log.id}</strong></span>
                                <span>User Agent: <span className="font-mono text-[11px] text-slate-500">{log.user_agent || 'N/A'}</span></span>
                              </div>
                              <div>
                                <span className="text-xs font-semibold text-slate-700 block mb-1">Sanitized Event Metadata:</span>
                                {renderDetails(log.details)}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {logData && logData.total_pages > 1 && (
          <div className="p-4 border-t border-slate-200 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Page {logData.page} of {logData.total_pages} ({logData.total} events)
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 text-slate-600"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(logData.total_pages, p + 1))}
                disabled={page >= logData.total_pages}
                className="p-1.5 border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 text-slate-600"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
