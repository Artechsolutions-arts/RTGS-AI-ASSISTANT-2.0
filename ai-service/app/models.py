from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    ENGLISH = "english"
    TELUGU = "telugu"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Intent(str, Enum):
    DISASTER_ALERT = "disaster_alert"
    MEETING = "meeting"
    INSTRUCTION = "instruction"
    STATUS_UPDATE = "status_update"
    FYI = "fyi"
    VIEW_CALENDAR = "view_calendar"
    REQUEST_APPOINTMENT = "request_appointment"
    UNKNOWN = "unknown"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WhatsAppMessage(BaseModel):
    message_text: str
    timestamp: str
    forwarded_from: str
    sender_role: str
    attachments: Optional[List[str]] = []


class Entity(BaseModel):
    type: str
    value: str
    confidence: float
    start: int
    end: int


class AIAnalysis(BaseModel):
    language: Language
    language_confidence: float
    intent: Intent
    intent_confidence: float
    priority: Priority
    priority_confidence: float
    entities: Dict[str, List[Entity]]
    corrected_text: Optional[str] = None
    keywords: List[str] = []
    sentiment: Optional[str] = None


class AnalyzeRequest(BaseModel):
    message_text: str
    metadata: Optional[Dict[str, Any]] = {}


class AnalyzeResponse(BaseModel):
    original_text: str
    analysis: AIAnalysis
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
    uptime_seconds: float


class StatsResponse(BaseModel):
    total_processed: int
    by_language: Dict[str, int]
    by_intent: Dict[str, int]
    by_priority: Dict[str, int]
    average_processing_time_ms: float


class TaskExtractionRequest(BaseModel):
    message_text: str
    intent: str
    priority: str
    departments: Optional[List[str]] = None
    locations: Optional[Dict[str, Any]] = None
    message_id: Optional[str] = None
    created_by: Optional[str] = "Telegram User"


class Task(BaseModel):
    task_id: str
    message_id: Optional[str]
    title: str
    description: str
    department: str
    assigned_to: str
    location: Dict[str, Optional[str]]
    deadline: str
    priority: str
    status: str
    created_at: str
    created_by: str
    completed_at: Optional[str]
    completed_by: Optional[str]
    reminder_sent: bool
    reminder_count: int
    last_reminder_at: Optional[str]


class TaskExtractionResponse(BaseModel):
    tasks: List[Task]
    task_count: int
    summary: str

