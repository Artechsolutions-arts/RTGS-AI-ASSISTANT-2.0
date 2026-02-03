import json
import os
from typing import Dict, List, Optional
import re


class SpellCorrector:
    """Dictionary-based spell corrector for government entities"""
    
    def __init__(self, dictionaries_path: str = "dictionaries"):
        self.dictionaries_path = dictionaries_path
        self.districts = self._load_dictionary("districts.json")
        self.mandals = self._load_dictionary("mandals.json")
        self.villages = self._load_dictionary("villages.json")
        self.departments = self._load_dictionary("departments.json")
        
        # Build lookup maps for fuzzy matching
        self.district_map = self._build_fuzzy_map(self.districts)
        self.mandal_map = self._build_fuzzy_map(self.mandals)
        self.village_map = self._build_fuzzy_map(self.villages)
        self.department_map = self._build_fuzzy_map(self.departments)
        
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
    
    def _build_fuzzy_map(self, words: List[str]) -> Dict[str, str]:
        """Build fuzzy matching map (lowercase, no spaces)"""
        fuzzy_map = {}
        for word in words:
            key = word.lower().replace(" ", "").replace("-", "")
            fuzzy_map[key] = word
        return fuzzy_map
    
    def _fuzzy_match(self, word: str, fuzzy_map: Dict[str, str]) -> Optional[str]:
        """Find fuzzy match in dictionary"""
        key = word.lower().replace(" ", "").replace("-", "")
        return fuzzy_map.get(key)
    
    def correct_text(self, text: str) -> str:
        """Correct spelling in text using government dictionaries"""
        corrected = text
        
        # Correct districts
        for word in re.findall(r'\b\w+\b', text):
            if len(word) > 3:  # Only check words longer than 3 chars
                # Check districts
                match = self._fuzzy_match(word, self.district_map)
                if match:
                    corrected = re.sub(r'\b' + re.escape(word) + r'\b', match, corrected, flags=re.IGNORECASE)
                    continue
                
                # Check mandals
                match = self._fuzzy_match(word, self.mandal_map)
                if match:
                    corrected = re.sub(r'\b' + re.escape(word) + r'\b', match, corrected, flags=re.IGNORECASE)
                    continue
                
                # Check villages
                match = self._fuzzy_match(word, self.village_map)
                if match:
                    corrected = re.sub(r'\b' + re.escape(word) + r'\b', match, corrected, flags=re.IGNORECASE)
                    continue
        
        return corrected
    
    def find_corrections(self, text: str) -> List[Dict[str, str]]:
        """Find all corrections made"""
        corrections = []
        
        for word in re.findall(r'\b\w+\b', text):
            if len(word) > 3:
                match = None
                entity_type = None
                
                # Check all dictionaries
                if not match:
                    match = self._fuzzy_match(word, self.district_map)
                    entity_type = "district"
                
                if not match:
                    match = self._fuzzy_match(word, self.mandal_map)
                    entity_type = "mandal"
                
                if not match:
                    match = self._fuzzy_match(word, self.village_map)
                    entity_type = "village"
                
                if not match:
                    match = self._fuzzy_match(word, self.department_map)
                    entity_type = "department"
                
                if match and match.lower() != word.lower():
                    corrections.append({
                        "original": word,
                        "corrected": match,
                        "type": entity_type
                    })
        
        return corrections
