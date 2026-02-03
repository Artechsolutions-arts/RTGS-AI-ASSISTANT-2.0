"""
System Validation Script
Checks all components of the Government AI Assistant
"""

import os
import json
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[FAIL] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}> {text}{Colors.END}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print_success(f"{description}: {size:,} bytes")
        return True
    else:
        print_error(f"{description}: NOT FOUND")
        return False

def validate_json_file(filepath, description):
    """Validate JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            print_success(f"{description}: {len(data)} items")
        elif isinstance(data, dict):
            print_success(f"{description}: {len(data.keys())} keys")
        return True
    except Exception as e:
        print_error(f"{description}: {str(e)}")
        return False

def main():
    print_header("GOVERNMENT AI ASSISTANT - SYSTEM VALIDATION")
    
    base_path = Path(__file__).parent
    results = {"passed": 0, "failed": 0}
    
    # Check main documentation files
    print_header("1. DOCUMENTATION FILES")
    docs = [
        ("README.md", "Main README"),
        ("SETUP_GUIDE.md", "Setup Guide"),
        ("TECHNICAL_DOCUMENTATION.md", "Technical Documentation"),
        ("PROJECT_SUMMARY.md", "Project Summary"),
        ("SYSTEM_FLOW.md", "System Flow Diagram"),
    ]
    for filename, desc in docs:
        if check_file_exists(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check AI service files
    print_header("2. AI SERVICE FILES")
    ai_files = [
        ("ai-service/requirements.txt", "Python Requirements"),
        ("ai-service/Dockerfile", "Docker Configuration"),
        ("ai-service/app/__init__.py", "Package Init"),
        ("ai-service/app/main.py", "FastAPI Application"),
        ("ai-service/app/models.py", "Data Models"),
        ("ai-service/app/nlp_engine.py", "NLP Engine"),
        ("ai-service/app/language_detector.py", "Language Detector"),
        ("ai-service/app/intent_classifier.py", "Intent Classifier"),
        ("ai-service/app/priority_classifier.py", "Priority Classifier"),
        ("ai-service/app/ner_engine.py", "NER Engine"),
        ("ai-service/app/spell_corrector.py", "Spell Corrector"),
    ]
    for filename, desc in ai_files:
        if check_file_exists(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check dictionaries
    print_header("3. GOVERNMENT DICTIONARIES")
    dict_files = [
        ("ai-service/dictionaries/districts.json", "Districts"),
        ("ai-service/dictionaries/mandals.json", "Mandals"),
        ("ai-service/dictionaries/villages.json", "Villages"),
        ("ai-service/dictionaries/departments.json", "Departments"),
    ]
    for filename, desc in dict_files:
        if validate_json_file(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check database files
    print_header("4. DATABASE SCHEMAS")
    db_files = [
        ("database/init_db.js", "MongoDB Init Script"),
        ("database/schemas/messages.json", "Messages Schema"),
        ("database/schemas/tasks.json", "Tasks Schema"),
        ("database/schemas/calendar_events.json", "Calendar Events Schema"),
        ("database/schemas/audit_logs.json", "Audit Logs Schema"),
        ("database/schemas/weekly_reports.json", "Weekly Reports Schema"),
    ]
    for filename, desc in db_files:
        if check_file_exists(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check n8n workflows
    print_header("5. N8N WORKFLOWS")
    workflow_files = [
        ("n8n-workflows/01-whatsapp-intake.json", "WhatsApp Intake Workflow"),
        ("n8n-workflows/03-rule-routing.json", "Rule-Based Routing Workflow"),
        ("n8n-workflows/04-task-creation.json", "Task Creation Workflow"),
        ("n8n-workflows/05-calendar-management.json", "Calendar Management Workflow"),
        ("n8n-workflows/06-weekly-digest.json", "Weekly Digest Workflow"),
    ]
    for filename, desc in workflow_files:
        if validate_json_file(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check synthetic data
    print_header("6. SYNTHETIC DATA")
    if os.path.exists(base_path / "synthetic-data/messages.json"):
        try:
            with open(base_path / "synthetic-data/messages.json", 'r', encoding='utf-8') as f:
                messages = json.load(f)
            print_success(f"Messages JSON: {len(messages)} messages")
            
            # Analyze categories
            categories = {}
            languages = {"english": 0, "telugu": 0, "mixed": 0}
            
            for msg in messages:
                cat = msg.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
                
                # Detect language
                text = msg.get('message_text', '')
                if any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in text):
                    if any(c.isalpha() and ord(c) < 128 for c in text):
                        languages["mixed"] += 1
                    else:
                        languages["telugu"] += 1
                else:
                    languages["english"] += 1
            
            print_info(f"Categories: {categories}")
            print_info(f"Languages: {languages}")
            results["passed"] += 1
        except Exception as e:
            print_error(f"Messages JSON: {str(e)}")
            results["failed"] += 1
    else:
        print_error("Messages JSON: NOT FOUND")
        results["failed"] += 1
    
    if check_file_exists(base_path / "synthetic-data/messages.csv", "Messages CSV"):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    if check_file_exists(base_path / "synthetic-data/generator.py", "Data Generator Script"):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    if check_file_exists(base_path / "synthetic-data/seed_mongodb.py", "MongoDB Seed Script"):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Check dashboard files
    print_header("7. DASHBOARD FILES")
    dashboard_files = [
        ("dashboard/index.html", "Dashboard HTML"),
        ("dashboard/style.css", "Dashboard CSS"),
        ("dashboard/app.js", "Dashboard JavaScript"),
    ]
    for filename, desc in dashboard_files:
        if check_file_exists(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Check deployment files
    print_header("8. DEPLOYMENT FILES")
    deploy_files = [
        ("docker-compose.yml", "Docker Compose"),
        ("quick_start.bat", "Quick Start Script"),
        ("test_integration.py", "Integration Tests"),
    ]
    for filename, desc in deploy_files:
        if check_file_exists(base_path / filename, desc):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Summary
    print_header("VALIDATION SUMMARY")
    total = results["passed"] + results["failed"]
    percentage = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Total Checks: {total}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    print(f"\n{Colors.BOLD}Success Rate: {percentage:.1f}%{Colors.END}\n")
    
    if results["failed"] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] ALL CHECKS PASSED! System is complete and ready.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}[WARNING] Some checks failed. Review the output above.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
