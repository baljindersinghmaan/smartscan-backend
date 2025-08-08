from pydantic import BaseModel, Field
from typing import Optional


class LanguageDetectionResponse(BaseModel):
    detected_language: Optional[str] = Field(None, description="Detected language code")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    hindi_score: Optional[float] = Field(None, ge=0, le=1, description="Hindi probability score")
    english_score: Optional[float] = Field(None, ge=0, le=1, description="English probability score")