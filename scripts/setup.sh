#!/bin/bash
# =============================================================================
# Databricks PS Risk Assessment Tool - Setup Script
# =============================================================================

set -e

echo "=============================================="
echo "Databricks PS Risk Assessment Tool Setup"
echo "=============================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
echo ""
echo "Setting up React frontend..."
cd frontend
npm install
cd ..

# Create .env from template if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env with your Databricks credentials"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your Databricks credentials"
echo "2. Start the backend: python -m backend.app"
echo "3. Start the frontend: cd frontend && npm start"
echo "4. Start the dashboard: python dashboards/app.py"
echo ""
echo "Access the application at:"
echo "  - React UI: http://localhost:3000"
echo "  - Dash Dashboard: http://localhost:8050"
echo "  - Backend API: http://localhost:5000"
echo ""
