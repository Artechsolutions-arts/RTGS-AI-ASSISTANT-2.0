'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { useDistrictStore } from '@/store/districtStore';
import { N8nMessage, N8nCalendarEvent } from '@/lib/n8nClient';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface AIChatBotProps {
  messages: N8nMessage[];
  calendar: N8nCalendarEvent[];
  appointments: N8nCalendarEvent[];
}

export const AIChatBot: React.FC<AIChatBotProps> = ({ messages, calendar, appointments }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([
    {
      id: '1',
      text: 'Good day, Collector. I am your RTGS AI Assistant. How can I assist with your administrative duties today?',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const district = useDistrictStore((state) => state.district);
  const scrollRef = useRef<HTMLDivElement>(null);

  const getFilteredOperationalMessages = () => {
    return messages.filter(m => {
      const summary = (m.summary || '').toLowerCase();
      const isMeetingRequest = summary.includes('meeting') || summary.includes('today meetings');
      const isAppointmentRequest = summary.includes('appointment') || summary.includes('/approve_') || summary.includes('/reject_');
      const hasNameReason = (summary.includes('name:') && summary.includes('reason:')) || 
                           summary.includes('full name:');
      
      // Filter out technical/scheduling clutter to isolate real grievances
      return !isMeetingRequest && !isAppointmentRequest && !hasNameReason;
    });
  };

  const getOperationalCommDetails = () => {
    const filtered = getFilteredOperationalMessages();
    if (filtered.length === 0) return "OPERATIONAL COMMUNICATIONS:\nNo active grievances identified in the current queue.";
    
    let response = `OPERATIONAL COMMUNICATIONS:\nYou have ${filtered.length} active administrative matters:\n\n`;
    filtered.slice(0, 5).forEach((m, i) => {
      response += `${i + 1}. [${m.department || 'GEN'}] FROM: ${m.from}\n   • SUMMARY: ${m.summary}\n   • PRIORITY: ${m.priority?.toUpperCase() || 'NORMAL'}\n\n`;
    });
    if (filtered.length > 5) response += `... and ${filtered.length - 5} more items.`;
    return response.trim();
  };

  const getTodayMeetingsDetails = () => {
    const now = new Date();
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    const todayEvents = calendar.filter(e => {
        const d = new Date(e.start).toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        return d === todayStr;
    });

    if (todayEvents.length === 0) return "TODAY'S MEETINGS:\nNo high-level meetings or briefings scheduled for today.";
    
    let response = `TODAY'S MEETINGS:\nYou have ${todayEvents.length} sessions scheduled:\n\n`;
    todayEvents.forEach((e, i) => {
      const start = new Date(e.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. ${e.title}\n   • TIME: ${start}\n   • LOC: ${e.location || 'Collectorate'}\n\n`;
    });
    return response.trim();
  };

  const getPendingMeetingsDetails = () => {
    const now = new Date();
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    
    const pending = calendar.filter(e => {
      const eventStart = new Date(e.start);
      const eventDay = eventStart.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      return eventDay === todayStr && eventStart > now;
    });

    if (pending.length === 0) return "TODAY'S PENDING MEETINGS:\nThere are no further meetings scheduled for the remainder of today.";
    
    let response = `TODAY'S PENDING MEETINGS:\nYou have ${pending.length} remaining sessions for today:\n\n`;
    pending.forEach((e, i) => {
      const start = new Date(e.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. ${e.title}\n   • TIME: ${start}\n   • LOC: ${e.location || 'Collectorate'}\n\n`;
    });
    return response.trim();
  };

  const getAppointmentDetails = () => {
    const now = new Date();
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    
    const pending = appointments.filter(a => {
      const apptStart = new Date(a.start);
      const apptDay = apptStart.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      return apptDay === todayStr && apptStart > now;
    });

    if (pending.length === 0) return "TODAY'S PENDING APPOINTMENTS:\nNo further citizen appointments are scheduled for the remainder of today.";
    
    let response = `TODAY'S PENDING APPOINTMENTS:\nYou have ${pending.length} remaining approved appointments for today:\n\n`;
    pending.forEach((a, i) => {
      const start = new Date(a.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. APPLICANT: ${a.title}\n   • REASON: ${a.description || 'Grievance Review'}\n   • TIME: ${start}\n\n`;
    });
    return response.trim();
  };

  const preBuiltQuestions = [
    { q: "Operational Communications", a: getOperationalCommDetails() },
    { q: "Today's Meetings", a: getTodayMeetingsDetails() },
    { q: "Today's Pending", a: getPendingMeetingsDetails() },
    { q: "Today's Appts", a: getAppointmentDetails() }
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, isTyping]);

  const getTomorrowMeetingsDetails = () => {
    const now = new Date();
    const tom = new Date(now);
    tom.setDate(tom.getDate() + 1);
    const tomStr = tom.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    const tomEvents = calendar.filter(e => {
        const d = new Date(e.start).toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        return d === tomStr;
    });

    if (tomEvents.length === 0) return "TOMORROW'S MEETINGS:\nNo meetings scheduled for tomorrow.";
    
    let response = `TOMORROW'S MEETINGS:\nYou have ${tomEvents.length} sessions scheduled:\n\n`;
    tomEvents.forEach((e, i) => {
      const start = new Date(e.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. ${e.title}\n   • TIME: ${start}\n   • LOC: ${e.location || 'Collectorate'}\n\n`;
    });
    return response.trim();
  };

  const getYesterdayMeetingsDetails = () => {
    const now = new Date();
    const yest = new Date(now);
    yest.setDate(yest.getDate() - 1);
    const yestStr = yest.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    const yestEvents = calendar.filter(e => {
        const d = new Date(e.start).toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        return d === yestStr;
    });

    if (yestEvents.length === 0) return "YESTERDAY'S MEETINGS:\nNo meeting records found for yesterday.";
    
    let response = `YESTERDAY'S MEETINGS:\nYou had ${yestEvents.length} sessions:\n\n`;
    yestEvents.forEach((e, i) => {
      const start = new Date(e.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. ${e.title}\n   • TIME: ${start}\n   • LOC: ${e.location || 'Collectorate'}\n\n`;
    });
    return response.trim();
  };

  const getDepartmentDetails = (deptQuery: string) => {
     const deptEvents = calendar.filter(e => 
        (e.title || '').toLowerCase().includes(deptQuery) || 
        (e.description || '').toLowerCase().includes(deptQuery)
     );
     const deptMsgs = messages.filter(m => 
        (m.forwardedDepartment || '').toLowerCase().includes(deptQuery) ||
        (m.department || '').toLowerCase().includes(deptQuery) ||
        (m.summary || '').toLowerCase().includes(deptQuery)
     );
     
     if (deptEvents.length === 0 && deptMsgs.length === 0) 
        return `DEPARTMENT INFO (${deptQuery.toUpperCase()}):\nNo specific records found for this department query.`;

     let response = `DEPARTMENT REPORT (${deptQuery.toUpperCase()}):\n`;
     if (deptEvents.length > 0) {
        response += `\nMEETINGS (${deptEvents.length}):\n`;
        deptEvents.slice(0,3).forEach((e, i) => response += `${i+1}. ${e.title} (${new Date(e.start).toLocaleDateString()})\n`);
     }
     if (deptMsgs.length > 0) {
        response += `\nOPERATIONAL MSGS (${deptMsgs.length}):\n`;
        deptMsgs.slice(0,3).forEach((m, i) => response += `${i+1}. [${m.priority?.toUpperCase()}] ${m.summary}\n`);
     }
     return response.trim();
  };

  const getTimeSpecificDetails = (query: string) => {
    // Improved regex to capture common time formats
    const timeMatch = query.match(/(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i);
    if (!timeMatch) return null;

    let hours = parseInt(timeMatch[1]);
    const minutes = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
    const ampm = timeMatch[3]?.toLowerCase();

    // Basic heuristic: if it's just a number like "meeting 2", check if it's likely a time
    // If it's a number > 24 and no am/pm/colon, it's probably not a time
    if (!ampm && !timeMatch[2] && hours > 24) return null;

    if (ampm === 'pm' && hours < 12) hours += 12;
    if (ampm === 'am' && hours === 12) hours = 0;
    
    // Heuristic for ambiguous times: if no am/pm and hours < 8, assume PM (most administrative meetings are 1pm-7pm, not 1am-7am)
    if (!ampm && hours > 0 && hours < 8) hours += 12;

    const targetDate = new Date();
    if (query.includes('tomorrow')) targetDate.setDate(targetDate.getDate() + 1);
    if (query.includes('yesterday')) targetDate.setDate(targetDate.getDate() - 1);

    const dateStr = targetDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });

    const filterByTime = (events: N8nCalendarEvent[]) => {
      return events.filter(e => {
        if (!e.start) return false;
        const d = new Date(e.start);
        
        // Compare date in IST
        const eventDateStr = d.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        if (eventDateStr !== dateStr) return false;
        
        // Extract hours/minutes in IST
        const istTime = d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata' });
        const [h, m] = istTime.split(':').map(Number);
        
        if (timeMatch[2]) {
           return h === hours && m === minutes;
        } else {
           // Range: match if the meeting starts at the specified hour
           return h === hours;
        }
      });
    };

    const periodStr = query.includes('tomorrow') ? 'tomorrow' : (query.includes('yesterday') ? 'yesterday' : 'today');
    const displayTime = `${hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours)}:${minutes.toString().padStart(2, '0')} ${hours >= 12 ? 'PM' : 'AM'}`;

    const matchedMeetings = filterByTime(calendar);
    const matchedAppts = filterByTime(appointments);

    if (matchedMeetings.length === 0 && matchedAppts.length === 0) {
      return `No specific meetings or appointments found for ${displayTime} ${periodStr}.`;
    }

    let response = `SCHEDULE FOR ${displayTime} (${periodStr.toUpperCase()}):\n`;
    
    if (matchedMeetings.length > 0) {
      response += `\nMEETINGS:\n`;
      matchedMeetings.forEach((e, i) => {
        response += `• ${e.title} (${e.location || 'Collectorate'})\n`;
      });
    }

    if (matchedAppts.length > 0) {
      response += `\nAPPOINTMENTS:\n`;
      matchedAppts.forEach((a, i) => {
        response += `• ${a.title}: ${a.description || 'Grievance Review'}\n`;
      });
    }

    return response.trim();
  };

   const processResponse = (input: string) => {
    const query = input.toLowerCase();
    
    // 0. Time-Specific Check (HIGH PRIORITY)
    // Check if query contains a time-like pattern (e.g., 2pm, 14:00, or "at 2")
    if (query.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)/i) || 
        query.match(/at\s+(\d{1,2})/i) || 
        query.match(/(\d{1,2}):(\d{2})/)) {
        const timeResponse = getTimeSpecificDetails(query);
        if (timeResponse) return timeResponse;
    }

    // 1. Specific Temporal Commands (PRIORITY)
    if (query.includes('tomorrow')) return getTomorrowMeetingsDetails();
    if (query.includes('yesterday')) return getYesterdayMeetingsDetails();

    // 2. Departmental Commands
    if (query.includes('health') || query.includes('medical') || query.includes('doctor')) return getDepartmentDetails('health');
    if (query.includes('revenue') || query.includes('tax')) return getDepartmentDetails('revenue');
    if (query.includes('police') || query.includes('law') || query.includes('crime')) return getDepartmentDetails('police');
    if (query.includes('education') || query.includes('school')) return getDepartmentDetails('education');
    if (query.includes('water') || query.includes('sanitation')) return getDepartmentDetails('water');
    if (query.includes('electricity') || query.includes('power')) return getDepartmentDetails('electricity');
    if (query.includes('disaster') || query.includes('flood') || query.includes('emergency')) return getDepartmentDetails('disaster');

    // 3. Core Action Commands
    if (query.includes('appointment') || query.includes('citizen') || query.includes('approved')) return preBuiltQuestions[3].a;
    if (query.includes('comm') || query.includes('operational') || query.includes('message')) return preBuiltQuestions[0].a;
    if (query.includes('pending') || query.includes('future') || query.includes('upcoming')) return preBuiltQuestions[2].a;
    if (query.includes('today') || query.includes('schedule') || query.includes('now') || query.includes('meeting')) return preBuiltQuestions[1].a;
    
    return "I am configured to provide details on Operational Communications, Meetings (Today/Tomorrow/Yesterday), and Appointments. You can also ask about specific departments like 'Health' or 'Power'.";
  };

  const handleSend = (text: string, isFromPrebuilt = false) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date()
    };
    
    setChatHistory(prev => [...prev, userMsg]);
    setUserInput('');
    setIsTyping(true);

    setTimeout(() => {
      const answer = isFromPrebuilt 
        ? preBuiltQuestions.find(pq => pq.q === text)?.a || "Information processed."
        : processResponse(text);

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: answer,
        sender: 'ai',
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, aiMsg]);
      setIsTyping(false);
    }, 800);
  };

  return (
    <div className="fixed bottom-6 right-6 z-[200] flex flex-col items-end">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-[350px] md:w-[420px] max-h-[70vh] h-[550px] bg-slate-50 rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.2)] border border-white overflow-hidden flex flex-col animate-scale-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#003366] to-[#004080] p-4 text-white flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center overflow-hidden relative border border-white/30">
                <Image src="/bot_final.jpg" alt="AI Agent" fill className="object-cover" priority />
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-200">RTGS AI Agent</p>
                <p className="text-xs font-black">Command Assistant</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white/60 hover:text-white transition-colors">✕</button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-gradient-to-b from-slate-50 to-white">
            {chatHistory.map(msg => (
              <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-2xl text-[12px] font-bold leading-relaxed shadow-sm whitespace-pre-wrap ${
                  msg.sender === 'user' 
                    ? 'bg-[#003366] text-white rounded-tr-none' 
                    : 'bg-white text-slate-800 border border-blue-100 rounded-tl-none'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white p-3 rounded-2xl border border-slate-100 shadow-sm flex space-x-1 items-center">
                  <div className="w-1 h-1 bg-slate-300 rounded-full animate-bounce"></div>
                  <div className="w-1 h-1 bg-slate-300 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1 h-1 bg-slate-300 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}
          </div>

          {/* Prompt & Input Section */}
          <div className="p-5 bg-white border-t border-slate-100 space-y-5">
            <div className="space-y-2">
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Recommended Queries</p>
              <div className="flex flex-wrap gap-2">
                {preBuiltQuestions.map((item, idx) => (
                  <button 
                    key={idx}
                    onClick={() => handleSend(item.q, true)}
                    className="text-left text-[10px] font-bold text-[#003366] bg-blue-50 hover:bg-blue-100 border border-blue-100 px-3 py-1.5 rounded-full transition-all active:scale-95"
                  >
                    {item.q}
                  </button>
                ))}
              </div>
            </div>

            <div className="relative">
              <input 
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend(userInput)}
                placeholder="Type your command..."
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-xs font-bold text-slate-700 focus:outline-none focus:border-[#003366] focus:bg-white transition-all pr-12"
              />
              <button 
                onClick={() => handleSend(userInput)}
                className="absolute right-2 top-2 w-8 h-8 bg-[#003366] text-white rounded-xl flex items-center justify-center hover:bg-black transition-all active:scale-95"
              >
                ↑
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button 
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className={`w-20 h-20 rounded-full shadow-2xl flex items-center justify-center transition-all ${
          isOpen ? 'bg-black rotate-90 scale-90' : 'bg-[#003366] hover:scale-110 active:scale-95'
        } border-4 border-white`}
      >
        {isOpen ? (
          <span className="text-white text-xl">✕</span>
        ) : (
          <div className="relative w-full h-full">
             <Image src="/bot_final.jpg" alt="AI Agent" fill className="object-cover rounded-full" priority />
             <div className="absolute top-0 right-0 w-4 h-4 bg-emerald-500 rounded-full border-2 border-white animate-pulse"></div>
          </div>
        )}
      </button>
    </div>
  );
};
