"""
Telegram Bot Integration Test Script
Tests the Telegram bot integration for AP Government AI Assistant
"""

import requests
import json
import time
from datetime import datetime

# Configuration
N8N_TELEGRAM_WEBHOOK = "http://localhost:5678/webhook/telegram-intake"
N8N_DEPARTMENT_WEBHOOK = "http://localhost:5678/webhook/telegram-department-update"

# Test messages
TEST_MESSAGES = [
    {
        "name": "Disaster Alert (High Priority)",
        "message": {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 987654321,
                    "is_bot": False,
                    "first_name": "District Collector",
                    "username": "collector_vijayawada"
                },
                "chat": {
                    "id": 987654321,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "URGENT: Cyclone warning for Visakhapatnam district. Evacuate coastal areas immediately."
            }
        }
    },
    {
        "name": "Power Outage (Medium Priority)",
        "message": {
            "update_id": 123456790,
            "message": {
                "message_id": 2,
                "from": {
                    "id": 987654322,
                    "is_bot": False,
                    "first_name": "Electricity Officer",
                    "username": "power_officer"
                },
                "chat": {
                    "id": 987654322,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Power outage in Krishna district affecting 5000 homes. Need immediate restoration."
            }
        }
    },
    {
        "name": "Meeting Request (Medium Priority)",
        "message": {
            "update_id": 123456791,
            "message": {
                "message_id": 3,
                "from": {
                    "id": 987654323,
                    "is_bot": False,
                    "first_name": "Finance Secretary",
                    "username": "finance_sec"
                },
                "chat": {
                    "id": 987654323,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Meeting scheduled for 20th January 2026 at 3 PM to discuss budget allocation."
            }
        }
    },
    {
        "name": "Infrastructure Update (Low Priority)",
        "message": {
            "update_id": 123456792,
            "message": {
                "message_id": 4,
                "from": {
                    "id": 987654324,
                    "is_bot": False,
                    "first_name": "PWD Engineer",
                    "username": "pwd_engineer"
                },
                "chat": {
                    "id": 987654324,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Road construction in Guntur district is 75% complete. Expected completion by end of month."
            }
        }
    }
]

def test_telegram_intake(message_data):
    """Test Telegram message intake workflow"""
    print(f"\n{'='*60}")
    print(f"Testing: {message_data['name']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            N8N_TELEGRAM_WEBHOOK,
            json=message_data['message'],
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
            print(f"Priority: {result.get('priority', 'N/A')}")
            print(f"Intent: {result.get('intent', 'N/A')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (AI service might be slow)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    time.sleep(2)  # Wait between tests

def test_department_routing(message_data):
    """Test department routing workflow"""
    print(f"\n{'='*60}")
    print(f"Testing Department Routing: {message_data['name']}")
    print(f"{'='*60}")
    
    # Simplify message for department routing
    simplified_message = {
        "message_text": message_data['message']['message']['text'],
        "forwarded_from": message_data['message']['message']['from']['first_name'],
        "sender_role": f"@{message_data['message']['message']['from']['username']}",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            N8N_DEPARTMENT_WEBHOOK,
            json=simplified_message,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Department: {result.get('department', 'N/A')}")
            print(f"Sender: {result.get('sender', 'N/A')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    time.sleep(2)

def check_services():
    """Check if required services are running"""
    print("\n" + "="*60)
    print("Checking Services")
    print("="*60)
    
    services = {
        "AI Service": "http://localhost:8000/health",
        "n8n": "http://localhost:5678",
    }
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Running")
            else:
                print(f"⚠️  {name}: Unexpected status {response.status_code}")
        except:
            print(f"❌ {name}: Not accessible")

def main():
    print("\n" + "="*60)
    print("Telegram Bot Integration Test")
    print("AP Government AI Assistant")
    print("="*60)
    
    # Check services
    check_services()
    
    # Test intake workflow
    print("\n\n" + "="*60)
    print("TESTING TELEGRAM INTAKE WORKFLOW")
    print("="*60)
    
    for message_data in TEST_MESSAGES:
        test_telegram_intake(message_data)
    
    # Test department routing
    print("\n\n" + "="*60)
    print("TESTING DEPARTMENT ROUTING WORKFLOW")
    print("="*60)
    
    for message_data in TEST_MESSAGES[:2]:  # Test first 2 messages
        test_department_routing(message_data)
    
    print("\n\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Check n8n dashboard: http://localhost:5678")
    print("2. Check MongoDB for stored messages")
    print("3. Verify Telegram bot responses (if bot token configured)")
    print("\nNote: For full Telegram integration, configure bot token in telegram_config.json")

if __name__ == "__main__":
    main()
