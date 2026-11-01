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
# (script-style tests; there is no pytest suite or tests/ directory.
#  test_phase2.py calls Gemini live and needs GEMINI_API_KEY exported; it does not read .env)
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

Frontend runs at: **http://localhost:8080** (port set in `frontend/vite.config.ts`)

## Architecture

### Backend Architecture (src/)

The backend follows a layered architecture with clear separation of concerns:

**Core Managers (Orchestration Layer):**
- `ProjectManager` - Project CRUD operations, orchestrates StateManager and VersionManager
- `ChatManager` - Chat session management, message storage and retrieval
- `AIAgent` - Gemini API integration, code generation and execution, manages AI conversation context
- `VersionManager` - CSV versioning system (initial snapshot, new version, revert, cleanup). Only `create_initial_version` is called by the app; nothing else is wired to the API or UI
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
- AI code execution uses plain `exec()` in the backend process. It is NOT sandboxed: globals are `df`, `pd`, `np`, `plt`, `sns`, and normal Python built-ins (including `open`, `import`) are available
- JSON writes are atomic (`safe_write_json`: temp file, then `shutil.move`); CSV writes are plain `to_csv`
- Each project has its own directory structure: `data/projects/{project-id}/` containing metadata.json, current.csv, chats/, and versions/

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
- `components/layout/` - App shell (`AppLayout`, `AppSidebar`)
- `components/project/` - `ProjectHome` (shown when no chat is active)
- `components/chat/` - Chat interface components
- `components/modals/` - Modal dialogs
- `components/ui/` - shadcn/ui primitives (Button, Card, Dialog, etc.)

**Pages:**
- `pages/Index.tsx` - Renders `AppLayout` (single-page app; `AppLayout` shows `ChatInterface` when a chat is active, else `ProjectHome`)
- `pages/NotFound.tsx` - 404

**Configuration:**
- API base URL configured via `VITE_API_BASE_URL` in `.env`
- Default: `http://localhost:8000` (in `config/api.ts`; the CSV download button in `ChatMessage.tsx` has no fallback, so set it)

### Data Flow

1. User uploads CSV → `POST /api/projects/upload` → ProjectManager creates project → VersionManager saves initial version (`versions/v1_<timestamp>.csv`) → default chat "Chat 1" created
2. User creates chat → `POST /api/chats/{projectId}` → ChatManager creates chat session
3. User sends query → `POST /api/ai/{projectId}/{chatId}/query` → first query for a chat creates an `AIAgent` (loads `current.csv`, builds the EDA context fresh, starts a Gemini chat) → Gemini returns JSON (`output_type`, `code`, `explanation`) → code run with `exec()` in the backend process → Results/plots returned → Message saved
4. Generated plots saved to `data/plots/plot_{chat_id}.png` (one file per chat, overwritten by each new chart) and served via `/static/plots/`
5. Modified datasets saved to `data/temp_modifications/{chat_id}_{hex8}.csv` and served via `/static/downloads/`. They are downloads only: `current.csv` is never updated and no new version is created

## Environment Variables

### Backend (`backend/.env`)
```env
# Required: Google Gemini API key
GEMINI_API_KEY=your_api_key_here

# Optional: data directory (default "data", relative to the backend cwd).
# api/main.py hard-codes data/plots and data/temp_modifications for static mounts,
# so keep this as "data" (or /app/data in the container).
DATA_DIR=data
```

The backend reads only `GEMINI_API_KEY` and `DATA_DIR`. There is no database. `API_HOST`/`API_PORT` (set in docker-compose) are not read; `run_api.py` always binds `0.0.0.0:8000`.

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Key Implementation Details

### AI Code Execution (backend/src/ai_agent.py)

The AIAgent uses Gemini to generate Python code that is executed with `exec()` in the backend process (`_execute_code`). This is not a sandbox:

```python
exec_globals = {
    'df': self.current_dataframe,   # the agent's live DataFrame, not a copy
    'pd': pd,
    'plt': plt,
    'np': numpy,
    'sns': seaborn,
}
exec(code, exec_globals)  # __builtins__ not overridden; stdout captured via StringIO
```

Behaviour depends on the `output_type` Gemini returns:
- `exploratory` - captured stdout is the result
- `visualization` - code must `plt.savefig('plot.png')` in the process cwd; the agent moves it to `data/plots/plot_{chat_id}.png`
- `modification` - code must assign a DataFrame to `result`; it is written to `data/temp_modifications/` and a before/after summary (rows, columns, new/removed columns, 10-row preview) is built
- Generated code has full filesystem and network access; in-place changes to `df` persist for later questions in that session (not to `current.csv`)

### EDA Context Generation (backend/src/eda_utils.py)

`generate_eda_context(df, name)` builds a text profile fresh each time an `AIAgent` is created (and `GET /api/projects/{id}/context` recomputes a structured profile on each call). Nothing is cached; `eda_context.json` path helpers exist but nothing writes the file. The profile is sent once, inside the system prompt that starts the Gemini chat:

- Column names, dtypes, non-null and unique counts
- Numeric columns: `[min, max]` only
- Non-numeric low-cardinality columns: value counts (all if ≤10 unique, top 10 if ≤50)
- Columns that look like stringified lists/dicts flagged with "⚠️ STORED AS STRING" and a parsing hint
- First three rows

### Version Management (backend/src/version_manager.py)

Versioning is implemented but not wired up. Only `create_initial_version` (on upload) is called by the app; `create_new_version` and `revert_to_version` are called only from `test_phase1.py`. AI modifications do NOT create versions, so every project has exactly one version in practice.

- Versions stored in `{project}/versions/v{N}_{timestamp}.csv`
- Version log tracks changes in `versions/version_log.json`
- `current.csv` is the active DataFrame (written on upload and by `revert_to_version`)
- Revert creates a new version copying the old data; no API route or UI exposes it

### API Error Handling

Errors are FastAPI `HTTPException`s, so the body is:
```json
{
  "detail": "Error message"
}
```
Note that a failed AI query (bad JSON, code error) may still return 200 with `success: false` and an error string in the response body.

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
- `_build_system_instruction()` - System prompt (sent as the first user message in `start_chat_session`, not as `system_instruction`)
- `process_query()` - Sends the query, strips a ```json fence, parses the JSON reply, saves messages and Gemini history
- `_execute_code()` - Execution scope and per-output-type handling

### Adding New Data to EDA Context

Modify `generate_eda_context()` in `backend/src/eda_utils.py` to include additional dataset statistics or metadata.

## Testing

Backend has test files for Phase 1 and 2 functionality:
- `test_phase1.py` - Tests core managers (Project, Chat, State, Version)
- `test_phase2.py` - Tests AI integration and code execution (live Gemini calls)

Run these directly with Python to verify backend functionality before UI changes.

## Important Notes

- **Gemini API Key Required:** Backend will not function without a valid `GEMINI_API_KEY` in `backend/.env`
- **No database:** persistence is file-based JSON and CSV under `DATA_DIR`
- **Sessions:** Gemini sessions live in an in-process dict (`active_agents` in `ai_query.py`). History is saved to each chat file but never loaded back, so a restart loses model memory
- **Model Selection:** Uses `gemini-2.0-flash-exp` by default (configured in AIAgent initialization)
- **CORS:** Frontend URLs must be in CORS allow list in `api/main.py` (localhost/127.0.0.1 on 5173, 3000, 8080; the Docker frontend on `http://localhost` is not included)
- **File Upload:** The upload endpoint reads the whole file into memory and parses it with `pd.read_csv`; there is no size limit
- **Plot Generation:** AI code must save to `plot.png` in the cwd (the prompt also tells it to call `plt.close()`); the agent then moves the file
- **Security:** generated code runs unsandboxed; see README.md. Detailed, code-checked notes are in `docs/NOTES.md`
