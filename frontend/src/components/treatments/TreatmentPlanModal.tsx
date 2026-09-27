import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, Activity } from 'lucide-react';
import { ProcedureCatalog } from '../../types';
import { treatmentsApi } from '../../api/treatments';
import { useAuth } from '../../context/AuthContext';

interface TreatmentPlanModalProps {
  patientId?: number;
  patientName?: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface PlanItemRow {
  procedure_name: string;
  tooth_number?: number;
  estimated_cost: number;
  notes?: string;
}

export const TreatmentPlanModal: React.FC<TreatmentPlanModalProps> = ({
  patientId,
  patientName,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { user } = useAuth();
  const dentistId = user?.dentist_profile?.id || 1;

  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [catalog, setCatalog] = useState<ProcedureCatalog[]>([]);
  const [items, setItems] = useState<PlanItemRow[]>([
    { procedure_name: 'Comprehensive Oral Examination', estimated_cost: 50.00 },
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      treatmentsApi.getCatalog().then(setCatalog);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAddItem = () => {
    setItems([
      ...items,
      { procedure_name: catalog[0]?.name || 'Dental Procedure', estimated_cost: catalog[0]?.default_cost || 100 },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, idx) => idx !== index));
  };

  const handleProcedureSelect = (index: number, procName: string) => {
    const selected = catalog.find((c) => c.name === procName);
    const updated = [...items];
    updated[index].procedure_name = procName;
    if (selected) {
      updated[index].estimated_cost = selected.default_cost;
    }
    setItems(updated);
  };

  const totalCost = items.reduce((sum, item) => sum + (Number(item.estimated_cost) || 0), 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) {
      setError('Please provide a title for the treatment plan.');
      return;
    }

    if (items.length === 0) {
      setError('Add at least one procedure to the plan.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await treatmentsApi.createPlan({
        patient_id: patientId || 1,
        dentist_id: dentistId,
        title,
        notes,
        treatments: items.map((i) => ({
          procedure_name: i.procedure_name,
          tooth_number: i.tooth_number ? Number(i.tooth_number) : undefined,
          estimated_cost: Number(i.estimated_cost),
          notes: i.notes,
        })),
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create treatment plan');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 flex items-center justify-center font-bold">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Create Treatment Plan</h2>
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

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Plan Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Comprehensive Molar Endodontics & Crown"
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Treatment Objectives / Notes</label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Phased treatment sequence, prognosis, patient consent notes..."
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          {/* Procedure Items Table */}
          <div className="pt-2">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
                Planned Procedures ({items.length})
              </label>
              <button
                type="button"
                onClick={handleAddItem}
                className="text-xs text-teal-600 hover:text-teal-700 font-bold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Procedure
              </button>
            </div>

            <div className="space-y-3">
              {items.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 border border-slate-200 rounded-xl grid grid-cols-12 gap-3 items-center"
                >
                  <div className="col-span-6">
                    <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Procedure</label>
                    <select
                      value={item.procedure_name}
                      onChange={(e) => handleProcedureSelect(idx, e.target.value)}
                      className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      {catalog.map((c) => (
                        <option key={c.id} value={c.name}>
                          {c.name} (${c.default_cost})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Tooth #</label>
                    <input
                      type="number"
                      placeholder="e.g. 16"
                      value={item.tooth_number || ''}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].tooth_number = e.target.value ? Number(e.target.value) : undefined;
                        setItems(updated);
                      }}
                      className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                  </div>

                  <div className="col-span-3">
                    <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Est. Cost ($)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={item.estimated_cost}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].estimated_cost = Number(e.target.value);
                        setItems(updated);
                      }}
                      className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                  </div>

                  <div className="col-span-1 flex justify-end pt-3">
                    <button
                      type="button"
                      onClick={() => handleRemoveItem(idx)}
                      disabled={items.length === 1}
                      className="text-slate-400 hover:text-red-600 disabled:opacity-30"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Plan Summary */}
          <div className="p-3 bg-teal-50 border border-teal-200 rounded-xl flex items-center justify-between">
            <span className="text-xs font-bold text-teal-900">Total Estimated Cost:</span>
            <span className="text-sm font-extrabold text-teal-700">${totalCost.toFixed(2)}</span>
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
              {isSubmitting ? 'Creating Plan...' : 'Save Treatment Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TreatmentPlanModal;
