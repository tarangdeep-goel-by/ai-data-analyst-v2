# 🐳 Running Backend and Frontend Separately

This guide shows how to run the backend and frontend containers independently, allowing you to start, stop, and restart each service separately.

---

## 🎯 Quick Commands

### Start Backend Only
```bash
# Build backend image
docker build -t ai-analyst-backend ./backend

# Run backend container
docker run -d \
  --name ai-analyst-backend \
  -p 8000:8000 \
  -v ai-analyst-data:/app/data \
  -e GEMINI_API_KEY=your_api_key_here \
  --restart unless-stopped \
  ai-analyst-backend
```

### Start Frontend Only
```bash
# Build frontend image
docker build -t ai-analyst-frontend ./frontend

# Run frontend container
docker run -d \
  --name ai-analyst-frontend \
  -p 80:80 \
  --restart unless-stopped \
  ai-analyst-frontend
```

---

## 📋 Detailed Instructions

### Option 1: Using Docker Run (Recommended)

#### Step 1: Build Images

```bash
# Navigate to project root
cd /path/to/ai-data-analyst-app

# Build backend
docker build -t ai-analyst-backend ./backend

# Build frontend
docker build -t ai-analyst-frontend ./frontend
```

#### Step 2: Start Backend

```bash
docker run -d \
  --name ai-analyst-backend \
  -p 8000:8000 \
  -v ai-analyst-data:/app/data \
  -e GEMINI_API_KEY=your_actual_api_key_here \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  --restart unless-stopped \
  ai-analyst-backend
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","gemini_configured":true}
```

#### Step 3: Start Frontend

```bash
docker run -d \
  --name ai-analyst-frontend \
  -p 80:80 \
  --restart unless-stopped \
  ai-analyst-frontend
```

**Access frontend:** Open http://localhost in your browser

---

### Option 2: Using Docker Compose with Individual Services

You can still use docker-compose but start services separately:

#### Start Backend Only
```bash
docker-compose up -d backend
```

#### Start Frontend Only
```bash
docker-compose up -d frontend
```

#### Start Both (but separately controllable)
```bash
docker-compose up -d backend
docker-compose up -d frontend
```

---

## 🛑 Stopping Services Separately

### Using Docker Run

```bash
# Stop backend only
docker stop ai-analyst-backend

# Stop frontend only
docker stop ai-analyst-frontend

# Start them again
docker start ai-analyst-backend
docker start ai-analyst-frontend

# Restart backend only
docker restart ai-analyst-backend

# Restart frontend only
docker restart ai-analyst-frontend
```

### Using Docker Compose

```bash
# Stop backend only
docker-compose stop backend

# Stop frontend only
docker-compose stop frontend

# Start backend only
docker-compose start backend

# Start frontend only
docker-compose start frontend

# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend
```

---

## 📊 Monitoring Individual Services

### View Logs

#### Backend Logs
```bash
# Docker run
docker logs -f ai-analyst-backend

# Docker compose
docker-compose logs -f backend
```

#### Frontend Logs
```bash
# Docker run
docker logs -f ai-analyst-frontend

# Docker compose
docker-compose logs -f frontend
```

### Check Status

```bash
# List all running containers
docker ps

# Check specific container
docker ps -f name=ai-analyst-backend
docker ps -f name=ai-analyst-frontend
```

### Resource Usage

```bash
# All containers
docker stats

# Backend only
docker stats ai-analyst-backend

# Frontend only
docker stats ai-analyst-frontend
```

---

## 🔄 Rebuilding Individual Services

### After Backend Code Changes

```bash
# Using docker run
docker stop ai-analyst-backend
docker rm ai-analyst-backend
docker build -t ai-analyst-backend ./backend
docker run -d \
  --name ai-analyst-backend \
  -p 8000:8000 \
  -v ai-analyst-data:/app/data \
  -e GEMINI_API_KEY=your_key \
  --restart unless-stopped \
  ai-analyst-backend

# Using docker-compose
docker-compose up -d --build backend
```

### After Frontend Code Changes

```bash
# Using docker run
docker stop ai-analyst-frontend
docker rm ai-analyst-frontend
docker build -t ai-analyst-frontend ./frontend
docker run -d \
  --name ai-analyst-frontend \
  -p 80:80 \
  --restart unless-stopped \
  ai-analyst-frontend

# Using docker-compose
docker-compose up -d --build frontend
```

---

## 🗑️ Removing Services

### Remove Backend

```bash
# Stop and remove container
docker stop ai-analyst-backend
docker rm ai-analyst-backend

# Remove image (optional)
docker rmi ai-analyst-backend

# Remove data volume (CAUTION: deletes all projects)
docker volume rm ai-analyst-data
```

### Remove Frontend

```bash
# Stop and remove container
docker stop ai-analyst-frontend
docker rm ai-analyst-frontend

# Remove image (optional)
docker rmi ai-analyst-frontend
```

---

## 🔧 Advanced: Running on Different Ports

### Backend on Port 9000

```bash
docker run -d \
  --name ai-analyst-backend \
  -p 9000:8000 \
  -v ai-analyst-data:/app/data \
  -e GEMINI_API_KEY=your_key \
  ai-analyst-backend

# Access at: http://localhost:9000
```

### Frontend on Port 3000

```bash
docker run -d \
  --name ai-analyst-frontend \
  -p 3000:80 \
  ai-analyst-frontend

# Access at: http://localhost:3000
```

**Note:** If you change the backend port, update the frontend environment variable:

```bash
docker run -d \
  --name ai-analyst-frontend \
  -p 3000:80 \
  -e VITE_API_BASE_URL=http://localhost:9000 \
  ai-analyst-frontend
```

---

## 📝 Helper Scripts

### Create Convenience Scripts

**`start-backend.sh`**
```bash
#!/bin/bash
docker run -d \
  --name ai-analyst-backend \
  -p 8000:8000 \
  -v ai-analyst-data:/app/data \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  --restart unless-stopped \
  ai-analyst-backend
```

**`start-frontend.sh`**
```bash
#!/bin/bash
docker run -d \
  --name ai-analyst-frontend \
  -p 80:80 \
  --restart unless-stopped \
  ai-analyst-frontend
```

**`stop-backend.sh`**
```bash
#!/bin/bash
docker stop ai-analyst-backend
```

**`stop-frontend.sh`**
```bash
#!/bin/bash
docker stop ai-analyst-frontend
```

**Make them executable:**
```bash
chmod +x start-backend.sh start-frontend.sh stop-backend.sh stop-frontend.sh
```

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check if container exists
docker ps -a -f name=ai-analyst-backend

# View logs
docker logs ai-analyst-backend

# Remove and recreate
docker rm -f ai-analyst-backend
docker run -d ... # (full command)
```

### Frontend Can't Connect to Backend

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS settings** in `backend/api/main.py`

3. **Clear browser cache** and hard refresh (Ctrl+Shift+R)

### Port Already in Use

```bash
# Find what's using the port
lsof -ti:8000  # or :80

# Kill the process
lsof -ti:8000 | xargs kill -9

# Or use different port
docker run ... -p 9000:8000 ...
```

---

## 📊 Comparison: Docker Run vs Docker Compose

| Feature | Docker Run | Docker Compose |
|---------|------------|----------------|
| **Start separately** | ✅ Yes | ✅ Yes |
| **Stop separately** | ✅ Yes | ✅ Yes |
| **Easier commands** | ❌ Longer | ✅ Shorter |
| **Network setup** | Manual | Automatic |
| **Environment vars** | Command line | .env file |
| **Best for** | Production | Development |

**Recommendation:** Use **docker-compose** with separate service commands for best balance:

```bash
# Start
docker-compose up -d backend
docker-compose up -d frontend

# Stop
docker-compose stop backend
docker-compose stop frontend

# Restart one
docker-compose restart backend

# View logs
docker-compose logs -f backend
```

---

## ✅ Quick Reference

### Most Common Commands

```bash
# START SEPARATELY
docker-compose up -d backend   # Start backend only
docker-compose up -d frontend  # Start frontend only

# STOP SEPARATELY
docker-compose stop backend    # Stop backend only
docker-compose stop frontend   # Stop frontend only

# RESTART SEPARATELY
docker-compose restart backend   # Restart backend only
docker-compose restart frontend  # Restart frontend only

# VIEW LOGS SEPARATELY
docker-compose logs -f backend   # Backend logs
docker-compose logs -f frontend  # Frontend logs

# REBUILD SEPARATELY
docker-compose up -d --build backend   # Rebuild backend
docker-compose up -d --build frontend  # Rebuild frontend

# CHECK STATUS
docker-compose ps               # See what's running
docker ps                       # All containers
```

---

## 💡 Pro Tips

1. **Use docker-compose for easier management** - Even when running separately, docker-compose commands are simpler

2. **Keep data volume** - The `ai-analyst-data` volume persists even when containers are removed

3. **View both logs simultaneously**:
   ```bash
   # Terminal 1
   docker-compose logs -f backend

   # Terminal 2
   docker-compose logs -f frontend
   ```

4. **Quick restart after code changes**:
   ```bash
   docker-compose up -d --build backend  # Rebuilds and restarts
   ```

5. **Health check**:
   ```bash
   # Backend
   curl http://localhost:8000/health

   # Frontend
   curl http://localhost/health
   ```

---

**Now you can start, stop, and manage each service independently!** 🎉
