/**
 * Projects Service
 * API methods for project management
 */

import api from './api';
import { API_ENDPOINTS } from '../config/api';

// API Response types matching backend
export interface ProjectResponse {
  id: string;
  name: string;
  original_filename: string;
  total_rows: number;
  total_columns: number;
  created_at: string;
  updated_at: string;
  current_version: number;
}

export interface FileUploadResponse {
  success: boolean;
  message: string;
  project_id?: string;
  error?: string;
}

export interface EDAContextResponse {
  dataset_name: string;
  total_rows: number;
  total_columns: number;
  columns: Array<{
    name: string;
    dtype: string;
    non_null: number;
    unique: number;
    min?: number;
    max?: number;
    values?: Array<{ value: string; count: number }>;
  }>;
  sample_data: Record<string, any>[];
  distributions?: Record<string, Array<{
    value: string;
    count: number;
    percentage: number;
  }>>;
}

/**
 * Projects Service
 */
export const projectsService = {
  /**
   * Get all projects
   */
  async getProjects(): Promise<ProjectResponse[]> {
    return api.get<ProjectResponse[]>(API_ENDPOINTS.projects);
  },

  /**
   * Get project by ID
   */
  async getProject(projectId: string): Promise<ProjectResponse> {
    return api.get<ProjectResponse>(API_ENDPOINTS.projectDetail(projectId));
  },

  /**
   * Upload CSV and create project
   */
  async uploadProject(file: File, projectName: string): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_name', projectName);

    return api.upload<FileUploadResponse>(API_ENDPOINTS.projectUpload, formData);
  },

  /**
   * Delete project
   */
  async deleteProject(projectId: string): Promise<{ success: boolean; message: string }> {
    return api.delete(API_ENDPOINTS.projectDetail(projectId));
  },

  /**
   * Get project EDA context
   */
  async getProjectContext(projectId: string): Promise<EDAContextResponse> {
    return api.get<EDAContextResponse>(API_ENDPOINTS.projectContext(projectId));
  },
};

export default projectsService;
