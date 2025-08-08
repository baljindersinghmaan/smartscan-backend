from pydantic import BaseModel
from typing import Optional


class HealthCheckResponse(BaseModel):
    message: Optional[str] = None
    status: Optional[str] = None
    spacy_loaded: Optional[bool] = None