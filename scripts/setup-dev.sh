#!/bin/bash

# Hospital Operations Platform - Development Setup Script

set -e

echo "🏥 Hospital Operations Platform - Development Setup"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION+ is required."
    exit 1
fi

print_success "Python $PYTHON_VERSION is installed"

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE_VERSION="18.0.0"

if [ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE_VERSION" ]; then
    print_error "Node.js $NODE_VERSION is installed, but Node.js $REQUIRED_NODE_VERSION+ is required."
    exit 1
fi

print_success "Node.js $NODE_VERSION is installed"

# Setup backend
print_status "Setting up Python backend..."

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

print_success "Backend dependencies installed"

# Setup frontend
print_status "Setting up React frontend..."
cd frontend

# Check if npm is available
if ! command -v npm >/dev/null 2>&1; then
    print_error "npm is not available. Please ensure Node.js is properly installed."
    exit 1
fi

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

print_success "Frontend dependencies installed"

cd ..

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating environment file..."
    cp config/.env.example .env
    print_warning "Please review and update the .env file with your configuration"
fi

# Create logs directory
mkdir -p logs

print_success "🎉 Development environment setup complete!"
echo ""
echo "🚀 To start development:"
echo "   1. Backend: source venv/bin/activate && python src/main.py"
echo "   2. Frontend: cd frontend && npm run dev"
echo ""
echo "📚 Useful commands:"
echo "   Run tests: pytest"
echo "   Format code: black src/"
echo "   Type checking: mypy src/"
echo "   Lint frontend: cd frontend && npm run lint"
echo ""
