import re
from typing import Tuple, Optional

try:
    import spacy
    from spacy.language import Language
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    Language = None


class LanguageDetector:
    def __init__(self, nlp_en: Optional[Language] = None, nlp_hi: Optional[Language] = None):
        self.nlp_en = nlp_en
        self.nlp_hi = nlp_hi
        # Common Hindi/Devanagari Unicode range
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]+')
        
        # Common English patterns
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        
        # Common Hindi words
        self.hindi_words = {
            'का', 'के', 'की', 'को', 'से', 'में', 'है', 'हैं', 'था', 'थे', 
            'और', 'या', 'पर', 'यह', 'वह', 'कि', 'जो', 'तो', 'ही', 'भी'
        }
        
        # Common English words
        self.english_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 
            'are', 'was', 'were', 'to', 'in', 'for', 'of', 'with', 'from'
        }
    
    def detect_language(self, text: str) -> Tuple[str, float, float, float]:
        """
        Detect if text is Hindi or English
        Returns: (detected_language, confidence, hindi_score, english_score)
        """
        if not text or not text.strip():
            return "en", 0.0, 0.0, 0.0
        
        # If SpaCy models are available, use them for better detection
        if self.nlp_en and self.nlp_hi:
            return self._detect_with_spacy(text)
        else:
            return self._detect_with_regex(text)
    
    def _detect_with_spacy(self, text: str) -> Tuple[str, float, float, float]:
        """
        Detect language using SpaCy models
        """
        try:
            # Process with both models
            doc_en = self.nlp_en(text)
            doc_hi = self.nlp_hi(text)
            
            # Calculate scores based on recognized tokens
            en_score = self._calculate_spacy_score(doc_en, "en", text)
            hi_score = self._calculate_spacy_score(doc_hi, "hi", text)
            
            # Determine language
            if hi_score > en_score:
                return "hi", hi_score, hi_score, en_score
            else:
                return "en", en_score, hi_score, en_score
        except:
            # Fallback to regex if SpaCy fails
            return self._detect_with_regex(text)
    
    def _calculate_spacy_score(self, doc, language: str, original_text: str) -> float:
        """
        Calculate confidence score for SpaCy language detection
        """
        if not doc or len(doc) == 0:
            return 0.0
        
        # Count recognized tokens (not out-of-vocabulary)
        recognized_tokens = sum(1 for token in doc if not token.is_oov)
        total_tokens = len(doc)
        
        if total_tokens == 0:
            return 0.0
        
        base_score = recognized_tokens / total_tokens
        
        # Boost Hindi score if Devanagari script is present
        if language == "hi":
            devanagari_chars = sum(1 for char in original_text if '\u0900' <= char <= '\u097F')
            if devanagari_chars > 0:
                base_score = min(base_score + 0.3, 1.0)
        
        return base_score
    
    def _detect_with_regex(self, text: str) -> Tuple[str, float, float, float]:
        """
        Detect if text is Hindi or English
        Returns: (detected_language, confidence, hindi_score, english_score)
        """
        if not text or not text.strip():
            return "en", 0.0, 0.0, 0.0
        
        text_lower = text.lower()
        
        # Count characters
        hindi_chars = len(self.hindi_pattern.findall(text))
        english_chars = len(self.english_pattern.findall(text))
        total_chars = len(re.findall(r'\S', text))  # Non-whitespace chars
        
        if total_chars == 0:
            return "en", 0.0, 0.0, 0.0
        
        # Calculate character-based scores
        hindi_char_score = hindi_chars / total_chars if total_chars > 0 else 0
        english_char_score = english_chars / total_chars if total_chars > 0 else 0
        
        # Count common words
        words = text_lower.split()
        hindi_word_count = sum(1 for word in words if word in self.hindi_words)
        english_word_count = sum(1 for word in words if word in self.english_words)
        
        # Calculate word-based scores
        total_words = len(words)
        hindi_word_score = hindi_word_count / total_words if total_words > 0 else 0
        english_word_score = english_word_count / total_words if total_words > 0 else 0
        
        # Combined scores (weighted average)
        hindi_score = (hindi_char_score * 0.7 + hindi_word_score * 0.3)
        english_score = (english_char_score * 0.7 + english_word_score * 0.3)
        
        # Determine language
        if hindi_score > english_score:
            detected_language = "hi"
            confidence = min(hindi_score * 1.2, 1.0)  # Boost confidence slightly
        else:
            detected_language = "en"
            confidence = min(english_score * 1.2, 1.0)
        
        # If no clear detection, default to English with low confidence
        if hindi_score == 0 and english_score == 0:
            detected_language = "en"
            confidence = 0.1
        
        return detected_language, confidence, hindi_score, english_score