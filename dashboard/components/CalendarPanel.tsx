'use client';

import { useEffect, useState } from 'react';
import { useDistrictStore } from '@/store/districtStore';
import { n8nClient, CalendarEvent } from '@/lib/n8nClient';

export function CalendarPanel() {
  const district = useDistrictStore((state) => state.district);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!district) {
      setLoading(false);
      return;
    }

    const fetchCalendar = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await n8nClient.getCalendar({
          district: district.name,
          slug: district.slug,
        });
        setEvents(data);
      } catch (err) {
        setError('Failed to load calendar');
        console.error('Error fetching calendar:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCalendar();
    // Refresh every 30 seconds
    const interval = setInterval(fetchCalendar, 30000);
    return () => clearInterval(interval);
  }, [district]);

  if (!district) {
    return (
      <div className="gov-card">
        <p className="text-gray-500">Please log in to view calendar</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="gov-card">
        <h2 className="text-xl font-semibold mb-4 text-gov-primary">Today&apos;s Schedule</h2>
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gov-card">
        <h2 className="text-xl font-semibold mb-4 text-gov-primary">Today&apos;s Schedule</h2>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  const today = new Date();
  const todayEvents = events.filter((event) => {
    const eventDate = new Date(event.start);
    return eventDate.toDateString() === today.toDateString();
  });

  return (
    <div className="gov-card">
      <h2 className="text-xl font-semibold mb-4 text-gov-primary">Today&apos;s Schedule</h2>
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {todayEvents.length === 0 ? (
          <p className="text-gray-500">No meetings scheduled for today</p>
        ) : (
          todayEvents.map((event) => (
            <div
              key={event.id}
              className="border border-gov-border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium text-gov-text">{event.title}</p>
                  {event.location && (
                    <p className="text-sm text-gray-600">📍 {event.location}</p>
                  )}
                </div>
                <p className="text-sm text-gray-500">
                  {new Date(event.start).toLocaleTimeString()}
                </p>
              </div>
              {event.department && (
                <p className="text-xs text-gray-500">Department: {event.department}</p>
              )}
              {event.attendees && event.attendees.length > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  Attendees: {event.attendees.join(', ')}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
