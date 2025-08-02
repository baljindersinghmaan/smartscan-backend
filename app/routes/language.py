from fastapi import APIRouter, HTTPException
from app.models.schemas import TextInput, LanguageDetectionResponse
from app.services.language_detection import LanguageDetector
from app.services.nlp_loader import load_spacy_models


router = APIRouter()

# Load SpaCy models once at startup
nlp_en, nlp_hi = load_spacy_models()
detector = LanguageDetector(nlp_en, nlp_hi)


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(input_data: TextInput):
    """Detect if text is Hindi or English"""
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        detected_language, confidence, hindi_score, english_score = detector.detect_language(text)
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            confidence=confidence,
            hindi_score=hindi_score,
            english_score=english_score
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")