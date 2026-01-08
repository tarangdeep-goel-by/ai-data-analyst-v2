/**
 * Core API Client
 * Centralized fetch wrapper with error handling
 */

import { API_BASE_URL, ERROR_MESSAGES } from '../config/api';

// API Error class
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Request options interface
interface RequestOptions extends RequestInit {
  timeout?: number;
}

/**
 * Make HTTP request with error handling
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { timeout = 30000, ...fetchOptions } = options;

  // Build full URL
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    // Build headers - only add Content-Type for JSON requests
    // For FormData, don't set Content-Type (browser sets it with boundary)
    const headers: HeadersInit = { ...fetchOptions.headers };
    const isFormData = fetchOptions.body instanceof FormData;

    if (fetchOptions.body && !isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // Make request
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers,
      mode: 'cors',
      credentials: 'include',
    });

    clearTimeout(timeoutId);

    // Handle non-OK responses
    if (!response.ok) {
      let errorMessage = ERROR_MESSAGES.SERVER_ERROR;
      let errorData;

      try {
        errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }

      // Map status codes to user-friendly messages
      switch (response.status) {
        case 404:
          errorMessage = ERROR_MESSAGES.NOT_FOUND;
          break;
        case 401:
        case 403:
          errorMessage = ERROR_MESSAGES.UNAUTHORIZED;
          break;
        case 400:
          errorMessage = errorData?.detail || ERROR_MESSAGES.VALIDATION_ERROR;
          break;
        case 500:
        case 502:
        case 503:
          errorMessage = ERROR_MESSAGES.SERVER_ERROR;
          break;
      }

      throw new APIError(errorMessage, response.status, errorData);
    }

    // Parse response
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text() as any;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle abort/timeout
    if (error instanceof Error && error.name === 'AbortError') {
      throw new APIError(ERROR_MESSAGES.TIMEOUT_ERROR);
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new APIError(ERROR_MESSAGES.NETWORK_ERROR);
    }

    // Re-throw API errors
    if (error instanceof APIError) {
      throw error;
    }

    // Unknown error
    throw new APIError(ERROR_MESSAGES.UNKNOWN_ERROR);
  }
}

/**
 * HTTP Methods
 */
export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),

  // Special method for file uploads (multipart/form-data)
  upload: <T>(endpoint: string, formData: FormData, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData - browser sets it with boundary
        ...options?.headers,
      },
    }),
};

export default api;
