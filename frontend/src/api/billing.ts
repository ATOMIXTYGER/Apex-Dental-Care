import { api } from './client';
import { Invoice, Payment } from '../types';

export const billingApi = {
  listInvoices: (params?: { patient_id?: number; status?: string }) => {
    return api.get<Invoice[]>('/billing/invoices', params);
  },

  getInvoiceById: (id: number) => {
    return api.get<Invoice>(`/billing/invoices/${id}`);
  },

  createInvoice: (data: any) => {
    return api.post<Invoice>('/billing/invoices', data);
  },

  recordPayment: (data: { invoice_id: number; amount: number; payment_method: string; transaction_reference?: string; notes?: string }) => {
    return api.post<Payment>('/billing/payments', data);
  },

  downloadPdf: async (id: number, invoiceNumber: string) => {
    const blob = await api.downloadBlob(`/billing/invoices/${id}/pdf`);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Invoice_${invoiceNumber}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
