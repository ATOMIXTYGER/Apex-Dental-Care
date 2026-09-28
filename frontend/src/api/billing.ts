import { api } from './client';
import { Invoice, Payment, PaymentOrderResponse, PaymentVerifyResponse } from '../types';

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

  createOnlineOrder: (invoiceId: number, amount?: number, idempotencyKey?: string) => {
    return api.post<PaymentOrderResponse>(`/billing/invoices/${invoiceId}/payments/order`, {
      amount,
      idempotency_key: idempotencyKey,
    });
  },

  verifyOnlinePayment: (data: {
    internal_payment_id: number;
    provider_order_id: string;
    provider_payment_id: string;
    provider_signature: string;
    invoice_id: number;
  }) => {
    return api.post<PaymentVerifyResponse>('/billing/payments/verify', data);
  },

  downloadReceiptPdf: async (paymentId: number, receiptNumber?: string) => {
    const blob = await api.downloadBlob(`/billing/payments/${paymentId}/receipt`);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Receipt_${receiptNumber || paymentId}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  reconcilePayment: (paymentId: number) => {
    return api.post<Payment>(`/billing/payments/${paymentId}/reconcile`, {});
  },

  refundPayment: (paymentId: number, amount?: number, reason?: string) => {
    return api.post(`/billing/payments/${paymentId}/refund`, { amount, reason });
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

