'use client';

import { useState, useRef, useEffect } from 'react';
import { useDistrictStore } from '@/store/districtStore';
import { n8nClient } from '@/lib/n8nClient';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const district = useDistrictStore((state) => state.district);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcome = district
        ? `Welcome to ${district.name} District Dashboard. How can I help you?`
        : 'Welcome. Please log in to access district information.';
      setMessages([{ role: 'assistant', content: welcome }]);
    }
  }, [isOpen, district, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !district) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Process query based on n8n data
      const response = await processQuery(userMessage, district);
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const processQuery = async (query: string, district: any): Promise<string> => {
    const lowerQuery = query.toLowerCase();

    // Check for meeting/calendar queries
    if (lowerQuery.includes('meeting') || lowerQuery.includes('calendar') || lowerQuery.includes('schedule')) {
      const events = await n8nClient.getCalendar({ district: district.name, slug: district.slug });
      if (events.length === 0) {
        return 'No meetings scheduled for today.';
      }
      return `You have ${events.length} meeting(s) today:\n${events
        .slice(0, 5)
        .map((e) => `• ${e.title} at ${new Date(e.start).toLocaleTimeString()}`)
        .join('\n')}`;
    }

    // Check for message queries
    if (lowerQuery.includes('message') || lowerQuery.includes('inbox')) {
      const messages = await n8nClient.getMessages({ district: district.name, slug: district.slug });
      if (messages.length === 0) {
        return 'No recent messages.';
      }
      return `You have ${messages.length} recent message(s):\n${messages
        .slice(0, 5)
        .map((m) => `• ${m.summary} (from ${m.from})`)
        .join('\n')}`;
    }

    // Check for department queries
    if (lowerQuery.includes('department')) {
      const departments = await n8nClient.getDepartments({ district: district.name, slug: district.slug });
      if (departments.length === 0) {
        return 'No department data available.';
      }
      return `Departments:\n${departments
        .slice(0, 5)
        .map((d) => `• ${d.name}: ${d.messageCount} messages, ${d.pendingTasks} pending tasks`)
        .join('\n')}`;
    }

    // Default response
    return 'I can help you with meetings, messages, and department information. What would you like to know?';
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-gov-primary text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-colors z-40"
        title="Open Chatbot"
      >
        💬
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white border border-gov-border rounded-lg shadow-xl flex flex-col z-50">
          {/* Header */}
          <div className="bg-gov-primary text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">Chat Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-gov-primary text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">Thinking...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gov-border">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask a question..."
                className="flex-1 border border-gov-border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gov-primary"
                disabled={loading || !district}
              />
              <button
                onClick={handleSend}
                disabled={loading || !district || !input.trim()}
                className="bg-gov-primary text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
