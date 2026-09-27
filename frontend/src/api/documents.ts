import { api } from './client';
import { DocumentItem } from '../types';

export const documentsApi = {
  listAll: (documentType?: string) => {
    return api.get<DocumentItem[]>('/documents', documentType ? { document_type: documentType } : undefined);
  },

  getPatientDocuments: (patientId: number) => {
    return api.get<DocumentItem[]>(`/documents/patient/${patientId}`);
  },

  upload: (patientId: number, documentType: string, file: File, visitId?: number, notes?: string) => {
    const formData = new FormData();
    formData.append('patient_id', String(patientId));
    formData.append('document_type', documentType);
    formData.append('file', file);
    if (visitId) formData.append('visit_id', String(visitId));
    if (notes) formData.append('notes', notes);
    return api.upload<DocumentItem>('/documents/upload', formData);
  },

  download: async (documentId: number, filename: string) => {
    const blob = await api.downloadBlob(`/documents/${documentId}/download`);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
