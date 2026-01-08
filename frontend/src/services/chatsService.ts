/**
 * Chats Service
 * API methods for chat management
 */

import api from './api';
import { API_ENDPOINTS } from '../config/api';

// API Response types matching backend
export interface ChatResponse {
  id: string;
  project_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface MessageResponse {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  output_type?: 'exploratory' | 'visualization' | 'modification';
  code?: string;
  output?: string;
  result?: string;
  plot_path?: string;
  modified_dataframe_path?: string;
  modification_summary?: Record<string, any>;
  explanation?: string;
}

/**
 * Chats Service
 */
export const chatsService = {
  /**
   * Get all chats for a project
   */
  async getChats(projectId: string): Promise<ChatResponse[]> {
    return api.get<ChatResponse[]>(API_ENDPOINTS.chats(projectId));
  },

  /**
   * Create new chat
   */
  async createChat(projectId: string, chatName: string): Promise<ChatResponse> {
    return api.post<ChatResponse>(API_ENDPOINTS.chats(projectId), { name: chatName });
  },

  /**
   * Get chat by ID
   */
  async getChat(projectId: string, chatId: string): Promise<ChatResponse> {
    return api.get<ChatResponse>(API_ENDPOINTS.chatDetail(projectId, chatId));
  },

  /**
   * Update/rename chat
   */
  async updateChat(projectId: string, chatId: string, chatName: string): Promise<ChatResponse> {
    return api.patch<ChatResponse>(API_ENDPOINTS.chatDetail(projectId, chatId), { name: chatName });
  },

  /**
   * Delete chat
   */
  async deleteChat(projectId: string, chatId: string): Promise<{ success: boolean; message: string }> {
    return api.delete(API_ENDPOINTS.chatDetail(projectId, chatId));
  },

  /**
   * Get chat messages
   */
  async getChatMessages(projectId: string, chatId: string): Promise<MessageResponse[]> {
    return api.get<MessageResponse[]>(API_ENDPOINTS.chatMessages(projectId, chatId));
  },

  /**
   * Clear chat messages
   */
  async clearChatMessages(projectId: string, chatId: string): Promise<{ success: boolean; message: string }> {
    return api.delete(API_ENDPOINTS.chatMessages(projectId, chatId));
  },
};

export default chatsService;
