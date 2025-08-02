from pydantic import BaseModel, Field
from typing import List, Optional


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Text to process")
    language: Optional[str] = Field(None, description="Language code (en/hi)")


class LanguageDetectionResponse(BaseModel):
    detected_language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    hindi_score: float = Field(..., ge=0, le=1, description="Hindi probability score")
    english_score: float = Field(..., ge=0, le=1, description="English probability score")


class Entity(BaseModel):
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity type (PERSON, ORG, EMAIL, PHONE, etc.)")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., gt=0, description="End position in text")
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")


class NERResponse(BaseModel):
    language_detected: str = Field(..., description="Detected language code")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence")


class HealthCheckResponse(BaseModel):
    message: str
    status: str
    spacy_loaded: bool