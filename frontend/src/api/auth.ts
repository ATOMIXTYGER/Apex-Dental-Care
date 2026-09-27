import { api, setAccessToken } from './client';
import { User } from '../types';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  expires_in: number;
  user: User;
}

export const authApi = {
  login: async (username_or_email: string, password: string): Promise<LoginResponse> => {
    const data = await api.post<LoginResponse>('/auth/login', { username_or_email, password });
    setAccessToken(data.access_token);
    return data;
  },

  getMe: async (): Promise<User> => {
    return api.get<User>('/auth/me');
  },

  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout');
    } finally {
      setAccessToken(null);
    }
  },

  changePassword: (current_password: string, new_password: string) => {
    return api.post('/auth/change-password', { current_password, new_password });
  },
};
