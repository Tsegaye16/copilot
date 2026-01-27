"""
Enterprise GitHub Copilot Guardrails - Main Application
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

# Import modules - use absolute imports when running from backend directory
from api import scan, policies, audit, dashboard
from core.config import settings
from core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Enterprise Guardrails Service...")
    yield
    logger.info("Shutting down Enterprise Guardrails Service...")


app = FastAPI(
    title="Enterprise GitHub Copilot Guardrails",
    description="AI-powered code review and compliance enforcement for GitHub",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "guardrails"}


# API routes
app.include_router(scan.router, prefix="/api/v1/scan", tags=["Scan"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


if __name__ == "__main__":
    import uvicorn
    import os
    # Render sets PORT automatically, use it if available
    port = int(os.getenv("PORT", str(settings.PORT)))
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG
    )
