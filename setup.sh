#!/bin/bash

# Setup script for Enterprise Guardrails Solution

set -e

echo "🚀 Setting up Enterprise GitHub Copilot Guardrails Solution..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version || { echo "❌ Python 3.9+ required"; exit 1; }

# Check Node.js version
echo "📋 Checking Node.js version..."
node --version || { echo "❌ Node.js 18+ required"; exit 1; }

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Setup GitHub App
echo "📦 Setting up GitHub App..."
cd github-app
npm install
npm run build
cd ..

# Setup GitHub Action
echo "⚙️ Setting up GitHub Action..."
cd github-action
npm install
npm run build
cd ..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p config/policies

# Copy environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Copying backend .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

if [ ! -f github-app/.env ]; then
    echo "📝 Copying github-app .env.example..."
    cp github-app/.env.example github-app/.env
    echo "⚠️  Please edit github-app/.env with your GitHub App credentials"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Gemini API key"
echo "2. Edit github-app/.env with your GitHub App credentials"
echo "3. Run 'docker-compose up' to start all services"
echo "   OR"
echo "3. Run 'cd backend && source venv/bin/activate && uvicorn backend.main:app --reload' for backend"
echo "4. Run 'cd github-app && npm start' for GitHub App"
