'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDistrictStore } from '@/store/districtStore';
import { Header } from '@/components/Header';
import { n8nClient, CalendarEvent } from '@/lib/n8nClient';

export default function CalendarPage() {
  const router = useRouter();
  const district = useDistrictStore((state) => state.district);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'month' | 'agenda'>('agenda');

  useEffect(() => {
    useDistrictStore.getState().initialize();
    const currentDistrict = useDistrictStore.getState().district;
    if (!currentDistrict) {
      router.push('/login');
      return;
    }

    const fetchCalendar = async () => {
      try {
        setLoading(true);
        const today = new Date();
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);

        const currentDistrict = useDistrictStore.getState().district;
        if (!currentDistrict) return;
        
        const data = await n8nClient.getCalendarByDateRange(
          { district: currentDistrict.name, slug: currentDistrict.slug },
          startOfMonth.toISOString(),
          endOfMonth.toISOString()
        );

        setEvents(data);
      } catch (error) {
        console.error('Error fetching calendar:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCalendar();
    const interval = setInterval(fetchCalendar, 30000);
    return () => clearInterval(interval);
  }, [district, router]);

  const currentDistrict = useDistrictStore((state) => state.district);
  
  if (!currentDistrict) {
    return null;
  }

  const groupedEvents = events.reduce((acc, event) => {
    const date = new Date(event.start).toDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(event);
    return acc;
  }, {} as Record<string, CalendarEvent[]>);

  return (
    <div className="min-h-screen bg-gov-bg">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="gov-card">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gov-primary">Calendar</h1>
            <div className="flex gap-2">
              <button
                onClick={() => setView('agenda')}
                className={`px-4 py-2 rounded ${
                  view === 'agenda' ? 'bg-gov-primary text-white' : 'bg-gray-200'
                }`}
              >
                Agenda
              </button>
              <button
                onClick={() => setView('month')}
                className={`px-4 py-2 rounded ${
                  view === 'month' ? 'bg-gov-primary text-white' : 'bg-gray-200'
                }`}
              >
                Month
              </button>
            </div>
          </div>

          {loading ? (
            <p className="text-gray-500">Loading calendar...</p>
          ) : events.length === 0 ? (
            <p className="text-gray-500">No events scheduled</p>
          ) : view === 'agenda' ? (
            <div className="space-y-6">
              {Object.entries(groupedEvents).map(([date, dayEvents]) => (
                <div key={date}>
                  <h3 className="text-lg font-semibold text-gov-primary mb-3">
                    {new Date(date).toLocaleDateString('en-IN', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </h3>
                  <div className="space-y-3">
                    {dayEvents.map((event) => (
                      <div
                        key={event.id}
                        className="border border-gov-border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-lg text-gov-text">{event.title}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              {new Date(event.start).toLocaleTimeString()} -{' '}
                              {new Date(event.end).toLocaleTimeString()}
                            </p>
                            {event.location && (
                              <p className="text-sm text-gray-600 mt-1">📍 {event.location}</p>
                            )}
                            {event.description && (
                              <p className="text-sm text-gray-500 mt-2">{event.description}</p>
                            )}
                          </div>
                        </div>
                        {event.department && (
                          <p className="text-xs text-gray-500 mt-2">
                            Department: {event.department}
                          </p>
                        )}
                        {event.attendees && event.attendees.length > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            Attendees: {event.attendees.join(', ')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">Month view coming soon</div>
          )}
        </div>
      </main>
    </div>
  );
}
