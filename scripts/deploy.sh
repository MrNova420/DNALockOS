#!/bin/bash
# DNALockOS - Production Deployment Script
# Copyright (c) 2025 WeNova Interactive
# Legal Owner: Kayden Shawn Massengill
# ALL RIGHTS RESERVED.
#
# PROPRIETARY AND CONFIDENTIAL
# Unauthorized use is strictly prohibited.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/dnalockos/deployment.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)  color=$GREEN ;;
        WARN)  color=$YELLOW ;;
        ERROR) color=$RED ;;
        *)     color=$NC ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE" 2>/dev/null || true
}

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo "║                    DNALockOS Production Deployment                   ║"
    echo "║                                                                      ║"
    echo "║              Copyright (c) 2025 WeNova Interactive                   ║"
    echo "║              Legal Owner: Kayden Shawn Massengill                    ║"
    echo "║                      ALL RIGHTS RESERVED                             ║"
    echo "║                                                                      ║"
    echo "║   PROPRIETARY AND CONFIDENTIAL - Unauthorized use is prohibited      ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    local missing=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing+=("pip3")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log ERROR "Missing prerequisites: ${missing[*]}"
        exit 1
    fi
    
    log INFO "All prerequisites satisfied"
}

# Verify system integrity
verify_integrity() {
    log INFO "Verifying system integrity..."
    
    cd "$PROJECT_ROOT"
    
    # Run integrity verification
    python3 -c "
from server.security.hardening import verify_system_integrity
if not verify_system_integrity():
    exit(1)
print('System integrity verified')
" || {
        log ERROR "System integrity verification failed"
        exit 1
    }
    
    log INFO "System integrity verified successfully"
}

# Create virtual environment
setup_virtualenv() {
    log INFO "Setting up virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log INFO "Virtual environment created"
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    log INFO "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    log INFO "Installing dependencies..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Install production dependencies
    pip install -r requirements.txt
    
    # Install production server
    pip install gunicorn uvicorn[standard]
    
    log INFO "Dependencies installed successfully"
}

# Validate configuration
validate_config() {
    log INFO "Validating configuration..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    python3 -c "
from server.config.production import get_config

config = get_config()
issues = config.validate()

if issues:
    print('Configuration issues found:')
    for issue in issues:
        print(f'  - {issue}')
    exit(1)
else:
    print('Configuration validated successfully')
" || {
        log ERROR "Configuration validation failed"
        exit 1
    }
    
    log INFO "Configuration validated successfully"
}

# Run security audit
run_security_audit() {
    log INFO "Running security audit..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run security checks
    python3 -c "
from server.security.hardening import SecurityHardeningEngine

engine = SecurityHardeningEngine()
engine.initialize()

# Check for debuggers
if engine.detect_debugger():
    print('WARNING: Debugger detected')

# Verify modules
if not engine.verify_all_modules():
    print('WARNING: Module integrity issues detected')

print('Security audit completed')
"
    
    log INFO "Security audit completed"
}

# Run all tests
run_tests() {
    log INFO "Running test suite..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run pytest
    python3 -m pytest tests/ -v --tb=short
    
    log INFO "All tests passed"
}

# Start production server
start_server() {
    log INFO "Starting production server..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Get configuration
    local host=${API_HOST:-0.0.0.0}
    local port=${API_PORT:-8000}
    local workers=${API_WORKERS:-4}
    
    # Start with gunicorn
    gunicorn server.api.main:app \
        --bind "$host:$port" \
        --workers "$workers" \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 30 \
        --keep-alive 5 \
        --capture-output \
        --daemon
    
    log INFO "Production server started on $host:$port"
}

# Stop production server
stop_server() {
    log INFO "Stopping production server..."
    
    pkill -f "gunicorn.*server.api.main" || true
    
    log INFO "Production server stopped"
}

# Health check
health_check() {
    log INFO "Running health check..."
    
    local host=${API_HOST:-localhost}
    local port=${API_PORT:-8000}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "http://$host:$port/health" || echo "000")
    
    if [ "$response" = "200" ]; then
        log INFO "Health check passed"
        return 0
    else
        log ERROR "Health check failed (HTTP $response)"
        return 1
    fi
}

# Full deployment
deploy() {
    print_banner
    
    log INFO "Starting DNALockOS production deployment..."
    log INFO "Timestamp: $TIMESTAMP"
    
    check_prerequisites
    verify_integrity
    setup_virtualenv
    install_dependencies
    validate_config
    run_security_audit
    run_tests
    stop_server
    start_server
    
    # Wait for server to start
    sleep 5
    
    health_check
    
    log INFO "═══════════════════════════════════════════════════════════════════"
    log INFO "DNALockOS deployment completed successfully!"
    log INFO "═══════════════════════════════════════════════════════════════════"
}

# Show usage
usage() {
    echo "DNALockOS Production Deployment Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  deploy          Full production deployment"
    echo "  start           Start production server"
    echo "  stop            Stop production server"
    echo "  restart         Restart production server"
    echo "  status          Check server status"
    echo "  health          Run health check"
    echo "  test            Run test suite"
    echo "  audit           Run security audit"
    echo "  validate        Validate configuration"
    echo ""
    echo "Environment Variables:"
    echo "  API_HOST        Server bind address (default: 0.0.0.0)"
    echo "  API_PORT        Server port (default: 8000)"
    echo "  API_WORKERS     Number of workers (default: 4)"
    echo "  DB_HOST         Database host"
    echo "  DB_PORT         Database port"
    echo "  DB_NAME         Database name"
    echo "  DB_USER         Database username"
    echo "  DB_PASSWORD     Database password"
    echo "  REDIS_HOST      Redis host"
    echo "  REDIS_PORT      Redis port"
    echo "  REDIS_PASSWORD  Redis password"
}

# Main entry point
main() {
    # Create log directory
    mkdir -p /var/log/dnalockos 2>/dev/null || true
    
    case "${1:-}" in
        deploy)
            deploy
            ;;
        start)
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart)
            stop_server
            sleep 2
            start_server
            ;;
        status)
            health_check
            ;;
        health)
            health_check
            ;;
        test)
            setup_virtualenv
            run_tests
            ;;
        audit)
            setup_virtualenv
            run_security_audit
            ;;
        validate)
            setup_virtualenv
            validate_config
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
