/**
 * n8n API Client
 * Optimized for secure, direct n8n workflow communication
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
  _raw?: any; // For debugging
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

      if (!response.ok) {
        console.warn(`[n8n SYNC] Proxy returned ${response.status}. This usually means an n8n node failed or had no output.`);
        return [];
      }
      const data = await response.json();
      return Array.isArray(data) ? data : (data ? [data] : []);
    } catch (error) {
      console.error('[n8n SYNC] Network Failure:', error);
      return null;
    }
  }

  private mapMessage(raw: any): Message {
    // Robust timestamp extraction
    const ts = raw.timestamp || raw.created_at || raw.date || new Date().toISOString();
    
    const routing = raw.routing || {};
    
    return {
      id: raw.id || raw._id || Math.random().toString(36).substr(2, 9),
      summary: raw.summary || raw.message_text || raw.text || raw.body || raw.content || 'No Content',
      from: raw.from || raw.sender_name || raw.sender_role || raw.user_id || 'Citizen',
      location: raw.location || raw.ai_analysis?.entities?.location?.[0]?.value || raw.analysis?.entities?.location?.[0]?.value || 'Unknown',
      forwardedDepartment: raw.forwarded_from || raw.category || routing.department || raw.routed_to || raw.assigned_to || raw.department || 'General',
      timestamp: ts,
      priority: (raw.priority || raw.analysis?.priority || 'medium').toLowerCase() as any,
      department: (() => {
        const baseDept = raw.forwarded_from || raw.category || routing.department || raw.department;
        
        // Map internal slugs to professional names
        const deptMap: Record<string, string> = {
          'electricity': 'ELECTRICITY DEPT',
          'infrastructure': 'INFRASTRUCTURE (R&B)',
          'disaster_management': 'DISASTER MANAGEMENT',
          'health': 'HEALTH & MEDICAL'
        };

        if (baseDept && deptMap[baseDept.toLowerCase()]) return deptMap[baseDept.toLowerCase()];
        if (baseDept) return baseDept.replace('_', ' ').toUpperCase();
        
        // Intelligence Fallback: Match text if routing is missing
        const text = (raw.message_text || raw.summary || raw.text || '').toLowerCase();
        
        // --- MULTILINGUAL ROUTING ENGINE (Telugu + English + Tanglish) ---
        
        // 🚨 DISASTER MANAGEMENT
        // Keywords: flood, rain, agni, mantalu, varada, storm, cyclone
        if (text.includes('flood') || text.includes('cyclone') || text.includes('fire') || text.includes('emergency') ||
            text.includes('varada') || text.includes('వరద') || text.includes('వర్షం') || text.includes('varsham') ||
            text.includes('agni') || text.includes('మంటలు') || text.includes('తుఫాను')) return 'DISASTER MANAGEMENT';
        
        // 🏥 HEALTH & MEDICAL
        // Keywords: medical, hospital, ambulance, arogyam, doctor, pichodu (medical/mental health), madyapanam
        if (text.includes('medical') || text.includes('hospital') || text.includes('ambulance') || text.includes('ambule') ||
            text.includes('arogyam') || text.includes('ఆరోగ్యం') || text.includes('ఆసుపత్రి') || text.includes('doctor') ||
            text.includes('డాక్టర్') || text.includes('అంబులెన్స్') || text.includes('వైద్య')) return 'HEALTH & MEDICAL';
        
        // ⚡ ELECTRICITY DEPT
        // Keywords: power, current, electricity, cut, transformer, shock, vidyut, currentu
        if (text.includes('power') || text.includes('current') || text.includes('electricity') || text.includes('cut') ||
            text.includes('transformer') || text.includes('vidyut') || text.includes('విద్యుత్') || text.includes('కరెంటు') ||
            text.includes('shock') || text.includes('తీగలు')) return 'ELECTRICITY DEPT';
        
        // 💧 WATER BOARD / GVMC
        // Keywords: water, leak, supply, drain, drainage, neellu, manchineeru
        if (text.includes('water') || text.includes('leak') || text.includes('supply') || text.includes('drain') ||
            text.includes('neellu') || text.includes('నీళ్లు') || text.includes('మంచినీరు') || text.includes('నల్లా') ||
            text.includes('మురికినీరు')) return 'WATER BOARD / GVMC';
        
        // 🏗️ INFRASTRUCTURE (R&B)
        // Keywords: road, pothole, bridge, construction, roadu, vantena
        if (text.includes('road') || text.includes('pothole') || text.includes('infrastructure') || text.includes('bridge') ||
            text.includes('రోడ్డు') || text.includes('వంతెన') || text.includes('గుంతలు') || text.includes('నిర్మాణం')) return 'INFRASTRUCTURE (R&B)';
        
        return 'RTGS';
      })(),
      status: raw.status || 'active',
      _raw: raw
    };
  }

  async getMessages(district: DistrictContext): Promise<Message[]> {
    const data = await this.fetch('/messages-recent', district);
    if (!Array.isArray(data)) return [];
    
    console.log(`[n8n SYNC] Received ${data.length} messages from DB`);
    return data.map(m => this.mapMessage(m));
  }

  async getCalendar(district: DistrictContext): Promise<CalendarEvent[]> {
    const data = await this.fetch('/calendar-today', district);
    if (!Array.isArray(data)) return [];
    
    return data.map((item: any) => ({
      id: item.id || item._id || Math.random().toString(36).substr(2, 9),
      title: item.title || item.event_name || 'Meeting',
      start: item.start || item.start_time || new Date().toISOString(),
      end: item.end || item.end_time || new Date().toISOString(),
      location: item.location || 'Conference Hall',
      department: item.department || 'General Admin'
    }));
  }
}

export const n8nClient = new N8nClient();
export type { Message as N8nMessage, CalendarEvent as N8nCalendarEvent };
