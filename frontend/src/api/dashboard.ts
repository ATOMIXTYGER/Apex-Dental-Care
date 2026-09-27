import { api } from './client';
import { DashboardSummary, DashboardAnalytics } from '../types';

export const dashboardApi = {
  getSummary: (period: 'today' | '7d' | '30d' = '30d') => {
    return api.get<DashboardSummary>('/dashboard/summary', { period });
  },

  getAnalytics: (days = 30) => {
    return api.get<DashboardAnalytics>('/dashboard/analytics', { days });
  },
};
