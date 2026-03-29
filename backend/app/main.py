from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
import uvicorn

app = FastAPI(
    title="AI-powered GitHub Repository Intelligence Analyzer",
    description="Backend for analyzing GitHub repositories with AI",
    version="0.1.0"
)

# CORS configuration
# Allowing all origins for development; in production, this should be restricted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Backend is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
