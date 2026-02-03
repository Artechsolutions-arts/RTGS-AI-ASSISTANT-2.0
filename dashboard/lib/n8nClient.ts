/**
 * n8n API Client
 * Optimized for secure, direct n8n workflow communication
 * STABLE VERSION: No dynamic time jumping, no mock fallbacks
 */

export interface DistrictContext {
  district: string;
  slug: string;
}

export interface Message {
  id: string;
  summary: string;
  from: string;
  location?: string;
  forwardedDepartment?: string;
  timestamp: string;
  priority?: 'high' | 'medium' | 'low';
  department?: string;
  status?: string;
  _raw?: any;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  location?: string;
  department?: string;
  description?: string;
}

class N8nClient {
  private async fetch(endpoint: string, district?: DistrictContext): Promise<any> {
    try {
      const proxyUrl = `/api/proxy?endpoint=${encodeURIComponent(endpoint)}${district ? `&district=${encodeURIComponent(district.slug)}` : ''}`;
      
      const response = await fetch(proxyUrl, {
        method: 'GET',
        cache: 'no-store'
      });

      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : (data ? [data] : []);
    } catch (error) {
      console.error('[n8n SYNC] Network Failure:', error);
      return [];
    }
  }

  private mapMessage(raw: any): Message {
    return {
      id: raw.id || raw._id,
      summary: raw.summary || raw.message_text || '',
      from: raw.from || raw.sender_name || 'Citizen',
      location: raw.location || '',
      forwardedDepartment: raw.department || raw.forwarded_from || '',
      timestamp: raw.timestamp || raw.created_at || '',
      priority: (raw.priority || 'medium').toLowerCase() as any,
      department: raw.department || '',
      status: raw.status || 'active',
      _raw: raw
    };
  }

  async getMessages(district: DistrictContext): Promise<Message[]> {
    const data = await this.fetch('/api/messages', district);
    return data.map(m => this.mapMessage(m));
  }

  async getCalendar(district: DistrictContext): Promise<CalendarEvent[]> {
    const data = await this.fetch('/api/calendar', district);
    return data.map((item: any) => ({
      id: item.id || item._id,
      title: item.title || '',
      start: item.start || item.start_time || '', // REMOVED Dynamic Fallback
      end: item.end || item.end_time || '',
      location: item.location || '',
      department: item.department || '',
      description: item.description || ''
    }));
  }

  async getAppointments(district: DistrictContext): Promise<CalendarEvent[]> {
    const data = await this.fetch('/api/appointments', district);
    return data.map((item: any) => ({
      id: item.id || item._id,
      title: item.citizen_name || 'Citizen',
      start: item.start || item.start_time || '', // REMOVED Dynamic Fallback 
      end: item.end || item.end_time || '',
      location: item.location || '',
      department: item.department || '',
      description: item.reason || ''
    }));
  }
}

export const n8nClient = new N8nClient();
export type { Message as N8nMessage, CalendarEvent as N8nCalendarEvent };
