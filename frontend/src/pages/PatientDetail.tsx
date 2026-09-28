import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
  AlertTriangle,
  Stethoscope,
  Activity,
  FileSpreadsheet,
  Receipt,
  FolderOpen,
  Clock,
  Edit,
  Download,
  Plus,
  ArrowLeft,
  CheckCircle2,
  IndianRupee
} from 'lucide-react';
import { formatINR, formatDateIN, formatDateTimeIN } from '../utils/formatters';
import {
  Patient,
  DentalChartDetail,
  Visit,
  TreatmentPlan,
  Prescription,
  Invoice,
  DocumentItem,
  FollowUp,
  Appointment,
  ToothConditionType
} from '../types';
import { patientsApi } from '../api/patients';
import { dentalChartApi } from '../api/dentalChart';
import { clinicalApi } from '../api/clinical';
import { treatmentsApi } from '../api/treatments';
import { prescriptionsApi } from '../api/prescriptions';
import { billingApi } from '../api/billing';
import { documentsApi } from '../api/documents';
import { followupsApi } from '../api/followups';
import { appointmentsApi } from '../api/appointments';

// Components
import { FDIToothChart } from '../components/dental/FDIToothChart';
import { ToothModal } from '../components/dental/ToothModal';
import { VisitModal } from '../components/clinical/VisitModal';
import { TreatmentPlanModal } from '../components/treatments/TreatmentPlanModal';
import { PrescriptionModal } from '../components/prescriptions/PrescriptionModal';
import { InvoiceModal } from '../components/billing/InvoiceModal';
import { PaymentModal } from '../components/billing/PaymentModal';
import { DocumentUploadModal } from '../components/documents/DocumentUploadModal';
import { FollowUpModal } from '../components/followups/FollowUpModal';
import { AppointmentModal } from '../components/appointments/AppointmentModal';
import { PatientFormModal } from '../components/patients/PatientFormModal';
import { useAuth } from '../context/AuthContext';

export const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const patientId = Number(id);
  const navigate = useNavigate();
  const { hasRole } = useAuth();

  const [patient, setPatient] = useState<Patient | null>(null);
  const [chartData, setChartData] = useState<DentalChartDetail | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [plans, setPlans] = useState<TreatmentPlan[]>([]);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [followups, setFollowups] = useState<FollowUp[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState<
    'chart' | 'visits' | 'treatments' | 'prescriptions' | 'billing' | 'documents' | 'appointments' | 'followups' | 'history' | 'timeline'
  >('chart');

  // Modals state
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);
  const [isVisitModalOpen, setIsVisitModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [isRxModalOpen, setIsRxModalOpen] = useState(false);
  const [isInvoiceModalOpen, setIsInvoiceModalOpen] = useState(false);
  const [paymentInvoice, setPaymentInvoice] = useState<Invoice | null>(null);
  const [isDocModalOpen, setIsDocModalOpen] = useState(false);
  const [isFollowupModalOpen, setIsFollowupModalOpen] = useState(false);
  const [isApptModalOpen, setIsApptModalOpen] = useState(false);
  const [isEditPatientOpen, setIsEditPatientOpen] = useState(false);

  const [isLoading, setIsLoading] = useState(true);

  const loadPatientData = async () => {
    if (!patientId) return;
    setIsLoading(true);
    try {
      const [
        patRes,
        chartRes,
        visRes,
        planRes,
        rxRes,
        invRes,
        docRes,
        fuRes,
        apptRes,
        tlRes,
      ] = await Promise.all([
        patientsApi.getById(patientId),
        dentalChartApi.getChart(patientId),
        clinicalApi.getPatientVisits(patientId),
        treatmentsApi.listPlans({ patient_id: patientId }),
        prescriptionsApi.list({ patient_id: patientId }),
        billingApi.listInvoices({ patient_id: patientId }),
        documentsApi.getPatientDocuments(patientId),
        followupsApi.list({ patient_id: patientId }),
        appointmentsApi.list({ patient_id: patientId }),
        patientsApi.getTimeline(patientId),
      ]);

      setPatient(patRes);
      setChartData(chartRes);
      setVisits(visRes);
      setPlans(planRes);
      setPrescriptions(rxRes);
      setInvoices(invRes);
      setDocuments(docRes);
      setFollowups(fuRes);
      setAppointments(apptRes);
      setTimeline(tlRes);
    } catch {
      // Handled by global interceptor
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPatientData();
  }, [patientId]);

  if (isLoading && !patient) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-400">
        Loading complete clinical records...
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="p-8 text-center text-slate-500">
        Patient record not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Patient Identity Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <button
              onClick={() => navigate('/patients')}
              className="p-2 border border-slate-200 hover:bg-slate-100 rounded-xl text-slate-500 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>

            <div className="w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-700 flex items-center justify-center font-extrabold text-xl shadow-inner">
              {patient.first_name[0]}
              {patient.last_name[0]}
            </div>

            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
                  {patient.first_name} {patient.last_name}
                </h1>
                <span className="font-mono text-xs font-bold text-teal-700 bg-teal-50 border border-teal-200 px-2.5 py-0.5 rounded-md">
                  {patient.patient_code}
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                  {patient.gender}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  {patient.phone}
                </span>
                {patient.email && (
                  <span className="flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    {patient.email}
                  </span>
                )}
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  DOB: {formatDateIN(patient.date_of_birth)}
                </span>
                {patient.blood_group && (
                  <span className="px-1.5 py-0.5 bg-rose-50 text-rose-700 font-bold rounded border border-rose-200 text-[10px]">
                    Blood Group: {patient.blood_group}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setIsEditPatientOpen(true)}
              className="px-3 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Edit className="w-3.5 h-3.5" />
              <span>Edit Details</span>
            </button>

            <button
              onClick={() => setIsApptModalOpen(true)}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Book Appointment</span>
            </button>

            {hasRole('dentist', 'admin') && (
              <button
                onClick={() => setIsVisitModalOpen(true)}
                className="px-3 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
              >
                <Stethoscope className="w-3.5 h-3.5" />
                <span>New Examination</span>
              </button>
            )}
          </div>
        </div>

        {/* Medical Allergy Banner if present */}
        {patient.medical_history?.allergies && patient.medical_history.allergies.toLowerCase() !== 'none' && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-2 text-xs font-bold text-red-700">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>MEDICAL ALERT - ALLERGIES: {patient.medical_history.allergies}</span>
          </div>
        )}
      </div>

      {/* Module Navigation Tabs */}
      <div className="flex border-b border-slate-200 gap-1 overflow-x-auto text-xs font-semibold">
        {[
          { id: 'chart', label: 'FDI Dental Chart', count: 32 },
          { id: 'visits', label: 'Examinations & Visits', count: visits.length },
          { id: 'treatments', label: 'Treatment Plans', count: plans.length },
          { id: 'prescriptions', label: 'Prescriptions', count: prescriptions.length },
          { id: 'billing', label: 'Billing & Invoices', count: invoices.length },
          { id: 'documents', label: 'X-Rays & Documents', count: documents.length },
          { id: 'appointments', label: 'Appointments', count: appointments.length },
          { id: 'followups', label: 'Follow-ups', count: followups.length },
          { id: 'history', label: 'Medical/Dental History' },
          { id: 'timeline', label: 'Event Timeline', count: timeline.length },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`py-3 px-4 rounded-t-xl transition-all whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === tab.id
                ? 'bg-white border-x border-t border-slate-200 text-teal-700 font-bold shadow-sm'
                : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100/50'
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                  activeTab === tab.id ? 'bg-teal-100 text-teal-800' : 'bg-slate-200 text-slate-600'
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab 1: FDI DENTAL CHART */}
      {activeTab === 'chart' && (
        <div className="space-y-6">
          <FDIToothChart
            teeth={chartData?.teeth || {}}
            selectedTooth={selectedTooth}
            onSelectTooth={(tNum) => setSelectedTooth(tNum)}
          />

          {/* Quick instructions */}
          <div className="p-4 bg-teal-50/60 border border-teal-100 rounded-2xl flex items-center justify-between text-xs text-teal-900">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-teal-600 flex-shrink-0" />
              <span>
                Click any tooth on the upper or lower arch above to view detailed clinical findings or update conditions (caries, filled, crown, root canal, missing).
              </span>
            </div>
            {selectedTooth && (
              <span className="font-bold text-teal-700 bg-white px-2 py-1 rounded-md border border-teal-200">
                Selected: Tooth {selectedTooth}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: CLINICAL EXAMINATIONS & VISITS */}
      {activeTab === 'visits' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Historical Clinical Visits & Diagnostic Examinations</h2>
            {hasRole('dentist', 'admin') && (
              <button
                onClick={() => setIsVisitModalOpen(true)}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Record New Examination
              </button>
            )}
          </div>

          {visits.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No clinical visits recorded yet.
            </div>
          ) : (
            <div className="space-y-4">
              {visits.map((v) => (
                <div key={v.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                    <div>
                      <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                        Visit Date: {formatDateIN(v.visit_date)}
                      </span>
                      <h3 className="text-sm font-bold text-slate-900 mt-1">
                        Diagnosis: {v.diagnosis || 'General Examination'}
                      </h3>
                      <p className="text-xs text-slate-500">Attending Doctor: {v.dentist_name || 'Dr. In-Charge'}</p>
                    </div>

                    <div className="flex gap-4 text-xs font-medium text-slate-600">
                      {v.vitals_blood_pressure && (
                        <span>BP: <b>{v.vitals_blood_pressure} {v.vitals_blood_pressure.includes('mmHg') ? '' : 'mmHg'}</b></span>
                      )}
                      {v.vitals_pulse && (
                        <span>Pulse: <b>{v.vitals_pulse} bpm</b></span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div>
                      <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Chief Complaint</p>
                      <p className="text-slate-800 mt-0.5">{v.chief_complaint || 'None reported'}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Oral Findings</p>
                      <p className="text-slate-800 mt-0.5">{v.oral_findings || 'Normal oral cavity'}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Periodontal / Gum Condition</p>
                      <p className="text-slate-800 mt-0.5">{v.gum_condition || 'Healthy'}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Hygiene Index</p>
                      <p className="text-slate-800 mt-0.5">{v.hygiene_index || 'Good'}</p>
                    </div>
                  </div>

                  {v.clinical_notes && (
                    <div className="pt-2 border-t border-slate-100 text-xs">
                      <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Clinical Notes & Operative Record</p>
                      <p className="text-slate-700 mt-0.5 italic">{v.clinical_notes}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: TREATMENT PLANS */}
      {activeTab === 'treatments' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Comprehensive Treatment Plans</h2>
            {hasRole('dentist', 'admin') && (
              <button
                onClick={() => setIsPlanModalOpen(true)}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> New Treatment Plan
              </button>
            )}
          </div>

          {plans.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No treatment plans active for this patient.
            </div>
          ) : (
            <div className="space-y-4">
              {plans.map((p) => (
                <div key={p.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-slate-900">{p.title}</h3>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-teal-100 text-teal-800">
                          {p.status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Supervising Doctor: {p.dentist_name || 'Dr. In-Charge'} • Created {formatDateIN(p.created_at)}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Total Estimated</p>
                      <p className="text-base font-extrabold text-teal-700">{formatINR(p.estimated_total)}</p>
                    </div>
                  </div>

                  {/* Procedures Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px]">
                        <tr>
                          <th className="py-2 px-4">Procedure</th>
                          <th className="py-2 px-4">Tooth #</th>
                          <th className="py-2 px-4">Status</th>
                          <th className="py-2 px-4 text-right">Cost (₹)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {p.treatments.map((t) => (
                          <tr key={t.id}>
                            <td className="py-2.5 px-4 font-semibold text-slate-800">{t.procedure_name}</td>
                            <td className="py-2.5 px-4">{t.tooth_number ? `Tooth #${t.tooth_number}` : 'Full Arch / General'}</td>
                            <td className="py-2.5 px-4">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                  t.status === 'completed'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : t.status === 'in_progress'
                                    ? 'bg-amber-100 text-amber-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {t.status}
                              </span>
                            </td>
                            <td className="py-2.5 px-4 text-right font-mono font-bold">
                              {formatINR(t.estimated_cost)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: PRESCRIPTIONS */}
      {activeTab === 'prescriptions' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Issued Prescriptions (℞)</h2>
            {hasRole('dentist', 'admin') && (
              <button
                onClick={() => setIsRxModalOpen(true)}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Write Prescription
              </button>
            )}
          </div>

          {prescriptions.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No prescriptions issued for this patient.
            </div>
          ) : (
            <div className="space-y-4">
              {prescriptions.map((rx) => (
                <div key={rx.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                          {rx.prescription_number}
                        </span>
                        <h3 className="text-sm font-bold text-slate-900">{rx.diagnosis_summary || 'Prescription'}</h3>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Doctor: {rx.dentist_name || 'Dr. In-Charge'} • Issued {new Date(rx.created_at).toLocaleDateString()}
                      </p>
                    </div>

                    <button
                      onClick={() => prescriptionsApi.downloadPdf(rx.id, rx.prescription_number)}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-teal-50 text-teal-700 border border-slate-200 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download PDF</span>
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px]">
                        <tr>
                          <th className="py-2 px-4">Medicine</th>
                          <th className="py-2 px-4">Dosage</th>
                          <th className="py-2 px-4">Frequency</th>
                          <th className="py-2 px-4">Duration</th>
                          <th className="py-2 px-4">Instructions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {rx.items.map((item, idx) => (
                          <tr key={idx}>
                            <td className="py-2.5 px-4 font-bold text-slate-800">{item.medicine_name}</td>
                            <td className="py-2.5 px-4">{item.dosage}</td>
                            <td className="py-2.5 px-4">{item.frequency}</td>
                            <td className="py-2.5 px-4">{item.duration}</td>
                            <td className="py-2.5 px-4 text-slate-600">{item.timing} {item.instructions && ` - ${item.instructions}`}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {rx.general_instructions && (
                    <p className="text-xs text-slate-600 italic bg-slate-50 p-3 rounded-xl border border-slate-100">
                      <b>General Advice:</b> {rx.general_instructions}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: BILLING & INVOICES */}
      {activeTab === 'billing' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Invoices & Payment Transactions</h2>
            {hasRole('admin', 'receptionist') && (
              <button
                onClick={() => setIsInvoiceModalOpen(true)}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Create Invoice
              </button>
            )}
          </div>

          {invoices.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No invoices generated for this patient yet.
            </div>
          ) : (
            <div className="space-y-4">
              {invoices.map((inv) => (
                <div key={inv.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                          {inv.invoice_number}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            inv.status === 'paid'
                              ? 'bg-emerald-100 text-emerald-800'
                              : inv.status === 'partially_paid'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {inv.status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Issued: {formatDateIN(inv.issue_date)} • Due: {formatDateIN(inv.due_date)}
                      </p>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-xs text-slate-400 uppercase font-semibold text-[10px]">Balance Due</p>
                        <p className="text-sm font-extrabold text-rose-600">{formatINR(inv.balance)}</p>
                      </div>

                      {hasRole('admin', 'receptionist') && Number(inv.balance) > 0 && (
                        <button
                          onClick={() => setPaymentInvoice(inv)}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                        >
                          <IndianRupee className="w-3.5 h-3.5" />
                          <span>Record Payment</span>
                        </button>
                      )}

                      <button
                        onClick={() => billingApi.downloadPdf(inv.id, inv.invoice_number)}
                        className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>PDF</span>
                      </button>
                    </div>
                  </div>

                  {/* Items breakdown */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px]">
                        <tr>
                          <th className="py-2 px-4">Item Description</th>
                          <th className="py-2 px-4">Unit Price</th>
                          <th className="py-2 px-4">Qty</th>
                          <th className="py-2 px-4 text-right">Total (₹)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {inv.items.map((i) => (
                          <tr key={i.id}>
                            <td className="py-2 px-4 font-medium text-slate-800">{i.description}</td>
                            <td className="py-2 px-4">{formatINR(i.unit_price)}</td>
                            <td className="py-2 px-4">{i.quantity}</td>
                            <td className="py-2 px-4 text-right font-mono font-bold">{formatINR(i.total)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Payment transactions history */}
                  {inv.payments && inv.payments.length > 0 && (
                    <div className="pt-2 border-t border-slate-100">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                        Recorded Payments ({inv.payments.length})
                      </p>
                      <div className="space-y-1.5">
                        {inv.payments.map((pay) => (
                          <div
                            key={pay.id}
                            className="flex items-center justify-between text-xs p-2 bg-slate-50 rounded-lg border border-slate-100"
                          >
                            <span className="text-slate-600 font-medium">
                              {formatDateIN(pay.payment_date)} • {pay.payment_method.toUpperCase()}
                              {pay.transaction_reference && ` (${pay.transaction_reference})`}
                            </span>
                            <span className="font-bold text-emerald-600">+{formatINR(pay.amount)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 6: DOCUMENTS & X-RAYS */}
      {activeTab === 'documents' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Diagnostic Radiographs & Clinical Files</h2>
            <button
              onClick={() => setIsDocModalOpen(true)}
              className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Upload File / X-Ray
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              No documents or X-rays uploaded for this patient.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                      <span className="font-bold uppercase tracking-wider text-[10px] text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                        {doc.document_type}
                      </span>
                      <span>{(doc.file_size / 1024).toFixed(0)} KB</span>
                    </div>
                    <p className="text-xs font-bold text-slate-900 truncate mt-1" title={doc.original_file_name}>
                      {doc.original_file_name}
                    </p>
                    {doc.notes && <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">{doc.notes}</p>}
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-[10px] text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                    <button
                      onClick={() => documentsApi.download(doc.id, doc.original_file_name)}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-teal-50 text-teal-700 rounded-lg font-semibold flex items-center gap-1 transition-colors"
                    >
                      <Download className="w-3 h-3" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 7: APPOINTMENTS */}
      {activeTab === 'appointments' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Appointment History</h2>
            <button
              onClick={() => setIsApptModalOpen(true)}
              className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Book Appointment
            </button>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-6">Date</th>
                  <th className="py-3 px-6">Time</th>
                  <th className="py-3 px-6">Dentist</th>
                  <th className="py-3 px-6">Type / Reason</th>
                  <th className="py-3 px-6 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {appointments.map((a) => (
                  <tr key={a.id}>
                    <td className="py-3 px-6 font-semibold text-slate-800">{a.appointment_date}</td>
                    <td className="py-3 px-6">{a.start_time.slice(0, 5)} - {a.end_time.slice(0, 5)}</td>
                    <td className="py-3 px-6">{a.dentist_name || 'Dr. In-Charge'}</td>
                    <td className="py-3 px-6">{a.reason || a.appointment_type_name || 'Routine Consultation'}</td>
                    <td className="py-3 px-6 text-right">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          a.status === 'completed'
                            ? 'bg-emerald-100 text-emerald-800'
                            : a.status === 'confirmed'
                            ? 'bg-cyan-100 text-cyan-800'
                            : a.status === 'cancelled'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 8: FOLLOW-UPS */}
      {activeTab === 'followups' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800">Scheduled Clinical Follow-ups</h2>
            <button
              onClick={() => setIsFollowupModalOpen(true)}
              className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Schedule Follow-up
            </button>
          </div>

          <div className="space-y-3">
            {followups.map((fu) => (
              <div
                key={fu.id}
                className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{fu.reason}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        fu.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : fu.status === 'cancelled'
                          ? 'bg-slate-100 text-slate-600'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {fu.status}
                    </span>
                  </div>
                  <p className="text-slate-500 mt-0.5">
                    Target Date: <b>{fu.scheduled_date}</b> • Dentist: {fu.dentist_name || 'Dr. In-Charge'}
                  </p>
                  {fu.notes && <p className="text-slate-600 mt-1 italic">{fu.notes}</p>}
                </div>

                {fu.status === 'pending' && (
                  <button
                    onClick={async () => {
                      await followupsApi.update(fu.id, { status: 'completed' });
                      loadPatientData();
                    }}
                    className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-lg font-semibold transition-colors"
                  >
                    Mark Done
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 9: MEDICAL & DENTAL HISTORY */}
      {activeTab === 'history' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Medical History */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <span>Medical History & Systemic Conditions</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Allergies:</span>
                <p className="text-slate-800 font-bold mt-0.5">
                  {patient.medical_history?.allergies || 'No known drug allergies'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Systemic Conditions:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.medical_history?.medical_conditions || 'None declared'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Current Medications:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.medical_history?.current_medications || 'None declared'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Bleeding / Anticoagulants:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.medical_history?.bleeding_disorders ? 'Positive (Patient on blood thinners)' : 'None'}
                </p>
              </div>
            </div>
          </div>

          {/* Dental History */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-teal-600" />
              <span>Dental Habits & Anamnesis</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Chief Complaint:</span>
                <p className="text-slate-800 font-bold mt-0.5">
                  {patient.dental_history?.chief_complaint || 'None'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Brushing Frequency:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.dental_history?.brushing_frequency || 'Twice daily'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Dental Anxiety Level:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.dental_history?.dental_anxiety_level || 'None'}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">Oral Habits:</span>
                <p className="text-slate-800 font-medium mt-0.5">
                  {patient.dental_history?.habits || 'None'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 10: CHRONOLOGICAL TIMELINE */}
      {activeTab === 'timeline' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <h2 className="text-sm font-bold text-slate-800">Unified Clinical History & Event Feed</h2>

          <div className="relative pl-6 border-l-2 border-slate-200 space-y-6">
            {timeline.map((event, idx) => (
              <div key={idx} className="relative group">
                {/* Dot */}
                <div className="absolute -left-[31px] top-0 w-3.5 h-3.5 rounded-full bg-teal-500 ring-4 ring-white" />

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-teal-200 transition-colors">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900">{event.title}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{event.date}</span>
                  </div>
                  {event.status && (
                    <span className="inline-block mt-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                      Status: {event.status}
                    </span>
                  )}
                  {event.notes && <p className="text-xs text-slate-600 mt-2">{event.notes}</p>}
                  {event.dentist && <p className="text-[10px] text-slate-400 mt-1">Doctor: {event.dentist}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tooth Modal */}
      {selectedTooth && chartData && (
        <ToothModal
          toothNumber={selectedTooth}
          conditionData={chartData.teeth[selectedTooth]}
          history={chartData.history}
          isOpen={!!selectedTooth}
          onClose={() => setSelectedTooth(null)}
          onUpdateCondition={async (data) => {
            await dentalChartApi.updateTooth(patientId, data as any);
            const freshChart = await dentalChartApi.getChart(patientId);
            setChartData(freshChart);
          }}
        />
      )}

      {/* Visit Modal */}
      {isVisitModalOpen && (
        <VisitModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isVisitModalOpen}
          onClose={() => setIsVisitModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Treatment Plan Modal */}
      {isPlanModalOpen && (
        <TreatmentPlanModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isPlanModalOpen}
          onClose={() => setIsPlanModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Prescription Modal */}
      {isRxModalOpen && (
        <PrescriptionModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isRxModalOpen}
          onClose={() => setIsRxModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Invoice Modal */}
      {isInvoiceModalOpen && (
        <InvoiceModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isInvoiceModalOpen}
          onClose={() => setIsInvoiceModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Payment Modal */}
      {paymentInvoice && (
        <PaymentModal
          invoice={paymentInvoice}
          isOpen={!!paymentInvoice}
          onClose={() => setPaymentInvoice(null)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Document Upload Modal */}
      {isDocModalOpen && (
        <DocumentUploadModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isDocModalOpen}
          onClose={() => setIsDocModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Follow-up Modal */}
      {isFollowupModalOpen && (
        <FollowUpModal
          patientId={patientId}
          patientName={`${patient.first_name} ${patient.last_name}`}
          isOpen={isFollowupModalOpen}
          onClose={() => setIsFollowupModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Appointment Modal */}
      {isApptModalOpen && (
        <AppointmentModal
          isOpen={isApptModalOpen}
          defaultPatientId={patientId}
          onClose={() => setIsApptModalOpen(false)}
          onSuccess={loadPatientData}
        />
      )}

      {/* Edit Patient Modal */}
      {isEditPatientOpen && (
        <PatientFormModal
          isOpen={isEditPatientOpen}
          initialData={patient}
          onClose={() => setIsEditPatientOpen(false)}
          onSubmit={async (payload) => {
            await patientsApi.update(patientId, payload);
            setIsEditPatientOpen(false);
            loadPatientData();
          }}
        />
      )}
    </div>
  );
};

export default PatientDetail;
