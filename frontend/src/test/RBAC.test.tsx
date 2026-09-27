import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ProtectedRoute } from '../components/layout/ProtectedRoute';
import { AuthContext } from '../context/AuthContext';
import { User } from '../types';

describe('RBAC & ProtectedRoute Component', () => {
  const dentistUser: User = {
    id: 2,
    email: 'dr.chen@clinic.com',
    username: 'dr.chen',
    full_name: 'Dr. Marcus Chen',
    role: 'dentist',
    is_active: true,
    created_at: '2026-01-01',
    dentist_profile: {
      id: 1,
      license_number: 'DEN-99214',
      specialization: 'Periodontics',
    },
  };

  const receptionistUser: User = {
    id: 4,
    email: 'reception1@clinic.com',
    username: 'reception1',
    full_name: 'Jessica Miller',
    role: 'receptionist',
    is_active: true,
    created_at: '2026-01-01',
  };

  it('allows dentist to access clinical module with allowedRoles=["dentist", "admin"]', () => {
    render(
      <AuthContext.Provider
        value={{
          user: dentistUser,
          role: 'dentist',
          isAuthenticated: true,
          isLoading: false,
          login: async () => dentistUser,
          logout: async () => {},
          hasRole: (...roles) => roles.includes('dentist'),
        }}
      >
        <MemoryRouter>
          <ProtectedRoute allowedRoles={['dentist', 'admin']}>
            <div>Clinical Dental Examination Protected View</div>
          </ProtectedRoute>
        </MemoryRouter>
      </AuthContext.Provider>
    );

    expect(screen.getByText('Clinical Dental Examination Protected View')).toBeInTheDocument();
  });

  it('denies receptionist access to clinical module and displays Access Restricted', () => {
    render(
      <AuthContext.Provider
        value={{
          user: receptionistUser,
          role: 'receptionist',
          isAuthenticated: true,
          isLoading: false,
          login: async () => receptionistUser,
          logout: async () => {},
          hasRole: (...roles) => roles.includes('receptionist'),
        }}
      >
        <MemoryRouter>
          <ProtectedRoute allowedRoles={['dentist', 'admin']}>
            <div>Clinical Dental Examination Protected View</div>
          </ProtectedRoute>
        </MemoryRouter>
      </AuthContext.Provider>
    );

    expect(screen.queryByText('Clinical Dental Examination Protected View')).not.toBeInTheDocument();
    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
  });
});
