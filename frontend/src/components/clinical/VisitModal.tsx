import React, { useState } from 'react';
import { X, Stethoscope, HeartPulse } from 'lucide-react';
import { clinicalApi } from '../../api/clinical';
import { useAuth } from '../../context/AuthContext';

interface VisitModalProps {
  patientId: number;
  patientName?: string;
  appointmentId?: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const VisitModal: React.FC<VisitModalProps> = ({
  patientId,
  patientName,
  appointmentId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { user } = useAuth();
  const dentistId = user?.dentist_profile?.id || 1;

  const [visitDate, setVisitDate] = useState(new Date().toISOString().slice(0, 10));
  const [bp, setBp] = useState('120/80');
  const [pulse, setPulse] = useState(72);
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [oralFindings, setOralFindings] = useState('');
  const [gumCondition, setGumCondition] = useState('Healthy');
  const [hygieneIndex, setHygieneIndex] = useState('Good');
  const [diagnosis, setDiagnosis] = useState('');
  const [clinicalNotes, setClinicalNotes] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!diagnosis || !chiefComplaint) {
      setError('Chief complaint and diagnosis are required.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await clinicalApi.createVisit({
        patient_id: patientId,
        dentist_id: dentistId,
        visit_date: visitDate,
        vitals_blood_pressure: bp,
        vitals_pulse: Number(pulse),
        chief_complaint: chiefComplaint,
        oral_findings: oralFindings,
        gum_condition: gumCondition,
        hygiene_index: hygieneIndex,
        diagnosis,
        clinical_notes: clinicalNotes,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to record clinical examination');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 flex items-center justify-center font-bold">
              <Stethoscope className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Record Clinical Examination</h2>
              <p className="text-xs text-slate-500">Patient: {patientName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium">
              {error}
            </div>
          )}

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Visit Date</label>
              <input
                type="date"
                required
                value={visitDate}
                onChange={(e) => setVisitDate(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Blood Pressure</label>
              <input
                type="text"
                placeholder="120/80"
                value={bp}
                onChange={(e) => setBp(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Pulse (bpm)</label>
              <input
                type="number"
                value={pulse}
                onChange={(e) => setPulse(Number(e.target.value))}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Chief Complaint *</label>
            <textarea
              required
              rows={2}
              value={chiefComplaint}
              onChange={(e) => setChiefComplaint(e.target.value)}
              placeholder="e.g. Severe toothache on upper right molar..."
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Gingival / Periodontal Status</label>
              <select
                value={gumCondition}
                onChange={(e) => setGumCondition(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="Healthy">Healthy Pink Stippled</option>
                <option value="Mild Gingivitis">Mild Marginal Gingivitis</option>
                <option value="Moderate Periodontitis">Moderate Periodontitis</option>
                <option value="Severe Periodontitis">Severe Periodontitis</option>
                <option value="Bleeding on Probing">Bleeding on Probing</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Oral Hygiene Index</label>
              <select
                value={hygieneIndex}
                onChange={(e) => setHygieneIndex(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="Good">Good</option>
                <option value="Fair">Fair</option>
                <option value="Poor">Poor</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Oral Findings & Soft Tissue</label>
            <textarea
              rows={2}
              value={oralFindings}
              onChange={(e) => setOralFindings(e.target.value)}
              placeholder="Record soft tissue examination, plaque score, mobility, percussion findings..."
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Clinical Diagnosis *</label>
            <input
              type="text"
              required
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="e.g. Acute Irreversible Pulpitis - Tooth 16"
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Treatment Performed / Notes</label>
            <textarea
              rows={2}
              value={clinicalNotes}
              onChange={(e) => setClinicalNotes(e.target.value)}
              placeholder="Operative procedures executed, anesthesia, canal medicament..."
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save Examination'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VisitModal;
