import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, FileSpreadsheet, Download } from 'lucide-react';
import { MedicineCatalog } from '../../types';
import { prescriptionsApi } from '../../api/prescriptions';
import { useAuth } from '../../context/AuthContext';

interface PrescriptionModalProps {
  patientId?: number;
  patientName?: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface MedItemRow {
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  timing: string;
  instructions?: string;
}

export const PrescriptionModal: React.FC<PrescriptionModalProps> = ({
  patientId,
  patientName,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { user } = useAuth();
  const dentistId = user?.dentist_profile?.id || 1;

  const [diagnosis, setDiagnosis] = useState('');
  const [generalInstructions, setGeneralInstructions] = useState(
    'Complete the entire medication course. Maintain gentle oral hygiene and rinse after meals.'
  );
  const [catalog, setCatalog] = useState<MedicineCatalog[]>([]);
  const [items, setItems] = useState<MedItemRow[]>([
    {
      medicine_name: 'Amoxicillin 500mg',
      dosage: '500mg',
      frequency: '1-0-1 (Twice daily)',
      duration: '5 days',
      timing: 'After Food',
      instructions: 'Take with full glass of water',
    },
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      prescriptionsApi.getCatalog().then(setCatalog);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAddItem = () => {
    setItems([
      ...items,
      {
        medicine_name: catalog[0]?.name || 'Medicine',
        dosage: catalog[0]?.default_dosage || '500mg',
        frequency: '1-0-1 (Twice daily)',
        duration: '5 days',
        timing: 'After Food',
      },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, idx) => idx !== index));
  };

  const handleMedicineSelect = (index: number, medName: string) => {
    const selected = catalog.find((m) => m.name === medName);
    const updated = [...items];
    updated[index].medicine_name = medName;
    if (selected) {
      if (selected.default_dosage) updated[index].dosage = selected.default_dosage;
      if (selected.instructions) updated[index].instructions = selected.instructions;
    }
    setItems(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) {
      setError('Prescription must include at least one medication.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const rx = await prescriptionsApi.create({
        patient_id: patientId || 1,
        dentist_id: dentistId,
        diagnosis_summary: diagnosis,
        general_instructions: generalInstructions,
        items,
      });

      // Automatically download generated PDF
      await prescriptionsApi.downloadPdf(rx.id, rx.prescription_number);

      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to issue prescription');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 flex items-center justify-center font-bold">
              <FileSpreadsheet className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Issue Digital Prescription (℞)</h2>
              <p className="text-xs text-slate-500">Patient: {patientName} • PDF Auto-Generated</p>
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
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Diagnosis / Clinical Summary
            </label>
            <input
              type="text"
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="e.g. Acute periapical abscess, post-extraction pain management"
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          {/* Medicines Table */}
          <div className="pt-2">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
                Prescribed Medications ({items.length})
              </label>
              <button
                type="button"
                onClick={handleAddItem}
                className="text-xs text-teal-600 hover:text-teal-700 font-bold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Medication
              </button>
            </div>

            <div className="space-y-3">
              {items.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5"
                >
                  <div className="grid grid-cols-12 gap-3 items-center">
                    <div className="col-span-5">
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Medicine Name</label>
                      <input
                        type="text"
                        list={`med-list-${idx}`}
                        value={item.medicine_name}
                        onChange={(e) => handleMedicineSelect(idx, e.target.value)}
                        placeholder="Select or enter medicine..."
                        className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                      <datalist id={`med-list-${idx}`}>
                        {catalog.map((m) => (
                          <option key={m.id} value={m.name} />
                        ))}
                      </datalist>
                    </div>

                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Dosage</label>
                      <input
                        type="text"
                        value={item.dosage}
                        onChange={(e) => {
                          const updated = [...items];
                          updated[idx].dosage = e.target.value;
                          setItems(updated);
                        }}
                        placeholder="500mg"
                        className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>

                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Frequency</label>
                      <input
                        type="text"
                        value={item.frequency}
                        onChange={(e) => {
                          const updated = [...items];
                          updated[idx].frequency = e.target.value;
                          setItems(updated);
                        }}
                        placeholder="1-0-1"
                        className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>

                    <div className="col-span-2">
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Duration</label>
                      <input
                        type="text"
                        value={item.duration}
                        onChange={(e) => {
                          const updated = [...items];
                          updated[idx].duration = e.target.value;
                          setItems(updated);
                        }}
                        placeholder="5 days"
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

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Timing</label>
                      <select
                        value={item.timing}
                        onChange={(e) => {
                          const updated = [...items];
                          updated[idx].timing = e.target.value;
                          setItems(updated);
                        }}
                        className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                      >
                        <option value="After Food">After Food</option>
                        <option value="Before Food">Before Food</option>
                        <option value="With Food">With Food</option>
                        <option value="Before Bedtime">Before Bedtime</option>
                        <option value="As Needed (PRN)">As Needed (PRN)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Special Instructions</label>
                      <input
                        type="text"
                        value={item.instructions || ''}
                        onChange={(e) => {
                          const updated = [...items];
                          updated[idx].instructions = e.target.value;
                          setItems(updated);
                        }}
                        placeholder="e.g. Swish and spit, avoid direct sunlight..."
                        className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">General Patient Advice & Instructions</label>
            <textarea
              rows={2}
              value={generalInstructions}
              onChange={(e) => setGeneralInstructions(e.target.value)}
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
              className="px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              {isSubmitting ? 'Issuing & Generating PDF...' : 'Issue & Download PDF'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PrescriptionModal;
