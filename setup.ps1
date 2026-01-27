# Setup script for Enterprise Guardrails Solution (PowerShell)

Write-Host "🚀 Setting up Enterprise GitHub Copilot Guardrails Solution..." -ForegroundColor Green

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Cyan
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python 3.9+ required" -ForegroundColor Red
    exit 1
}

# Check Node.js version
Write-Host "📋 Checking Node.js version..." -ForegroundColor Cyan
node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js 18+ required" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host "🐍 Setting up Python backend..." -ForegroundColor Cyan
Set-Location backend
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Set-Location ..

# Setup GitHub App
Write-Host "📦 Setting up GitHub App..." -ForegroundColor Cyan
Set-Location github-app
npm install
npm run build
Set-Location ..

# Setup GitHub Action
Write-Host "⚙️ Setting up GitHub Action..." -ForegroundColor Cyan
Set-Location github-action
npm install
npm run build
Set-Location ..

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path config\policies | Out-Null

# Copy environment files if they don't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Copying backend .env.example..." -ForegroundColor Cyan
    Copy-Item backend\.env.example backend\.env
    Write-Host "⚠️  Please edit backend\.env with your configuration" -ForegroundColor Yellow
}

if (-not (Test-Path "github-app\.env")) {
    Write-Host "📝 Copying github-app .env.example..." -ForegroundColor Cyan
    Copy-Item github-app\.env.example github-app\.env
    Write-Host "⚠️  Please edit github-app\.env with your GitHub App credentials" -ForegroundColor Yellow
}

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env with your Gemini API key"
Write-Host "2. Edit github-app\.env with your GitHub App credentials"
Write-Host "3. Run 'docker-compose up' to start all services"
Write-Host "   OR"
Write-Host "3. Run backend: 'cd backend && .\venv\Scripts\Activate.ps1 && uvicorn backend.main:app --reload'"
Write-Host "4. Run GitHub App: 'cd github-app && npm start'"
