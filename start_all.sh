#!/bin/bash
# ==============================================================================
# DNALockOS - DNA-Key Authentication System
# Copyright (c) 2025 WeNova Interactive
# ==============================================================================
#
# OWNERSHIP: Kayden Shawn Massengill (Operating as WeNova Interactive)
#
# COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
#
# This is proprietary commercial software. A valid commercial license is
# required for ANY use. Unauthorized use, copying, modification, or
# distribution is strictly prohibited and will be prosecuted.
#
# For licensing inquiries: WeNova Interactive
# ==============================================================================

# DNALockOS Startup Script
# Starts all required services for the DNA-Key Authentication System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           DNALockOS - DNA-Key Authentication System                   ║"
echo "║                     Starting Services...                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[i]${NC} $1"
}

# Check for Python
print_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Found $PYTHON_VERSION"
else
    print_error "Python3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version is 3.10+
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    print_error "Python 3.10 or higher is required. Found Python $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_status "Virtual environment activated"

# Install dependencies if needed
if [ ! -f "venv/.installed" ] || [ "requirements.txt" -nt "venv/.installed" ]; then
    print_info "Installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        print_warning "If you're on Termux/Android, try: pkg install libsodium clang"
        exit 1
    fi
    touch venv/.installed
    print_status "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Verify core imports work
print_info "Verifying system integrity..."
python3 -c "from server.api.main import app" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Failed to import API server module"
    exit 1
fi
print_status "System verification passed"

# Get host and port from environment or defaults
HOST="${DNAKEY_API_HOST:-0.0.0.0}"
PORT="${DNAKEY_API_PORT:-8000}"

# Kill any existing process on the port
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        print_warning "Port $PORT is in use. Stopping existing process..."
        # Try graceful shutdown first
        kill -TERM $PID 2>/dev/null
        sleep 2
        # If still running, force kill
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null
        fi
        sleep 1
    fi
fi

# Start the API server
print_info "Starting API server on http://$HOST:$PORT"
python3 -m uvicorn server.api.main:app --host "$HOST" --port "$PORT" --reload &
API_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if kill -0 $API_PID 2>/dev/null; then
    print_status "API server started successfully (PID: $API_PID)"
else
    print_error "Failed to start API server"
    exit 1
fi

# Test health endpoint
print_info "Testing health endpoint..."
HEALTH_CHECK=$(curl -s "http://localhost:$PORT/health" 2>/dev/null)
if [ -n "$HEALTH_CHECK" ]; then
    print_status "Health check passed"
else
    print_warning "Health endpoint not responding yet (server may still be starting)"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   DNALockOS is running!                                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}API Server:${NC}  http://localhost:$PORT"
echo -e "  ${CYAN}API Docs:${NC}    http://localhost:$PORT/api/docs"
echo -e "  ${CYAN}Health:${NC}      http://localhost:$PORT/health"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for interrupt
trap "echo ''; print_info 'Shutting down...'; kill $API_PID 2>/dev/null; print_status 'DNALockOS stopped'; exit 0" INT TERM
wait