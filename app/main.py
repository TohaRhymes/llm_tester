"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health, grade, generate

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(grade.router)
app.include_router(generate.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Create output directory if it doesn't exist
    import os
    os.makedirs(settings.output_dir, exist_ok=True)
    print(f"✓ Output directory: {settings.output_dir}")
    print(f"✓ API ready at http://localhost:8000")
    print(f"✓ Swagger UI at http://localhost:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
