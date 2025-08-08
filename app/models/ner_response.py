from pydantic import BaseModel, Field
from typing import List, Optional
from .entity import Entity


class NERResponse(BaseModel):
    language_detected: Optional[str] = Field(None, description="Detected language code")
    entities: Optional[List[Entity]] = Field(default_factory=list, description="Extracted entities")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Overall confidence")