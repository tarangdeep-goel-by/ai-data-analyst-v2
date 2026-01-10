#!/bin/bash
# Start Frontend Container

echo "🚀 Starting AI Data Analyst Frontend..."

docker-compose up -d frontend

echo "✅ Frontend started!"
echo "📍 Application: http://localhost"
echo ""
echo "📊 View logs: docker-compose logs -f frontend"
echo "🛑 Stop: docker-compose stop frontend"
