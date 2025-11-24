#!/bin/bash

# ============================================
# AI Kitchen Assistant - Setup and Run Script
# ============================================
#
# This script automates the setup and execution of the AI Kitchen Assistant application.
# It performs the following tasks:
# 1. Checks for required dependencies (Python 3, pip3)
# 2. Creates and activates a Python virtual environment
# 3. Installs required Python packages
# 4. Sets up necessary directories
# 5. Runs the Flask application
#
# Usage:
#     ./run.sh
#
# Environment Variables:
#     - FLASK_APP: Set to 'app.py' (automatically configured)
#     - FLASK_ENV: Set to 'development' (can be overridden in .env)

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print a success message
print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

# Function to print a warning message
print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Function to print an error message and exit
print_error() {
    echo -e "${RED}[✗] $1${NC}" >&2
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${GREEN}🚀 Starting AI Kitchen Assistant setup...${NC}\n"

# Check if Python 3 is installed
if ! command_exists python3; then
    print_error "Python 3 is required but not installed. Please install Python 3.8 or higher."
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
    print_warning "Python 3.8 or higher is recommended. Detected version: $PYTHON_VERSION"
fi

# Check if pip is installed
if ! command_exists pip3; then
    print_error "pip3 is required but not installed. Please install pip3."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_success "Creating virtual environment..."
    python3 -m venv venv || print_error "Failed to create virtual environment"
fi

# Activate virtual environment
print_success "Activating virtual environment..."
source venv/bin/activate || print_error "Failed to activate virtual environment"

# Install/update pip and setuptools
print_success "Updating pip and setuptools..."
pip install --upgrade pip setuptools || print_error "Failed to update pip and setuptools"

# Install dependencies
print_success "Installing dependencies..."
pip install -r requirements.txt || print_warning "Some dependencies failed to install"

# Create necessary directories
print_success "Setting up directories..."
mkdir -p temp_uploads
chmod 755 temp_uploads

# Set default environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    # Read each line in .env file
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip comments and empty lines
        if [[ "$line" =~ ^[^#]*= && ! "$line" =~ ^[[:space:]]*# ]]; then
            # Export the variable
            export "$line"
        fi
    done < .env
fi

# Run the application
print_success "Starting the application..."
echo -e "\n${GREEN}✅ Setup completed successfully!${NC}"
echo -e "${YELLOW}🌐 Open http://localhost:5050 in your browser to access the application.${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop the server.${NC}\n"

# Run Flask with debug mode if in development
if [ "$FLASK_ENV" = "development" ]; then
    flask run --host=0.0.0.0 --port=5050 --debug
else
    flask run --host=0.0.0.0 --port=5050
fi
