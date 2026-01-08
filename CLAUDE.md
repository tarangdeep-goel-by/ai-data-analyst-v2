# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Data Analyst is a full-stack application that enables conversational data analysis powered by Google's Gemini AI. Users upload CSV files, and the AI generates Python code to analyze data, create visualizations, and modify datasets based on natural language queries.

**Tech Stack:**
- **Backend:** FastAPI (Python), Google Gemini API, pandas, matplotlib/seaborn
- **Frontend:** React 18, TypeScript, Vite, Zustand, shadcn/ui, Tailwind CSS

## Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Run development server (with auto-reload)
python3 run_api.py

# Alternative: Run with uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (Phase 1 and 2 tests)
python3 test_phase1.py
python3 test_phase2.py
pytest tests/  # if pytest tests exist
```

Backend runs at: **http://localhost:8000**
API docs: **http://localhost:8000/api/docs**

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Type checking (no separate command - included in lint)
npm run lint

# Build for production
npm run build

# Build for development mode
npm run build:dev

# Preview production build
npm run preview
```

Frontend runs at: **http://localhost:5173**

## Architecture

### Backend Architecture (src/)

The backend follows a layered architecture with clear separation of concerns:

**Core Managers (Orchestration Layer):**
- `ProjectManager` - Project CRUD operations, orchestrates StateManager and VersionManager
- `ChatManager` - Chat session management, message storage and retrieval
- `AIAgent` - Gemini API integration, code generation and execution, manages AI conversation context
- `VersionManager` - CSV versioning system, tracks data modifications, handles version snapshots
- `StateManager` - Low-level persistence layer, atomic file I/O, JSON serialization

**Data Models (`models.py`):**
- `Project` - CSV project with metadata (rows, columns, size)
- `Chat` - Conversation session linked to a project
- `Message` - Individual message (user/assistant) with role, content, timestamp
- `Version` - CSV snapshot with change tracking

**API Layer (`api/`):**
- `api/main.py` - FastAPI app initialization, CORS configuration, static file mounting
- `api/routers/projects.py` - Project endpoints (upload, list, get, delete, context)
- `api/routers/chats.py` - Chat endpoints (create, list, get messages, delete)
- `api/routers/ai_query.py` - AI query endpoint, code execution, session management
- `api/schemas.py` - Pydantic models for request/response validation

**Key Design Patterns:**
- Managers instantiate their dependencies (e.g., ProjectManager creates StateManager and VersionManager)
- AI code execution uses sandboxed exec() with limited scope containing only pandas, numpy, matplotlib, and the current DataFrame
- File operations are atomic through StateManager to prevent corruption
- Each project has its own directory structure: `data/projects/{project-id}/` containing metadata.json, current.csv, eda_context.json, chats/, and versions/

### Frontend Architecture (src/)

**State Management (`store/`):**
- `appStore.ts` - Zustand store for global state (projects, chats, messages)
- Currently uses API services to fetch data from backend
- State updates trigger re-renders across components

**API Layer (`services/`):**
- `api.ts` - Core fetch wrapper with error handling, timeout support, APIError class
- `projectsService.ts` - Projects API (upload, list, get, delete, get context)
- `chatsService.ts` - Chats API (create, list, get messages, delete)
- `aiService.ts` - AI query API (send query, clear session)
- `typeConverters` in `types/index.ts` - Transform API responses to frontend types

**Component Structure:**
- `components/layout/` - App shell (Header, Sidebar)
- `components/project/` - Project-related components
- `components/chat/` - Chat interface components
- `components/modals/` - Modal dialogs
- `components/ui/` - shadcn/ui primitives (Button, Card, Dialog, etc.)

**Pages:**
- `pages/ProjectsPage.tsx` - Project list and management
- `pages/AnalysisPage.tsx` - Main chat/analysis interface

**Configuration:**
- API base URL configured via `VITE_API_BASE_URL` in `.env`
- Default: `http://localhost:8000`

### Data Flow

1. User uploads CSV → `POST /api/projects/upload` → ProjectManager creates project → VersionManager saves initial version → EDA context generated
2. User creates chat → `POST /api/chats/{projectId}` → ChatManager creates chat session
3. User sends query → `POST /api/ai/{projectId}/{chatId}/query` → AIAgent generates Python code → Code executed in sandboxed environment → Results/plots returned → Message saved
4. Generated plots saved to `data/plots/{uuid}.png` and served via `/static/plots/`
5. Modified datasets saved to `data/temp_modifications/` and served via `/static/downloads/`

## Environment Variables

### Backend (`backend/.env`)
```env
# Required: Google Gemini API key
GEMINI_API_KEY=your_api_key_here

# Optional: Database and API config
DATABASE_URL=sqlite:///./data/app.db
API_HOST=0.0.0.0
API_PORT=8000
DATA_DIR=data
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Key Implementation Details

### AI Code Execution (backend/src/ai_agent.py)

The AIAgent uses Gemini to generate Python code that is executed in a controlled environment:

```python
# Code execution scope includes only:
exec_scope = {
    'pd': pd,
    'np': np,
    'plt': plt,
    'sns': sns,
    'df': current_dataframe,
    'result': None,
    'plot_path': None
}
exec(generated_code, exec_scope)
```

- Code must set `result` variable for text output
- Code must set `plot_path` variable for visualization output
- No file system access except through these variables
- DataFrame modifications are detected by comparing before/after state

### EDA Context Generation (backend/src/eda_utils.py)

When a CSV is uploaded, an automatic EDA (Exploratory Data Analysis) context is generated and cached in `{project}/eda_context.json`. This context is sent to the AI with every query to provide dataset understanding:

- Column names and data types
- Shape (rows × columns)
- Missing values count per column
- Numeric column statistics (mean, std, min, max, quartiles)
- Sample rows (first few rows)

### Version Management (backend/src/version_manager.py)

Every time the AI modifies the dataset, a new version is automatically created:

- Versions stored in `{project}/versions/v{N}_{timestamp}.csv`
- Version log tracks changes in `versions/version_log.json`
- `current.csv` always points to the active version
- Users can theoretically revert (though UI not yet implemented)

### API Error Handling

The backend returns consistent error responses:
```json
{
  "detail": "Error message",
  "error": "Detailed error info"
}
```

Frontend APIError class captures status codes and error data for proper error display.

## Common Development Tasks

### Adding a New API Endpoint

1. Define Pydantic schema in `backend/api/schemas.py`
2. Add endpoint to appropriate router in `backend/api/routers/`
3. Implement business logic using managers in `backend/src/`
4. Create service method in frontend `src/services/`
5. Update Zustand store in `src/store/appStore.ts` if needed
6. Test via API docs at http://localhost:8000/api/docs

### Modifying AI Behavior

Edit the system prompt and code generation logic in `backend/src/ai_agent.py`:
- `_build_system_prompt()` - Instructions for the AI
- `_build_user_query()` - User query formatting with context
- `_extract_code_blocks()` - Parse generated code
- Execution scope in `process_query()` method

### Adding New Data to EDA Context

Modify `generate_eda_context()` in `backend/src/eda_utils.py` to include additional dataset statistics or metadata.

## Testing

Backend has test files for Phase 1 and 2 functionality:
- `test_phase1.py` - Tests core managers (Project, Chat, State, Version)
- `test_phase2.py` - Tests AI integration and code execution

Run these directly with Python to verify backend functionality before UI changes.

## Important Notes

- **Gemini API Key Required:** Backend will not function without a valid `GEMINI_API_KEY` in `backend/.env`
- **SQLite Database:** Currently defined in env but not actively used; main persistence is file-based JSON
- **Model Selection:** Uses `gemini-2.0-flash-exp` by default (configured in AIAgent initialization)
- **CORS:** Frontend URLs must be in CORS allow list in `api/main.py`
- **File Upload:** Maximum file size and CSV validation happens in the upload endpoint
- **Plot Generation:** Plots must be saved by AI code to specific paths; matplotlib figures are automatically closed after saving
