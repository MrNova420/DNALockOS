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

# DNALockOS Deployment Script
# Prepares the system for production deployment
# Supports both standard and mobile/Termux environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

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

# Cleanup function for failed deployments
cleanup_on_failure() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}[✗]${NC} Deployment failed. Cleaning up..."
        if [ -d "venv_prod" ] && [ ! -f "venv_prod/.deploy_complete" ]; then
            rm -rf venv_prod
            echo -e "${YELLOW}[!]${NC} Removed incomplete production environment"
        fi
    fi
}

# Set trap for cleanup on exit
trap cleanup_on_failure EXIT

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           DNALockOS - Production Deployment Script                     ║"
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
    print_info "Detected Termux environment - using mobile configuration"
elif [ "$IS_ANDROID" = true ]; then
    print_info "Detected Android environment - using mobile configuration"
fi

# Check for required tools
print_info "Checking required tools..."

check_command() {
    if command -v $1 &> /dev/null; then
        print_status "$1 found"
        return 0
    else
        print_warning "$1 not found"
        return 1
    fi
}

# Find Python command
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        print_status "$cmd found"
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

# Check for pip
if ! command -v pip &> /dev/null && ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip not found"
    exit 1
fi
print_status "pip found"

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    print_error "Python 3.10+ required. Found Python $PYTHON_VERSION"
    exit 1
fi
print_status "Python $PYTHON_VERSION"

# Determine requirements file
REQUIREMENTS_FILE="requirements.txt"
if [ "$IS_MOBILE" = true ]; then
    if [ -f "requirements-mobile.txt" ]; then
        REQUIREMENTS_FILE="requirements-mobile.txt"
        print_info "Using mobile requirements for deployment"
    fi
fi

# Create production virtual environment
print_info "Setting up production environment..."
if [ -d "venv_prod" ]; then
    print_warning "Removing existing production environment..."
    rm -rf venv_prod
fi

$PYTHON_CMD -m venv venv_prod
if [ -f "venv_prod/bin/activate" ]; then
    source venv_prod/bin/activate
elif [ -f "venv_prod/Scripts/activate" ]; then
    source venv_prod/Scripts/activate
else
    print_error "Failed to create virtual environment"
    exit 1
fi
print_status "Production virtual environment created"

# Install production dependencies
print_info "Installing production dependencies from $REQUIREMENTS_FILE..."
pip install --upgrade pip > /dev/null 2>&1 || true

if pip install -r "$REQUIREMENTS_FILE" --no-cache-dir 2>&1; then
    print_status "Dependencies installed"
else
    print_warning "Some dependencies failed to install"
    if [ "$IS_MOBILE" = true ]; then
        print_info "This is expected on mobile platforms"
        print_info "The system will run in degraded mode with available features"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Run tests (skip on mobile if tests require unavailable dependencies)
print_info "Running test suite..."
if [ "$IS_MOBILE" = true ]; then
    print_warning "Skipping full test suite on mobile platform"
    # Run basic import test instead
    if $PYTHON_CMD -c "from server.api.main import app; print('Import OK')" 2>&1; then
        print_status "Basic import test passed"
    else
        print_warning "Some imports failed - running in degraded mode"
    fi
else
    if $PYTHON_CMD -m pytest tests/unit/ -q --tb=no 2>&1; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed. Review before deploying to production."
    fi
fi

# Verify system
print_info "Verifying system integrity..."
VERIFY_RESULT=$($PYTHON_CMD -c "
try:
    from server.api.main import app, CORE_SERVICES_AVAILABLE
    if CORE_SERVICES_AVAILABLE:
        print('FULL')
    else:
        print('DEGRADED')
except Exception as e:
    print(f'ERROR:{e}')
" 2>&1)

if [ "$VERIFY_RESULT" = "FULL" ]; then
    print_status "System verification passed - full functionality"
elif [ "$VERIFY_RESULT" = "DEGRADED" ]; then
    print_warning "System verification passed - degraded mode (some features unavailable)"
else
    print_warning "System verification issues: ${VERIFY_RESULT#ERROR:}"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "IMPORTANT: Edit .env file with production values!"
    else
        print_warning "No .env.example file found - using defaults"
    fi
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_status "Logs directory created"
fi

# Mark deployment as complete (for cleanup function)
touch venv_prod/.deploy_complete

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Preparation Complete!                          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$IS_MOBILE" = true ]; then
    echo -e "${YELLOW}Mobile/Termux Deployment Notes:${NC}"
    echo "  - Running in lightweight mode"
    echo "  - Some features may be unavailable (uvloop, pyzmq)"
    echo "  - Using cryptography library for crypto operations"
    echo ""
fi

echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Edit .env with production values"
if [ "$IS_MOBILE" != true ]; then
    echo "  2. Set up a process manager (systemd, supervisor, or PM2)"
    echo "  3. Configure a reverse proxy (nginx or caddy)"
    echo "  4. Enable HTTPS with SSL certificates"
fi
echo ""
echo -e "${CYAN}Start Production Server:${NC}"
echo "  source venv_prod/bin/activate"
if [ "$IS_MOBILE" = true ]; then
    echo "  python -m uvicorn server.api.main:app --host 0.0.0.0 --port 8000"
else
    echo "  uvicorn server.api.main:app --host 0.0.0.0 --port 8000 --workers 4"
fi
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo "  See PLATFORM_START_GUIDE.md for detailed deployment instructions"
echo ""