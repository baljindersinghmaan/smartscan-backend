from typing import Optional, Tuple

try:
    import spacy
    from spacy.language import Language
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    Language = None


def load_spacy_models() -> Tuple[Optional[Language], Optional[Language]]:
    """
    Load SpaCy models for English and Hindi
    Returns: (nlp_en, nlp_hi)
    """
    nlp_en = None
    nlp_hi = None
    
    if not SPACY_AVAILABLE:
        print("⚠️  SpaCy not available. Using regex-based extraction only.")
        return nlp_en, nlp_hi
    
    # Try to load English model
    try:
        nlp_en = spacy.load("en_core_web_sm")
        print("✅ English SpaCy model loaded successfully")
    except Exception as e:
        print(f"⚠️  English SpaCy model not available: {e}")
        print("   Falling back to regex-based extraction for English")
    
    # Try to load Hindi model
    try:
        # No pre-trained Hindi model available, use blank model
        nlp_hi = spacy.blank("hi")
        print("✅ Hindi SpaCy blank model loaded successfully")
        print("   Note: Using tokenizer only, no pre-trained NER model available")
    except Exception as e:
        print(f"⚠️  Hindi SpaCy model not available: {e}")
        print("   Falling back to regex-based extraction for Hindi")
    
    return nlp_en, nlp_hi