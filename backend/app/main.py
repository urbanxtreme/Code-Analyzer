"""
FastAPI application entry point.

Sets up:
- CORS middleware (allow all origins in dev)
- API router from app/api/routes.py
- Root welcome endpoint
- Structured logging
"""

import logging
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .utils.logger import setup_logging

# Initialise structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered GitHub Repository Intelligence Analyzer",
    description=(
        "Analyzes a public GitHub repository and returns a rich intelligence report "
        "covering contributor stats, commit quality, AI code estimation, contribution "
        "patterns, and LLM-generated insights."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins in development.
# In production restrict this to your frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API router
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint — confirms the backend is running."""
    return {
        "message": "AI-Powered GitHub Repository Intelligence Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "analyze": "POST /api/analyze",
    }
