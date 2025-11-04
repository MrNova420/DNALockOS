#!/bin/bash
#
# DNA-Key Authentication System - Production-Ready Startup Script
# Starts backend API and frontend web application with full error handling
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_PORT="${DNAKEY_API_PORT:-8000}"
API_HOST="${DNAKEY_API_HOST:-0.0.0.0}"
FRONTEND_PORT="${DNAKEY_FRONTEND_PORT:-3000}"
LOG_DIR="logs"
API_LOG="$LOG_DIR/api.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create logs directory
mkdir -p "$LOG_DIR"

echo -e "${CYAN}🔷 DNA-KEY AUTHENTICATION SYSTEM - PRODUCTION STARTUP${NC}"
echo "========================================================================"
echo ""

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $name failed to start within 30 seconds${NC}"
    return 1
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    
    if [ ! -z "$API_PID" ] && ps -p $API_PID > /dev/null 2>&1; then
        echo "   → Stopping Backend API (PID: $API_PID)"
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "   → Stopping Frontend Server (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM EXIT

# System validation
echo -e "${BLUE}📋 SYSTEM VALIDATION${NC}"
echo "──────────────────────────────────────────────────────────────────────"

# Check Python version
echo -n "   Python version: "
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}$PYTHON_VERSION${NC}"

# Check if Python 3.8+ is installed
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed${NC}"
    exit 1
fi
echo -e "   pip3: ${GREEN}✓${NC}"

# Check Python dependencies
echo ""
echo -e "${BLUE}📦 CHECKING DEPENDENCIES${NC}"
echo "──────────────────────────────────────────────────────────────────────"
python3 -c "import nacl, fastapi, uvicorn, cbor2, argon2, cryptography" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Installing Python dependencies...${NC}"
    pip3 install --user -r requirements.txt || {
        echo -e "${RED}❌ Failed to install Python dependencies${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
}
echo -e "   Python packages: ${GREEN}✓ All required packages available${NC}"

# Check Node.js if frontend exists
FRONTEND_AVAILABLE=false
if [ -d "web/frontend" ]; then
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1)
        echo -e "   Node.js: ${GREEN}$NODE_VERSION${NC}"
        
        if [ -d "web/frontend/node_modules" ]; then
            echo -e "   Frontend dependencies: ${GREEN}✓ Installed${NC}"
            FRONTEND_AVAILABLE=true
        else
            echo -e "   Frontend dependencies: ${YELLOW}⚠️  Not installed${NC}"
            echo -e "   ${YELLOW}Run: cd web/frontend && npm install${NC}"
        fi
    else
        echo -e "   Node.js: ${YELLOW}⚠️  Not installed (frontend unavailable)${NC}"
    fi
fi

# Check port availability
echo ""
echo -e "${BLUE}🔌 CHECKING PORTS${NC}"
echo "──────────────────────────────────────────────────────────────────────"
if ! check_port $API_PORT; then
    echo -e "${RED}❌ Port $API_PORT is already in use${NC}"
    exit 1
fi
echo -e "   API port $API_PORT: ${GREEN}✓ Available${NC}"

if [ "$FRONTEND_AVAILABLE" = true ]; then
    if ! check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}⚠️  Port $FRONTEND_PORT is already in use (frontend will not start)${NC}"
        FRONTEND_AVAILABLE=false
    else
        echo -e "   Frontend port $FRONTEND_PORT: ${GREEN}✓ Available${NC}"
    fi
fi

# Start services
echo ""
echo -e "${BLUE}🚀 STARTING SERVICES${NC}"
echo "========================================================================"

# Start Backend API
echo ""
echo -e "${CYAN}🔷 Starting Backend API Server...${NC}"
echo "   → Host: $API_HOST"
echo "   → Port: $API_PORT"
echo "   → URL: http://localhost:$API_PORT"
echo "   → API Docs: http://localhost:$API_PORT/docs"
echo "   → Log: $API_LOG"

# Start API with proper environment
export DNAKEY_API_HOST="$API_HOST"
export DNAKEY_API_PORT="$API_PORT"
python3 -m server.api.main > "$API_LOG" 2>&1 &
API_PID=$!
echo "   → PID: $API_PID"

# Wait for API to be ready
if wait_for_service "http://localhost:$API_PORT/health" "Backend API"; then
    echo -e "${GREEN}✅ Backend API is operational${NC}"
else
    echo -e "${RED}❌ Backend API failed to start. Check $API_LOG for details${NC}"
    tail -20 "$API_LOG"
    exit 1
fi

# Start Frontend if available
FRONTEND_PID=""
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo ""
    echo -e "${CYAN}🌐 Starting Frontend Server...${NC}"
    echo "   → Port: $FRONTEND_PORT"
    echo "   → URL: http://localhost:$FRONTEND_PORT"
    echo "   → Log: $FRONTEND_LOG"
    
    cd web/frontend
    PORT=$FRONTEND_PORT npm run dev > "../../$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    cd "$DIR"
    echo "   → PID: $FRONTEND_PID"
    
    # Give frontend a moment to start
    sleep 3
    
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend server started${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend may have failed to start. Check $FRONTEND_LOG${NC}"
        FRONTEND_PID=""
    fi
fi

# Display system status
echo ""
echo "========================================================================"
echo -e "${GREEN}✅ SYSTEM OPERATIONAL${NC}"
echo "========================================================================"
echo ""
echo -e "${CYAN}📊 Service Status:${NC}"
echo "   Backend API:  http://localhost:$API_PORT (PID: $API_PID)"
echo "   API Docs:     http://localhost:$API_PORT/docs"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   Frontend:     http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
fi
echo ""
echo -e "${CYAN}💻 CLI Tool:${NC}"
echo "   python3 dnakey_cli.py --help"
echo ""
echo -e "${CYAN}📝 Logs:${NC}"
echo "   Backend:      tail -f $API_LOG"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   Frontend:     tail -f $FRONTEND_LOG"
fi
echo ""
echo -e "${CYAN}🔧 Environment Variables:${NC}"
echo "   DNAKEY_API_HOST=$API_HOST"
echo "   DNAKEY_API_PORT=$API_PORT"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   DNAKEY_FRONTEND_PORT=$FRONTEND_PORT"
fi
echo ""
echo "========================================================================"
echo -e "${YELLOW}Press Ctrl+C to stop all services...${NC}"
echo ""

# Keep script running and monitor services
while true; do
    # Check if API is still running
    if ! ps -p $API_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend API has stopped unexpectedly${NC}"
        exit 1
    fi
    
    # Check if frontend is still running (if it was started)
    if [ ! -z "$FRONTEND_PID" ] && ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Frontend has stopped${NC}"
        FRONTEND_PID=""
    fi
    
    sleep 5
done
