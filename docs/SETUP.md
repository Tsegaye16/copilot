# Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose (optional)
- Google Gemini API key
- GitHub App credentials

## Quick Start with Docker

1. Clone the repository
2. Copy environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp github-app/.env.example github-app/.env
   ```

3. Update `.env` files with your credentials:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GITHUB_APP_ID`: Your GitHub App ID
   - `GITHUB_APP_PRIVATE_KEY`: Your GitHub App private key
   - `GITHUB_WEBHOOK_SECRET`: Your webhook secret

4. Start services:
   ```bash
   docker-compose up -d
   ```

5. Access the API:
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - GitHub App: http://localhost:3000

## Manual Setup

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run the server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### GitHub App Setup

1. Navigate to github-app directory:
   ```bash
   cd github-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub App credentials
   ```

4. Build TypeScript:
   ```bash
   npm run build
   ```

5. Run the app:
   ```bash
   npm start
   ```

## GitHub App Configuration

1. Create a GitHub App:
   - Go to GitHub Settings > Developer settings > GitHub Apps
   - Create a new app
   - Set webhook URL: `https://your-domain.com/webhook`
   - Grant permissions:
     - Repository contents: Read
     - Pull requests: Read & Write
     - Issues: Write
     - Commit statuses: Write

2. Install the app on your repositories

3. Configure webhook secret

## Testing

Run the test suite:
```bash
cd backend
pytest
```

## Production Deployment

See `docs/DEPLOYMENT.md` for production deployment instructions.
