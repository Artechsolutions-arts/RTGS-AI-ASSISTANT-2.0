import re
from typing import Tuple
from langdetect import detect, LangDetectException
from app.models import Language


class LanguageDetector:
    """Detects language of text: English, Telugu, or Mixed"""
    
    def __init__(self):
        # Telugu Unicode range
        self.telugu_pattern = re.compile(r'[\u0C00-\u0C7F]+')
        # English pattern
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        
    def detect(self, text: str) -> Tuple[Language, float]:
        """
        Detect language of text
        Returns: (Language, confidence_score)
        """
        if not text or len(text.strip()) == 0:
            return Language.UNKNOWN, 0.0
        
        # Count Telugu characters
        telugu_chars = len(self.telugu_pattern.findall(text))
        # Count English characters
        english_chars = len(self.english_pattern.findall(text))
        
        total_chars = telugu_chars + english_chars
        
        if total_chars == 0:
            return Language.UNKNOWN, 0.0
        
        telugu_ratio = telugu_chars / total_chars
        english_ratio = english_chars / total_chars
        
        # Mixed language detection
        if telugu_ratio > 0.2 and english_ratio > 0.2:
            confidence = min(telugu_ratio, english_ratio) * 2
            return Language.MIXED, min(confidence, 1.0)
        
        # Primarily Telugu
        if telugu_ratio > 0.5:
            return Language.TELUGU, telugu_ratio
        
        # Primarily English
        if english_ratio > 0.5:
            # Use langdetect for confirmation
            try:
                detected = detect(text)
                if detected == 'en':
                    return Language.ENGLISH, 0.9
                else:
                    return Language.ENGLISH, 0.7
            except LangDetectException:
                return Language.ENGLISH, english_ratio
        
        # Fallback to langdetect
        try:
            detected = detect(text)
            if detected == 'en':
                return Language.ENGLISH, 0.8
            elif detected == 'te':
                return Language.TELUGU, 0.8
            else:
                return Language.UNKNOWN, 0.5
        except LangDetectException:
            return Language.UNKNOWN, 0.3
    
    def is_telugu(self, text: str) -> bool:
        """Check if text contains Telugu characters"""
        return bool(self.telugu_pattern.search(text))
    
    def is_english(self, text: str) -> bool:
        """Check if text contains English characters"""
        return bool(self.english_pattern.search(text))
