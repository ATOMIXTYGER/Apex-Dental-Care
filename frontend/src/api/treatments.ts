import { api } from './client';
import { TreatmentPlan, TreatmentItem, ProcedureCatalog } from '../types';

export const treatmentsApi = {
  getCatalog: () => {
    return api.get<ProcedureCatalog[]>('/treatments/catalog');
  },

  listPlans: (params?: { patient_id?: number; dentist_id?: number; status?: string }) => {
    return api.get<TreatmentPlan[]>('/treatments/plans', params);
  },

  getPlanById: (id: number) => {
    return api.get<TreatmentPlan>(`/treatments/plans/${id}`);
  },

  createPlan: (data: any) => {
    return api.post<TreatmentPlan>('/treatments/plans', data);
  },

  addItem: (planId: number, data: any) => {
    return api.post<TreatmentItem>(`/treatments/plans/${planId}/items`, data);
  },

  updateItem: (itemId: number, data: any) => {
    return api.put<TreatmentItem>(`/treatments/items/${itemId}`, data);
  },
};
