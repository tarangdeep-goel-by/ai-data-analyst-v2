#!/bin/bash
# Stop All Services

echo "🛑 Stopping all services..."

docker-compose stop

echo "✅ All services stopped!"
echo ""
echo "🔄 To start again:"
echo "  Backend: ./start-backend.sh"
echo "  Frontend: ./start-frontend.sh"
echo "  Both: docker-compose up -d"
