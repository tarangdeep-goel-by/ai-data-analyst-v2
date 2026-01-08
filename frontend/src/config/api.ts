/**
 * API Configuration
 * Central configuration for API client
 */

// API Base URL from environment or default to localhost
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  // System
  root: '/',
  health: '/health',

  // Projects
  projects: '/api/projects',
  projectDetail: (id: string) => `/api/projects/${id}`,
  projectUpload: '/api/projects/upload',
  projectContext: (id: string) => `/api/projects/${id}/context`,

  // Chats
  chats: (projectId: string) => `/api/chats/${projectId}`,
  chatDetail: (projectId: string, chatId: string) => `/api/chats/${projectId}/${chatId}`,
  chatMessages: (projectId: string, chatId: string) => `/api/chats/${projectId}/${chatId}/messages`,

  // AI
  aiQuery: (projectId: string, chatId: string) => `/api/ai/${projectId}/${chatId}/query`,
  aiSession: (projectId: string, chatId: string) => `/api/ai/${projectId}/${chatId}/session`,
  aiHealth: '/api/ai/health',

  // Static files
  plotUrl: (filename: string) => `/static/plots/${filename}`,
  downloadUrl: (filename: string) => `/static/downloads/${filename}`,
} as const;

// HTTP Methods
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
} as const;

// Request configuration
export const REQUEST_CONFIG = {
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT_ERROR: 'Request timeout. Please try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  UNAUTHORIZED: 'Unauthorized access.',
  VALIDATION_ERROR: 'Invalid data provided.',
  UNKNOWN_ERROR: 'An unknown error occurred.',
} as const;
