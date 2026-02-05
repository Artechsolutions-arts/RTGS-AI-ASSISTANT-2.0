import re
from typing import Tuple, List
from app.models import Intent


class IntentClassifier:
    """Rule-based intent classifier for government messages"""
    
    def __init__(self):
        # Define keyword patterns for each intent
        self.patterns = {
            Intent.DISASTER_ALERT: [
                r'\b(urgent|emergency|alert|warning|disaster|flood|cyclone|earthquake|fire|accident|storm|rain alert|heat wave|outage|failure)\b',
                r'\b(immediate|critical|evacuate|rescue|casualty|casualties|damage|relief material|safety audit|restock)\b',
                r'(వరద|తుఫాను|హెచ్చరిక|అత్యవసర|కొండచరియలు|ముంపు|గాలివాన|అగ్ని ప్రమాదం|అప్రమత్తం|ప్రమాదకర)',  # Telugu: flood, cyclone, alert, emergency, landslide, submerged, storm, fire accident, warn, dangerous
            ],
            Intent.MEETING: [
                r'\b(meeting|conference|discussion|session|agenda|attend)\b',
                r'\b(schedule|scheduled|timing|venue|location|zoom|teams)\b',
                r'(మీటింగ్|సమావేశం|చర్చ)',  # Telugu: meeting, conference, discussion
                r'\b(on|at|@)\s*\d{1,2}[:\s]?\d{0,2}\s*(am|pm|AM|PM)?\b',  # Time patterns
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Date patterns
            ],
            Intent.INSTRUCTION: [
                r'\b(please|kindly|request|submit|prepare|complete|action|implement|infrastructure|repairs|fix|install)\b',
                r'\b(task|assignment|work|duty|responsibility|deadline|by|audit|check|verify)\b',
                r'(చేయండి|సిద్ధం|పూర్తి|సమర్పించండి|బాగు చేయాలి)',  # Telugu: do, prepare, complete, submit, fix it
                r'\b(ensure|make sure|verify|check|review|approve)\b',
            ],
            Intent.STATUS_UPDATE: [
                r'\b(status|update|progress|completed|done|finished|ongoing)\b',
                r'\b(report|reporting|reported|statistics|data|numbers)\b',
                r'(స్థితి|నివేదిక|పూర్తయింది)',  # Telugu: status, report, completed
                r'\b(\d+%|percent|percentage)\b',
            ],
            Intent.FYI: [
                r'\b(fyi|for your information|note|noted|inform|information)\b',
                r'\b(circular|notification|notice|announcement|memo)\b',
                r'(సమాచారం|నోటీసు|ప్రకటన)',  # Telugu: information, notice, announcement
                r'\b(attached|attachment|please find|pfa)\b',
            ],
            Intent.VIEW_CALENDAR: [
                r'\b(schedule|calendar|appointments?|meetings?|agenda)\b',
                r'\b(what.*meetings?|show.*schedule|any.*appointments?|view.*calendar)\b',
                r'\b(what|show|view|display|get|list).*\b(my|our).*\b(schedule|meetings?|calendar|appointments?)\b',
                r'\b(my|our).*\b(schedule|meetings?|calendar|appointments?)\b',
                r'(షెడ్యూల్|కాలెండర్|సమావేశాలు|ఈరోజు|రేపు|ఎజెండా)',  # Telugu: schedule, calendar, meetings, today, tomorrow, agenda
                r'(చూపించు|ఏమిటి|ఉన్నాయా).*(షెడ్యూల్|సమావేశాలు|అపాయింట్మెంట్)',  # Telugu: show/what/any + schedule/meetings/appointment
                r'\b(today|tomorrow|this week).*\b(schedule|meetings?|appointments?)\b',
                r'\b(schedule|meetings?|appointments?).*\b(today|tomorrow|this week)\b',
            ],
            Intent.REQUEST_APPOINTMENT: [
                r'\b(appointment|meeting).*\b(collector|dm|magistrate|officer)\b',
                r'\b(want|need|request).*\b(meet|see).*\b(collector|dm|magistrate)\b',
                r'\b(book|schedule|fix).*\b(slot|appointment|time)\b',
                r'(అపాయింట్మెంట్|కలవాలి|సమయం కావాలి)', # Telugu: appointment, want to meet, want time
                r'\b(appointment|meeting).*\b(request|booking)\b',
            ],
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for intent, patterns in self.patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def classify(self, text: str) -> Tuple[Intent, float]:
        """
        Classify intent of message
        Returns: (Intent, confidence_score)
        """
        if not text or len(text.strip()) == 0:
            return Intent.UNKNOWN, 0.0
        
        # Score each intent
        scores = {}
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            matches = 0
            for pattern in patterns:
                if pattern.search(text):
                    matches += 1
                    score += 1
            
            # Normalize score
            if len(patterns) > 0:
                scores[intent] = score / len(patterns)
            else:
                scores[intent] = 0.0
        
        # Find highest scoring intent
        if not scores:
            return Intent.UNKNOWN, 0.0
        
        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        
        # If score is too low, return UNKNOWN
        if max_score < 0.15:
            return Intent.UNKNOWN, max_score
        
        # Calculate confidence (0.0 to 1.0)
        confidence = min(max_score * 2, 1.0)
        
        return max_intent, confidence
    
    def get_all_scores(self, text: str) -> dict:
        """Get scores for all intents"""
        scores = {}
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(text):
                    score += 1
            scores[intent.value] = score / len(patterns) if patterns else 0.0
        return scores
