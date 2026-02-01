#!/bin/bash

# ScooterMap Setup Script
# Automates the initial setup process

set -e

echo "🗺️  ScooterMap - Real-Time Shared Mobility Heatmap"
echo "=================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please review and update if needed"
else
    echo "⚠️  .env file already exists"
fi
echo ""

# Create data directory
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
    echo "✅ Data directory created"
else
    echo "⚠️  Data directory already exists"
fi
echo ""

# Start Redpanda
echo "🚀 Starting Redpanda..."
docker compose up -d
echo "⏳ Waiting for Redpanda to be ready..."
sleep 5
echo "✅ Redpanda started"
echo ""

# Check Redpanda health
echo "🔍 Checking Redpanda status..."
if docker exec scootermap-redpanda rpk cluster health &> /dev/null; then
    echo "✅ Redpanda is healthy"
else
    echo "⚠️  Redpanda may not be fully ready yet"
fi
echo ""

# Final instructions
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the producer (in a new terminal):"
echo "   source .venv/bin/activate"
echo "   PYTHONPATH=backend python backend/app/run_producer.py"
echo ""
echo "2. Start the consumer (in another terminal):"
echo "   source .venv/bin/activate"
echo "   PYTHONPATH=backend python backend/app/run_consumer.py"
echo ""
echo "3. Start the API server (in another terminal):"
echo "   source .venv/bin/activate"
echo "   PYTHONPATH=backend python backend/app/main.py"
echo ""
echo "4. Access the API:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/api/health"
echo "   - Heatmap: http://localhost:8000/api/heatmap?resolution=6"
echo "   - Redpanda Console: http://localhost:8080"
echo ""
echo "=================================================="
