from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import spacy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app (like const app = express())
app = FastAPI(
    title="SmartScanAI Backend",
    description="Hindi/English NER service for business cards",
    version="1.0.0"
)

# Add CORS middleware (like app.use(cors()))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SpaCy models at startup (like loading modules)
try:
    nlp_en = spacy.load("en_core_web_sm")
    nlp_hi = spacy.load("hi_core_news_sm")
    print("✅ SpaCy models loaded successfully")
except Exception as e:
    print(f"❌ Error loading SpaCy models: {e}")
    nlp_en = None
    nlp_hi = None

# Pydantic models (like TypeScript interfaces)
class TextInput(BaseModel):
    text: str
    language: Optional[str] = None

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    hindi_score: float
    english_score: float

class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float

class NERResponse(BaseModel):
    language_detected: str
    entities: List[Entity]
    confidence_score: float

# Routes (like app.get(), app.post())
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SmartScanAI Backend is running!",
        "status": "healthy",
        "spacy_loaded": nlp_en is not None and nlp_hi is not None
    }

@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(input_data: TextInput):
    """Detect if text is Hindi or English"""
    if not nlp_en or not nlp_hi:
        raise HTTPException(status_code=500, detail="SpaCy models not loaded")
    
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Process with both models
        doc_hi = nlp_hi(text)
        doc_en = nlp_en(text)
        
        # Calculate confidence scores
        hindi_score = calculate_language_confidence(doc_hi, "hi", text)
        english_score = calculate_language_confidence(doc_en, "en", text)
        
        # Determine primary language
        detected_language = "hi" if hindi_score > english_score else "en"
        confidence = max(hindi_score, english_score)
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            confidence=confidence,
            hindi_score=hindi_score,
            english_score=english_score
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@app.post("/extract-entities", response_model=NERResponse)
async def extract_entities(input_data: TextInput):
    """Extract named entities from text"""
    if not nlp_en or not nlp_hi:
        raise HTTPException(status_code=500, detail="SpaCy models not loaded")
    
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Auto-detect language if not provided
        language = input_data.language
        if not language:
            lang_result = await detect_language(input_data)
            language = lang_result.detected_language
        
        # Choose appropriate model
        nlp = nlp_hi if language == "hi" else nlp_en
        doc = nlp(text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.8  # SpaCy doesn't provide confidence directly
            ))
        
        # Add business card specific patterns
        business_entities = extract_business_patterns(text)
        entities.extend(business_entities)
        
        # Calculate overall confidence
        confidence_score = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
        
        return NERResponse(
            language_detected=language,
            entities=entities,
            confidence_score=confidence_score
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")

# Helper functions
def calculate_language_confidence(doc, language, original_text):
    """Calculate confidence score for language detection"""
    if not doc or len(doc) == 0:
        return 0.0
    
    # Count recognized vs unrecognized tokens
    recognized_tokens = sum(1 for token in doc if not token.is_oov)
    total_tokens = len(doc)
    
    if total_tokens == 0:
        return 0.0
    
    base_score = recognized_tokens / total_tokens
    
    # Boost for language-specific characteristics
    if language == "hi":
        # Check for Devanagari script
        devanagari_chars = sum(1 for char in original_text if '\u0900' <= char <= '\u097F')
        if devanagari_chars > 0:
            base_score += 0.3
    
    return min(base_score, 1.0)

def extract_business_patterns(text):
    """Extract business card specific patterns using regex"""
    import re
    
    entities = []
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for match in re.finditer(email_pattern, text, re.IGNORECASE):
        entities.append(Entity(
            text=match.group(),
            label="EMAIL",
            start=match.start(),
            end=match.end(),
            confidence=0.95
        ))
    
    # Phone pattern (Indian)
    phone_pattern = r'(\+91[\-\s]?)?[6-9]\d{9}'
    for match in re.finditer(phone_pattern, text):
        entities.append(Entity(
            text=match.group(),
            label="PHONE",
            start=match.start(),
            end=match.end(),
            confidence=0.9
        ))
    
    return entities

# Run the server (like app.listen())
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Auto-restart on file changes (like nodemon)
        log_level="info"
    )