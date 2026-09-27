import { api } from './client';
import { Appointment, AppointmentType } from '../types';

export const appointmentsApi = {
  list: (params?: { appointment_date?: string; dentist_id?: number; patient_id?: number; status?: string }) => {
    return api.get<Appointment[]>('/appointments', params);
  },

  getTypes: () => {
    return api.get<AppointmentType[]>('/appointments/types');
  },

  getById: (id: number) => {
    return api.get<Appointment>(`/appointments/${id}`);
  },

  create: (data: Partial<Appointment>) => {
    return api.post<Appointment>('/appointments', data);
  },

  update: (id: number, data: Partial<Appointment>) => {
    return api.put<Appointment>(`/appointments/${id}`, data);
  },

  updateStatus: (id: number, status: string, cancellation_reason?: string) => {
    return api.patch<Appointment>(`/appointments/${id}/status`, { status, cancellation_reason });
  },
};
