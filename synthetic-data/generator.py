"""
Synthetic WhatsApp Message Generator for Government AI Assistant
Generates realistic government messages in English, Telugu, and mixed languages
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid


class SyntheticDataGenerator:
    """Generate realistic synthetic WhatsApp messages for government officers"""
    
    def __init__(self):
        # Load dictionaries
        self.districts = self._load_json("../ai-service/dictionaries/districts.json")
        self.mandals = self._load_json("../ai-service/dictionaries/mandals.json")
        self.villages = self._load_json("../ai-service/dictionaries/villages.json")
        self.departments = self._load_json("../ai-service/dictionaries/departments.json")
        
        # Message templates by category
        self.templates = {
            "disaster_alert": [
                "URGENT: {disaster_type} alert in {location}. Immediate action required.",
                "Emergency: {disaster_type} warning for {location} district. Evacuate {area_type} areas immediately.",
                "Critical: {disaster_type} situation in {location}. {action} needed urgently.",
                "Alert: Heavy {disaster_type} expected in {location}. Please take necessary precautions.",
                "{disaster_type} హెచ్చరిక {location}లో. తక్షణ చర్య అవసరం.",  # Telugu
                "Urgent {disaster_type} in {location}. Immediate evacuation చేయండి.",  # Mixed
                "{disaster_type} damage reported in {location}. {casualties} casualties. Send rescue teams.",
                "Flash flood warning for {location} mandal. Alert all villages immediately.",
            ],
            "meeting": [
                "Meeting scheduled for {date} at {time} to discuss {topic}.",
                "Please attend the {meeting_type} on {date} at {time} in {venue}.",
                "Reminder: {meeting_type} tomorrow at {time}. Agenda: {topic}.",
                "{date}న {time}కి మీటింగ్. దయచేసి హాజరు అవ్వండి.",  # Telugu
                "Meeting on {date} at {time} regarding {topic}. Attendance mandatory.",
                "Video conference scheduled for {date} at {time}. Join link will be shared.",
                "{meeting_type} postponed to {date} at {time}. Venue: {venue}.",
                "Request to reschedule meeting from {date} to alternate date.",
            ],
            "instruction": [
                "Please submit {document} by {deadline}. This is urgent.",
                "Kindly prepare {document} and send to {department} by {deadline}.",
                "Action required: {task}. Deadline: {deadline}.",
                "{task} complete చేసి {deadline} లోపు submit చేయండి.",  # Mixed
                "Ensure {task} is completed before {deadline}. No extensions.",
                "Request to verify {document} and provide status update by {deadline}.",
                "Please review and approve {document} at the earliest.",
                "Implement {policy} in {location} mandal. Report progress weekly.",
            ],
            "status_update": [
                "Status update: {task} is {status}. {percentage}% completed.",
                "{project} progress report: {status}. Expected completion: {date}.",
                "Update on {task}: {status}. {details}.",
                "{task} పూర్తయింది. రిపోర్ట్ attached.",  # Telugu
                "Work on {project} is {status}. No major issues reported.",
                "{task} completed successfully. {statistics}.",
                "Progress report for {project}: {percentage}% done. On track.",
                "Delay in {task} due to {reason}. New deadline: {date}.",
            ],
            "fyi": [
                "FYI: New circular regarding {topic} has been uploaded to portal.",
                "For your information: {announcement}.",
                "Please note: {information}. No action required.",
                "Circular: {topic}. Effective from {date}.",
                "Information: {announcement}. Please share with your team.",
                "FYI - {topic} guidelines updated. Check portal for details.",
                "Notification: {announcement}. For reference only.",
                "Attached: {document} for your information.",
            ]
        }
        
        # Context data
        self.disaster_types = [
            "Flood", "Cyclone", "Heavy rainfall", "Drought", "Fire", 
            "Landslide", "Heat wave", "Storm", "వరద", "తుఫాన్"
        ]
        
        self.meeting_types = [
            "Review meeting", "Budget meeting", "Planning session",
            "Video conference", "District meeting", "Department meeting",
            "Emergency meeting", "Coordination meeting"
        ]
        
        self.topics = [
            "budget allocation", "project implementation", "disaster preparedness",
            "infrastructure development", "welfare schemes", "revenue collection",
            "education initiatives", "health programs", "agricultural support",
            "rural development", "urban planning", "road construction"
        ]
        
        self.documents = [
            "monthly report", "budget proposal", "project status report",
            "attendance records", "expenditure statement", "action taken report",
            "compliance certificate", "utilization certificate", "progress report"
        ]
        
        self.tasks = [
            "data collection", "field survey", "inspection", "verification",
            "documentation", "report preparation", "fund allocation",
            "scheme implementation", "beneficiary identification"
        ]
        
        self.statuses = [
            "in progress", "completed", "pending approval", "under review",
            "delayed", "on track", "partially completed"
        ]
        
        self.sender_roles = [
            "District Collector", "Joint Collector", "Revenue Officer",
            "Tahsildar", "Mandal Officer", "Department Secretary",
            "Project Director", "Chief Engineer", "Superintendent",
            "Inspector", "Assistant Commissioner", "Deputy Director"
        ]
        
        self.venues = [
            "Collectorate", "District Office", "Mandal Office",
            "Conference Hall", "Secretariat", "Project Office"
        ]
    
    def _load_json(self, filepath: str) -> List[str]:
        """Load JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _random_date(self, days_ahead: int = 30) -> str:
        """Generate random future date"""
        date = datetime.now() + timedelta(days=random.randint(1, days_ahead))
        return date.strftime("%d-%m-%Y")
    
    def _random_time(self) -> str:
        """Generate random time"""
        hour = random.randint(9, 17)
        minute = random.choice([0, 15, 30, 45])
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        return f"{display_hour}:{minute:02d} {period}"
    
    def _random_timestamp(self, days_back: int = 7) -> str:
        """Generate random past timestamp"""
        date = datetime.now() - timedelta(
            days=random.randint(0, days_back),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        return date.isoformat() + "Z"
    
    def _add_typos(self, text: str, typo_rate: float = 0.1) -> str:
        """Add realistic typos to text"""
        if random.random() > typo_rate:
            return text
        
        # Common typos
        typo_map = {
            "Visakhapatnam": "Vizag",
            "Vijayawada": "Vijayawda",
            "immediately": "immediatly",
            "necessary": "neccessary",
            "schedule": "shedule",
            "receive": "recieve",
            "separate": "seperate",
        }
        
        for correct, typo in typo_map.items():
            if correct in text and random.random() < 0.3:
                text = text.replace(correct, typo)
        
        return text
    
    def generate_message(self, category: str = None) -> Dict:
        """Generate a single synthetic message"""
        if not category:
            category = random.choice(list(self.templates.keys()))
        
        template = random.choice(self.templates[category])
        
        # Fill template with random data
        message_text = template.format(
            disaster_type=random.choice(self.disaster_types),
            location=random.choice(self.districts + self.mandals),
            area_type=random.choice(["coastal", "low-lying", "affected", "vulnerable"]),
            action=random.choice(["Relief measures", "Evacuation", "Emergency response"]),
            casualties=random.randint(0, 50),
            date=self._random_date(),
            time=self._random_time(),
            topic=random.choice(self.topics),
            meeting_type=random.choice(self.meeting_types),
            venue=random.choice(self.venues),
            document=random.choice(self.documents),
            deadline=self._random_date(15),
            task=random.choice(self.tasks),
            department=random.choice(self.departments),
            status=random.choice(self.statuses),
            percentage=random.randint(10, 100),
            project=random.choice(self.topics),
            details=random.choice(["No issues", "Some delays", "On schedule"]),
            statistics=f"{random.randint(100, 1000)} beneficiaries covered",
            reason=random.choice(["technical issues", "staff shortage", "weather conditions"]),
            announcement=random.choice(self.topics),
            information=random.choice(self.topics),
            policy=random.choice(["new scheme", "updated guidelines", "revised procedure"])
        )
        
        # Add typos occasionally
        if random.random() < 0.15:
            message_text = self._add_typos(message_text)
        
        return {
            "message_id": str(uuid.uuid4()),
            "message_text": message_text,
            "timestamp": self._random_timestamp(),
            "forwarded_from": f"+91{random.randint(9000000000, 9999999999)}",
            "sender_role": random.choice(self.sender_roles),
            "category": category,
            "attachments": []
        }
    
    def generate_dataset(self, count: int = 500) -> List[Dict]:
        """Generate a dataset of messages"""
        messages = []
        
        # Distribution of categories
        distribution = {
            "disaster_alert": 0.15,  # 15%
            "meeting": 0.25,         # 25%
            "instruction": 0.25,     # 25%
            "status_update": 0.20,   # 20%
            "fyi": 0.15              # 15%
        }
        
        for category, ratio in distribution.items():
            category_count = int(count * ratio)
            for _ in range(category_count):
                messages.append(self.generate_message(category))
        
        # Shuffle messages
        random.shuffle(messages)
        
        return messages
    
    def save_to_csv(self, messages: List[Dict], filename: str = "messages.csv"):
        """Save messages to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "message_id", "message_text", "timestamp", 
                "forwarded_from", "sender_role", "category"
            ])
            writer.writeheader()
            for msg in messages:
                writer.writerow({
                    "message_id": msg["message_id"],
                    "message_text": msg["message_text"],
                    "timestamp": msg["timestamp"],
                    "forwarded_from": msg["forwarded_from"],
                    "sender_role": msg["sender_role"],
                    "category": msg["category"]
                })
    
    def save_to_json(self, messages: List[Dict], filename: str = "messages.json"):
        """Save messages to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print("Generating synthetic WhatsApp messages...")
    
    generator = SyntheticDataGenerator()
    
    # Generate 500 messages
    messages = generator.generate_dataset(count=500)
    
    print(f"Generated {len(messages)} messages")
    
    # Save to CSV
    generator.save_to_csv(messages, "messages.csv")
    print("Saved to messages.csv")
    
    # Save to JSON
    generator.save_to_json(messages, "messages.json")
    print("Saved to messages.json")
    
    # Print sample messages
    print("\nSample Messages:\n")
    for i, msg in enumerate(messages[:5], 1):
        print(f"{i}. [{msg['category']}] {msg['message_text'][:100]}...")
    
    print(f"\nSynthetic data generation complete!")
