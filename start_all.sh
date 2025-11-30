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
# Supports both production and mobile/Termux environments

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

# Detect platform
IS_TERMUX=false
IS_ANDROID=false
IS_MOBILE=false

if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=true
    IS_MOBILE=true
fi

if [ -f "/system/build.prop" ] || [[ "$PREFIX" == *"termux"* ]]; then
    IS_ANDROID=true
    IS_MOBILE=true
fi

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

# Print platform info
if [ "$IS_TERMUX" = true ]; then
    print_info "Detected Termux environment"
elif [ "$IS_ANDROID" = true ]; then
    print_info "Detected Android environment"
fi

# Check for Python
print_info "Checking Python installation..."
PYTHON_CMD=""

# Try different Python commands
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python not found. Please install Python 3.10 or higher."
    if [ "$IS_TERMUX" = true ]; then
        print_info "On Termux, run: pkg install python"
    fi
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_status "Found $PYTHON_VERSION"

# Check Python version is 3.10+
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    print_error "Python 3.10 or higher is required. Found Python $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi

# Determine which requirements file to use
REQUIREMENTS_FILE="requirements.txt"
if [ "$IS_MOBILE" = true ]; then
    if [ -f "requirements-mobile.txt" ]; then
        print_info "Using mobile requirements file for Termux/Android"
        REQUIREMENTS_FILE="requirements-mobile.txt"
    else
        print_warning "Mobile requirements file not found, using standard requirements"
    fi
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        if [ "$IS_TERMUX" = true ]; then
            print_info "On Termux, you may need: pkg install python"
        fi
        exit 1
    fi
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    print_error "Cannot find virtual environment activation script"
    exit 1
fi

if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_status "Virtual environment activated"

# Install dependencies if needed
INSTALL_MARKER="venv/.installed_${REQUIREMENTS_FILE//\//_}"
if [ ! -f "$INSTALL_MARKER" ] || [ "$REQUIREMENTS_FILE" -nt "$INSTALL_MARKER" ]; then
    print_info "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip > /dev/null 2>&1 || true

    # Try to install dependencies with error handling
    if pip install -r "$REQUIREMENTS_FILE" 2>&1; then
        touch "$INSTALL_MARKER"
        print_status "Dependencies installed"
    else
        print_warning "Some dependencies failed to install"
        if [ "$IS_MOBILE" = true ]; then
            print_info "This is expected on mobile. Trying with mobile requirements..."
            if [ "$REQUIREMENTS_FILE" != "requirements-mobile.txt" ] && [ -f "requirements-mobile.txt" ]; then
                print_info "Falling back to requirements-mobile.txt..."
                pip install -r requirements-mobile.txt 2>&1 || true
                touch "venv/.installed_requirements-mobile.txt"
            fi
        fi
        print_warning "Continuing with available dependencies..."
    fi
else
    print_status "Dependencies already installed"
fi

# Verify core imports work (with fallback)
print_info "Verifying system integrity..."
IMPORT_CHECK=$($PYTHON_CMD -c "
try:
    from server.api.main import app
    print('OK')
except ImportError as e:
    print(f'WARN:{e}')
except Exception as e:
    print(f'ERROR:{e}')
" 2>&1)

if [[ "$IMPORT_CHECK" == "OK" ]]; then
    print_status "System verification passed"
elif [[ "$IMPORT_CHECK" == WARN:* ]]; then
    print_warning "Some modules not available: ${IMPORT_CHECK#WARN:}"
    print_info "Running in degraded mode..."
else
    print_error "System verification failed: ${IMPORT_CHECK#ERROR:}"
    print_info "Attempting to start anyway..."
fi

# Get host and port from environment or defaults
HOST="${DNAKEY_API_HOST:-0.0.0.0}"
PORT="${DNAKEY_API_PORT:-8000}"

# Kill any existing process on the port (with error handling)
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$PID" ]; then
        print_warning "Port $PORT is in use. Stopping existing process..."
        kill -TERM $PID 2>/dev/null || true
        sleep 2
        # If still running, force kill
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null || true
        fi
        sleep 1
    fi
elif command -v fuser &> /dev/null; then
    fuser -k $PORT/tcp 2>/dev/null || true
    sleep 1
fi

# Start the API server
print_info "Starting API server on http://$HOST:$PORT"

# Use different startup methods based on platform
if [ "$IS_MOBILE" = true ]; then
    # On mobile, run in foreground for better control
    print_info "Running in mobile mode (foreground)..."
    $PYTHON_CMD -m uvicorn server.api.main:app --host "$HOST" --port "$PORT" &
    API_PID=$!
else
    # On desktop/server, run with reload for development
    $PYTHON_CMD -m uvicorn server.api.main:app --host "$HOST" --port "$PORT" --reload &
    API_PID=$!
fi

# Wait for server to start
print_info "Waiting for server to start..."
for i in {1..10}; do
    sleep 1
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq 10 ]; then
        print_warning "Server may still be starting..."
    fi
done

# Check if server is running
if kill -0 $API_PID 2>/dev/null; then
    print_status "API server started successfully (PID: $API_PID)"
else
    print_error "Failed to start API server"
    print_info "Check the logs above for errors"
    exit 1
fi

# Test health endpoint
print_info "Testing health endpoint..."
HEALTH_CHECK=$(curl -s "http://localhost:$PORT/health" 2>/dev/null || echo "")
if [ -n "$HEALTH_CHECK" ]; then
    print_status "Health check passed"
    # Show status
    STATUS=$(echo "$HEALTH_CHECK" | grep -o '"status":"[^"]*"' | head -1 || echo "")
    if [ -n "$STATUS" ]; then
        print_info "Server status: ${STATUS}"
    fi
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
echo -e "  ${CYAN}Status:${NC}      http://localhost:$PORT/api/v1/status"
echo ""

if [ "$IS_MOBILE" = true ]; then
    echo -e "  ${YELLOW}Running in mobile/Termux mode${NC}"
    echo -e "  ${YELLOW}Some features may be limited${NC}"
    echo ""
fi

echo -e "  ${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for interrupt
trap "echo ''; print_info 'Shutting down...'; kill $API_PID 2>/dev/null; print_status 'DNALockOS stopped'; exit 0" INT TERM
wait