from pydantic import BaseModel, Field
from typing import Optional


class TextInput(BaseModel):
    text: Optional[str] = Field(None, min_length=1, description="Text to process")
    language: Optional[str] = Field(None, description="Language code (en/hi)")