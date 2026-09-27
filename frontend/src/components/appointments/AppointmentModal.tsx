import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, User, AlertCircle } from 'lucide-react';
import { Patient, User as UserType, AppointmentType, Appointment } from '../../types';
import { usersApi } from '../../api/users';
import { patientsApi } from '../../api/patients';
import { appointmentsApi } from '../../api/appointments';

interface AppointmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  initialData?: Appointment | null;
  defaultPatientId?: number;
  defaultDate?: string;
}

export const AppointmentModal: React.FC<AppointmentModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialData,
  defaultPatientId,
  defaultDate,
}) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [dentists, setDentists] = useState<UserType[]>([]);
  const [types, setTypes] = useState<AppointmentType[]>([]);

  const [patientId, setPatientId] = useState<number | ''>(defaultPatientId || initialData?.patient_id || '');
  const [dentistId, setDentistId] = useState<number | ''>(initialData?.dentist_id || '');
  const [typeId, setTypeId] = useState<number | ''>(initialData?.appointment_type_id || '');
  const [apptDate, setApptDate] = useState(
    initialData?.appointment_date || new Date().toISOString().slice(0, 10)
  );
  const [startTime, setStartTime] = useState(initialData?.start_time || '10:00:00');
  const [endTime, setEndTime] = useState(initialData?.end_time || '10:30:00');
  const [reason, setReason] = useState(initialData?.reason || '');
  const [notes, setNotes] = useState(initialData?.notes || '');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Load prerequisites
      Promise.all([
        patientsApi.list(1, 100),
        usersApi.getDentists(),
        appointmentsApi.getTypes(),
      ]).then(([pRes, dRes, tRes]) => {
        setPatients(pRes.items);
        setDentists(dRes);
        setTypes(tRes);

        if (!dentistId && dRes.length > 0) {
          setDentistId(dRes[0].id);
        }
        if (!typeId && tRes.length > 0) {
          setTypeId(tRes[0].id);
        }
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientId || !dentistId || !apptDate || !startTime || !endTime) {
      setError('Please select patient, dentist, date, and valid time.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const payload: any = {
        patient_id: Number(patientId),
        dentist_id: Number(dentistId),
        appointment_type_id: typeId ? Number(typeId) : undefined,
        appointment_date: apptDate,
        start_time: startTime.length === 5 ? `${startTime}:00` : startTime,
        end_time: endTime.length === 5 ? `${endTime}:00` : endTime,
        reason,
        notes,
      };

      if (initialData) {
        await appointmentsApi.update(initialData.id, payload);
      } else {
        await appointmentsApi.create(payload);
      }

      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Scheduling conflict detected or request failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 flex items-center justify-center font-bold">
              <Calendar className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">
                {initialData ? 'Reschedule Appointment' : 'Book Dental Appointment'}
              </h2>
              <p className="text-xs text-slate-500">Live conflict detection and operatory scheduling</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Select Patient *</label>
            <select
              value={patientId}
              disabled={!!defaultPatientId}
              onChange={(e) => setPatientId(Number(e.target.value))}
              required
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500 disabled:bg-slate-100"
            >
              <option value="">-- Choose Patient --</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.first_name} {p.last_name} ({p.patient_code}) - {p.phone}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Attending Dentist *</label>
              <select
                value={dentistId}
                onChange={(e) => setDentistId(Number(e.target.value))}
                required
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {dentists.map((d) => (
                  <option key={d.id} value={d.dentist_profile?.id || d.id}>
                    {d.full_name} ({d.dentist_profile?.specialization || 'Dentist'})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Appointment Type</label>
              <select
                value={typeId}
                onChange={(e) => setTypeId(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                {types.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.duration_minutes} min)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Date *</label>
              <input
                type="date"
                required
                value={apptDate}
                onChange={(e) => setApptDate(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Start Time *</label>
              <input
                type="time"
                required
                value={startTime.slice(0, 5)}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">End Time *</label>
              <input
                type="time"
                required
                value={endTime.slice(0, 5)}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Reason for Visit</label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Toothache, Scaling, Root Canal Follow-up"
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Internal Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              placeholder="Special instructions or patient requests..."
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Checking Conflicts...' : initialData ? 'Update Appointment' : 'Confirm Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AppointmentModal;
