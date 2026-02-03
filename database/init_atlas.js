// MongoDB Atlas Initialization Script
// Run this script to initialize the gov_ai_assistant database in MongoDB Atlas

// Connect to MongoDB Atlas
// mongosh "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant"

print("=== Initializing MongoDB Atlas Database ===");
print("Database: gov_ai_assistant");
print("");

// Use the database
db = db.getSiblingDB('gov_ai_assistant');

// Drop existing collections (optional - comment out if you want to keep existing data)
// print("Dropping existing collections...");
// db.messages.drop();
// db.tasks.drop();
// db.calendar_events.drop();
// db.audit_logs.drop();
// db.weekly_reports.drop();

// Create collections
print("Creating collections...");

db.createCollection("messages", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["message_id", "message_text", "status", "created_at"],
            properties: {
                message_id: { bsonType: "string" },
                message_text: { bsonType: "string" },
                timestamp: { bsonType: "date" },
                forwarded_from: { bsonType: "string" },
                sender_role: { bsonType: "string" },
                sender_info: { bsonType: "object" },
                attachments: { bsonType: "array" },
                ai_analysis: { bsonType: "object" },
                routing: { bsonType: "object" },
                status: { bsonType: "string", enum: ["new", "processed", "routed", "completed"] },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

db.createCollection("tasks", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["task_id", "source_message_id", "title", "priority", "status"],
            properties: {
                task_id: { bsonType: "string" },
                source_message_id: { bsonType: "string" },
                title: { bsonType: "string" },
                description: { bsonType: "string" },
                department: { bsonType: "string" },
                owner_role: { bsonType: "string" },
                priority: { bsonType: "string", enum: ["high", "medium", "low"] },
                deadline: { bsonType: "date" },
                status: { bsonType: "string", enum: ["pending", "in_progress", "completed", "overdue"] },
                reminders_sent: { bsonType: "int" },
                escalated: { bsonType: "bool" },
                escalation_level: { bsonType: "int" }
            }
        }
    }
});

db.createCollection("calendar_events", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["event_id", "title", "start_time", "end_time", "status"],
            properties: {
                event_id: { bsonType: "string" },
                source_message_id: { bsonType: "string" },
                title: { bsonType: "string" },
                description: { bsonType: "string" },
                start_time: { bsonType: "date" },
                end_time: { bsonType: "date" },
                location: { bsonType: "string" },
                attendees: { bsonType: "array" },
                conflict_detected: { bsonType: "bool" },
                conflicting_events: { bsonType: "array" },
                status: { bsonType: "string", enum: ["scheduled", "confirmed", "cancelled"] }
            }
        }
    }
});

db.createCollection("audit_logs");
db.createCollection("weekly_reports");

print("✓ Collections created");
print("");

// Create indexes
print("Creating indexes...");

// Messages indexes
db.messages.createIndex({ "message_id": 1 }, { unique: true });
db.messages.createIndex({ "status": 1 });
db.messages.createIndex({ "created_at": -1 });
db.messages.createIndex({ "sender_info.department": 1 });
db.messages.createIndex({ "ai_analysis.priority": 1 });
db.messages.createIndex({ "ai_analysis.intent": 1 });

// Tasks indexes
db.tasks.createIndex({ "task_id": 1 }, { unique: true });
db.tasks.createIndex({ "status": 1 });
db.tasks.createIndex({ "priority": 1 });
db.tasks.createIndex({ "deadline": 1 });
db.tasks.createIndex({ "department": 1 });

// Calendar events indexes
db.calendar_events.createIndex({ "event_id": 1 }, { unique: true });
db.calendar_events.createIndex({ "start_time": 1 });
db.calendar_events.createIndex({ "status": 1 });

// Audit logs indexes
db.audit_logs.createIndex({ "timestamp": -1 });
db.audit_logs.createIndex({ "action_type": 1 });

// Weekly reports indexes
db.weekly_reports.createIndex({ "week_start": -1 });
db.weekly_reports.createIndex({ "created_at": -1 });

print("✓ Indexes created");
print("");

// Insert sample data (optional)
print("Inserting sample data...");

db.messages.insertOne({
    message_id: "sample-001",
    message_text: "Sample message for testing",
    timestamp: new Date(),
    forwarded_from: "+919876543210",
    sender_role: "Test User",
    sender_info: {
        name: "Test User",
        role: "System",
        department: "testing",
        phone: "+919876543210"
    },
    attachments: [],
    ai_analysis: {
        language: "english",
        intent: "test",
        priority: "low",
        confidence: 0.95,
        entities: {}
    },
    routing: {
        department: "testing",
        whatsapp_group: "test_group",
        sent_to_group: false,
        sent_to_collector: false
    },
    status: "new",
    created_at: new Date(),
    updated_at: new Date()
});

print("✓ Sample data inserted");
print("");

// Verify setup
print("=== Verification ===");
print("Collections:");
db.getCollectionNames().forEach(function (col) {
    print("  - " + col + ": " + db[col].countDocuments() + " documents");
});

print("");
print("=== Setup Complete! ===");
print("Database: gov_ai_assistant");
print("Connection: mongodb+srv://artechnical707_db_user@rtgsai.pjyqjep.mongodb.net/");
print("");
print("Next steps:");
print("1. Update n8n MongoDB credentials with Atlas connection string");
print("2. Test connection from n8n workflows");
print("3. Run test_department_routing.bat to verify end-to-end flow");
