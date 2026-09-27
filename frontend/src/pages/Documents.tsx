import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Upload, 
  Search, 
  Download, 
  Image as ImageIcon, 
  Calendar, 
  User as UserIcon, 
  File, 
  Eye, 
  Filter,
  CheckCircle,
  HardDrive
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { useAuth } from '../context/AuthContext';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import { DocumentItem } from '../types';

export default function Documents() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  // Fetch Documents
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['allDocuments', typeFilter],
    queryFn: () => documentsApi.listAll(typeFilter !== 'all' ? typeFilter : undefined),
  });

  const handleDownload = async (doc: DocumentItem) => {
    try {
      setDownloadingId(doc.id);
      await documentsApi.download(doc.id, doc.original_file_name);
    } catch (err) {
      console.error('Download error:', err);
      alert('Could not download file.');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const name = (doc.original_file_name || '').toLowerCase();
    const patient = (doc.patient_name || '').toLowerCase();
    const notes = (doc.notes || '').toLowerCase();
    return name.includes(q) || patient.includes(q) || notes.includes(q);
  });

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '0 KB';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getDocTypeBadge = (type: string) => {
    switch (type) {
      case 'xray':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-800">X-Ray (OPG/IOPA)</span>;
      case 'lab_report':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">Lab Report</span>;
      case 'consent':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">Consent Form</span>;
      case 'photo':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800">Clinical Photo</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700 capitalize">{type.replace('_', ' ')}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Documents & Diagnostic Imaging</h1>
          <p className="text-sm text-slate-500 mt-1">Centralized clinical digital vault for panoramic X-rays, CBCT scans, lab orders, and consent forms.</p>
        </div>
        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 transition"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by file name or patient..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-slate-500">Category:</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="text-xs font-medium border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Documents</option>
              <option value="xray">X-Rays & Imaging</option>
              <option value="lab_report">Lab Reports</option>
              <option value="consent">Consent Forms</option>
              <option value="photo">Photographs</option>
              <option value="other">Other Records</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          {filteredDocs.length} documents archived
        </div>
      </div>

      {/* Grid of Documents */}
      {isLoading ? (
        <div className="py-16 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-sm text-slate-500 mt-3 font-medium">Loading clinical documents...</p>
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="bg-white py-16 text-center rounded-xl border border-slate-200">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-slate-700">No documents found</p>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            No diagnostic images or patient records match the selected criteria.
          </p>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="mt-4 inline-flex items-center px-3.5 py-2 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
          >
            <Upload className="w-4 h-4 mr-1.5" /> Upload File
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredDocs.map((doc) => {
            const isImage = doc.mime_type?.startsWith('image/');
            const isPdf = doc.mime_type?.includes('pdf');

            return (
              <div 
                key={doc.id} 
                className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  {/* File Icon Header */}
                  <div className="flex items-start justify-between">
                    <div className={`p-3 rounded-xl ${
                      doc.document_type === 'xray' 
                        ? 'bg-purple-50 text-purple-600' 
                        : isPdf 
                          ? 'bg-rose-50 text-rose-600' 
                          : 'bg-blue-50 text-blue-600'
                    }`}>
                      {doc.document_type === 'xray' || isImage ? (
                        <ImageIcon className="w-6 h-6" />
                      ) : (
                        <FileText className="w-6 h-6" />
                      )}
                    </div>
                    {getDocTypeBadge(doc.document_type)}
                  </div>

                  {/* File Name & Details */}
                  <div className="mt-3">
                    <h4 className="text-sm font-semibold text-slate-900 truncate" title={doc.original_file_name}>
                      {doc.original_file_name}
                    </h4>
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>•</span>
                      <span className="font-mono uppercase">{doc.mime_type?.split('/')[1] || 'FILE'}</span>
                    </div>
                  </div>

                  {/* Patient Info */}
                  <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Patient:</span>
                      <Link 
                        to={`/patients/${doc.patient_id}`}
                        className="font-medium text-blue-600 hover:underline truncate max-w-[140px]"
                      >
                        {doc.patient_name || `Patient #${doc.patient_id}`}
                      </Link>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Uploaded:</span>
                      <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                    {doc.notes && (
                      <p className="text-[11px] text-slate-500 italic truncate mt-1" title={doc.notes}>
                        "{doc.notes}"
                      </p>
                    )}
                  </div>
                </div>

                {/* Download Button */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end">
                  <button
                    onClick={() => handleDownload(doc)}
                    disabled={downloadingId === doc.id}
                    className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition w-full justify-center disabled:opacity-50"
                  >
                    <Download className="w-3.5 h-3.5 mr-1.5" />
                    {downloadingId === doc.id ? 'Downloading...' : 'Secure Download'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Upload Modal */}
      {isUploadModalOpen && (
        <DocumentUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onSuccess={() => {
            setIsUploadModalOpen(false);
            queryClient.invalidateQueries({ queryKey: ['allDocuments'] });
          }}
        />
      )}
    </div>
  );
}
