import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search, UserPlus, ArrowRight, Phone, Calendar, HeartPulse } from 'lucide-react';
import { Patient, PaginatedResult } from '../types';
import { patientsApi } from '../api/patients';
import { PatientFormModal } from '../components/patients/PatientFormModal';
import { useAuth } from '../context/AuthContext';
import { formatDateIN } from '../utils/formatters';

export const Patients: React.FC = () => {
  const [data, setData] = useState<PaginatedResult<Patient> | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { hasRole } = useAuth();
  const canRegister = hasRole('admin', 'receptionist');
  const navigate = useNavigate();

  const fetchPatients = async () => {
    setIsLoading(true);
    try {
      const res = await patientsApi.list(page, 15, search);
      setData(res);
    } catch {
      // Handled by global interceptor
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPatients();
    }, 250);
    return () => clearTimeout(timer);
  }, [search, page]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Patient Directory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Registered patients, demographic profiles, and medical alert summaries.
          </p>
        </div>

        {canRegister && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-md shadow-teal-600/20 transition-all flex items-center gap-2 self-start sm:self-auto"
          >
            <UserPlus className="w-4 h-4" />
            <span>Register New Patient</span>
          </button>
        )}
      </div>

      {/* Search Input Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search patients by name, patient code (e.g. P-1001), or phone number..."
            className="w-full text-xs pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white transition-all text-slate-800 placeholder-slate-400"
          />
        </div>
      </div>

      {/* Patients Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-6">Patient Code</th>
                <th className="py-3.5 px-6">Full Name</th>
                <th className="py-3.5 px-6">DOB / Age</th>
                <th className="py-3.5 px-6">Gender</th>
                <th className="py-3.5 px-6">Phone</th>
                <th className="py-3.5 px-6">Blood Group</th>
                <th className="py-3.5 px-6">Registered</th>
                <th className="py-3.5 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    Loading patient records...
                  </td>
                </tr>
              ) : !data?.items.length ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No matching patient records found.
                  </td>
                </tr>
              ) : (
                data.items.map((patient) => {
                  const birthDate = new Date(patient.date_of_birth);
                  const age = Math.floor(
                    (new Date().getTime() - birthDate.getTime()) / (365.25 * 24 * 3600 * 1000)
                  );

                  return (
                    <tr
                      key={patient.id}
                      onClick={() => navigate(`/patients/${patient.id}`)}
                      className="hover:bg-teal-50/40 cursor-pointer transition-colors group"
                    >
                      <td className="py-4 px-6 font-mono font-bold text-teal-700">
                        {patient.patient_code}
                      </td>
                      <td className="py-4 px-6 font-bold text-slate-900 group-hover:text-teal-700 transition-colors">
                        {patient.first_name} {patient.last_name}
                      </td>
                      <td className="py-4 px-6 text-slate-500">
                        {formatDateIN(birthDate)} ({age} yrs)
                      </td>
                      <td className="py-4 px-6">{patient.gender}</td>
                      <td className="py-4 px-6 text-slate-600 font-mono">{patient.phone}</td>
                      <td className="py-4 px-6">
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-bold text-[10px]">
                          {patient.blood_group || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-slate-400 text-[11px]">
                        {formatDateIN(patient.created_at)}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/patients/${patient.id}`);
                          }}
                          className="px-3 py-1.5 rounded-lg bg-slate-100 group-hover:bg-teal-600 group-hover:text-white text-slate-700 font-semibold text-[11px] transition-all inline-flex items-center gap-1.5"
                        >
                          <span>Profile</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {data && data.total_pages > 1 && (
          <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {data.items.length} of {data.total} patients
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40"
              >
                Previous
              </button>
              <span className="font-semibold text-slate-800">
                Page {page} of {data.total_pages}
              </span>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Register Patient Modal */}
      {isModalOpen && (
        <PatientFormModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={async (payload) => {
            const newPat = await patientsApi.create(payload);
            setIsModalOpen(false);
            fetchPatients();
            navigate(`/patients/${newPat.id}`);
          }}
        />
      )}
    </div>
  );
};

export default Patients;
