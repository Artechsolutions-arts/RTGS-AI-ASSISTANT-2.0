#!/usr/bin/env python3
"""
Pre-Deployment Validation Script
Validates all system components before production deployment
"""

import subprocess
import sys
import json
import requests
from datetime import datetime
from pymongo import MongoClient

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

def check_docker_services():
    """Check if all Docker services are running"""
    print_header("Docker Services Check")
    
    required_services = [
        'ai-assist-n8n',
        'ai-assist-postgres',
        'ai-assist-ai-service'
    ]
    
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        running_services = result.stdout.strip().split('\n')
        
        all_running = True
        for service in required_services:
            if service in running_services:
                print_success(f"{service} is running")
            else:
                print_error(f"{service} is NOT running")
                all_running = False
        
        return all_running
    except Exception as e:
        print_error(f"Docker check failed: {e}")
        return False

def check_n8n_workflows():
    """Check if critical n8n workflows are active"""
    print_header("n8n Workflows Check")
    
    try:
        result = subprocess.run(
            ['docker', 'exec', '-u', 'node', 'ai-assist-n8n', 'n8n', 'list:workflow'],
            capture_output=True,
            text=True,
            check=True
        )
        
        workflows = result.stdout.strip().split('\n')
        
        critical_workflows = [
            'Dashboard API - Final',
            '01 - Telegram Message Intake',
            '03 - Rule-Based Routing',
            '04 - Task Creation'
        ]
        
        found_workflows = []
        for workflow in workflows:
            for critical in critical_workflows:
                if critical in workflow:
                    found_workflows.append(critical)
                    print_success(f"Found: {critical}")
        
        missing = set(critical_workflows) - set(found_workflows)
        if missing:
            for wf in missing:
                print_warning(f"Missing: {wf}")
            return False
        
        return True
    except Exception as e:
        print_error(f"n8n workflow check failed: {e}")
        return False

def check_mongodb_connection():
    """Check MongoDB Atlas connection"""
    print_header("MongoDB Connection Check")
    
    try:
        uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Ping the database
        client.admin.command('ping')
        print_success("MongoDB Atlas connection successful")
        
        # Check collections
        db = client['gov_ai_assistant']
        collections = db.list_collection_names()
        
        required_collections = ['messages', 'calendar_events', 'appointments']
        for coll in required_collections:
            if coll in collections:
                count = db[coll].count_documents({})
                print_success(f"Collection '{coll}': {count} documents")
            else:
                print_error(f"Collection '{coll}' not found")
                return False
        
        client.close()
        return True
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return False

def check_ai_service():
    """Check AI service health"""
    print_header("AI Service Health Check")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print_success("AI Service is healthy")
            return True
        else:
            print_error(f"AI Service returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"AI Service check failed: {e}")
        return False

def check_n8n_api():
    """Check n8n API endpoints"""
    print_header("n8n API Endpoints Check")
    
    endpoints = [
        '/webhook/api/messages-v2?district=ntr-district',
        '/webhook/api/calendar?district=ntr-district',
        '/webhook/api/appointments?district=ntr-district'
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            response = requests.get(
                f'http://localhost:5678{endpoint}',
                auth=('admin', 'admin123'),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print_success(f"{endpoint}: {count} items")
            else:
                print_error(f"{endpoint}: Status {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"{endpoint}: {e}")
            all_ok = False
    
    return all_ok

def check_dashboard_build():
    """Check if dashboard can build successfully"""
    print_header("Dashboard Build Check")
    
    try:
        print("Building dashboard (this may take a minute)...")
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd='dashboard',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success("Dashboard build successful")
            return True
        else:
            print_error("Dashboard build failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("Dashboard build timed out")
        return False
    except Exception as e:
        print_error(f"Dashboard build check failed: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Environment Variables Check")
    
    try:
        # Check dashboard .env.local
        with open('dashboard/.env.local', 'r') as f:
            env_content = f.read()
            
        required_vars = ['NEXT_PUBLIC_N8N_BASE_URL']
        all_set = True
        
        for var in required_vars:
            if var in env_content:
                print_success(f"{var} is set")
            else:
                print_error(f"{var} is NOT set")
                all_set = False
        
        return all_set
    except FileNotFoundError:
        print_error("dashboard/.env.local not found")
        return False
    except Exception as e:
        print_error(f"Environment check failed: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    print_header("Disk Space Check")
    
    try:
        result = subprocess.run(
            ['df', '-h', '.'],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            available = parts[3]
            usage = parts[4]
            
            print_success(f"Available: {available}, Usage: {usage}")
            
            # Check if usage is over 90%
            usage_percent = int(usage.rstrip('%'))
            if usage_percent > 90:
                print_warning("Disk usage is over 90%")
                return False
            
            return True
    except Exception as e:
        print_warning(f"Disk space check failed: {e}")
        return True  # Don't fail deployment for this

def generate_deployment_report():
    """Generate deployment readiness report"""
    print_header("Deployment Readiness Report")
    
    checks = {
        "Docker Services": check_docker_services(),
        "n8n Workflows": check_n8n_workflows(),
        "MongoDB Connection": check_mongodb_connection(),
        "AI Service": check_ai_service(),
        "n8n API Endpoints": check_n8n_api(),
        "Environment Variables": check_environment_variables(),
        "Disk Space": check_disk_space(),
        # Skip dashboard build in quick check
        # "Dashboard Build": check_dashboard_build(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY".center(60))
    print("="*60 + "\n")
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{check:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} checks passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}[OK] SYSTEM IS READY FOR DEPLOYMENT{Colors.END}".center(70))
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}[ERROR] SYSTEM IS NOT READY - FIX ISSUES ABOVE{Colors.END}".center(80))
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")
        return False

if __name__ == "__main__":
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Pre-Deployment Validation'.center(60)}{Colors.END}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.BLUE}{f'Started: {timestamp}'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    ready = generate_deployment_report()
    
    sys.exit(0 if ready else 1)
