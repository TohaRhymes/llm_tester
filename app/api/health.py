"""
Health check endpoint.
"""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and version.
    """
    return HealthResponse(
        status="ok",
        version=settings.api_version
    )
