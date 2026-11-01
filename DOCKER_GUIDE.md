# 🐳 Docker Deployment Guide

Run the AI Data Analyst application on any device using Docker!

## 📋 Prerequisites

- **Docker Desktop** (includes Docker and Docker Compose)
  - **macOS/Windows:** [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - **Linux:** Install Docker Engine and Docker Compose separately

Verify installation:
```bash
docker --version
docker-compose --version
```

---

## ⚡ Quick Start (3 steps)

### 1. Set Your Gemini API Key

Export the key in your shell (Compose interpolates `${GEMINI_API_KEY}`), and create `backend/.env` because Compose mounts it:

```bash
export GEMINI_API_KEY=your_api_key_here
cd backend
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

The mounted `backend/.env` alone does not supply the key: Compose always sets `GEMINI_API_KEY` (empty if not exported) and python-dotenv does not override an existing variable. Alternatively, hard-code it in `docker-compose.yml` under `backend.environment`.

### 2. Build and Start

From the project root:

```bash
docker-compose up --build
```

### 3. Access the Application

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

**That's it!** 🎉

---

## 🎯 Common Commands

### Start the application
```bash
docker-compose up
```

### Start in background (detached mode)
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### Stop and remove all data
```bash
docker-compose down -v
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### View logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Check service status
```bash
docker-compose ps
```

### Restart a service
```bash
docker-compose restart backend
docker-compose restart frontend
```

---

## 📂 Project Structure

```
ai-data-analyst-app/
├── backend/
│   ├── Dockerfile           # Backend container config
│   ├── .dockerignore        # Files to exclude
│   ├── .env                 # Your API keys (create this)
│   └── ...
├── frontend/
│   ├── Dockerfile           # Frontend container config
│   ├── nginx.conf           # Web server config
│   ├── .dockerignore        # Files to exclude
│   └── ...
└── docker-compose.yml       # Orchestration config
```

---

## 🔧 Configuration

### Environment Variables

#### Backend (docker-compose.yml `environment`)
```env
GEMINI_API_KEY=${GEMINI_API_KEY}   # from your shell
API_HOST=0.0.0.0                   # set but not read; run_api.py always binds 0.0.0.0:8000
API_PORT=8000                      # set but not read
DATA_DIR=/app/data
```

#### Frontend
`VITE_API_BASE_URL` is a build-time variable. The value in `docker-compose.yml` is a runtime env var on the nginx container and has no effect on the built bundle. The build uses `frontend/.env` if it exists; most calls fall back to `http://localhost:8000`, but the CSV download button needs it set.

### Port Configuration

Default ports:
- Frontend: `80` (http://localhost)
- Backend: `8000` (http://localhost:8000)

To change ports, edit `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3000:80"  # Run on port 3000 instead

  backend:
    ports:
      - "9000:8000"  # Run on port 9000 instead
```

---

## 💾 Data Persistence

Project data is stored in a Docker volume named `backend-data`. This means:

✅ **Data persists** between container restarts
✅ **Projects remain** when you stop/start containers
✅ **Data is lost** only if you run `docker-compose down -v`

### Backup Data

```bash
# Create backup
docker run --rm -v ai-data-analyst-app_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore backup
docker run --rm -v ai-data-analyst-app_backend-data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

---

## 🚀 Deployment to Another Device

### Option 1: Using Docker Hub (Recommended)

**On your current device:**

```bash
# Build and tag images
docker build -t yourusername/ai-analyst-backend:latest ./backend
docker build -t yourusername/ai-analyst-frontend:latest ./frontend

# Push to Docker Hub
docker push yourusername/ai-analyst-backend:latest
docker push yourusername/ai-analyst-frontend:latest
```

**On the new device:**

```bash
# Pull and run
docker pull yourusername/ai-analyst-backend:latest
docker pull yourusername/ai-analyst-frontend:latest
docker-compose up
```

### Option 2: Export/Import Images

**On your current device:**

```bash
# Save images to tar files
docker save -o backend.tar ai-data-analyst-app-backend
docker save -o frontend.tar ai-data-analyst-app-frontend

# Transfer backend.tar and frontend.tar to the new device
```

**On the new device:**

```bash
# Load images
docker load -i backend.tar
docker load -i frontend.tar

# Run
docker-compose up
```

### Option 3: Clone Repository

**On any device:**

```bash
# Clone the repository
git clone https://github.com/tarangdeep-goel-by/ai-data-analyst-v2.git
cd ai-data-analyst-v2

# Checkout React branch
git checkout react-frontend

# Add your API key (exported; backend/.env must also exist for the mount)
export GEMINI_API_KEY=your_key
cd backend
echo "GEMINI_API_KEY=your_key" > .env
cd ..

# Start
docker-compose up --build
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change the port in docker-compose.yml
```

### Gemini API Not Configured

**Error:** `"gemini_configured": false`

**Solution:**
```bash
# Check if .env file exists
cat backend/.env

# The key must be exported in the shell that runs Compose;
# backend/.env does not override the (possibly empty) value Compose sets
export GEMINI_API_KEY=your_actual_key

# Rebuild
docker-compose up --build
```

### Cannot Connect to Backend

**Error:** `Failed to load projects` or CORS errors

**Solution:**
```bash
# Check backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

CORS: the frontend container is served from `http://localhost` (port 80), which is not in the allow list in `backend/api/main.py` (ports 5173, 3000, 8080 only). Add `http://localhost` there if browser requests are blocked.

### Build Fails

**Error:** Various build errors

**Solution:**
```bash
# Clean everything and rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Frontend Shows Blank Page

**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

---

## 🔍 Health Checks

Both services have built-in health checks:

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend health
curl http://localhost/health

# View health status in Docker
docker-compose ps
```

---

## 🛑 Stopping and Cleanup

### Stop without removing data
```bash
docker-compose down
```

### Stop and remove containers, networks
```bash
docker-compose down
```

### Stop and remove EVERYTHING (including data)
```bash
docker-compose down -v
```

### Remove all unused Docker resources
```bash
docker system prune -a
```

---

## 📊 Resource Usage

### View resource usage
```bash
docker stats
```

### Limit resources (docker-compose.yml)
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** with real API keys
2. **Use environment variables** for sensitive data
3. **Keep images updated**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```
4. **Scan images for vulnerabilities**:
   ```bash
   docker scan ai-data-analyst-app-backend
   ```

---

## 🌐 Production Deployment

For production, consider:

1. **Use a reverse proxy** (nginx, Traefik)
2. **Enable HTTPS** with Let's Encrypt
3. **Set up monitoring** (Prometheus, Grafana)
4. **Use Docker Swarm or Kubernetes** for orchestration
5. **Configure automatic backups**
6. **Set resource limits**
7. **Use production-grade WSGI server** (Gunicorn) instead of development server

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)

---

## 🆘 Need Help?

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify services: `docker-compose ps`
3. Check health: `curl http://localhost:8000/health`
4. Review this guide
5. Check GitHub issues

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Both containers are running: `docker-compose ps`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Frontend loads: Open http://localhost in browser
- [ ] Can upload CSV file
- [ ] Can create chat and send query
- [ ] Data persists after restart: `docker-compose restart`

---

**Happy Dockerizing! 🐳**
