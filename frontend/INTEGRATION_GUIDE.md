# Frontend-Backend Integration Guide

## ✅ Completed Tasks

### 1. API Service Layer (DONE)
Created complete API infrastructure:

**Files Created:**
- `src/config/api.ts` - API configuration (base URL, endpoints, error messages)
- `src/services/api.ts` - Core fetch wrapper with error handling
- `src/services/projectsService.ts` - Projects API methods
- `src/services/chatsService.ts` - Chats API methods
- `src/services/aiService.ts` - AI query API methods

**Features:**
- ✅ Type-safe API client
- ✅ Centralized error handling
- ✅ Request timeout support
- ✅ File upload support (multipart/form-data)
- ✅ Full CRUD operations for all entities

### 2. TypeScript Types (DONE)
Updated type definitions:

**File Updated:**
- `src/types/index.ts`

**Added:**
- Type converters (`typeConverters`) to transform API responses → frontend types
- Re-exports of API response types
- Helper functions for seamless integration

### 3. Environment Configuration (DONE)
**File Created:**
- `.env` with `VITE_API_BASE_URL=http://localhost:8000`

---

## 🔄 Remaining Tasks

### Task 1: Update Zustand Store (CRITICAL)

**File to Modify:** `src/store/appStore.ts`

**Current State:** Uses mock data arrays
**Target State:** Fetch data from API services

**Changes Needed:**

```typescript
// Import API services at top
import { projectsService } from '../services/projectsService';
import { chatsService } from '../services/chatsService';
import { aiService } from '../services/aiService';
import { typeConverters } from '../types';

// Replace mock data with empty arrays
projects: Project[] = []
chats: Chat[] = []
messages: Message[] = []

// Add new async methods:

/**
 * Load projects from API
 */
loadProjects: async () => {
  set({ isLoading: true });
  try {
    const apiProjects = await projectsService.getProjects();
    const projects = apiProjects.map(typeConverters.projectFromAPI);
    set({ projects, isLoading: false });
  } catch (error) {
    console.error('Failed to load projects:', error);
    set({ isLoading: false });
    // TODO: Add toast notification for error
  }
},

/**
 * Load chats for a project
 */
loadChats: async (projectId: string) => {
  set({ isLoading: true });
  try {
    const apiChats = await chatsService.getChats(projectId);
    const chats = apiChats.map(typeConverters.chatFromAPI);
    set({ chats, isLoading: false });
  } catch (error) {
    console.error('Failed to load chats:', error);
    set({ isLoading: false });
  }
},

/**
 * Load messages for a chat
 */
loadMessages: async (projectId: string, chatId: string) => {
  set({ isLoading: true });
  try {
    const apiMessages = await chatsService.getChatMessages(projectId, chatId);
    const messages = apiMessages.map(typeConverters.messageFromAPI);
    set({ messages, isLoading: false });
  } catch (error) {
    console.error('Failed to load messages:', error);
    set({ isLoading: false });
  }
},

/**
 * Create new project (upload CSV)
 */
createProject: async (name: string, file: File) => {
  set({ isLoading: true });
  try {
    const response = await projectsService.uploadProject(file, name);
    if (response.success && response.project_id) {
      // Reload projects
      await get().loadProjects();
      return response.project_id;
    }
    throw new Error(response.error || 'Failed to create project');
  } catch (error) {
    console.error('Failed to create project:', error);
    set({ isLoading: false });
    throw error;
  }
},

/**
 * Create new chat
 */
createChat: async (projectId: string, name?: string) => {
  set({ isLoading: true });
  try {
    const chatName = name || `Chat ${get().chats.length + 1}`;
    const apiChat = await chatsService.createChat(projectId, chatName);
    const chat = typeConverters.chatFromAPI(apiChat);

    set(state => ({
      chats: [...state.chats, chat],
      isLoading: false
    }));

    return chat.id;
  } catch (error) {
    console.error('Failed to create chat:', error);
    set({ isLoading: false });
    throw error;
  }
},

/**
 * Send AI query
 */
sendQuery: async (projectId: string, chatId: string, query: string) => {
  try {
    const response = await aiService.sendQuery(projectId, chatId, query);

    if (!response.success) {
      throw new Error(response.error || 'Query failed');
    }

    // Reload messages to get latest
    await get().loadMessages(projectId, chatId);

    return response;
  } catch (error) {
    console.error('Failed to send query:', error);
    throw error;
  }
},

/**
 * Get dataset context
 */
getDatasetContext: async (projectId: string) => {
  try {
    const apiContext = await projectsService.getProjectContext(projectId);
    return typeConverters.datasetContextFromAPI(apiContext);
  } catch (error) {
    console.error('Failed to load dataset context:', error);
    throw error;
  }
},
```

---

### Task 2: Update ChatInterface Component

**File to Modify:** `src/components/chat/ChatInterface.tsx`

**Lines to Change:** Lines 42-56 (remove mock setTimeout)

**Replace:**
```typescript
// OLD: Mock response
setTimeout(() => {
  const mockAssistantMessage: Message = {
    // ... mock data ...
  };
  addMessage(mockAssistantMessage);
}, 1500);
```

**With:**
```typescript
// NEW: Real API call
const { activeProjectId } = useAppStore();
const activeProject = getActiveProject();

if (!activeProjectId || !activeChat) {
  console.error('No active project or chat');
  return;
}

try {
  // Send query to API
  const response = await useAppStore.getState().sendQuery(
    activeProjectId,
    activeChat.id,
    userMessage
  );

  // Messages are auto-reloaded by sendQuery
  // No need to manually add response
} catch (error) {
  console.error('Failed to send message:', error);
  // TODO: Show error toast to user
}
```

---

### Task 3: Update AppSidebar Component

**File to Modify:** `src/components/layout/AppSidebar.tsx`

**Add useEffect to load projects on mount:**

```typescript
import { useEffect } from 'react';

function AppSidebar() {
  const { projects, loadProjects } = useAppStore();

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // ... rest of component
}
```

---

### Task 4: Update ProjectHome Component

**File to Modify:** `src/components/project/ProjectHome.tsx`

**Add useEffect to load chats when project changes:**

```typescript
import { useEffect } from 'react';

function ProjectHome() {
  const { activeProjectId, chats, loadChats } = useAppStore();

  // Load chats when project changes
  useEffect(() => {
    if (activeProjectId) {
      loadChats(activeProjectId);
    }
  }, [activeProjectId]);

  // ... rest of component
}
```

---

### Task 5: Update DataContextModal Component

**File to Modify:** `src/components/modals/DataContextModal.tsx`

**Replace `getDatasetContext()` call:**

```typescript
// OLD: Synchronous mock call
const datasetContext = getDatasetContext();

// NEW: Async API call
const [datasetContext, setDatasetContext] = useState<DatasetContext | null>(null);
const [isLoading, setIsLoading] = useState(false);

useEffect(() => {
  if (showDataModal && activeProjectId) {
    setIsLoading(true);
    useAppStore.getState().getDatasetContext(activeProjectId)
      .then(context => {
        setDatasetContext(context);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Failed to load context:', error);
        setIsLoading(false);
      });
  }
}, [showDataModal, activeProjectId]);
```

---

## 🧪 Testing Checklist

### Before Testing
1. Ensure FastAPI backend is running: `python3 run_api.py` (in backend directory)
2. Backend should be accessible at http://localhost:8000
3. Check backend has existing projects (upload CSV if needed via Swagger docs)

### Start Frontend
```bash
cd ai-data-analyst-app/frontend
npm install  # If dependencies not installed
npm run dev
```

### Test Scenarios

#### 1. Projects List
- [ ] Open http://localhost:5173
- [ ] Sidebar should load and display projects from API
- [ ] Should show loading state while fetching
- [ ] Projects should match those in backend

#### 2. Create Project (Upload CSV)
- [ ] Click upload button
- [ ] Select CSV file
- [ ] Enter project name
- [ ] Submit → Should create via API
- [ ] New project should appear in list

#### 3. View Project
- [ ] Click on a project
- [ ] Should load chats for that project
- [ ] Should show project details

#### 4. Create Chat
- [ ] In project view, click "New Chat"
- [ ] Enter chat name
- [ ] Should create via API
- [ ] New chat should appear in list

#### 5. Send Message
- [ ] Select a chat
- [ ] Type a message
- [ ] Click send
- [ ] Should see message appear
- [ ] Should get AI response back
- [ ] Response should include code, explanation

#### 6. View Dataset Context
- [ ] Click "View Data" button
- [ ] Modal should open
- [ ] Should load dataset context from API
- [ ] Should show columns, sample data, distributions

#### 7. Visualizations
- [ ] Ask for a visualization (e.g., "plot distribution of column X")
- [ ] Should see chart appear
- [ ] Chart URL should point to backend /static/plots/

#### 8. Error Handling
- [ ] Stop backend server
- [ ] Try to send a message
- [ ] Should show error (not crash)
- [ ] Should display user-friendly error message

---

## 🐛 Common Issues & Solutions

### Issue: "Network Error"
**Solution:** Check that backend is running on port 8000

### Issue: "CORS Error"
**Solution:** Verify CORS middleware in `api/main.py` includes frontend URL (localhost:5173)

### Issue: Types mismatch errors
**Solution:** Check type converters in `src/types/index.ts` match API response structure

### Issue: Empty data after API call
**Solution:** Check browser console for errors, verify API endpoints in `src/config/api.ts`

### Issue: Images not loading
**Solution:** Verify static file serving in backend, check plot URLs use correct base URL

---

## 📁 Files Modified Summary

### Created (7 files)
1. `src/config/api.ts`
2. `src/services/api.ts`
3. `src/services/projectsService.ts`
4. `src/services/chatsService.ts`
5. `src/services/aiService.ts`
6. `.env`
7. `INTEGRATION_GUIDE.md` (this file)

### Modified (1 file)
1. `src/types/index.ts` - Added type converters

### To Modify (5 files)
1. `src/store/appStore.ts` - Replace mock data with API calls
2. `src/components/chat/ChatInterface.tsx` - Real AI query
3. `src/components/layout/AppSidebar.tsx` - Load projects on mount
4. `src/components/project/ProjectHome.tsx` - Load chats on project select
5. `src/components/modals/DataContextModal.tsx` - Async dataset context

---

## 🎯 Next Steps

### Immediate (Required)
1. Complete Task 1: Update Zustand store
2. Complete Task 2: Update ChatInterface
3. Complete Task 3-5: Update other components
4. Test all scenarios

### Optional Enhancements
- Add React Query for caching and optimistic updates
- Add error boundary component
- Add toast notifications for errors
- Add loading skeletons
- Add file upload progress bar
- Add WebSocket support for streaming AI responses

---

## 📞 API Endpoints Reference

**Backend:** http://localhost:8000

- **GET** `/api/projects/` - List projects
- **POST** `/api/projects/upload` - Upload CSV
- **GET** `/api/projects/{id}/context` - Dataset context
- **GET** `/api/chats/{projectId}` - List chats
- **POST** `/api/chats/{projectId}` - Create chat
- **GET** `/api/chats/{projectId}/{chatId}/messages` - Get messages
- **POST** `/api/ai/{projectId}/{chatId}/query` - Send AI query

**Interactive Docs:** http://localhost:8000/api/docs

---

## ✅ Integration Status

- ✅ **API Service Layer** - Complete
- ✅ **Type System** - Complete
- ✅ **Environment Config** - Complete
- 🔄 **State Management** - Needs update (store)
- 🔄 **Components** - Need updates (5 files)
- ⏳ **Testing** - Pending

**Estimated Time to Complete:** 2-3 hours

---

## 🚀 Quick Start

```bash
# Terminal 1: Start Backend
cd /Users/tarang.goel/Downloads/ai-data-analyst-app/backend
python3 run_api.py

# Terminal 2: Start Frontend
cd /Users/tarang.goel/Downloads/ai-data-analyst-app/frontend
npm run dev

# Open browser: http://localhost:5173
```

**Backend API running at:** http://localhost:8000
**Frontend running at:** http://localhost:5173
