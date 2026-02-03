"""
Integration Test Script for Government AI Assistant
Tests the complete end-to-end flow
"""

import requests
import json
import time
from datetime import datetime


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def test_ai_service():
    """Test AI Service health and analysis"""
    print_header("Testing AI Service")
    
    try:
        # Test health endpoint
        print_info("Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("AI Service is healthy")
            data = response.json()
            print(f"   Version: {data.get('version')}")
            print(f"   Uptime: {data.get('uptime_seconds', 0):.2f} seconds")
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
        
        # Test analysis endpoint
        print_info("Testing message analysis...")
        test_message = {
            "message_text": "URGENT: Flood alert in Vijayawada. Immediate action required.",
            "metadata": {}
        }
        
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_message,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Message analysis successful")
            data = response.json()
            analysis = data.get('analysis', {})
            print(f"   Language: {analysis.get('language')}")
            print(f"   Intent: {analysis.get('intent')}")
            print(f"   Priority: {analysis.get('priority')}")
            print(f"   Processing time: {data.get('processing_time_ms', 0):.2f}ms")
        else:
            print_error(f"Analysis failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to AI Service. Is it running on port 8000?")
        return False
    except Exception as e:
        print_error(f"Error testing AI Service: {e}")
        return False


def test_n8n_webhook():
    """Test n8n webhook intake"""
    print_header("Testing n8n Webhook")
    
    try:
        print_info("Sending test message to n8n webhook...")
        
        test_message = {
            "message_text": "Meeting scheduled for 15th January 2026 at 3 PM to discuss budget allocation.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "forwarded_from": "+919876543210",
            "sender_role": "Finance Secretary"
        }
        
        response = requests.post(
            "http://localhost:5678/webhook/whatsapp-intake",
            json=test_message,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Webhook processed successfully")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message ID: {data.get('message_id')}")
            print(f"   Priority: {data.get('priority')}")
            print(f"   Intent: {data.get('intent')}")
        else:
            print_error(f"Webhook failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to n8n. Is it running on port 5678?")
        return False
    except Exception as e:
        print_error(f"Error testing n8n webhook: {e}")
        return False


def test_mongodb():
    """Test MongoDB connection"""
    print_header("Testing MongoDB")
    
    try:
        from pymongo import MongoClient
        
        print_info("Connecting to MongoDB...")
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        print_success("MongoDB connection successful")
        
        # Check database
        db = client['gov_ai_assistant']
        collections = db.list_collection_names()
        print(f"   Collections: {', '.join(collections)}")
        
        # Check message count
        message_count = db.messages.count_documents({})
        print(f"   Messages in database: {message_count}")
        
        # Check task count
        task_count = db.tasks.count_documents({})
        print(f"   Tasks in database: {task_count}")
        
        # Check event count
        event_count = db.calendar_events.count_documents({})
        print(f"   Calendar events: {event_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print_error(f"MongoDB test failed: {e}")
        return False


def test_complete_flow():
    """Test complete end-to-end flow"""
    print_header("Testing Complete Flow")
    
    test_scenarios = [
        {
            "name": "Disaster Alert (High Priority)",
            "message": {
                "message_text": "URGENT: Cyclone warning for Visakhapatnam district. Evacuate coastal areas immediately.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "forwarded_from": "+919876543210",
                "sender_role": "Meteorological Officer"
            },
            "expected_priority": "high",
            "expected_intent": "disaster_alert"
        },
        {
            "name": "Meeting Request (Medium Priority)",
            "message": {
                "message_text": "Meeting scheduled for tomorrow at 10 AM to discuss project implementation.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "forwarded_from": "+919876543211",
                "sender_role": "Project Director"
            },
            "expected_priority": "medium",
            "expected_intent": "meeting"
        },
        {
            "name": "Routine FYI (Low Priority)",
            "message": {
                "message_text": "FYI: New guidelines for office timings have been uploaded to the portal.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "forwarded_from": "+919876543212",
                "sender_role": "Admin Officer"
            },
            "expected_priority": "low",
            "expected_intent": "fyi"
        }
    ]
    
    success_count = 0
    
    for scenario in test_scenarios:
        print_info(f"Testing: {scenario['name']}")
        
        try:
            response = requests.post(
                "http://localhost:5678/webhook/whatsapp-intake",
                json=scenario['message'],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                priority = data.get('priority')
                intent = data.get('intent')
                
                if priority == scenario['expected_priority'] and intent == scenario['expected_intent']:
                    print_success(f"  ✓ Correctly classified as {intent} with {priority} priority")
                    success_count += 1
                else:
                    print_error(f"  ✗ Expected {scenario['expected_intent']}/{scenario['expected_priority']}, got {intent}/{priority}")
            else:
                print_error(f"  ✗ Request failed: {response.status_code}")
        
        except Exception as e:
            print_error(f"  ✗ Error: {e}")
        
        time.sleep(2)  # Wait between requests
    
    print(f"\n{Colors.BOLD}Results: {success_count}/{len(test_scenarios)} scenarios passed{Colors.ENDC}")
    return success_count == len(test_scenarios)


def main():
    """Run all tests"""
    print_header("Government AI Assistant - Integration Tests")
    print(f"{Colors.BOLD}Testing system components...{Colors.ENDC}\n")
    
    results = {
        "AI Service": test_ai_service(),
        "MongoDB": test_mongodb(),
        "n8n Webhook": test_n8n_webhook(),
        "Complete Flow": test_complete_flow()
    }
    
    print_header("Test Summary")
    
    all_passed = True
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print()
    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! System is working correctly.{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}⚠️  Some tests failed. Please check the errors above.{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    exit(main())
