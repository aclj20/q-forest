#!/bin/bash

# Q-FOREST Backend Setup Script

set -e  # Exit on error

echo "🌲 Q-FOREST Backend Setup"
echo "========================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads results

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Deactivate venv
deactivate

cd ..

echo -e "${GREEN}✨ Setup Complete!${NC}"
echo ""
echo "To start the API server:"
echo ""
echo "  cd backend"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "API will be available at http://localhost:8000"
echo "API Documentation at http://localhost:8000/docs"
echo ""
echo "📚 For more info, see README.md or backend/README.md"
