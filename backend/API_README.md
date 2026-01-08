# AI Data Analyst REST API

FastAPI-based REST API for the AI Data Analyst backend. This API enables conversational data analysis with AI, replacing the Streamlit UI with a modern React frontend.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   React UI      │  HTTP   │   FastAPI        │  Uses   │  Existing Core   │
│  (Port 5173)    │ ◄─────► │   (Port 8000)    │ ◄─────► │  (ProjectMgr,    │
│                 │         │                  │         │   ChatMgr, etc)  │
└─────────────────┘         └──────────────────┘         └──────────────────┘
```

## Installation

Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

Or install FastAPI dependencies separately:

```bash
pip3 install fastapi "uvicorn[standard]" python-multipart
```

## Running the API

### Development Mode (with auto-reload)

```bash
python3 run_api.py
```

The API will start on `http://localhost:8000` with auto-reload enabled.

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### System Endpoints

#### Root
- **GET** `/`
- Returns API information and version

#### Health Check
- **GET** `/health`
- Returns system health status and configuration

### Projects

#### List All Projects
- **GET** `/api/projects/`
- Returns list of all projects

#### Get Project by ID
- **GET** `/api/projects/{project_id}`
- Returns project details

#### Upload CSV and Create Project
- **POST** `/api/projects/upload`
- **Body**: `multipart/form-data`
  - `file`: CSV file
  - `project_name`: Project name
- Returns project ID

#### Delete Project
- **DELETE** `/api/projects/{project_id}`
- Deletes project and all associated data

#### Get Project EDA Context
- **GET** `/api/projects/{project_id}/context`
- Returns comprehensive EDA context including:
  - Dataset overview
  - Column information with types, nulls, unique counts
  - Sample data
  - Value distributions for low-cardinality columns

### Chats

#### List All Chats for a Project
- **GET** `/api/chats/{project_id}`
- Returns list of chats for the project

#### Create New Chat
- **POST** `/api/chats/{project_id}`
- **Body**: `{"name": "Chat name"}`
- Returns chat ID

#### Get Chat by ID
- **GET** `/api/chats/{project_id}/{chat_id}`
- Returns chat metadata

#### Update/Rename Chat
- **PATCH** `/api/chats/{project_id}/{chat_id}`
- **Body**: `{"name": "New chat name"}`
- Updates chat name

#### Delete Chat
- **DELETE** `/api/chats/{project_id}/{chat_id}`
- Deletes chat and all messages

#### Get Chat Messages
- **GET** `/api/chats/{project_id}/{chat_id}/messages`
- Returns all messages in the chat

#### Clear Chat Messages
- **DELETE** `/api/chats/{project_id}/{chat_id}/messages`
- Clears all messages but keeps chat metadata

### AI Query

#### Query AI Agent
- **POST** `/api/ai/{project_id}/{chat_id}/query`
- **Body**: `{"query": "Your question here"}`
- Returns:
  - Generated Python code
  - Explanation
  - Execution results
  - Plot URL (if visualization)
  - Download URL (if modification)
  - Modification summary (if modification)

#### Clear AI Session
- **DELETE** `/api/ai/{project_id}/{chat_id}/session`
- Clears AI agent session (forces re-initialization)

#### AI Health Check
- **GET** `/api/ai/health`
- Returns AI service status and active agent count

## Static File Serving

The API serves static files for:

- **Plots**: `/static/plots/` → Generated visualization images
- **Downloads**: `/static/downloads/` → Modified CSV files

## CORS Configuration

The API is configured to allow requests from:

- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev port)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

## Environment Variables

Create a `.env` file in the root directory:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
DATA_DIR=data  # Default data directory
```

## Example API Usage

### 1. Upload a CSV File

```bash
curl -X POST http://localhost:8000/api/projects/upload \
  -F "file=@data.csv" \
  -F "project_name=My Project"
```

Response:
```json
{
  "success": true,
  "message": "Project created successfully",
  "project_id": "abc123..."
}
```

### 2. Create a Chat

```bash
curl -X POST http://localhost:8000/api/chats/abc123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Analysis Chat"}'
```

Response:
```json
{
  "id": "def456...",
  "project_id": "abc123...",
  "name": "Analysis Chat",
  "message_count": 0,
  "created_at": "2026-01-08T...",
  "updated_at": "2026-01-08T..."
}
```

### 3. Query the AI

```bash
curl -X POST http://localhost:8000/api/ai/abc123/def456/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the average of column X?"}'
```

Response:
```json
{
  "success": true,
  "output_type": "exploratory",
  "code": "print(df['X'].mean())",
  "explanation": "Calculating the average of column X",
  "output": "42.5\n",
  "result": null
}
```

### 4. Get EDA Context

```bash
curl http://localhost:8000/api/projects/abc123/context
```

Response:
```json
{
  "dataset_name": "My Project",
  "total_rows": 1000,
  "total_columns": 5,
  "columns": [
    {
      "name": "age",
      "dtype": "int64",
      "non_null": 950,
      "unique": 45,
      "min": 18,
      "max": 75
    }
  ],
  "sample_data": [...],
  "distributions": {...}
}
```

## Directory Structure

```
api/
├── __init__.py
├── main.py              # FastAPI application
├── schemas.py           # Pydantic models
└── routers/
    ├── __init__.py
    ├── projects.py      # Project endpoints
    ├── chats.py         # Chat endpoints
    └── ai_query.py      # AI query endpoints
```

## Next Steps: Connecting React Frontend

To connect the React frontend from `/Users/tarang.goel/Downloads/Project Insight Hub`:

1. **Update Frontend API Base URL**
   ```typescript
   // In your React app
   const API_BASE_URL = "http://localhost:8000";
   ```

2. **Example React API Service**
   ```typescript
   // api/projectsService.ts
   export const projectsService = {
     async listProjects() {
       const response = await fetch(`${API_BASE_URL}/api/projects/`);
       return response.json();
     },

     async uploadProject(file: File, name: string) {
       const formData = new FormData();
       formData.append('file', file);
       formData.append('project_name', name);

       const response = await fetch(`${API_BASE_URL}/api/projects/upload`, {
         method: 'POST',
         body: formData
       });
       return response.json();
     }
   };
   ```

3. **WebSocket Support** (Future Enhancement)
   - For real-time AI responses
   - Currently using standard HTTP POST

## Development Notes

- The API reuses all existing core modules (ProjectManager, ChatManager, AIAgent, etc.)
- No changes needed to core business logic
- AI agents are cached per chat session for efficiency
- Static files are served directly from `data/plots/` and `data/temp_modifications/`

## Testing

Test the API endpoints:

```bash
# Test root
curl http://localhost:8000/

# Test health
curl http://localhost:8000/health

# Test list projects
curl http://localhost:8000/api/projects/
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)

# Or use a different port
uvicorn api.main:app --port 8001
```

### Module Not Found Errors

Ensure you're in the correct directory and dependencies are installed:

```bash
cd /Users/tarang.goel/Downloads/agent_dir/ai_data_analyst_v2
pip3 install -r requirements.txt
```

### CORS Errors in Frontend

If you get CORS errors, verify:
1. Frontend is running on an allowed origin (localhost:5173 or localhost:3000)
2. CORS middleware is properly configured in `api/main.py`

## License

Same as parent project.
