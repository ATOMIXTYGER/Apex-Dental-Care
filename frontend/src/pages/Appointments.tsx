import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  User as UserIcon, 
  Plus, 
  Search, 
  Filter, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Eye, 
  Stethoscope, 
  ChevronLeft, 
  ChevronRight,
  Phone,
  FileText
} from 'lucide-react';
import { appointmentsApi } from '../api/appointments';
import { usersApi } from '../api/users';
import { useAuth } from '../context/AuthContext';
import AppointmentModal from '../components/appointments/AppointmentModal';
import VisitModal from '../components/clinical/VisitModal';
import { Appointment, User } from '../types';

export default function Appointments() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [selectedDentist, setSelectedDentist] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  const [isBookModalOpen, setIsBookModalOpen] = useState(false);
  const [activeAppointmentForVisit, setActiveAppointmentForVisit] = useState<Appointment | null>(null);

  // Fetch Dentists
  const { data: dentists = [] } = useQuery({
    queryKey: ['activeDentists'],
    queryFn: usersApi.getActiveDentists
  });

  // Fetch Appointments
  const { data: appointments = [], isLoading, error } = useQuery({
    queryKey: ['appointments', selectedDate, selectedDentist, selectedStatus],
    queryFn: () => appointmentsApi.list({
      appointment_date: selectedDate || undefined,
      dentist_id: selectedDentist !== 'all' ? Number(selectedDentist) : undefined,
      status: selectedStatus !== 'all' ? selectedStatus : undefined,
    }),
  });

  // Mutations for appointment status updates
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      appointmentsApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
    },
  });

  // Date controls
  const handlePrevDay = () => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() - 1);
    setSelectedDate(d.toISOString().split('T')[0]);
  };

  const handleNextDay = () => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + 1);
    setSelectedDate(d.toISOString().split('T')[0]);
  };

  const handleToday = () => {
    setSelectedDate(new Date().toISOString().split('T')[0]);
  };

  // Filter list by patient name or reason search
  const filteredAppointments = appointments.filter((app: Appointment) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const patientName = `${app.patient?.first_name || ''} ${app.patient?.last_name || ''}`.toLowerCase();
    const patientCode = app.patient?.patient_id?.toLowerCase() || '';
    const reason = app.reason?.toLowerCase() || '';
    return patientName.includes(q) || patientCode.includes(q) || reason.includes(q);
  });

  // Count stats
  const totalCount = filteredAppointments.length;
  const confirmedCount = filteredAppointments.filter((a: Appointment) => a.status === 'confirmed').length;
  const completedCount = filteredAppointments.filter((a: Appointment) => a.status === 'completed').length;
  const cancelledCount = filteredAppointments.filter((a: Appointment) => a.status === 'cancelled' || a.status === 'no_show').length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200"><CheckCircle className="w-3 h-3 mr-1" /> Confirmed</span>;
      case 'completed':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200"><CheckCircle className="w-3 h-3 mr-1" /> Completed</span>;
      case 'cancelled':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800 border border-rose-200"><XCircle className="w-3 h-3 mr-1" /> Cancelled</span>;
      case 'no_show':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200"><AlertCircle className="w-3 h-3 mr-1" /> No-Show</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200"><Clock className="w-3 h-3 mr-1" /> Scheduled</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Appointment Schedule</h1>
          <p className="text-sm text-slate-500 mt-1">Manage clinical consultations, bookings, and patient arrival statuses.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsBookModalOpen(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4 mr-2" />
            Book Appointment
          </button>
        </div>
      </div>

      {/* Quick Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Scheduled</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{totalCount}</div>
          </div>
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg">
            <CalendarIcon className="w-5 h-5" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmed</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{confirmedCount}</div>
          </div>
          <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-lg">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">{completedCount}</div>
          </div>
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg">
            <Stethoscope className="w-5 h-5" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cancelled / Missed</div>
            <div className="text-2xl font-bold text-rose-600 mt-1">{cancelledCount}</div>
          </div>
          <div className="p-2.5 bg-rose-50 text-rose-600 rounded-lg">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Date Navigation Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Date Selector Navigation */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevDay}
              className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600"
              title="Previous Day"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleNextDay}
              className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600"
              title="Next Day"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={handleToday}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
            >
              Today
            </button>
          </div>

          {/* Dentist & Status Filters */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2">
              <label className="text-xs font-medium text-slate-500">Dentist:</label>
              <select
                value={selectedDentist}
                onChange={(e) => setSelectedDentist(e.target.value)}
                className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Dentists</option>
                {dentists.map((d: User) => (
                  <option key={d.id} value={d.id}>{d.full_name}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <label className="text-xs font-medium text-slate-500">Status:</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="no_show">No-Show</option>
              </select>
            </div>

            {/* Quick search */}
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search patient or reason..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 sm:w-60"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Appointments List / Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Loading schedule...</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-rose-500">
            <AlertCircle className="w-8 h-8 mx-auto mb-2" />
            <p className="text-sm font-semibold">Failed to load appointments</p>
          </div>
        ) : filteredAppointments.length === 0 ? (
          <div className="py-16 text-center">
            <CalendarIcon className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-base font-semibold text-slate-700">No appointments scheduled</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              There are no patient visits booked for the selected date and filters.
            </p>
            <button
              onClick={() => setIsBookModalOpen(true)}
              className="mt-4 inline-flex items-center px-3.5 py-2 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
            >
              <Plus className="w-4 h-4 mr-1.5" /> Book an Appointment
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/75 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  <th className="py-3 px-4">Time</th>
                  <th className="py-3 px-4">Patient</th>
                  <th className="py-3 px-4">Dentist</th>
                  <th className="py-3 px-4">Type / Reason</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredAppointments.map((app: Appointment) => (
                  <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                    {/* Time */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex items-center text-slate-900 font-semibold">
                        <Clock className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                        {app.start_time.substring(0, 5)} - {app.end_time.substring(0, 5)}
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">{app.appointment_date}</div>
                    </td>

                    {/* Patient */}
                    <td className="py-3.5 px-4">
                      {app.patient ? (
                        <div>
                          <Link
                            to={`/patients/${app.patient_id}`}
                            className="font-medium text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                          >
                            {app.patient.first_name} {app.patient.last_name}
                          </Link>
                          <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                            <span className="font-mono">{app.patient.patient_id}</span>
                            {app.patient.phone && (
                              <span className="flex items-center text-slate-400">
                                <Phone className="w-3 h-3 mr-0.5" /> {app.patient.phone}
                              </span>
                            )}
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-400">ID #{app.patient_id}</span>
                      )}
                    </td>

                    {/* Dentist */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="text-slate-800 font-medium">{app.dentist?.full_name || 'Assigned Dentist'}</div>
                      <div className="text-xs text-slate-500">{app.dentist?.dentist_profile?.specialization || 'General Dentist'}</div>
                    </td>

                    {/* Type & Reason */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="inline-block px-2 py-0.5 text-xs font-medium rounded bg-slate-100 text-slate-700 capitalize">
                        {app.appointment_type.replace('_', ' ')}
                      </div>
                      {app.reason && (
                        <div className="text-xs text-slate-600 mt-1 truncate" title={app.reason}>
                          {app.reason}
                        </div>
                      )}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {getStatusBadge(app.status)}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-2">
                        {/* Clinical Visit Initiation for Dentists */}
                        {(user?.role === 'dentist' || user?.role === 'admin') && app.status !== 'cancelled' && (
                          <button
                            onClick={() => setActiveAppointmentForVisit(app)}
                            className="inline-flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-md transition"
                            title="Start or Record Clinical Visit"
                          >
                            <Stethoscope className="w-3.5 h-3.5 mr-1" />
                            Visit
                          </button>
                        )}

                        {/* Status Change Dropdown / Quick Buttons */}
                        {app.status === 'scheduled' && (
                          <button
                            onClick={() => updateStatusMutation.mutate({ id: app.id, status: 'confirmed' })}
                            className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                            title="Confirm Arrival / Booking"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}

                        {(app.status === 'scheduled' || app.status === 'confirmed') && (
                          <>
                            <button
                              onClick={() => updateStatusMutation.mutate({ id: app.id, status: 'completed' })}
                              className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                              title="Mark as Completed"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                if (window.confirm('Are you sure you want to cancel this appointment?')) {
                                  updateStatusMutation.mutate({ id: app.id, status: 'cancelled' });
                                }
                              }}
                              className="p-1 text-rose-500 hover:bg-rose-50 rounded"
                              title="Cancel Appointment"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}

                        {/* Patient Link */}
                        <Link
                          to={`/patients/${app.patient_id}`}
                          className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded"
                          title="View Patient Record"
                        >
                          <Eye className="w-4 h-4" />
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

      {/* Book Appointment Modal */}
      {isBookModalOpen && (
        <AppointmentModal
          isOpen={isBookModalOpen}
          onClose={() => setIsBookModalOpen(false)}
          defaultDate={selectedDate}
        />
      )}

      {/* Start Visit Modal */}
      {activeAppointmentForVisit && (
        <VisitModal
          isOpen={!!activeAppointmentForVisit}
          onClose={() => setActiveAppointmentForVisit(null)}
          patientId={activeAppointmentForVisit.patient_id}
          appointmentId={activeAppointmentForVisit.id}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['appointments'] });
            navigate(`/patients/${activeAppointmentForVisit.patient_id}?tab=visits`);
          }}
        />
      )}
    </div>
  );
}
