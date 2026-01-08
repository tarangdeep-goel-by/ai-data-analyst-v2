# 🚀 AI Data Analyst - Startup Guide

## Prerequisites

- ✅ Python 3.9+
- ✅ Node.js 18+
- ✅ Google Gemini API Key

---

## 🔧 One-Time Setup

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip3 install -r requirements.txt

# Create .env file and add your Gemini API key
nano .env
```

Add to `.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./data/app.db
API_HOST=0.0.0.0
API_PORT=8000
DATA_DIR=data
```

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Verify .env exists (already configured)
cat .env
```

Should show:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## ▶️ Starting the Application

### Terminal 1: Start Backend

```bash
cd backend
python3 run_api.py
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend is Running:**
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy","gemini_configured":true}`
- API Docs: http://localhost:8000/api/docs

---

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  VITE v5.4.19  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Access the Application:**
- Open browser: **http://localhost:5173/** (or the port shown)
- Or: **http://localhost:8080/** (if running on different port)

---

## 🛑 Stopping the Application

### Stop Backend
In the backend terminal:
- Press `CTRL + C`

### Stop Frontend
In the frontend terminal:
- Press `CTRL + C`

---

## 🔄 Restarting After Code Changes

### Backend Changes
The backend auto-reloads with `--reload` flag. If not:
```bash
# In backend terminal
CTRL + C  # Stop
python3 run_api.py  # Restart
```

### Frontend Changes
Vite has Hot Module Replacement (HMR) - saves auto-refresh.
If needed:
```bash
# In frontend terminal
CTRL + C  # Stop
npm run dev  # Restart
```

---

## ✅ Quick Test

After starting both servers:

### 1. Test Backend API
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy","gemini_configured":true}`

### 2. Test Frontend
1. Open http://localhost:5173 (or 8080)
2. Click "New Project" button
3. Upload the `test_data.csv` file
4. Should see success toast and project in sidebar

### 3. Test Full Flow
1. Select the uploaded project
2. Click "Start New Chat"
3. Type: "Show me the first 5 rows"
4. Should see AI response with data

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or find and kill manually
lsof -i:8000
kill -9 <PID>
```

**Gemini API not configured:**
- Check `backend/.env` has `GEMINI_API_KEY=...`
- Verify API key is valid at: https://makersuite.google.com/app/apikey

**Module not found errors:**
```bash
cd backend
pip3 install -r requirements.txt
```

**Database locked:**
```bash
cd backend
rm data/app.db
# Restart backend - will recreate
```

---

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or Vite will suggest alternative port
# Use the port shown in terminal
```

**CORS errors in browser console:**
- Check backend is running on port 8000
- Check browser URL matches allowed origins:
  - ✅ http://localhost:5173
  - ✅ http://localhost:8080
  - ✅ http://localhost:3000
- If using different port, add to `backend/api/main.py` CORS config

**Module not found / Build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `frontend/.env` has correct URL
3. Check browser console for actual error

---

### Common CORS Issues

**Error:** `Access to fetch at 'http://localhost:8000/api/projects' from origin 'http://localhost:XXXX' has been blocked by CORS policy`

**Solution:**
1. Check what port your frontend is running on (check terminal or browser URL)
2. Add that port to `backend/api/main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:YOUR_PORT",  # Add your port here
    ...
],
```

3. Restart backend

---

## 📁 Project Structure After Startup

```
ai-data-analyst-app/
├── backend/
│   ├── data/                    # Created on first run
│   │   ├── projects/           # User projects stored here
│   │   ├── plots/              # Generated visualizations
│   │   └── temp_modifications/ # Modified datasets
│   └── api.log                 # Backend logs (if configured)
│
├── frontend/
│   └── dist/                    # Created after npm run build
│
└── test_data.csv               # Sample CSV for testing
```

---

## 🎯 What Each Server Does

### Backend (Port 8000)
- Handles CSV file uploads
- Stores project metadata
- Manages chat sessions
- Integrates with Google Gemini AI
- Executes generated Python code
- Generates visualizations
- Serves static files (plots, downloads)

### Frontend (Port 5173 or 8080)
- User interface
- File upload dialog
- Project management
- Chat interface
- API communication
- Real-time updates

---

## 📝 Environment Variables Reference

### Backend `.env`
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `DATABASE_URL` | No | `sqlite:///./data/app.db` | Database connection |
| `API_HOST` | No | `0.0.0.0` | Backend host |
| `API_PORT` | No | `8000` | Backend port |
| `DATA_DIR` | No | `data` | Data storage directory |

### Frontend `.env`
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Backend API URL |

---

## 🚀 Production Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to static hosting (Vercel, Netlify, etc.)
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs (when backend running)
- **Testing Guide:** See `POSTMAN_API_TESTS.md`
- **Architecture Guide:** See `CLAUDE.md`
- **Sample Data:** Use `test_data.csv` for testing

---

## ⚡ Quick Command Reference

```bash
# Backend
cd backend && python3 run_api.py          # Start
curl http://localhost:8000/health          # Test

# Frontend
cd frontend && npm run dev                 # Start
npm run build                              # Build for production
npm run preview                            # Preview production build

# Kill ports
lsof -ti:8000 | xargs kill -9             # Kill backend
lsof -ti:5173 | xargs kill -9             # Kill frontend

# Logs
tail -f backend/api.log                    # Watch backend logs (if configured)
```

---

## 🎉 You're Ready!

Start both servers and navigate to http://localhost:5173 (or 8080) to begin analyzing your data!
