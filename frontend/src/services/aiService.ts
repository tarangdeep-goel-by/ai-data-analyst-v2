/**
 * AI Service
 * API methods for AI query processing
 */

import api from './api';
import { API_ENDPOINTS, API_BASE_URL } from '../config/api';

// API Request types
export interface AIQueryRequest {
  query: string;
}

// API Response types matching backend
export interface AIQueryResponse {
  success: boolean;
  output_type: 'exploratory' | 'visualization' | 'modification';
  code: string;
  explanation: string;
  output?: string;
  result?: string;
  plot_path?: string;
  plot_url?: string;
  modified_dataframe_path?: string;
  download_url?: string;
  modification_summary?: Record<string, any>;
  error?: string;
}

/**
 * AI Service
 */
export const aiService = {
  /**
   * Send query to AI agent
   */
  async sendQuery(
    projectId: string,
    chatId: string,
    query: string
  ): Promise<AIQueryResponse> {
    const request: AIQueryRequest = { query };
    return api.post<AIQueryResponse>(API_ENDPOINTS.aiQuery(projectId, chatId), request);
  },

  /**
   * Clear AI session (force re-initialization)
   */
  async clearSession(
    projectId: string,
    chatId: string
  ): Promise<{ success: boolean; message: string }> {
    return api.delete(API_ENDPOINTS.aiSession(projectId, chatId));
  },

  /**
   * AI health check
   */
  async healthCheck(): Promise<{
    status: string;
    gemini_configured: boolean;
    active_agents: number;
  }> {
    return api.get(API_ENDPOINTS.aiHealth);
  },

  /**
   * Get full URL for plot
   */
  getPlotUrl(filename: string): string {
    return `${API_BASE_URL}${API_ENDPOINTS.plotUrl(filename)}`;
  },

  /**
   * Get full URL for download
   */
  getDownloadUrl(filename: string): string {
    return `${API_BASE_URL}${API_ENDPOINTS.downloadUrl(filename)}`;
  },
};

export default aiService;
