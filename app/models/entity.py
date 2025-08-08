from pydantic import BaseModel, Field
from typing import Optional


class Entity(BaseModel):
    text: Optional[str] = Field(None, description="Entity text")
    label: Optional[str] = Field(None, description="Entity type (PERSON, ORG, EMAIL, PHONE, etc.)")
    start: Optional[int] = Field(None, ge=0, description="Start position in text")
    end: Optional[int] = Field(None, gt=0, description="End position in text")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Extraction confidence")