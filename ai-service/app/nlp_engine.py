import re
from typing import List
from app.language_detector import LanguageDetector
from app.intent_classifier import IntentClassifier
from app.priority_classifier import PriorityClassifier
from app.ner_engine import NEREngine
from app.spell_corrector import SpellCorrector
from app.models import AIAnalysis, Language


class NLPEngine:
    """Main NLP engine that orchestrates all NLP components"""
    
    def __init__(self, dictionaries_path: str = "dictionaries"):
        self.language_detector = LanguageDetector()
        self.intent_classifier = IntentClassifier()
        self.priority_classifier = PriorityClassifier()
        self.ner_engine = NEREngine(dictionaries_path)
        self.spell_corrector = SpellCorrector(dictionaries_path)
    
    def analyze(self, text: str) -> AIAnalysis:
        """
        Perform complete NLP analysis on text
        Returns: AIAnalysis object
        """
        # Step 1: Language detection
        language, lang_confidence = self.language_detector.detect(text)
        
        # Step 2: Spell correction (only for English and Mixed)
        corrected_text = None
        if language in [Language.ENGLISH, Language.MIXED]:
            corrected_text = self.spell_corrector.correct_text(text)
            # Use corrected text for further analysis
            analysis_text = corrected_text
        else:
            analysis_text = text
        
        # Step 3: Intent classification
        intent, intent_confidence = self.intent_classifier.classify(analysis_text)
        
        # Step 4: Priority classification (with intent context)
        priority, priority_confidence = self.priority_classifier.classify(analysis_text, intent)
        
        # Step 5: Named Entity Recognition
        entities = self.ner_engine.extract_entities(analysis_text)
        
        # Step 6: Extract keywords
        keywords = self._extract_keywords(analysis_text)
        
        # Step 7: Sentiment analysis (basic)
        sentiment = self._analyze_sentiment(analysis_text)
        
        return AIAnalysis(
            language=language,
            language_confidence=lang_confidence,
            intent=intent,
            intent_confidence=intent_confidence,
            priority=priority,
            priority_confidence=priority_confidence,
            entities=entities,
            corrected_text=corrected_text if corrected_text != text else None,
            keywords=keywords,
            sentiment=sentiment
        )
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words and get unique keywords
        keywords = []
        seen = set()
        for word in words:
            if word not in stop_words and word not in seen:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= max_keywords:
                    break
        
        return keywords
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        # Positive words
        positive_words = [
            'good', 'great', 'excellent', 'success', 'completed', 'achieved',
            'progress', 'improved', 'positive', 'well', 'better'
        ]
        
        # Negative words
        negative_words = [
            'bad', 'poor', 'failed', 'failure', 'problem', 'issue', 'critical',
            'urgent', 'emergency', 'disaster', 'damage', 'loss', 'delay'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
