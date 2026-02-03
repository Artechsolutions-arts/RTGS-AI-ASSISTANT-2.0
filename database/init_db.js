// MongoDB Initialization Script for Government AI Assistant

// Switch to database
db = db.getSiblingDB('gov_ai_assistant');

print('🗄️  Initializing Government AI Assistant Database...');

// Drop existing collections if they exist
print('🧹 Cleaning up existing collections...');
db.messages.drop();
db.tasks.drop();
db.calendar_events.drop();
db.audit_logs.drop();
db.weekly_reports.drop();

// Create collections with validation
print('📋 Creating collections with schemas...');

// Messages collection
db.createCollection('messages', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['message_id', 'message_text', 'timestamp', 'forwarded_from', 'sender_role', 'created_at'],
            properties: {
                message_id: { bsonType: 'string' },
                message_text: { bsonType: 'string' },
                timestamp: { bsonType: 'date' },
                forwarded_from: { bsonType: 'string' },
                sender_role: { bsonType: 'string' },
                attachments: { bsonType: 'array' },
                ai_analysis: { bsonType: 'object' },
                routing: { bsonType: 'object' },
                status: {
                    bsonType: 'string',
                    enum: ['new', 'processed', 'routed', 'completed', 'archived']
                },
                created_at: { bsonType: 'date' },
                updated_at: { bsonType: 'date' }
            }
        }
    }
});

// Tasks collection
db.createCollection('tasks', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['task_id', 'source_message_id', 'title', 'department', 'priority', 'status', 'created_at'],
            properties: {
                task_id: { bsonType: 'string' },
                source_message_id: { bsonType: 'string' },
                title: { bsonType: 'string' },
                description: { bsonType: 'string' },
                department: { bsonType: 'string' },
                owner_role: { bsonType: 'string' },
                priority: {
                    bsonType: 'string',
                    enum: ['high', 'medium', 'low']
                },
                deadline: { bsonType: ['date', 'null'] },
                status: {
                    bsonType: 'string',
                    enum: ['pending', 'in_progress', 'completed', 'overdue', 'cancelled']
                },
                reminders_sent: { bsonType: 'int' },
                escalated: { bsonType: 'bool' },
                created_at: { bsonType: 'date' },
                updated_at: { bsonType: 'date' }
            }
        }
    }
});

// Calendar events collection
db.createCollection('calendar_events', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['event_id', 'source_message_id', 'title', 'start_time', 'status', 'created_at'],
            properties: {
                event_id: { bsonType: 'string' },
                source_message_id: { bsonType: 'string' },
                title: { bsonType: 'string' },
                description: { bsonType: 'string' },
                start_time: { bsonType: 'date' },
                end_time: { bsonType: ['date', 'null'] },
                location: { bsonType: ['string', 'null'] },
                attendees: { bsonType: 'array' },
                conflict_detected: { bsonType: 'bool' },
                status: {
                    bsonType: 'string',
                    enum: ['scheduled', 'confirmed', 'cancelled', 'completed', 'rescheduled']
                },
                created_at: { bsonType: 'date' },
                updated_at: { bsonType: 'date' }
            }
        }
    }
});

// Audit logs collection
db.createCollection('audit_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['log_id', 'action_type', 'timestamp'],
            properties: {
                log_id: { bsonType: 'string' },
                action_type: {
                    bsonType: 'string',
                    enum: ['ai_analysis', 'message_routing', 'task_creation', 'calendar_event', 'reminder_sent', 'escalation', 'weekly_digest']
                },
                entity_type: {
                    bsonType: 'string',
                    enum: ['message', 'task', 'event', 'system']
                },
                entity_id: { bsonType: ['string', 'null'] },
                timestamp: { bsonType: 'date' }
            }
        }
    }
});

// Weekly reports collection
db.createCollection('weekly_reports', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['report_id', 'week_start', 'week_end', 'created_at'],
            properties: {
                report_id: { bsonType: 'string' },
                week_start: { bsonType: 'date' },
                week_end: { bsonType: 'date' },
                summary: { bsonType: 'object' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

print('✅ Collections created successfully');

// Create indexes
print('🔍 Creating indexes...');

// Messages indexes
db.messages.createIndex({ message_id: 1 }, { unique: true });
db.messages.createIndex({ timestamp: -1 });
db.messages.createIndex({ 'ai_analysis.priority': 1 });
db.messages.createIndex({ 'ai_analysis.intent': 1 });
db.messages.createIndex({ status: 1 });
db.messages.createIndex({ created_at: -1 });

// Tasks indexes
db.tasks.createIndex({ task_id: 1 }, { unique: true });
db.tasks.createIndex({ source_message_id: 1 });
db.tasks.createIndex({ department: 1 });
db.tasks.createIndex({ priority: 1 });
db.tasks.createIndex({ status: 1 });
db.tasks.createIndex({ deadline: 1 });
db.tasks.createIndex({ created_at: -1 });

// Calendar events indexes
db.calendar_events.createIndex({ event_id: 1 }, { unique: true });
db.calendar_events.createIndex({ source_message_id: 1 });
db.calendar_events.createIndex({ start_time: 1 });
db.calendar_events.createIndex({ status: 1 });
db.calendar_events.createIndex({ conflict_detected: 1 });

// Audit logs indexes
db.audit_logs.createIndex({ log_id: 1 }, { unique: true });
db.audit_logs.createIndex({ timestamp: -1 });
db.audit_logs.createIndex({ action_type: 1 });
db.audit_logs.createIndex({ entity_type: 1, entity_id: 1 });

// Weekly reports indexes
db.weekly_reports.createIndex({ report_id: 1 }, { unique: true });
db.weekly_reports.createIndex({ week_start: -1 });
db.weekly_reports.createIndex({ created_at: -1 });

print('✅ Indexes created successfully');

// Insert sample data
print('📝 Inserting sample data...');

// Sample message
db.messages.insertOne({
    message_id: 'sample-msg-001',
    message_text: 'URGENT: Flood alert in Vijayawada. Immediate action required.',
    timestamp: new Date(),
    forwarded_from: '+919876543210',
    sender_role: 'District Collector',
    attachments: [],
    ai_analysis: {
        language: 'english',
        language_confidence: 0.95,
        intent: 'disaster_alert',
        intent_confidence: 0.92,
        priority: 'high',
        priority_confidence: 0.88,
        entities: {
            district: [{ type: 'district', value: 'Vijayawada', confidence: 0.9 }]
        },
        keywords: ['urgent', 'flood', 'alert', 'vijayawada', 'immediate', 'action'],
        sentiment: 'negative'
    },
    routing: {
        department: 'Disaster Management',
        assigned_to: 'Emergency Response Team',
        routed_at: new Date()
    },
    status: 'routed',
    created_at: new Date(),
    updated_at: new Date()
});

// Sample task
db.tasks.insertOne({
    task_id: 'task-001',
    source_message_id: 'sample-msg-001',
    title: 'Emergency flood response in Vijayawada',
    description: 'Coordinate emergency response for flood situation in Vijayawada district',
    department: 'Disaster Management',
    owner_role: 'Emergency Response Coordinator',
    priority: 'high',
    deadline: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours from now
    status: 'pending',
    reminders_sent: 0,
    escalated: false,
    created_at: new Date(),
    updated_at: new Date()
});

// Sample calendar event
db.calendar_events.insertOne({
    event_id: 'event-001',
    source_message_id: 'sample-msg-002',
    title: 'Budget Review Meeting',
    description: 'Quarterly budget review and planning session',
    start_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    end_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000), // 2 hours duration
    location: 'Collectorate Conference Hall',
    attendees: [],
    conflict_detected: false,
    status: 'scheduled',
    reminder_sent: false,
    created_at: new Date(),
    updated_at: new Date()
});

// Sample audit log
db.audit_logs.insertOne({
    log_id: 'log-001',
    action_type: 'ai_analysis',
    entity_type: 'message',
    entity_id: 'sample-msg-001',
    user_role: 'system',
    input_data: {
        message_text: 'URGENT: Flood alert in Vijayawada...'
    },
    output_data: {
        intent: 'disaster_alert',
        priority: 'high'
    },
    ai_confidence: 0.92,
    decision_rationale: 'High priority keywords detected: urgent, flood, alert. Location entity: Vijayawada.',
    status: 'success',
    timestamp: new Date(),
    processing_time_ms: 125.5
});

print('✅ Sample data inserted successfully');

// Print statistics
print('\n📊 Database Statistics:');
print('Messages:', db.messages.countDocuments({}));
print('Tasks:', db.tasks.countDocuments({}));
print('Calendar Events:', db.calendar_events.countDocuments({}));
print('Audit Logs:', db.audit_logs.countDocuments({}));
print('Weekly Reports:', db.weekly_reports.countDocuments({}));

print('\n✅ Database initialization complete!');
