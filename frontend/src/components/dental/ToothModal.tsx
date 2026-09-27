import React, { useState } from 'react';
import { X, History, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';
import { ToothCondition, ToothHistory, ToothConditionType } from '../../types';
import { getConditionColor, getToothName, getConditionBadgeClass } from './FDIToothChart';
import { useAuth } from '../../context/AuthContext';

interface ToothModalProps {
  toothNumber: number;
  conditionData?: ToothCondition;
  history: ToothHistory[];
  isOpen: boolean;
  onClose: () => void;
  onUpdateCondition: (data: {
    tooth_number: number;
    condition: ToothConditionType;
    severity?: string;
    surfaces?: string;
    notes?: string;
  }) => Promise<void>;
}

export const ToothModal: React.FC<ToothModalProps> = ({
  toothNumber,
  conditionData,
  history,
  isOpen,
  onClose,
  onUpdateCondition,
}) => {
  const { hasRole } = useAuth();
  const canEdit = hasRole('dentist', 'admin');

  const [condition, setCondition] = useState<ToothConditionType>(
    conditionData?.current_condition || 'healthy'
  );
  const [severity, setSeverity] = useState<string>(conditionData?.severity || 'none');
  const [surfaces, setSurfaces] = useState<string>(conditionData?.surfaces || '');
  const [notes, setNotes] = useState<string>(conditionData?.notes || '');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const toothHistory = history.filter((h) => h.tooth_number === toothNumber);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await onUpdateCondition({
        tooth_number: toothNumber,
        condition,
        severity,
        surfaces,
        notes,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to update tooth condition');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleSurface = (surf: string) => {
    if (surfaces.includes(surf)) {
      setSurfaces(surfaces.replace(surf, ''));
    } else {
      setSurfaces(surfaces + surf);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-teal-700 bg-teal-100 px-2 py-0.5 rounded">
                Tooth #{toothNumber}
              </span>
              <h2 className="text-base font-bold text-slate-800">{getToothName(toothNumber)}</h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Permanent Dentition • FDI World Dental Federation Notation
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 font-medium">
              {error}
            </div>
          )}

          {/* Current State Summary */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Current Status</p>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${getConditionBadgeClass(
                    conditionData?.current_condition || 'healthy'
                  )}`}
                >
                  {conditionData?.current_condition || 'healthy'}
                </span>
                {conditionData?.severity && conditionData.severity !== 'none' && (
                  <span className="text-xs font-semibold text-slate-600 capitalize">
                    ({conditionData.severity})
                  </span>
                )}
              </div>
            </div>
            {conditionData?.surfaces && (
              <div className="text-right">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Involved Surfaces</p>
                <p className="text-xs font-bold text-slate-800 font-mono mt-0.5">{conditionData.surfaces}</p>
              </div>
            )}
          </div>

          {/* Edit Form (Dentist / Admin) */}
          {canEdit ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Dental Condition *
                  </label>
                  <select
                    value={condition}
                    onChange={(e) => setCondition(e.target.value as ToothConditionType)}
                    className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="healthy">Healthy</option>
                    <option value="caries">Caries / Cavity</option>
                    <option value="filled">Filled / Restored</option>
                    <option value="crown">Crown Fitted</option>
                    <option value="root_canal">Root Canal (RCT)</option>
                    <option value="missing">Missing / Extracted</option>
                    <option value="extraction">Extraction Indicated</option>
                    <option value="fracture">Fractured / Cracked</option>
                    <option value="sensitivity">Dentin Hypersensitivity</option>
                    <option value="mobility">Mobility</option>
                    <option value="bridge">Bridge Abutment / Pontic</option>
                    <option value="implant">Dental Implant</option>
                    <option value="impacted">Impacted Tooth</option>
                    <option value="other">Other Pathologic Finding</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Severity</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="none">None / Standard</option>
                    <option value="mild">Mild (Early stage)</option>
                    <option value="moderate">Moderate (Dentin involvement)</option>
                    <option value="severe">Severe (Deep / Pulpal)</option>
                  </select>
                </div>
              </div>

              {/* Surface Selector Buttons */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Surfaces Involved (Click to Toggle)
                </label>
                <div className="flex items-center gap-2">
                  {[
                    { key: 'O', label: 'Occlusal (O)' },
                    { key: 'M', label: 'Mesial (M)' },
                    { key: 'D', label: 'Distal (D)' },
                    { key: 'B', label: 'Buccal / Facial (B)' },
                    { key: 'L', label: 'Lingual / Palatal (L)' },
                  ].map((s) => (
                    <button
                      key={s.key}
                      type="button"
                      onClick={() => toggleSurface(s.key)}
                      className={`text-xs px-2.5 py-1.5 rounded-lg font-semibold border transition-all ${
                        surfaces.includes(s.key)
                          ? 'bg-teal-600 text-white border-teal-600 shadow-sm'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Clinical Examination Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  placeholder="Record diagnostic findings, percussion response, vitality, or planned procedure..."
                  className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
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
                  className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Saving...' : 'Update Tooth Record'}
                </button>
              </div>
            </form>
          ) : (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 flex-shrink-0" />
              <span>
                Read-only mode. Only dentists and administrators have clinical authorization to modify dental chart states.
              </span>
            </div>
          )}

          {/* Historical Changes Timeline for this Tooth */}
          <div className="pt-4 border-t border-slate-200">
            <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5 mb-3">
              <History className="w-4 h-4 text-slate-400" />
              <span>Tooth Clinical History</span>
            </h4>

            {toothHistory.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No past clinical updates recorded for this tooth.</p>
            ) : (
              <div className="space-y-2.5">
                {toothHistory.map((h) => (
                  <div
                    key={h.id}
                    className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-start justify-between text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-800 capitalize">{h.condition}</span>
                        {h.severity && h.severity !== 'none' && (
                          <span className="text-[11px] text-slate-500">({h.severity})</span>
                        )}
                        {h.surfaces && (
                          <span className="font-mono text-[10px] bg-slate-200 px-1 rounded text-slate-700">
                            {h.surfaces}
                          </span>
                        )}
                      </div>
                      {h.notes && <p className="text-slate-600 mt-1">{h.notes}</p>}
                      <p className="text-[10px] text-slate-400 mt-1">
                        Recorded by {h.dentist_name || 'Attending Doctor'}
                      </p>
                    </div>
                    <span className="text-[10px] text-slate-400 font-medium whitespace-nowrap">
                      {new Date(h.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
