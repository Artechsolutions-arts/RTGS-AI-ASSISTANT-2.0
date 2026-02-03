/**
 * Mock Data Provider for Dashboard
 * Provides realistic government-grade operational data
 */

import { N8nMessage, N8nCalendarEvent } from './n8nClient';

export function getMockMessages(): N8nMessage[] {
  const now = new Date();
  
  return [
    {
      id: '1',
      summary: 'Severe water logging reported at Benz Circle after heavy rains',
      from: 'Officer 247',
      timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
      priority: 'high',
      department: 'Disaster Management',
      status: 'in_progress'
    },
    {
      id: '2',
      summary: 'Request for urgent medical supplies at Vijayawada General Hospital',
      from: 'Officer 189',
      timestamp: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(),
      priority: 'high',
      department: 'Health',
      status: 'new'
    },
    {
      id: '3',
      summary: 'Street lights not working in Patamata area for 3 days',
      from: 'Officer 512',
      timestamp: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(),
      priority: 'medium',
      department: 'Electricity',
      status: 'new'
    },
    {
      id: '4',
      summary: 'Review meeting on road widening project at 4 PM today',
      from: 'Officer 891',
      timestamp: new Date(now.getTime() - 8 * 60 * 60 * 1000).toISOString(),
      priority: 'medium',
      department: 'Infrastructure',
      status: 'closed'
    },
    {
      id: '5',
      summary: 'Maintenance work scheduled for substation-4 tomorrow morning',
      from: 'Officer 634',
      timestamp: new Date(now.getTime() - 10 * 60 * 60 * 1000).toISOString(),
      priority: 'low',
      department: 'Electricity',
      status: 'new'
    },
    {
      id: '6',
      summary: 'Emergency flood relief camp setup at Governorpet Community Hall',
      from: 'Officer 423',
      timestamp: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString(),
      priority: 'high',
      department: 'Disaster Management',
      status: 'in_progress'
    },
    {
      id: '7',
      summary: 'Power outage in Bhavanipuram sector - restoration in progress',
      from: 'Officer 778',
      timestamp: new Date(now.getTime() - 14 * 60 * 60 * 1000).toISOString(),
      priority: 'medium',
      department: 'Electricity',
      status: 'in_progress'
    },
    {
      id: '8',
      summary: 'COVID-19 vaccination drive completion report submitted',
      from: 'Officer 156',
      timestamp: new Date(now.getTime() - 16 * 60 * 60 * 1000).toISOString(),
      priority: 'low',
      department: 'Health',
      status: 'closed'
    }
  ];
}

export function getMockCalendar(): N8nCalendarEvent[] {
  const now = new Date();
  
  return [
    {
      id: '1',
      title: 'NTR District Collectorate - Weekly Review',
      start: new Date(now.setHours(10, 0, 0, 0)).toISOString(),
      end: new Date(now.setHours(11, 0, 0, 0)).toISOString(),
      location: 'Conference Hall, Vijayawada',
      department: 'Administration'
    },
    {
      id: '2',
      title: 'Emergency Response Team Briefing',
      start: new Date(now.setHours(14, 30, 0, 0)).toISOString(),
      end: new Date(now.setHours(15, 30, 0, 0)).toISOString(),
      location: 'Situation Room',
      department: 'Disaster Management'
    },
    {
      id: '3',
      title: 'Infrastructure Development Committee Meeting',
      start: new Date(now.setHours(16, 0, 0, 0)).toISOString(),
      end: new Date(now.setHours(17, 30, 0, 0)).toISOString(),
      location: 'District Collectorate',
      department: 'Infrastructure'
    }
  ];
}
