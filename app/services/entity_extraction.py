import re
from typing import List, Dict, Any, Optional
from app.models.schemas import Entity

try:
    import spacy
    from spacy.language import Language
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    Language = None


class EntityExtractor:
    def __init__(self, nlp_en: Optional[Language] = None, nlp_hi: Optional[Language] = None):
        self.nlp_en = nlp_en
        self.nlp_hi = nlp_hi
        # Regex patterns for common entities
        self.patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'(\+91[\-\s]?)?[6-9]\d{9}',
            'URL': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
            'PIN_CODE': r'\b[1-9][0-9]{5}\b',
            'PAN': r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            'AADHAAR': r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b',
        }
        
        # Common designation patterns
        self.designation_keywords = [
            'CEO', 'CTO', 'CFO', 'COO', 'Director', 'Manager', 'Executive',
            'Developer', 'Engineer', 'Designer', 'Consultant', 'Analyst',
            'President', 'Vice President', 'VP', 'Head', 'Lead', 'Senior',
            'Junior', 'Associate', 'Assistant', 'Coordinator', 'Specialist'
        ]
        
        # Common company suffixes
        self.company_suffixes = [
            'Ltd', 'Limited', 'Inc', 'Incorporated', 'Corp', 'Corporation',
            'LLC', 'LLP', 'Pvt', 'Private', 'Co', 'Company', 'Group',
            'Industries', 'Enterprises', 'Solutions', 'Services', 'Technologies'
        ]
    
    def extract_entities(self, text: str, language: str = 'en') -> List[Entity]:
        """Extract entities from text using SpaCy or regex patterns"""
        entities = []
        
        # Try SpaCy first if available
        if language == 'en' and self.nlp_en:
            entities.extend(self._extract_with_spacy(text, self.nlp_en))
        elif language == 'hi' and self.nlp_hi:
            entities.extend(self._extract_with_spacy(text, self.nlp_hi))
        
        # Extract pattern-based entities
        for label, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95
                ))
        
        # Extract designations
        designation_pattern = r'\b(' + '|'.join(self.designation_keywords) + r')\b'
        for match in re.finditer(designation_pattern, text, re.IGNORECASE):
            entities.append(Entity(
                text=match.group(),
                label='DESIGNATION',
                start=match.start(),
                end=match.end(),
                confidence=0.85
            ))
        
        # Extract potential company names
        company_pattern = r'\b[\w\s]+\s+(' + '|'.join(self.company_suffixes) + r')\b'
        for match in re.finditer(company_pattern, text, re.IGNORECASE):
            entities.append(Entity(
                text=match.group().strip(),
                label='ORG',
                start=match.start(),
                end=match.end(),
                confidence=0.75
            ))
        
        # Extract potential person names (simple heuristic)
        # This looks for capitalized words that might be names
        if language == 'en':
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
            for match in re.finditer(name_pattern, text):
                # Skip if it's already identified as something else
                overlap = any(
                    match.start() >= ent.start and match.end() <= ent.end
                    for ent in entities
                )
                if not overlap:
                    # Check if it's not a known designation or company
                    match_text = match.group()
                    if not any(keyword in match_text for keyword in self.designation_keywords):
                        entities.append(Entity(
                            text=match_text,
                            label='PERSON',
                            start=match.start(),
                            end=match.end(),
                            confidence=0.65
                        ))
        
        # Remove duplicates and sort by position
        seen = set()
        unique_entities = []
        for entity in sorted(entities, key=lambda x: x.start):
            key = (entity.text, entity.label, entity.start, entity.end)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _extract_with_spacy(self, text: str, nlp: Language) -> List[Entity]:
        """Extract entities using SpaCy NER"""
        entities = []
        try:
            doc = nlp(text)
            for ent in doc.ents:
                # Map SpaCy labels to our labels
                label = self._map_spacy_label(ent.label_)
                if label:
                    entities.append(Entity(
                        text=ent.text,
                        label=label,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=0.85
                    ))
        except:
            pass  # Fall back to regex
        return entities
    
    def _map_spacy_label(self, spacy_label: str) -> str:
        """Map SpaCy entity labels to our labels"""
        label_mapping = {
            'PERSON': 'PERSON',
            'PER': 'PERSON',
            'ORG': 'ORG',
            'GPE': 'LOCATION',
            'LOC': 'LOCATION',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'MONEY': 'MONEY',
            'PERCENT': 'PERCENT',
            'EMAIL': 'EMAIL',
            'PHONE': 'PHONE',
            'FAC': 'ORG',  # Facility
            'PRODUCT': 'PRODUCT',
            'EVENT': 'EVENT',
            'WORK_OF_ART': 'WORK_OF_ART',
            'LAW': 'LAW',
            'LANGUAGE': 'LANGUAGE',
            'NORP': 'NORP',  # Nationalities or religious or political groups
            'CARDINAL': 'NUMBER',
            'ORDINAL': 'NUMBER',
            'QUANTITY': 'QUANTITY'
        }
        return label_mapping.get(spacy_label, None)
    
    def extract_business_card_info(self, text: str, entities: List[Entity]) -> Dict[str, Any]:
        """Extract structured business card information from entities"""
        info = {
            'name': None,
            'designation': None,
            'company': None,
            'email': None,
            'phone': None,
            'address': None,
            'website': None
        }
        
        for entity in entities:
            if entity.label == 'PERSON' and not info['name']:
                info['name'] = entity.text
            elif entity.label == 'DESIGNATION' and not info['designation']:
                info['designation'] = entity.text
            elif entity.label == 'ORG' and not info['company']:
                info['company'] = entity.text
            elif entity.label == 'EMAIL' and not info['email']:
                info['email'] = entity.text
            elif entity.label == 'PHONE' and not info['phone']:
                info['phone'] = entity.text
            elif entity.label == 'URL' and not info['website']:
                info['website'] = entity.text
        
        return info