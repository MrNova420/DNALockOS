#!/bin/bash
#
# DNA-Key Authentication System - Complete Startup Script
# Starts both backend API and frontend web application
#

set -e

echo "🔷 DNA-KEY AUTHENTICATION SYSTEM STARTUP"
echo "========================================"
echo ""

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
python3 -c "import nacl, fastapi, uvicorn" 2>/dev/null || {
    echo "⚠️  Installing Python dependencies..."
    pip3 install --user -r requirements.txt
    echo "✅ Python dependencies installed"
}

# Check if Node dependencies are installed (if needed)
if [ -d "web/frontend" ]; then
    echo "📦 Checking Node.js dependencies..."
    if [ ! -d "web/frontend/node_modules" ]; then
        echo "⚠️  Node modules not installed. Run 'cd web/frontend && npm install' to enable frontend."
    fi
fi

echo ""
echo "🚀 STARTING SERVICES..."
echo ""

# Start backend API
echo "🔷 Starting FastAPI Backend Server..."
echo "   → http://localhost:8000"
echo "   → API Docs: http://localhost:8000/api/docs"
echo ""

python3 -m server.api.main &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Check if API started
if ps -p $API_PID > /dev/null; then
    echo "✅ Backend API started successfully (PID: $API_PID)"
else
    echo "❌ Failed to start backend API"
    exit 1
fi

echo ""
echo "🌐 Frontend Note:"
if [ -d "web/frontend/node_modules" ]; then
    echo "   To start frontend: cd web/frontend && npm run dev"
    echo "   → http://localhost:3000"
else
    echo "   Install frontend: cd web/frontend && npm install && npm run dev"
fi

echo ""
echo "💻 CLI Tool:"
echo "   python3 dnakey_cli.py --help"
echo ""

echo "========================================"
echo "✅ SYSTEM STARTED!"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
trap "echo ''; echo 'Stopping services...'; kill $API_PID 2>/dev/null; echo '✅ Stopped'; exit 0" INT TERM

# Keep script running
wait $API_PID
