import { api } from './client';
import { DentalChartDetail, ToothCondition, ToothHistory } from '../types';

export interface ToothUpdatePayload {
  tooth_number: number;
  condition: string;
  severity?: string;
  surfaces?: string;
  notes?: string;
  visit_id?: number;
}

export const dentalChartApi = {
  getChart: (patientId: number) => {
    return api.get<DentalChartDetail>(`/dental-chart/${patientId}`);
  },

  updateTooth: (patientId: number, data: ToothUpdatePayload) => {
    return api.post<ToothCondition>(`/dental-chart/${patientId}/tooth`, data);
  },

  getToothHistory: (patientId: number, toothNumber: number) => {
    return api.get<ToothHistory[]>(`/dental-chart/${patientId}/tooth/${toothNumber}/history`);
  },
};
