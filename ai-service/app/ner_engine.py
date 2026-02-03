import json
import os
import re
from typing import Dict, List
from app.models import Entity


class NEREngine:
    """Named Entity Recognition for government entities"""
    
    def __init__(self, dictionaries_path: str = "dictionaries"):
        self.dictionaries_path = dictionaries_path
        
        # Load dictionaries
        self.districts = self._load_dictionary("districts.json")
        self.mandals = self._load_dictionary("mandals.json")
        self.villages = self._load_dictionary("villages.json")
        self.departments = self._load_dictionary("departments.json")
        
        # Build regex patterns
        self.district_pattern = self._build_pattern(self.districts)
        self.mandal_pattern = self._build_pattern(self.mandals)
        self.village_pattern = self._build_pattern(self.villages)
        self.department_pattern = self._build_pattern(self.departments)
        
        # Date and time patterns
        self.date_pattern = re.compile(
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})\b',
            re.IGNORECASE
        )
        # Date and time patterns
        self.date_pattern = re.compile(
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})\b',
            re.IGNORECASE
        )
        self.time_pattern = re.compile(
            r'\b(\d{1,2}[:\s]?\d{0,2}\s*(am|pm|AM|PM|hours?|hrs?))\b'
        )
        
        # Name and Reason patterns
        self.person_pattern = re.compile(
            r'(?:my name is|i am|this is|name:)\s*([a-zA-Z\s]{2,40})',
            re.IGNORECASE
        )
        self.reason_pattern = re.compile(
            r'(?:reason is|regarding|to discuss|for|reason:)\s*([a-zA-Z0-9\s,\.\-]{3,150})',
            re.IGNORECASE
        )
        
    def _load_dictionary(self, filename: str) -> List[str]:
        """Load dictionary from JSON file"""
        filepath = os.path.join(self.dictionaries_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            print(f"Warning: Dictionary file {filename} not found")
            return []
    
    def _build_pattern(self, words: List[str]) -> re.Pattern:
        """Build regex pattern from word list"""
        if not words:
            return re.compile(r'(?!.*)')  # Never matches
        
        # Sort by length (longest first) to match longer names first
        sorted_words = sorted(words, key=len, reverse=True)
        # Escape special regex characters
        escaped = [re.escape(word) for word in sorted_words]
        pattern = r'\b(' + '|'.join(escaped) + r')\b'
        return re.compile(pattern, re.IGNORECASE)
    
    def extract_entities(self, text: str) -> Dict[str, List[Entity]]:
        """
        Extract named entities from text
        Returns: Dictionary of entity types to list of entities
        """
        entities = {
            "district": [],
            "mandal": [],
            "village": [],
            "department": [],
            "date": [],
            "time": [],
            "person": [],
            "reason": [],
        }
        
        # Extract districts
        for match in self.district_pattern.finditer(text):
            entities["district"].append(Entity(
                type="district",
                value=match.group(0),
                confidence=0.9,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract mandals
        for match in self.mandal_pattern.finditer(text):
            entities["mandal"].append(Entity(
                type="mandal",
                value=match.group(0),
                confidence=0.85,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract villages
        for match in self.village_pattern.finditer(text):
            entities["village"].append(Entity(
                type="village",
                value=match.group(0),
                confidence=0.8,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract departments
        for match in self.department_pattern.finditer(text):
            entities["department"].append(Entity(
                type="department",
                value=match.group(0),
                confidence=0.9,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract dates
        for match in self.date_pattern.finditer(text):
            entities["date"].append(Entity(
                type="date",
                value=match.group(0),
                confidence=0.85,
                start=match.start(),
                end=match.end()
            ))
        
        # Extract times
        for match in self.time_pattern.finditer(text):
            entities["time"].append(Entity(
                type="time",
                value=match.group(0),
                confidence=0.85,
                start=match.start(),
                end=match.end()
            ))

        # Extract person names
        for match in self.person_pattern.finditer(text):
            val = match.group(1).strip()
            if val:
                entities["person"].append(Entity(
                    type="person",
                    value=val,
                    confidence=0.7,
                    start=match.start(1),
                    end=match.end(1)
                ))

        # Extract reasons
        for match in self.reason_pattern.finditer(text):
            val = match.group(1).strip()
            if val:
                entities["reason"].append(Entity(
                    type="reason",
                    value=val,
                    confidence=0.7,
                    start=match.start(1),
                    end=match.end(1)
                ))
        
        return entities
        
        return entities
    
    def get_entity_summary(self, entities: Dict[str, List[Entity]]) -> Dict[str, int]:
        """Get count of each entity type"""
        return {
            entity_type: len(entity_list)
            for entity_type, entity_list in entities.items()
        }
