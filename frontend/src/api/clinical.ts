import { api } from './client';
import { Visit } from '../types';

export const clinicalApi = {
  createVisit: (data: Partial<Visit>) => {
    return api.post<Visit>('/visits', data);
  },

  getVisitById: (id: number) => {
    return api.get<Visit>(`/visits/${id}`);
  },

  getPatientVisits: (patientId: number) => {
    return api.get<Visit[]>(`/visits/patient/${patientId}`);
  },

  updateVisit: (id: number, data: Partial<Visit>) => {
    return api.put<Visit>(`/visits/${id}`, data);
  },
};
