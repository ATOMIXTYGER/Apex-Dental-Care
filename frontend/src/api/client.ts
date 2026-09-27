const BASE_URL = '/api/v1';

let currentAccessToken: string | null = localStorage.getItem('access_token');

export const setAccessToken = (token: string | null) => {
  currentAccessToken = token;
  if (token) {
    localStorage.setItem('access_token', token);
  } else {
    localStorage.removeItem('access_token');
  }
};

export const getAccessToken = () => currentAccessToken;

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export class ApiError extends Error {
  code: string;
  details?: any;
  status: number;

  constructor(status: number, code: string, message: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const reqHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  if (currentAccessToken) {
    reqHeaders['Authorization'] = `Bearer ${currentAccessToken}`;
  }

  const response = await fetch(url, {
    ...customConfig,
    headers: reqHeaders,
  });

  if (!response.ok) {
    let errorCode = 'REQUEST_FAILED';
    let errorMessage = `Request failed with status ${response.status}`;
    let errorDetails = null;

    try {
      const errorJson = await response.json();
      if (errorJson.error) {
        errorCode = errorJson.error.code || errorCode;
        errorMessage = errorJson.error.message || errorMessage;
        errorDetails = errorJson.error.details || null;
      }
    } catch {
      // Non-JSON response
    }

    if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh')) {
      // Trigger logout / token clear if expired
      setAccessToken(null);
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }

    throw new ApiError(response.status, errorCode, errorMessage, errorDetails);
  }

  // Handle empty 204 or void response
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string, params?: Record<string, any>) => 
    request<T>(endpoint, { method: 'GET', params }),

  post: <T>(endpoint: string, body?: any, params?: Record<string, any>) =>
    request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      params,
    }),

  put: <T>(endpoint: string, body?: any) =>
    request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: any) =>
    request<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),

  upload: async <T>(endpoint: string, formData: FormData): Promise<T> => {
    const reqHeaders: Record<string, string> = {};
    if (currentAccessToken) {
      reqHeaders['Authorization'] = `Bearer ${currentAccessToken}`;
    }
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
      headers: reqHeaders,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        err.error?.code || 'UPLOAD_FAILED',
        err.error?.message || 'File upload failed'
      );
    }
    return response.json();
  },

  downloadBlob: async (endpoint: string): Promise<Blob> => {
    const reqHeaders: Record<string, string> = {};
    if (currentAccessToken) {
      reqHeaders['Authorization'] = `Bearer ${currentAccessToken}`;
    }
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: reqHeaders,
    });
    if (!response.ok) {
      throw new ApiError(response.status, 'DOWNLOAD_FAILED', 'Failed to download file');
    }
    return response.blob();
  }
};
