export type Role = 'admin' | 'dentist' | 'receptionist' | 'patient';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: Role;
  phone?: string;
  is_active: boolean;
  created_at: string;
  dentist_profile?: DentistProfile;
}

export interface DentistProfile {
  id: number;
  user_id?: number;
  license_number: string;
  specialization: string;
  qualifications?: string;
  cabin_number?: string;
  is_active?: boolean;
}

export interface MedicalHistory {
  id?: number;
  patient_id?: number;
  allergies?: string;
  medical_conditions?: string;
  current_medications?: string;
  past_surgeries?: string;
  bleeding_disorders: boolean;
  is_pregnant: boolean;
  notes?: string;
  updated_at?: string;
}

export interface DentalHistory {
  id?: number;
  patient_id?: number;
  chief_complaint?: string;
  past_dental_treatments?: string;
  brushing_frequency?: string;
  flossing: boolean;
  habits?: string;
  dental_anxiety_level?: string;
  notes?: string;
  updated_at?: string;
}

export interface Patient {
  id: number;
  patient_code: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'Male' | 'Female' | 'Other';
  phone: string;
  email?: string;
  address?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  blood_group?: string;
  created_at: string;
  updated_at?: string;
  medical_history?: MedicalHistory;
  dental_history?: DentalHistory;
}

export interface AppointmentType {
  id: number;
  name: string;
  duration_minutes: number;
  color_code: string;
  default_fee: number;
}

export type AppointmentStatus = 'scheduled' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';

export interface Appointment {
  id: number;
  patient_id: number;
  dentist_id: number;
  appointment_type_id?: number;
  appointment_date: string;
  start_time: string;
  end_time: string;
  status: AppointmentStatus;
  reason?: string;
  cancellation_reason?: string;
  notes?: string;
  created_at: string;
  patient_name?: string;
  patient_code?: string;
  dentist_name?: string;
  appointment_type_name?: string;
  patient?: any;
  dentist?: any;
  appointment_type?: any;
}

export interface Visit {
  id: number;
  patient_id: number;
  dentist_id: number;
  appointment_id?: number;
  visit_date: string;
  vitals_blood_pressure?: string;
  vitals_pulse?: number;
  chief_complaint?: string;
  oral_findings?: string;
  gum_condition?: string;
  hygiene_index?: string;
  diagnosis?: string;
  clinical_notes?: string;
  created_at: string;
  dentist_name?: string;
  patient_name?: string;
}

export type ToothConditionType = 
  | 'healthy'
  | 'caries'
  | 'missing'
  | 'filled'
  | 'crown'
  | 'root_canal'
  | 'extraction'
  | 'fracture'
  | 'sensitivity'
  | 'mobility'
  | 'bridge'
  | 'implant'
  | 'impacted'
  | 'other';

export interface ToothCondition {
  id: number;
  patient_id: number;
  tooth_number: number;
  current_condition: ToothConditionType;
  condition?: ToothConditionType;
  severity?: 'none' | 'mild' | 'moderate' | 'severe';
  surfaces?: string;
  notes?: string;
  updated_at: string;
}

export interface ToothHistory {
  id: number;
  patient_id: number;
  visit_id?: number;
  dentist_id: number;
  dentist_name?: string;
  tooth_number: number;
  condition: ToothConditionType;
  severity?: string;
  surfaces?: string;
  notes?: string;
  created_at: string;
}

export interface DentalChartDetail {
  patient_id: number;
  teeth: Record<number, ToothCondition>;
  history: ToothHistory[];
}

export interface ProcedureCatalog {
  id: number;
  code: string;
  name: string;
  category: string;
  default_cost: number;
  description?: string;
}

export type TreatmentStatus = 'planned' | 'in_progress' | 'completed' | 'cancelled';

export interface TreatmentItem {
  id: number;
  treatment_plan_id: number;
  procedure_name: string;
  tooth_number?: number;
  estimated_cost: number;
  actual_cost: number;
  status: TreatmentStatus;
  visit_id?: number;
  notes?: string;
  completed_at?: string;
  created_at: string;
}

export interface TreatmentPlan {
  id: number;
  patient_id: number;
  dentist_id: number;
  title: string;
  status: 'draft' | 'active' | 'completed' | 'cancelled';
  estimated_total: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  dentist_name?: string;
  patient_name?: string;
  treatments: TreatmentItem[];
}

export interface MedicineCatalog {
  id: number;
  name: string;
  generic_name?: string;
  dosage_form: string;
  default_dosage?: string;
  instructions?: string;
}

export interface PrescriptionItem {
  id?: number;
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  timing: string;
  instructions?: string;
}

export interface Prescription {
  id: number;
  prescription_number: string;
  patient_id: number;
  dentist_id: number;
  visit_id?: number;
  diagnosis_summary?: string;
  general_instructions?: string;
  created_at: string;
  dentist_name?: string;
  patient_name?: string;
  items: PrescriptionItem[];
}

export interface InvoiceItem {
  id?: number;
  description: string;
  unit_price: number;
  quantity: number;
  total: number;
}

export interface Payment {
  id: number;
  invoice_id: number;
  patient_id: number;
  amount: number;
  payment_method: 'cash' | 'card' | 'upi' | 'bank_transfer' | 'other';
  transaction_reference?: string;
  payment_date: string;
  notes?: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  patient_id: number;
  visit_id?: number;
  treatment_plan_id?: number;
  issue_date: string;
  due_date: string;
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  paid_amount: number;
  balance: number;
  status: 'unpaid' | 'partially_paid' | 'paid' | 'voided';
  notes?: string;
  created_at: string;
  patient_name?: string;
  items: InvoiceItem[];
  payments: Payment[];
}

export interface DocumentItem {
  id: number;
  patient_id: number;
  visit_id?: number;
  document_type: string;
  file_name: string;
  original_file_name: string;
  file_size: number;
  mime_type: string;
  notes?: string;
  created_at: string;
  patient_name?: string;
}

export interface FollowUp {
  id: number;
  patient_id: number;
  dentist_id: number;
  visit_id?: number;
  scheduled_date: string;
  reason: string;
  status: 'pending' | 'completed' | 'cancelled';
  notes?: string;
  created_at: string;
  patient_name?: string;
  dentist_name?: string;
}

export interface DashboardSummary {
  total_patients: number;
  new_patients_period: number;
  today_appointments: number;
  upcoming_appointments: number;
  pending_treatments: number;
  completed_treatments: number;
  total_revenue: number;
  outstanding_payments: number;
  followups_due: number;
}

export interface DashboardAnalytics {
  appointments_by_status: { status: string; count: number }[];
  treatments_by_procedure: { procedure_name: string; count: number }[];
  revenue_trend: { date: string; revenue: number; invoiced: number }[];
  patients_trend: { date: string; new_patients: number }[];
}

export interface AuditLogItem {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  entity_name?: string;
  entity_id?: string;
  details?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
