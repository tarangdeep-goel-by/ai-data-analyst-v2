#!/bin/bash
# Start Backend Container

echo "🚀 Starting AI Data Analyst Backend..."

docker-compose up -d backend

echo "✅ Backend started!"
echo "📍 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "📊 View logs: docker-compose logs -f backend"
echo "🛑 Stop: docker-compose stop backend"
