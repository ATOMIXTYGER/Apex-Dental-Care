import { api } from './client';
import { Patient, PaginatedResult } from '../types';

export const patientsApi = {
  list: (page = 1, pageSize = 20, search?: string) => {
    return api.get<PaginatedResult<Patient>>('/patients', { page, page_size: pageSize, search });
  },

  getById: (id: number) => {
    return api.get<Patient>(`/patients/${id}`);
  },

  create: (data: Partial<Patient>) => {
    return api.post<Patient>('/patients', data);
  },

  update: (id: number, data: Partial<Patient>) => {
    return api.put<Patient>(`/patients/${id}`, data);
  },

  delete: (id: number) => {
    return api.delete<{ message: string }>(`/patients/${id}`);
  },

  getTimeline: (id: number) => {
    return api.get<any[]>(`/patients/${id}/timeline`);
  },
};
