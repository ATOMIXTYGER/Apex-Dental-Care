import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Bell, 
  Plus, 
  Search, 
  Calendar, 
  CheckCircle, 
  Clock, 
  XCircle, 
  AlertCircle, 
  User as UserIcon, 
  Phone,
  ArrowRight
} from 'lucide-react';
import { followupsApi } from '../api/followups';
import { useAuth } from '../context/AuthContext';
import FollowUpModal from '../components/followups/FollowUpModal';
import { FollowUp } from '../types';

export default function Followups() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch Follow-Ups
  const { data: followups = [], isLoading } = useQuery({
    queryKey: ['followups', statusFilter],
    queryFn: () => followupsApi.list(statusFilter !== 'all' ? { status: statusFilter } : undefined),
  });

  // Update Status Mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: 'completed' | 'cancelled' | 'pending' }) =>
      followupsApi.update(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['followups'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });

  const filteredFollowups = followups.filter((f) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const patient = (f.patient_name || '').toLowerCase();
    const reason = (f.reason || '').toLowerCase();
    const notes = (f.notes || '').toLowerCase();
    return patient.includes(q) || reason.includes(q) || notes.includes(q);
  });

  const getDueStatus = (dueDateStr: string, status: string) => {
    if (status === 'completed') {
      return <span className="text-xs font-medium text-emerald-600">Completed</span>;
    }
    if (status === 'cancelled') {
      return <span className="text-xs font-medium text-slate-400">Cancelled</span>;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const due = new Date(dueDateStr);
    due.setHours(0, 0, 0, 0);

    const diffDays = Math.round((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return <span className="inline-flex items-center text-xs font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded"><AlertCircle className="w-3 h-3 mr-1" /> Overdue by {Math.abs(diffDays)}d</span>;
    } else if (diffDays === 0) {
      return <span className="inline-flex items-center text-xs font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded"><Clock className="w-3 h-3 mr-1" /> Due Today</span>;
    } else {
      return <span className="text-xs font-medium text-blue-600">In {diffDays} days</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Patient Care Follow-Ups</h1>
          <p className="text-sm text-slate-500 mt-1">Post-operative checks, suture removals, and clinical recalls.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4 mr-2" />
          Schedule Follow-Up
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search patient, reason or notes..."
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
              <option value="pending">Pending Follow-Ups</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="all">All Records</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          {filteredFollowups.length} records found
        </div>
      </div>

      {/* Follow-Ups Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Loading clinical recalls...</p>
          </div>
        ) : filteredFollowups.length === 0 ? (
          <div className="py-16 text-center">
            <Bell className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-base font-semibold text-slate-700">No follow-ups found</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              There are no patient follow-up appointments matching this status.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  <th className="py-3 px-4">Scheduled Date</th>
                  <th className="py-3 px-4">Urgency / Due</th>
                  <th className="py-3 px-4">Patient</th>
                  <th className="py-3 px-4">Reason & Instructions</th>
                  <th className="py-3 px-4">Dentist</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredFollowups.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex items-center text-slate-900 font-semibold">
                        <Calendar className="w-4 h-4 text-blue-500 mr-2" />
                        {f.scheduled_date}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {getDueStatus(f.scheduled_date, f.status)}
                    </td>

                    <td className="py-3.5 px-4">
                      <Link
                        to={`/patients/${f.patient_id}`}
                        className="font-medium text-blue-600 hover:underline"
                      >
                        {f.patient_name || `Patient #${f.patient_id}`}
                      </Link>
                    </td>

                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-semibold text-slate-800 text-xs">{f.reason}</div>
                      {f.notes && (
                        <div className="text-xs text-slate-500 mt-0.5 italic">{f.notes}</div>
                      )}
                    </td>

                    <td className="py-3.5 px-4 whitespace-nowrap text-xs text-slate-700">
                      {f.dentist_name || 'Assigned Doctor'}
                    </td>

                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-2">
                        {f.status === 'pending' && (
                          <>
                            <button
                              onClick={() => updateStatusMutation.mutate({ id: f.id, status: 'completed' })}
                              className="inline-flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-md transition"
                              title="Mark Follow-up as Completed"
                            >
                              <CheckCircle className="w-3.5 h-3.5 mr-1" />
                              Done
                            </button>
                            <button
                              onClick={() => {
                                if (window.confirm('Cancel this follow-up?')) {
                                  updateStatusMutation.mutate({ id: f.id, status: 'cancelled' });
                                }
                              }}
                              className="p-1 text-rose-500 hover:bg-rose-50 rounded"
                              title="Cancel"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        <Link
                          to={`/patients/${f.patient_id}`}
                          className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded"
                          title="View Patient Profile"
                        >
                          <ArrowRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Schedule Follow-up Modal */}
      {isModalOpen && (
        <FollowUpModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={() => {
            setIsModalOpen(false);
            queryClient.invalidateQueries({ queryKey: ['followups'] });
          }}
        />
      )}
    </div>
  );
}
