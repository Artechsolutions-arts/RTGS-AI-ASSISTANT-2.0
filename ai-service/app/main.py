from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from datetime import datetime
from typing import Dict

from app.models import (
    AnalyzeRequest, AnalyzeResponse, HealthResponse, StatsResponse,
    TaskExtractionRequest, TaskExtractionResponse, Task
)
from app.nlp_engine import NLPEngine
from app.task_extractor import extract_tasks, format_task_summary

# Global variables
nlp_engine = None
stats = {
    "total_processed": 0,
    "by_language": {},
    "by_intent": {},
    "by_priority": {},
    "total_processing_time_ms": 0.0,
    "start_time": time.time()
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global nlp_engine
    
    # Startup
    print("🚀 Starting AI Service...")
    print("📚 Loading NLP models...")
    
    try:
        nlp_engine = NLPEngine(dictionaries_path="dictionaries")
        print("✅ NLP Engine loaded successfully")
    except Exception as e:
        print(f"❌ Error loading NLP Engine: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Shutting down AI Service...")


# Create FastAPI app
app = FastAPI(
    title="Government AI Personal Assistant - AI Service",
    description="NLP and AI processing service for government message analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Government AI Personal Assistant - AI Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/analyze",
            "extract_tasks": "/extract-tasks",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - stats["start_time"]
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={
            "nlp_engine": nlp_engine is not None,
            "language_detector": True,
            "intent_classifier": True,
            "priority_classifier": True,
            "ner_engine": True,
            "spell_corrector": True
        },
        uptime_seconds=uptime
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(request: AnalyzeRequest):
    """
    Analyze a message using NLP
    
    This endpoint performs:
    - Language detection
    - Intent classification
    - Priority classification
    - Named Entity Recognition
    - Spell correction
    - Keyword extraction
    - Sentiment analysis
    """
    if not nlp_engine:
        raise HTTPException(status_code=503, detail="NLP Engine not initialized")
    
    if not request.message_text or len(request.message_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="message_text cannot be empty")
    
    # Start timing
    start_time = time.time()
    
    try:
        # Perform NLP analysis
        analysis = nlp_engine.analyze(request.message_text)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Update stats
        stats["total_processed"] += 1
        stats["total_processing_time_ms"] += processing_time_ms
        
        # Update language stats
        lang_key = analysis.language.value
        stats["by_language"][lang_key] = stats["by_language"].get(lang_key, 0) + 1
        
        # Update intent stats
        intent_key = analysis.intent.value
        stats["by_intent"][intent_key] = stats["by_intent"].get(intent_key, 0) + 1
        
        # Update priority stats
        priority_key = analysis.priority.value
        stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1
        
        return AnalyzeResponse(
            original_text=request.message_text,
            analysis=analysis,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/extract-tasks", response_model=TaskExtractionResponse)
async def extract_tasks_endpoint(request: TaskExtractionRequest):
    """
    Extract tasks from message text
    
    This endpoint performs:
    - Task identification from action verbs
    - Deadline extraction
    - Assignee detection
    - Task object generation
    """
    if not request.message_text or len(request.message_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="message_text cannot be empty")
    
    try:
        # Extract tasks
        tasks = extract_tasks(
            message_text=request.message_text,
            intent=request.intent,
            priority=request.priority,
            departments=request.departments,
            locations=request.locations,
            message_id=request.message_id,
            created_by=request.created_by
        )
        
        # Format summary
        summary = format_task_summary(tasks)
        
        # Convert to Task models
        task_models = [Task(**task) for task in tasks]
        
        return TaskExtractionResponse(
            tasks=task_models,
            task_count=len(task_models),
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task extraction failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get processing statistics"""
    avg_processing_time = 0.0
    if stats["total_processed"] > 0:
        avg_processing_time = stats["total_processing_time_ms"] / stats["total_processed"]
    
    return StatsResponse(
        total_processed=stats["total_processed"],
        by_language=stats["by_language"],
        by_intent=stats["by_intent"],
        by_priority=stats["by_priority"],
        average_processing_time_ms=avg_processing_time
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
