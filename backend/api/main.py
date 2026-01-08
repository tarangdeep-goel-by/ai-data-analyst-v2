"""
FastAPI Main Application
REST API for AI Data Analyst backend
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers (will be created next)
from api.routers import projects, chats, ai_query

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Analyst API",
    description="REST API for conversational data analysis with AI",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default)
        "http://localhost:3000",  # Alternative dev port
        "http://localhost:8080",  # Another common dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["*"],
    max_age=3600,
)

# Static files for serving plots and downloads
os.makedirs("data/plots", exist_ok=True)
os.makedirs("data/temp_modifications", exist_ok=True)

app.mount("/static/plots", StaticFiles(directory="data/plots"), name="plots")
app.mount("/static/downloads", StaticFiles(directory="data/temp_modifications"), name="downloads")

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(chats.router, prefix="/api/chats", tags=["Chats"])
app.include_router(ai_query.router, prefix="/api/ai", tags=["AI Query"])

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Data Analyst API",
        "version": "2.0.0",
        "docs": "/api/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("GEMINI_API_KEY")
    return {
        "status": "healthy",
        "gemini_configured": bool(api_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
