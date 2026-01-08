export interface Project {
  id: string;
  name: string;
  datasetFilename: string;
  rowCount: number;
  columnCount: number;
  lastActive: Date;
  createdAt: Date;
}

export interface Chat {
  id: string;
  projectId: string;
  name: string;
  firstQuery: string;
  messageCount: number;
  lastActive: Date;
  createdAt: Date;
}

export interface Message {
  id: string;
  chatId: string;
  role: 'user' | 'assistant';
  content: string;
  outputType?: 'exploratory' | 'visualization' | 'modification';
  code?: string;
  output?: string;
  chartUrl?: string;
  modifiedData?: {
    beforeRows: number;
    afterRows: number;
    beforeColumns: number;
    afterColumns: number;
    preview: Record<string, unknown>[];
  };
  createdAt: Date;
}

export interface DatasetColumn {
  name: string;
  type: string;
  nullPercentage: number;
}

export interface DatasetContext {
  filename: string;
  rowCount: number;
  columnCount: number;
  columns: DatasetColumn[];
  sampleData: Record<string, unknown>[];
  numericColumns: number;
  categoricalColumns: number;
  missingValuePercentage: number;
}

// API Response types (from backend)
import type { ProjectResponse, EDAContextResponse } from '../services/projectsService';
import type { ChatResponse, MessageResponse } from '../services/chatsService';
import type { AIQueryResponse } from '../services/aiService';

// Type converters to transform API responses to frontend types
export const typeConverters = {
  /**
   * Convert API ProjectResponse to frontend Project
   */
  projectFromAPI(apiProject: ProjectResponse): Project {
    return {
      id: apiProject.id,
      name: apiProject.name,
      datasetFilename: apiProject.original_filename,
      rowCount: apiProject.total_rows,
      columnCount: apiProject.total_columns,
      lastActive: new Date(apiProject.updated_at),
      createdAt: new Date(apiProject.created_at),
    };
  },

  /**
   * Convert API ChatResponse to frontend Chat
   */
  chatFromAPI(apiChat: ChatResponse): Chat {
    return {
      id: apiChat.id,
      projectId: apiChat.project_id,
      name: apiChat.name,
      firstQuery: '', // Will be populated from first message
      messageCount: apiChat.message_count,
      lastActive: new Date(apiChat.updated_at),
      createdAt: new Date(apiChat.created_at),
    };
  },

  /**
   * Convert API MessageResponse to frontend Message
   */
  messageFromAPI(apiMessage: MessageResponse): Message {
    return {
      id: apiMessage.id,
      chatId: apiMessage.chat_id,
      role: apiMessage.role,
      content: apiMessage.content,
      outputType: apiMessage.output_type,
      code: apiMessage.code,
      output: apiMessage.output,
      chartUrl: apiMessage.plot_path,
      modifiedData: apiMessage.modification_summary ? {
        beforeRows: apiMessage.modification_summary.before_rows || 0,
        afterRows: apiMessage.modification_summary.after_rows || 0,
        beforeColumns: apiMessage.modification_summary.before_columns || 0,
        afterColumns: apiMessage.modification_summary.after_columns || 0,
        preview: apiMessage.modification_summary.preview || [],
      } : undefined,
      createdAt: new Date(apiMessage.timestamp),
    };
  },

  /**
   * Convert API EDAContextResponse to frontend DatasetContext
   */
  datasetContextFromAPI(apiContext: EDAContextResponse): DatasetContext {
    const numericCols = apiContext.columns.filter(col =>
      col.dtype.includes('int') || col.dtype.includes('float')
    ).length;

    const categoricalCols = apiContext.columns.length - numericCols;

    const totalNulls = apiContext.columns.reduce((sum, col) =>
      sum + (apiContext.total_rows - col.non_null), 0
    );

    const missingPct = (totalNulls / (apiContext.total_rows * apiContext.columns.length)) * 100;

    return {
      filename: apiContext.dataset_name,
      rowCount: apiContext.total_rows,
      columnCount: apiContext.total_columns,
      columns: apiContext.columns.map(col => ({
        name: col.name,
        type: col.dtype,
        nullPercentage: ((apiContext.total_rows - col.non_null) / apiContext.total_rows) * 100,
      })),
      sampleData: apiContext.sample_data,
      numericColumns: numericCols,
      categoricalColumns: categoricalCols,
      missingValuePercentage: missingPct,
    };
  },
};

// Re-export API types for direct use
export type { ProjectResponse, ChatResponse, MessageResponse, AIQueryResponse, EDAContextResponse };
