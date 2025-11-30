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

# Check for required tools
print_info "Checking required tools..."

check_command() {
    if command -v $1 &> /dev/null; then
        print_status "$1 found"
        return 0
    else
        print_error "$1 not found"
        return 1
    fi
}

MISSING_TOOLS=0
check_command python3 || MISSING_TOOLS=1
check_command pip || MISSING_TOOLS=1

if [ $MISSING_TOOLS -eq 1 ]; then
    print_error "Please install missing tools before continuing"
    exit 1
fi

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    print_error "Python 3.10+ required. Found Python $PYTHON_VERSION"
    exit 1
fi
print_status "Python $PYTHON_VERSION"

# Create production virtual environment
print_info "Setting up production environment..."
if [ -d "venv_prod" ]; then
    print_warning "Removing existing production environment..."
    rm -rf venv_prod
fi

python3 -m venv venv_prod
source venv_prod/bin/activate
print_status "Production virtual environment created"

# Install production dependencies
print_info "Installing production dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt --no-cache-dir
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi
print_status "Dependencies installed"

# Run tests
print_info "Running test suite..."
python3 -m pytest tests/unit/ -q --tb=no
if [ $? -ne 0 ]; then
    print_error "Some tests failed. Please fix before deploying."
    exit 1
fi
print_status "All tests passed"

# Verify system
print_info "Verifying system integrity..."
python3 validate_system.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_error "System validation failed"
    exit 1
fi
print_status "System validation passed"

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "IMPORTANT: Edit .env file with production values!"
    else
        print_error "No .env.example file found"
    fi
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_status "Logs directory created"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Preparation Complete!                          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Edit .env with production values"
echo "  2. Set up a process manager (systemd, supervisor, or PM2)"
echo "  3. Configure a reverse proxy (nginx or caddy)"
echo "  4. Enable HTTPS with SSL certificates"
echo ""
echo -e "${CYAN}Start Production Server:${NC}"
echo "  source venv_prod/bin/activate"
echo "  uvicorn server.api.main:app --host 0.0.0.0 --port 8000 --workers 4"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo "  See PLATFORM_START_GUIDE.md for detailed deployment instructions"
echo ""