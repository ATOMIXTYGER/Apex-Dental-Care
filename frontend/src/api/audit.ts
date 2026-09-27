import { api } from './client';
import { AuditLogItem, PaginatedResult, User } from '../types';

export const auditApi = {
  list: (params?: { page?: number; page_size?: number; action?: string; entity_name?: string; user_email?: string }) => {
    return api.get<PaginatedResult<AuditLogItem>>('/audit-logs', params);
  },
};

export const usersApi = {
  list: (role?: string) => {
    return api.get<User[]>('/users', { role });
  },

  getDentists: () => {
    return api.get<User[]>('/users/dentists');
  },

  create: (data: any) => {
    return api.post<User>('/users', data);
  },

  update: (id: number, data: any) => {
    return api.put<User>(`/users/${id}`, data);
  },
};
