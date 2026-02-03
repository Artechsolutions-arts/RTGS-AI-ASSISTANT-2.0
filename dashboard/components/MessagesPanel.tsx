'use client';

import { useEffect, useState } from 'react';
import { useDistrictStore } from '@/store/districtStore';
import { n8nClient, Message } from '@/lib/n8nClient';

export function MessagesPanel() {
  const district = useDistrictStore((state) => state.district);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!district) {
      setLoading(false);
      return;
    }

    const fetchMessages = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await n8nClient.getMessages({
          district: district.name,
          slug: district.slug,
        });
        setMessages(data);
      } catch (err) {
        setError('Failed to load messages');
        console.error('Error fetching messages:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
    // Refresh every 30 seconds
    const interval = setInterval(fetchMessages, 30000);
    return () => clearInterval(interval);
  }, [district]);

  if (!district) {
    return (
      <div className="gov-card">
        <p className="text-gray-500">Please log in to view messages</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="gov-card">
        <h2 className="text-xl font-semibold mb-4 text-gov-primary">Recent Messages</h2>
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gov-card">
        <h2 className="text-xl font-semibold mb-4 text-gov-primary">Recent Messages</h2>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="gov-card">
      <h2 className="text-xl font-semibold mb-4 text-gov-primary">Recent Messages</h2>
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages</p>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className="border border-gov-border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium text-gov-text">{message.from}</p>
                  <p className="text-sm text-gray-600">{message.summary}</p>
                </div>
                {message.priority && (
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      message.priority === 'high'
                        ? 'bg-red-100 text-red-800'
                        : message.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {message.priority}
                  </span>
                )}
              </div>
              {message.forwardedDepartment && (
                <p className="text-xs text-gray-500">
                  Forwarded to: {message.forwardedDepartment}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-2">
                {new Date(message.timestamp).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
