import { api } from './client';
import { FollowUp } from '../types';

export const followupsApi = {
  list: (params?: { patient_id?: number; dentist_id?: number; status?: string }) => {
    return api.get<FollowUp[]>('/followups', params);
  },

  create: (data: Partial<FollowUp>) => {
    return api.post<FollowUp>('/followups', data);
  },

  update: (id: number, data: Partial<FollowUp>) => {
    return api.put<FollowUp>(`/followups/${id}`, data);
  },
};
