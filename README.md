# AI Data Analyst Application

A full-stack AI-powered data analysis application with a React frontend and FastAPI backend.

## Project Structure

```
ai-data-analyst-app/
├── backend/          # FastAPI backend service
│   ├── api/          # API routers and schemas
│   ├── data/         # SQLite database and uploaded datasets
│   ├── plots/        # Generated visualization plots
│   ├── static/       # Static file serving
│   ├── .env          # Backend environment variables
│   ├── run_api.py    # Backend entry point
│   └── requirements.txt
│
├── frontend/         # React + TypeScript frontend
│   ├── src/          # Source code
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   ├── store/       # Zustand state management
│   │   └── types/       # TypeScript types
│   ├── .env          # Frontend environment variables
│   ├── package.json  # Node dependencies
│   └── INTEGRATION_GUIDE.md  # Detailed integration documentation
│
└── README.md         # This file
```

## Quick Start

### 🐳 Option 1: Docker (Recommended - Works on Any Device)

**Prerequisites:** Docker Desktop installed

```bash
# 1. Set your Gemini API key
cd backend
echo "GEMINI_API_KEY=your_api_key_here" > .env
cd ..

# 2. Start everything with one command
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

**See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for complete Docker instructions**

---

### 💻 Option 2: Local Development

**Prerequisites:** Python 3.9+, Node.js 18+, npm

### 1. Start the Backend

```bash
cd backend
pip3 install -r requirements.txt
python3 run_api.py
```

Backend will run at: **http://localhost:8000**

API Documentation: **http://localhost:8000/api/docs**

### 2. Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at: **http://localhost:5173**

### 3. Access the Application

Open your browser to **http://localhost:5173** and start analyzing data!

## Features

### Backend (FastAPI)
- RESTful API for data management
- CSV file upload and processing
- AI-powered data analysis with pandas
- Automatic EDA (Exploratory Data Analysis)
- Visualization generation with matplotlib/seaborn
- SQLite database for persistence
- CORS enabled for frontend integration

### Frontend (React + TypeScript)
- Modern, responsive UI with shadcn/ui components
- Project and chat management
- Real-time AI conversation interface
- Interactive data visualizations
- Dataset context viewer
- Type-safe API integration with Zustand state management

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python3 run_api.py

# Run tests (if available)
pytest

# Check logs
tail -f api.log
```

### Frontend Development

```bash
cd frontend

# Development server with HMR
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

### Backend (.env in backend/)
```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env in frontend/)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Endpoints

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/upload` - Upload CSV and create project
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/context` - Get dataset context (EDA)
- `DELETE /api/projects/{id}` - Delete project

### Chats
- `GET /api/chats/{projectId}` - List chats for project
- `POST /api/chats/{projectId}` - Create new chat
- `GET /api/chats/{projectId}/{chatId}/messages` - Get chat messages
- `DELETE /api/chats/{projectId}/{chatId}` - Delete chat

### AI Analysis
- `POST /api/ai/{projectId}/{chatId}/query` - Send analysis query
- `DELETE /api/ai/{projectId}/session` - Clear AI session

### Static Files
- `GET /static/plots/{filename}` - Get generated plot
- `GET /api/download/{filename}` - Download modified dataset

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM
- **pandas** - Data analysis
- **matplotlib/seaborn** - Visualizations
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Zustand** - State management
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Radix UI** - Accessible primitives
- **date-fns** - Date utilities

## Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Deployment

### Backend Deployment
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy dist/ folder to static hosting (Vercel, Netlify, etc.)
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Database locked:**
```bash
rm backend/data/app.db
# Restart backend to recreate database
```

### Frontend Issues

**API connection errors:**
- Verify backend is running on port 8000
- Check CORS configuration in `backend/api/main.py`
- Verify `.env` file has correct `VITE_API_BASE_URL`

**Build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Documentation

- **Frontend Integration Guide**: `frontend/INTEGRATION_GUIDE.md`
- **API Documentation**: http://localhost:8000/api/docs (when backend running)
- **Backend Code**: `backend/api/`
- **Frontend Code**: `frontend/src/`

## License

Proprietary - Internal Use Only

## Support

For issues or questions, contact the development team.
