import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Pill, 
  Plus, 
  Search, 
  Download, 
  FileText, 
  Calendar, 
  User as UserIcon, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  Info,
  ShieldAlert,
  BookOpen
} from 'lucide-react';
import { prescriptionsApi } from '../api/prescriptions';
import { useAuth } from '../context/AuthContext';
import PrescriptionModal from '../components/prescriptions/PrescriptionModal';
import { Prescription, MedicineCatalog } from '../types';

export default function Prescriptions() {
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<'prescriptions' | 'formulary'>('prescriptions');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedRxId, setExpandedRxId] = useState<number | null>(null);
  const [isRxModalOpen, setIsRxModalOpen] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  // Fetch Prescriptions
  const { data: prescriptions = [], isLoading: isRxLoading } = useQuery({
    queryKey: ['prescriptions'],
    queryFn: () => prescriptionsApi.list(),
  });

  // Fetch Medicine Catalog
  const { data: formulary = [], isLoading: isFormularyLoading } = useQuery({
    queryKey: ['medicineCatalog'],
    queryFn: prescriptionsApi.getCatalog,
  });

  const handleDownloadPdf = async (rx: Prescription, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setDownloadingId(rx.id);
      await prescriptionsApi.downloadPdf(rx.id, rx.prescription_number);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Could not download prescription PDF.');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredRx = prescriptions.filter((rx) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const rxNum = (rx.prescription_number || '').toLowerCase();
    const patient = (rx.patient_name || '').toLowerCase();
    const dentist = (rx.dentist_name || '').toLowerCase();
    return rxNum.includes(q) || patient.includes(q) || dentist.includes(q);
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Prescriptions & Formulary</h1>
          <p className="text-sm text-slate-500 mt-1">Generate dental prescriptions, print signed official PDFs, and reference medication guidelines.</p>
        </div>
        {(user?.role === 'dentist' || user?.role === 'admin') && (
          <button
            onClick={() => setIsRxModalOpen(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4 mr-2" />
            Write Prescription
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('prescriptions')}
          className={`py-3 px-6 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'prescriptions'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          Issued Prescriptions ({prescriptions.length})
        </button>
        <button
          onClick={() => setActiveTab('formulary')}
          className={`py-3 px-6 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'formulary'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Medication Formulary ({formulary.length})
        </button>
      </div>

      {activeTab === 'prescriptions' && (
        <div className="space-y-4">
          {/* Search bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search by Rx #, patient or dentist..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-72"
              />
            </div>
            <div className="text-xs text-slate-500 font-medium">
              Showing {filteredRx.length} prescriptions
            </div>
          </div>

          {/* Prescriptions List */}
          {isRxLoading ? (
            <div className="py-16 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
              <p className="text-sm text-slate-500 mt-3 font-medium">Loading prescriptions...</p>
            </div>
          ) : filteredRx.length === 0 ? (
            <div className="bg-white py-16 text-center rounded-xl border border-slate-200">
              <Pill className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <p className="text-base font-semibold text-slate-700">No prescriptions found</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                No issued prescriptions match the current search criteria.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredRx.map((rx) => {
                const isExpanded = expandedRxId === rx.id;
                const itemsCount = rx.items?.length || 0;

                return (
                  <div key={rx.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all">
                    {/* Header Item */}
                    <div
                      onClick={() => setExpandedRxId(isExpanded ? null : rx.id)}
                      className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer hover:bg-slate-50/60"
                    >
                      <div className="flex items-start space-x-4">
                        <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl mt-1">
                          <Pill className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-slate-900 text-sm">{rx.prescription_number}</span>
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                              {itemsCount} {itemsCount === 1 ? 'Medication' : 'Medications'}
                            </span>
                          </div>
                          <div className="text-xs text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                            <span className="flex items-center">
                              <UserIcon className="w-3.5 h-3.5 mr-1 text-slate-400" />
                              Patient: <Link to={`/patients/${rx.patient_id}`} onClick={(e) => e.stopPropagation()} className="ml-1 text-blue-600 hover:underline font-medium">{rx.patient_name || `Patient #${rx.patient_id}`}</Link>
                            </span>
                            {rx.dentist_name && (
                              <span>Prescribing Doctor: <strong className="text-slate-700">{rx.dentist_name}</strong></span>
                            )}
                            <span className="flex items-center">
                              <Calendar className="w-3.5 h-3.5 mr-1 text-slate-400" />
                              Date: {new Date(rx.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          {rx.general_instructions && (
                            <p className="text-xs text-slate-600 mt-2 bg-slate-50 p-2 rounded border border-slate-100 italic">
                              "{rx.general_instructions}"
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Right PDF Download button */}
                      <div className="flex items-center justify-between md:justify-end gap-3 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                        <button
                          onClick={(e) => handleDownloadPdf(rx, e)}
                          disabled={downloadingId === rx.id}
                          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition disabled:opacity-50"
                        >
                          <Download className="w-3.5 h-3.5 mr-1.5" />
                          {downloadingId === rx.id ? 'Generating...' : 'Download PDF'}
                        </button>
                        <div className="text-slate-400 p-1">
                          {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </div>
                      </div>
                    </div>

                    {/* Expanded Medicine Details */}
                    {isExpanded && (
                      <div className="border-t border-slate-200 bg-slate-50/50 p-4 sm:p-5">
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5">
                          Prescribed Medication Details
                        </h4>
                        <div className="overflow-x-auto bg-white rounded-lg border border-slate-200">
                          <table className="w-full text-left text-xs">
                            <thead>
                              <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-600">
                                <th className="py-2.5 px-3">Medicine Name</th>
                                <th className="py-2.5 px-3">Dosage</th>
                                <th className="py-2.5 px-3">Frequency</th>
                                <th className="py-2.5 px-3">Duration</th>
                                <th className="py-2.5 px-3">Special Instructions</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {rx.items?.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-50/60">
                                  <td className="py-2.5 px-3 font-semibold text-slate-900">{item.medicine_name}</td>
                                  <td className="py-2.5 px-3 text-slate-700">{item.dosage}</td>
                                  <td className="py-2.5 px-3 text-slate-700">{item.frequency}</td>
                                  <td className="py-2.5 px-3 text-slate-700">{item.duration}</td>
                                  <td className="py-2.5 px-3 text-slate-500 italic">{item.instructions || 'As directed'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Formulary Tab */}
      {activeTab === 'formulary' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Approved Dental Pharmacy Formulary</h3>
              <p className="text-xs text-slate-500 mt-0.5">Standard dental analgesics, antibiotics, antiseptics, and local therapeutics.</p>
            </div>
            <span className="text-xs text-slate-500 font-medium">{formulary.length} drugs listed</span>
          </div>

          {isFormularyLoading ? (
            <div className="py-12 text-center">
              <div className="inline-block animate-spin rounded-full h-7 w-7 border-4 border-blue-600 border-t-transparent"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    <th className="py-3 px-4">Name / Generic</th>
                    <th className="py-3 px-4">Form</th>
                    <th className="py-3 px-4">Default Dosage</th>
                    <th className="py-3 px-4">Standard Instructions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs">
                  {formulary.map((drug) => (
                    <tr key={drug.id} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-900">{drug.name}</div>
                        {drug.generic_name && (
                          <div className="text-slate-500 font-mono text-[11px]">{drug.generic_name}</div>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 capitalize">
                          {drug.dosage_form}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-medium text-slate-800">{drug.default_dosage || '-'}</td>
                      <td className="py-3 px-4 text-slate-500 max-w-sm truncate">{drug.instructions || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Prescription Creation Modal */}
      {isRxModalOpen && (
        <PrescriptionModal
          isOpen={isRxModalOpen}
          onClose={() => setIsRxModalOpen(false)}
        />
      )}
    </div>
  );
}
