'use client';

import React, { useState, useRef, useEffect } from 'react';
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
    const pending = calendar.filter(e => new Date(e.start) > now);

    if (pending.length === 0) return "PENDING MEETINGS:\nThere are no upcoming meetings scheduled beyond the current session.";
    
    let response = `PENDING MEETINGS (UPCOMING):\nI have identified ${pending.length} future meetings in the pipeline:\n\n`;
    pending.slice(0, 5).forEach((e, i) => {
      const date = new Date(e.start).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
      response += `${i + 1}. ${e.title}\n   • DATE: ${date}\n   • TIME: ${new Date(e.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}\n\n`;
    });
    return response.trim();
  };

  const getAppointmentDetails = () => {
    if (appointments.length === 0) return "APPROVED APPOINTMENTS:\nNo citizen appointments have been confirmed for the current reporting period.";
    
    let response = `APPROVED APPOINTMENTS (CITIZEN):\nYou have ${appointments.length} approved appointments:\n\n`;
    appointments.forEach((a, i) => {
      const start = new Date(a.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      response += `${i + 1}. APPLICANT: ${a.title}\n   • REASON: ${a.description || 'Grievance Review'}\n   • TIME: ${start}\n\n`;
    });
    return response.trim();
  };

  const preBuiltQuestions = [
    { q: "Operational Communications", a: getOperationalCommDetails() },
    { q: "Today's Meetings", a: getTodayMeetingsDetails() },
    { q: "Pending Meetings", a: getPendingMeetingsDetails() },
    { q: "Approved Appointments", a: getAppointmentDetails() }
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, isTyping]);

  const processResponse = (input: string) => {
    const query = input.toLowerCase();
    
    if (query.includes('comm') || query.includes('operational') || query.includes('message')) return preBuiltQuestions[0].a;
    if (query.includes('today') || query.includes('schedule') || query.includes('now')) return preBuiltQuestions[1].a;
    if (query.includes('pending') || query.includes('future') || query.includes('upcoming')) return preBuiltQuestions[2].a;
    if (query.includes('appointment') || query.includes('citizen') || query.includes('approved')) return preBuiltQuestions[3].a;
    
    return "I am configured to only provide details on: Operational Communications, Today's Meetings, Pending Meetings, and Approved Appointments. Please use the recommended queries above.";
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
    <div className="fixed bottom-8 right-8 z-[200] flex flex-col items-end">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-[350px] md:w-[400px] max-h-[calc(100vh-120px)] h-[600px] bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col animate-scale-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#003366] to-[#004080] p-4 text-white flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-white/40 animate-pulse"></div>
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-200">RTGS AI Agent</p>
                <p className="text-xs font-black">Command Assistant</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white/60 hover:text-white transition-colors">✕</button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-50">
            {chatHistory.map(msg => (
              <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl text-[12px] font-medium leading-relaxed shadow-sm whitespace-pre-wrap ${
                  msg.sender === 'user' 
                    ? 'bg-[#003366] text-white rounded-tr-none' 
                    : 'bg-white text-slate-700 border border-slate-100 rounded-tl-none'
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
          <div className="p-4 bg-white border-t border-slate-100 space-y-4">
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
        onClick={() => setIsOpen(!isOpen)}
        className={`w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all ${
          isOpen ? 'bg-black rotate-90 scale-90' : 'bg-[#003366] hover:scale-110 active:scale-95'
        } border-4 border-white`}
      >
        {isOpen ? (
          <span className="text-white text-xl">✕</span>
        ) : (
          <div className="relative">
            <div className="w-6 h-6 border-2 border-white rounded flex items-center justify-center">
              <div className="w-3 h-3 bg-white/40 rounded-full animate-pulse"></div>
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#003366]"></div>
          </div>
        )}
      </button>
    </div>
  );
};
