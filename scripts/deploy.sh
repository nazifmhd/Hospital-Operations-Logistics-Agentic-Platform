#!/bin/bash

# Hospital Operations Platform - Build and Deploy Script
# This script builds and deploys the complete platform

set -e  # Exit on any error

echo "🏥 Hospital Operations Platform - Build & Deploy"
echo "==============================================="

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Building Hospital Operations Platform..."

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/kafka
mkdir -p data/influxdb

# Set environment variables
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check if backend is responding
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    print_success "Backend API is healthy"
else
    print_warning "Backend API is not responding yet. It may take a few more seconds."
fi

# Check if frontend is accessible
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend is not accessible yet. It may take a few more seconds."
fi

# Show running containers
print_status "Running containers:"
docker-compose ps

echo ""
print_success "🎉 Hospital Operations Platform deployed successfully!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Grafana Dashboard: http://localhost:3001 (admin/admin)"
echo ""
echo "🔧 Management commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""
echo "📈 Monitoring:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3001"
echo ""
