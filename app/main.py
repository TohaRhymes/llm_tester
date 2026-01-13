"""
Main FastAPI application.
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from app.config import settings
from app.api import health, grade, generate, files, import_exam
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Basic logging for container/stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
# Security: Use environment-based CORS origins instead of wildcard
# For development, you can set CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(grade.router)
app.include_router(generate.router)
app.include_router(files.router)
app.include_router(import_exam.router)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Create runtime directories
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    print(f"✓ Data directory: {settings.data_dir}")
    print(f"✓ Output directory: {settings.output_dir}")
    print(f"✓ Uploads directory: {settings.uploads_dir}")
    print(f"✓ API ready at http://localhost:8000")
    print(f"✓ Swagger UI at http://localhost:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
