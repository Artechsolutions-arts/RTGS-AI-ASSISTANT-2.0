import re
from typing import Tuple
from app.models import Priority, Intent


class PriorityClassifier:
    """Rule-based priority classifier"""
    
    def __init__(self):
        # High priority keywords
        self.high_priority_keywords = [
            r'\b(urgent|emergency|immediate|critical|asap|priority)\b',
            r'\b(disaster|flood|cyclone|fire|accident|casualty)\b',
            r'\b(alert|warning|evacuate|rescue)\b',
            r'\b(అత్యవసర|తక్షణ|ముఖ్యమైన)\b',  # Telugu: emergency, immediate, important
        ]
        
        # Low priority keywords
        self.low_priority_keywords = [
            r'\b(fyi|for your information|note|circular|notification)\b',
            r'\b(routine|regular|normal|general)\b',
            r'\b(సమాచారం|సాధారణ)\b',  # Telugu: information, general
        ]
        
        # Compile patterns
        self.high_patterns = [re.compile(p, re.IGNORECASE) for p in self.high_priority_keywords]
        self.low_patterns = [re.compile(p, re.IGNORECASE) for p in self.low_priority_keywords]
    
    def classify(self, text: str, intent: Intent = None) -> Tuple[Priority, float]:
        """
        Classify priority of message
        Returns: (Priority, confidence_score)
        """
        if not text or len(text.strip()) == 0:
            return Priority.MEDIUM, 0.5
        
        # Count high priority matches
        high_score = sum(1 for pattern in self.high_patterns if pattern.search(text))
        
        # Count low priority matches
        low_score = sum(1 for pattern in self.low_patterns if pattern.search(text))
        
        # Intent-based priority boost
        if intent == Intent.DISASTER_ALERT:
            high_score += 3
        elif intent == Intent.FYI:
            low_score += 2
        elif intent == Intent.MEETING:
            # Only escalate if explicitly urgent, not just because it's tomorrow
            if re.search(r'\b(urgent|immediate|emergency)\b', text, re.IGNORECASE):
                high_score += 1
            else:
                # Meetings are typically informational unless urgent
                low_score += 1
        
        # Determine priority
        if high_score > low_score and high_score >= 1:
            confidence = min(0.6 + (high_score * 0.1), 1.0)
            return Priority.HIGH, confidence
        elif low_score > high_score and low_score >= 1:
            confidence = min(0.6 + (low_score * 0.1), 1.0)
            return Priority.LOW, confidence
        else:
            # Default to medium
            return Priority.MEDIUM, 0.6
    
    def has_deadline(self, text: str) -> bool:
        """Check if message contains deadline"""
        deadline_patterns = [
            r'\b(deadline|due|by|before|until)\b',
            r'\b(today|tomorrow|asap)\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Date
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in deadline_patterns)
