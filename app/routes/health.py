from fastapi import APIRouter
from app.models.schemas import HealthCheckResponse


router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        message="SmartScanAI Backend is running!",
        status="healthy",
        spacy_loaded=True  # SpaCy English model is available
    )