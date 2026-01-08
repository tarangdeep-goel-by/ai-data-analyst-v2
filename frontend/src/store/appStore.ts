import { create } from 'zustand';
import { toast } from '@/components/ui/sonner';
import type { Project, Chat, Message, DatasetContext } from '@/types';
import { projectsService } from '../services/projectsService';
import { chatsService } from '../services/chatsService';
import { aiService } from '../services/aiService';
import { typeConverters } from '../types';

interface AppState {
  // Data (fetched from API)
  projects: Project[];
  chats: Chat[];
  messages: Message[];

  // UI State
  activeProjectId: string | null;
  activeChatId: string | null;
  showDataModal: boolean;
  isLoading: boolean;
  error: string | null;

  // Synchronous Actions (UI state)
  setActiveProject: (id: string | null) => void;
  setActiveChat: (id: string | null) => void;
  setShowDataModal: (show: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Getters
  getActiveProject: () => Project | undefined;
  getActiveChat: () => Chat | undefined;
  getProjectChats: (projectId: string) => Chat[];
  getChatMessages: (chatId: string) => Message[];

  // Async Actions (API calls)
  loadProjects: () => Promise<void>;
  loadChats: (projectId: string) => Promise<void>;
  loadMessages: (projectId: string, chatId: string) => Promise<void>;
  createProject: (name: string, file: File) => Promise<string | undefined>;
  deleteProject: (projectId: string) => Promise<void>;
  createChat: (projectId: string, name?: string) => Promise<string | undefined>;
  sendQuery: (projectId: string, chatId: string, query: string) => Promise<any>;
  getDatasetContext: (projectId: string) => Promise<DatasetContext>;
  addMessage: (message: Omit<Message, 'id' | 'createdAt'>) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state - empty arrays (will be populated by API calls)
  projects: [],
  chats: [],
  messages: [],
  activeProjectId: null,
  activeChatId: null,
  showDataModal: false,
  isLoading: false,
  error: null,

  // ===== Synchronous Actions (UI State) =====

  setActiveProject: (id) => {
    set({ activeProjectId: id, activeChatId: null });
    // Load chats when project is selected
    if (id) {
      get().loadChats(id);
    }
  },

  setActiveChat: (id) => {
    set({ activeChatId: id });
    // Load messages when chat is selected
    if (id && get().activeProjectId) {
      get().loadMessages(get().activeProjectId!, id);
    }
  },

  setShowDataModal: (show) => set({ showDataModal: show }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  // ===== Getters =====

  getActiveProject: () => {
    const { projects, activeProjectId } = get();
    return projects.find((p) => p.id === activeProjectId);
  },

  getActiveChat: () => {
    const { chats, activeChatId } = get();
    return chats.find((c) => c.id === activeChatId);
  },

  getProjectChats: (projectId) => {
    const { chats } = get();
    return chats.filter((c) => c.projectId === projectId);
  },

  getChatMessages: (chatId) => {
    const { messages } = get();
    return messages.filter((m) => m.chatId === chatId);
  },

  // ===== Async Actions (API Calls) =====

  /**
   * Load all projects from API
   */
  loadProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const apiProjects = await projectsService.getProjects();
      const projects = apiProjects.map(typeConverters.projectFromAPI);
      set({ projects, isLoading: false });
    } catch (error) {
      console.error('Failed to load projects:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to load projects',
        isLoading: false,
      });
    }
  },

  /**
   * Load chats for a project
   */
  loadChats: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const apiChats = await chatsService.getChats(projectId);
      const chats = apiChats.map(typeConverters.chatFromAPI);
      set({ chats, isLoading: false });
    } catch (error) {
      console.error('Failed to load chats:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to load chats',
        isLoading: false,
      });
    }
  },

  /**
   * Load messages for a chat
   */
  loadMessages: async (projectId: string, chatId: string) => {
    set({ isLoading: true, error: null });
    try {
      const apiMessages = await chatsService.getChatMessages(projectId, chatId);
      const messages = apiMessages.map(typeConverters.messageFromAPI);
      set({ messages, isLoading: false });
    } catch (error) {
      console.error('Failed to load messages:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to load messages',
        isLoading: false,
      });
    }
  },

  /**
   * Create new project (upload CSV)
   */
  createProject: async (name: string, file: File) => {
    set({ isLoading: true, error: null });
    try {
      const response = await projectsService.uploadProject(file, name);

      if (!response.success || !response.project_id) {
        throw new Error(response.error || 'Failed to create project');
      }

      // Reload projects to get the new one
      await get().loadProjects();

      // Set as active project
      set({ activeProjectId: response.project_id, isLoading: false });

      toast.success('Project created successfully', {
        description: `${name} is ready for analysis`,
      });

      return response.project_id;
    } catch (error) {
      console.error('Failed to create project:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to create project';
      set({
        error: errorMessage,
        isLoading: false,
      });
      throw error;
    }
  },

  /**
   * Delete project
   */
  deleteProject: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      await projectsService.deleteProject(projectId);

      // Remove from state
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== projectId),
        activeProjectId: state.activeProjectId === projectId ? null : state.activeProjectId,
        activeChatId: null,
        chats: state.activeProjectId === projectId ? [] : state.chats,
        messages: [],
        isLoading: false,
      }));

      toast.success('Project deleted', {
        description: 'Project and all associated data have been removed',
      });
    } catch (error) {
      console.error('Failed to delete project:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete project';
      set({
        error: errorMessage,
        isLoading: false,
      });
      toast.error('Failed to delete project', {
        description: errorMessage,
      });
      throw error;
    }
  },

  /**
   * Create new chat
   */
  createChat: async (projectId: string, name?: string) => {
    set({ isLoading: true, error: null });
    try {
      const chatName = name || `Chat ${get().chats.length + 1}`;
      const apiChat = await chatsService.createChat(projectId, chatName);
      const chat = typeConverters.chatFromAPI(apiChat);

      // Add to chats array
      set((state) => ({
        chats: [chat, ...state.chats],
        activeChatId: chat.id,
        isLoading: false,
      }));

      toast.success('Chat created', {
        description: 'Start asking questions about your data',
      });

      return chat.id;
    } catch (error) {
      console.error('Failed to create chat:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to create chat';
      set({
        error: errorMessage,
        isLoading: false,
      });
      toast.error('Failed to create chat', {
        description: errorMessage,
      });
      throw error;
    }
  },

  /**
   * Send AI query
   */
  sendQuery: async (projectId: string, chatId: string, query: string) => {
    set({ error: null });
    try {
      const response = await aiService.sendQuery(projectId, chatId, query);

      if (!response.success) {
        throw new Error(response.error || 'Query failed');
      }

      // Reload messages to get the latest (including AI response)
      await get().loadMessages(projectId, chatId);

      return response;
    } catch (error) {
      console.error('Failed to send query:', error);
      set({
        error: error instanceof Error ? error.message : 'Failed to send query',
      });
      throw error;
    }
  },

  /**
   * Get dataset context for a project
   */
  getDatasetContext: async (projectId: string): Promise<DatasetContext> => {
    try {
      const apiContext = await projectsService.getProjectContext(projectId);
      return typeConverters.datasetContextFromAPI(apiContext);
    } catch (error) {
      console.error('Failed to load dataset context:', error);
      throw error;
    }
  },

  /**
   * Add message to local state (for optimistic UI updates)
   */
  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      createdAt: new Date(),
    };
    set((state) => ({ messages: [...state.messages, newMessage] }));
  },
}));
