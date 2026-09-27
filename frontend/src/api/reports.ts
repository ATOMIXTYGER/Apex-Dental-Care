import { api } from './client';

export const reportsApi = {
  getRevenue: (startDate?: string, endDate?: string) => {
    return api.get<any[]>('/reports/revenue', { start_date: startDate, end_date: endDate });
  },

  getOutstanding: () => {
    return api.get<any[]>('/reports/outstanding');
  },

  exportRevenueCsv: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const blob = await api.downloadBlob(`/reports/revenue/export-csv${query}`);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Revenue_Report_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
