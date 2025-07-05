#!/bin/bash

# LCSC Electronics Email Customer Service System - Startup Script
# Handles port conflicts and launches the application safely

set -e  # Exit on any error

# Configuration
PORT=7860
HOST="0.0.0.0"
APP_FILE="app.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🎯 LCSC Email Customer Service System${NC}"
    echo "=============================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find processes using the port
find_processes() {
    lsof -Pi :$PORT -sTCP:LISTEN 2>/dev/null || true
}

# Function to kill processes using the port
kill_port_processes() {
    local pids=$(lsof -ti :$PORT 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Found processes using port $PORT:"
        find_processes
        echo
        
        print_info "Automatically killing processes using port $PORT..."
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti :$PORT 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            print_warning "Force killing remaining processes..."
            echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
            sleep 1
        fi
        
        print_success "Processes terminated"
        return 0
    else
        print_success "No processes found using port $PORT"
        return 0
    fi
}

# Function to find alternative port
find_alternative_port() {
    local start_port=$((PORT + 1))
    local max_port=$((PORT + 10))
    
    for ((p=start_port; p<=max_port; p++)); do
        if ! lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $p
            return 0
        fi
    done
    
    return 1
}

# Function to check environment
check_environment() {
    print_info "Checking environment..."
    
    # Check if we're in the right directory
    if [ ! -f "$APP_FILE" ]; then
        print_error "$APP_FILE not found in current directory"
        print_info "Make sure you're in the lcsc-csagent directory"
        exit 1
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found"
        exit 1
    fi
    
    # Check if virtual environment is recommended
    if [ -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment detected but not activated"
        print_info "Consider running: source .venv/bin/activate"
        echo
    fi
    
    print_success "Environment check passed"
}

# Function to launch the app
launch_app() {
    local use_port=$1
    
    print_info "Launching LCSC Email Customer Service System on $HOST:$use_port"
    print_info "Access the interface at: http://localhost:$use_port"
    print_info "Press Ctrl+C to stop the server"
    echo "=============================================="
    
    # Modify the app.py port if different from default
    if [ "$use_port" != "$PORT" ]; then
        print_info "Using alternative port $use_port"
        # Create a temporary modified version
        sed "s/server_port=7860/server_port=$use_port/g" "$APP_FILE" > "${APP_FILE}.tmp"
        python3 "${APP_FILE}.tmp"
        rm -f "${APP_FILE}.tmp"
    else
        python3 "$APP_FILE"
    fi
}

# Main execution
main() {
    print_status
    
    # Check environment
    check_environment
    
    # Check if port is available
    if check_port; then
        print_warning "Port $PORT is already in use"
        
        # Automatically kill processes using the port
        kill_port_processes
        
        # Wait a moment and check again
        sleep 1
        if check_port; then
            print_error "Port $PORT still in use after cleanup"
            
            # Find alternative port
            alternative_port=$(find_alternative_port)
            if [ $? -eq 0 ]; then
                print_info "Using alternative port $alternative_port"
                launch_app $alternative_port
            else
                print_error "No available ports found"
                exit 1
            fi
        else
            print_success "Port $PORT is now available"
            launch_app $PORT
        fi
    else
        print_success "Port $PORT is available"
        launch_app $PORT
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}🛑 Server stopped by user${NC}"; exit 0' INT

# Run main function
main "$@"
