from fastapi import APIRouter, HTTPException
from app.models.schemas import TextInput, NERResponse
from app.services.language_detection import LanguageDetector
from app.services.entity_extraction import EntityExtractor
from app.services.nlp_loader import load_spacy_models


router = APIRouter()

# Load SpaCy models once at startup
nlp_en, nlp_hi = load_spacy_models()
language_detector = LanguageDetector(nlp_en, nlp_hi)
entity_extractor = EntityExtractor(nlp_en, nlp_hi)


@router.post("/extract-entities", response_model=NERResponse)
async def extract_entities(input_data: TextInput):
    """Extract named entities from text"""
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Auto-detect language if not provided
        language = input_data.language
        if not language:
            detected_language, _, _, _ = language_detector.detect_language(text)
            language = detected_language
        
        # Extract entities
        entities = entity_extractor.extract_entities(text, language)
        
        # Calculate overall confidence
        confidence_score = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
        
        return NERResponse(
            language_detected=language,
            entities=entities,
            confidence_score=confidence_score
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")