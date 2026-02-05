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
  private async fetch(endpoint: string, district?: DistrictContext, date?: string): Promise<any> {
    try {
      let proxyUrl = `/api/proxy?endpoint=${encodeURIComponent(endpoint)}${district ? `&district=${encodeURIComponent(district.slug)}` : ''}`;
      if (date) {
        proxyUrl += `&date=${encodeURIComponent(date)}`;
      }
      
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

  private getDepartmentFallback(summary: string): string {
    const text = (summary || '').toLowerCase();
    
    // Electricity
    if (text.includes('power') || text.includes('current') || text.includes('vidyut') || 
        text.includes('కరెంటు') || text.includes('విద్యుత్') || text.includes('వైర్')) return 'Electricity';
    
    // Health
    if (text.includes('doctor') || text.includes('hospital') || text.includes('ambulance') || 
        text.includes('వైద్య') || text.includes('ఆరోగ్య') || text.includes('చికిత్స') || 
        text.includes('మెడికల్')) return 'Health Department';
    
    // Disaster
    if (text.includes('flood') || text.includes('fire') || text.includes('varada') || 
        text.includes('వరద') || text.includes('వర్షం') || text.includes('గాలివాన')) return 'Disaster Management';
    
    // Infrastructure
    if (text.includes('road') || text.includes('bridge') || text.includes('building') || 
        text.includes('రోడ్డు') || text.includes('వంతెన') || text.includes('రోడ్')) return 'Infrastructure';
    
    // Water
    if (text.includes('water') || text.includes('drainage') || text.includes('నీరు') || 
        text.includes('మంచినీరు')) return 'Water & Sanitation';
        
    return 'General Administration';
  }

  private mapMessage(raw: any): Message {
    const summary = raw.summary || raw.message_text || '';
    const dept = raw.department || this.getDepartmentFallback(summary);
    
    return {
      id: raw.id || raw._id,
      summary: summary,
      from: raw.from || raw.sender_name || 'Citizen',
      location: raw.location || (raw.ai_analysis?.entities?.location?.[0]?.value) || 'Unknown',
      forwardedDepartment: dept,
      timestamp: raw.timestamp || raw.created_at || '',
      priority: (raw.priority || raw.ai_analysis?.priority || 'medium').toLowerCase() as any,
      department: dept,
      status: raw.status || 'active',
      _raw: raw
    };
  }

  async getMessages(district: DistrictContext, date?: string): Promise<Message[]> {
    const data = await this.fetch('/api/messages-v2', district, date);
    return data.map((m: any) => this.mapMessage(m));
  }

  async getCalendar(district: DistrictContext, date?: string): Promise<CalendarEvent[]> {
    const data = await this.fetch('/api/calendar', district, date);
    return data.map((item: any) => ({
      id: item.id || item._id,
      title: item.title || item.summary || 'Untitled Event',
      start: item.start || item.start_time || '',
      end: item.end || item.end_time || '',
      location: item.location || '',
      department: item.department || '',
      description: item.description || ''
    }));
  }

  async getCalendarByDateRange(district: DistrictContext, start: string, end: string): Promise<CalendarEvent[]> {
    // For now, repurpose getCalendar or use a dedicated endpoint if available.
    // Given the request constraints and existing unified API:
    const data = await this.fetch(`/api/calendar?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`, district);
    return data.map((item: any) => ({
      id: item.id || item._id,
      title: item.title || item.summary || 'Untitled Event',
      start: item.start || item.start_time || '',
      end: item.end || item.end_time || '',
      location: item.location || '',
      department: item.department || '',
      description: item.description || ''
    }));
  }

  async getAppointments(district: DistrictContext, date?: string): Promise<CalendarEvent[]> {
    const data = await this.fetch('/api/appointments', district, date);
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
