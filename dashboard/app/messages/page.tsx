'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDistrictStore } from '@/store/districtStore';
import { Header } from '@/components/Header';
import { n8nClient, Message } from '@/lib/n8nClient';

export default function MessagesPage() {
  const router = useRouter();
  const district = useDistrictStore((state) => state.district);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<{ department?: string; priority?: string }>({});

  useEffect(() => {
    useDistrictStore.getState().initialize();
    const currentDistrict = useDistrictStore.getState().district;
    if (!currentDistrict) {
      router.push('/login');
      return;
    }

    const fetchMessages = async () => {
      try {
        setLoading(true);
        let data: Message[];
        
        if (filter.department) {
          data = await n8nClient.getMessagesByDepartment(
            { district: currentDistrict.name, slug: currentDistrict.slug },
            filter.department
          );
        } else {
          data = await n8nClient.getMessages({
            district: currentDistrict.name,
            slug: currentDistrict.slug,
          });
        }

        if (filter.priority) {
          data = data.filter((m) => m.priority === filter.priority);
        }

        setMessages(data);
      } catch (error) {
        console.error('Error fetching messages:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
    const interval = setInterval(fetchMessages, 30000);
    return () => clearInterval(interval);
  }, [district, router, filter]);

  const currentDistrict = useDistrictStore((state) => state.district);
  
  if (!currentDistrict) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gov-bg">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="gov-card">
          <h1 className="text-2xl font-bold text-gov-primary mb-6">Messages</h1>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <select
              value={filter.department || ''}
              onChange={(e) =>
                setFilter({ ...filter, department: e.target.value || undefined })
              }
              className="gov-input"
            >
              <option value="">All Departments</option>
              <option value="Health">Health</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Education">Education</option>
            </select>

            <select
              value={filter.priority || ''}
              onChange={(e) =>
                setFilter({ ...filter, priority: e.target.value || undefined })
              }
              className="gov-input"
            >
              <option value="">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Messages List */}
          {loading ? (
            <p className="text-gray-500">Loading messages...</p>
          ) : messages.length === 0 ? (
            <p className="text-gray-500">No messages found</p>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className="border border-gov-border rounded-lg p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="font-semibold text-lg text-gov-text">{message.from}</p>
                      <p className="text-gray-600 mt-1">{message.summary}</p>
                    </div>
                    {message.priority && (
                      <span
                        className={`px-3 py-1 rounded text-sm font-medium ${
                          message.priority === 'high'
                            ? 'bg-red-100 text-red-800'
                            : message.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {message.priority.toUpperCase()}
                      </span>
                    )}
                  </div>
                  {message.forwardedDepartment && (
                    <p className="text-sm text-gray-500 mb-2">
                      Forwarded to: <span className="font-medium">{message.forwardedDepartment}</span>
                    </p>
                  )}
                  {message.department && (
                    <p className="text-sm text-gray-500 mb-2">
                      Department: <span className="font-medium">{message.department}</span>
                    </p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(message.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
