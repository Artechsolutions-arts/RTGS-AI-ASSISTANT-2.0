"""
Task Extractor Module
Extracts action items and tasks from message text using NLP
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# Action verbs that indicate tasks
ACTION_VERBS = [
    'inspect', 'check', 'verify', 'review', 'submit', 'prepare', 'send',
    'arrange', 'organize', 'coordinate', 'schedule', 'complete', 'finish',
    'deliver', 'provide', 'ensure', 'confirm', 'investigate', 'resolve',
    'fix', 'repair', 'install', 'setup', 'configure', 'update', 'implement',
    'conduct', 'perform', 'execute', 'process', 'handle', 'manage', 'monitor'
]

# Intent types that typically contain tasks
TASK_INTENTS = ['instruction', 'action_required', 'request', 'complaint', 'meeting']


def extract_deadline(text: str) -> Optional[str]:
    """
    Extract deadline from text
    Returns ISO format datetime string or None
    """
    text_lower = text.lower()
    now = datetime.now()
    
    # Patterns for deadline detection
    patterns = {
        r'by tomorrow|tomorrow': timedelta(days=1),
        r'by today|today|asap|urgent|immediately': timedelta(hours=4),
        r'by end of day|eod': timedelta(hours=8),
        r'by end of week|this week': timedelta(days=7 - now.weekday()),
        r'next week': timedelta(days=7),
        r'in (\d+) days?': None,  # Will be handled separately
        r'in (\d+) hours?': None,  # Will be handled separately
        r'within (\d+) days?': None,  # Will be handled separately
    }
    
    # Check for specific date patterns (DD-MM-YYYY, DD/MM/YYYY)
    date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
    date_match = re.search(date_pattern, text)
    if date_match:
        day, month, year = date_match.groups()
        try:
            deadline = datetime(int(year), int(month), int(day), 17, 0)  # Default to 5 PM
            return deadline.isoformat()
        except:
            pass
    
    # Check for relative time patterns
    for pattern, delta in patterns.items():
        if re.search(pattern, text_lower):
            if delta:
                deadline = now + delta
                return deadline.isoformat()
            else:
                # Handle "in X days/hours" patterns
                match = re.search(pattern, text_lower)
                if match:
                    num = int(match.group(1))
                    if 'day' in pattern:
                        deadline = now + timedelta(days=num)
                    elif 'hour' in pattern:
                        deadline = now + timedelta(hours=num)
                    return deadline.isoformat()
    
    # Default deadline: 3 days from now for high priority, 7 days for others
    default_deadline = now + timedelta(days=3)
    return default_deadline.isoformat()


def extract_assignee(text: str, departments: List[str]) -> Optional[str]:
    """
    Extract assignee from text
    Returns department name or None
    """
    text_lower = text.lower()
    
    # Check for explicit department mentions
    for dept in departments:
        if dept.lower() in text_lower:
            return dept
    
    # Check for role-based assignments
    role_patterns = {
        r'collector|district collector': 'Revenue',
        r'health officer|medical officer|doctor': 'Health',
        r'engineer|pwd': 'Infrastructure',
        r'education officer|principal|teacher': 'Education',
        r'police|sp|dsp': 'Police',
    }
    
    for pattern, dept in role_patterns.items():
        if re.search(pattern, text_lower):
            return dept
    
    return None


def generate_task_title(text: str, max_length: int = 80) -> str:
    """
    Generate a concise task title from message text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # If text is short enough, use it as is
    if len(text) <= max_length:
        return text
    
    # Try to extract first sentence
    sentences = re.split(r'[.!?]', text)
    if sentences and len(sentences[0]) <= max_length:
        return sentences[0].strip()
    
    # Truncate and add ellipsis
    return text[:max_length-3].strip() + '...'


def extract_tasks(
    message_text: str,
    intent: str,
    priority: str,
    departments: List[str] = None,
    locations: Dict = None,
    message_id: str = None,
    created_by: str = "Telegram User"
) -> List[Dict]:
    """
    Extract tasks from message text
    
    Args:
        message_text: The message content
        intent: Classified intent
        priority: Message priority (HIGH, MEDIUM, LOW)
        departments: List of available departments
        locations: Extracted location entities
        message_id: Original message ID
        created_by: User who created the message
    
    Returns:
        List of task dictionaries
    """
    # Only extract tasks from relevant intents
    if intent not in TASK_INTENTS:
        return []
    
    # Default values
    if departments is None:
        departments = ['Health', 'Revenue', 'Education', 'Infrastructure', 'Police']
    if locations is None:
        locations = {}
    
    # Process text with spaCy
    doc = nlp(message_text)
    
    # Check if message contains action verbs
    has_action = False
    for token in doc:
        if token.lemma_.lower() in ACTION_VERBS:
            has_action = True
            break
    
    # If no action verbs found and intent is not instruction/action_required, skip
    if not has_action and intent not in ['instruction', 'action_required']:
        return []
    
    # Extract deadline
    deadline = extract_deadline(message_text)
    
    # Extract assignee
    assigned_to = extract_assignee(message_text, departments)
    if not assigned_to and locations.get('department'):
        assigned_to = locations['department']
    
    # Generate task title
    title = generate_task_title(message_text)
    
    # Generate task ID
    timestamp = int(datetime.now().timestamp() * 1000)
    task_id = f"task_{timestamp}_{message_id.split('_')[-1] if message_id else 'unknown'}"
    
    # Create task object
    task = {
        'task_id': task_id,
        'message_id': message_id,
        'title': title,
        'description': message_text,
        'department': assigned_to or 'Unassigned',
        'assigned_to': assigned_to or 'Unassigned',
        'location': {
            'district': locations.get('district'),
            'mandal': locations.get('mandal'),
            'village': locations.get('village')
        },
        'deadline': deadline,
        'priority': priority,
        'status': 'PENDING',
        'created_at': datetime.now().isoformat(),
        'created_by': created_by,
        'completed_at': None,
        'completed_by': None,
        'reminder_sent': False,
        'reminder_count': 0,
        'last_reminder_at': None
    }
    
    return [task]


def format_task_summary(tasks: List[Dict]) -> str:
    """
    Format a summary of extracted tasks for display
    """
    if not tasks:
        return "No tasks extracted."
    
    summary = f"📋 **{len(tasks)} Task(s) Created:**\n\n"
    
    for i, task in enumerate(tasks, 1):
        deadline_str = datetime.fromisoformat(task['deadline']).strftime('%d-%m-%Y')
        summary += f"{i}. {task['title']}\n"
        summary += f"   📅 Deadline: {deadline_str}\n"
        summary += f"   👤 Assigned: {task['assigned_to']}\n"
        if i < len(tasks):
            summary += "\n"
    
    return summary
