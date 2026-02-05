'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useDistrictStore } from '@/store/districtStore';
import { n8nClient, N8nMessage, N8nCalendarEvent } from '@/lib/n8nClient';
import Image from 'next/image';
import { DistrictMap } from '@/components/DistrictMap';
import { DetailModal } from '@/components/DetailModal';
import { AIChatBot } from '@/components/AIChatBot';

export default function HomePage() {
  const router = useRouter();
  const district = useDistrictStore((state) => state.district);
  const [isInitialized, setIsInitialized] = useState(false);
  
  const [messages, setMessages] = useState<N8nMessage[]>([]);
  const [calendar, setCalendar] = useState<N8nCalendarEvent[]>([]);
  const [appointments, setAppointments] = useState<N8nCalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [isOnline, setIsOnline] = useState(true);
  
  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState<any>(null);
  const [modalType, setModalType] = useState<'message' | 'event' | 'stat'>('message');
  const [modalTitle, setModalTitle] = useState('');

  // Local Filter State
  const [activeFilter, setActiveFilter] = useState<'active' | 'meetings_today' | 'meetings_pending' | 'meetings_completed' | 'appointments_approved'>('active');

  // Time Filters
  // Time Filters
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' }));
  const [selectedHour, setSelectedHour] = useState<string>('all');
  const [isDatePickerOpen, setIsDatePickerOpen] = useState(false);
  const [isHourPickerOpen, setIsHourPickerOpen] = useState(false);
  
  // Custom Calendar State
  const [viewDate, setViewDate] = useState(new Date());
  
  const getDaysInMonth = (month: number, year: number) => new Date(year, month + 1, 0).getDate();
  const getStartDayOfMonth = (month: number, year: number) => new Date(year, month, 1).getDay();

  // Mobile Menu State
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleShowDetail = (data: any, type: 'message' | 'event' | 'stat', title: string) => {
    setModalData(data);
    setModalType(type);
    setModalTitle(title);
    setModalOpen(true);
  };

  useEffect(() => {
    useDistrictStore.getState().initialize();
    setIsInitialized(true);
    
    const currentDistrict = useDistrictStore.getState().district;
    if (!currentDistrict) {
      router.push('/login');
    }
  }, [router]);

  const fetchData = async () => {
    if (!district) return;
    try {
      const districtContext = { district: district.name, slug: district.id };
      const [msgs, cal, appts] = await Promise.all([
        n8nClient.getMessages(districtContext),
        n8nClient.getCalendar(districtContext),
        n8nClient.getAppointments(districtContext)
      ]);
      
      // Ensure all are arrays
      setMessages(Array.isArray(msgs) ? msgs : []);
      setCalendar(Array.isArray(cal) ? cal : []);
      setAppointments(Array.isArray(appts) ? appts : []);
      setLastSync(new Date());
      setIsOnline(true);
    } catch (error) {
      console.error("Data fetch failed:", error);
      setIsOnline(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!district) return;
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30s polling to reduce n8n executions
    return () => clearInterval(interval);
  }, [district, selectedDate]);

  const filteredMessages = useMemo(() => {
    return messages.filter(m => {
      const msgDate = new Date(m.timestamp);
      // We want to compare what day this is in IST
      const day = msgDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      const hour = msgDate.getHours().toString();
      
      const dateMatch = day === selectedDate;
      const hourMatch = selectedHour === 'all' || hour === selectedHour;
      
      // Exclude meeting and appointment requests from Operational Communications
      // Exclude meeting and appointment requests from Operational Communications
      // Removed simple 'am'/'pm' checks to avoid false positives (e.g. 'damage', 'program')
      const summary = (m.summary || '').toLowerCase();
      const isMeetingRequest = summary.includes('meeting') || summary.includes('schedule') || 
                               summary.includes('calendar') || summary.includes('today schedule') || 
                               summary.includes('tomorrow schedule') || 
                               /\b(am|pm)\b/.test(summary) || // Only match whole words 'am' or 'pm'
                               summary.includes('tomorrow') ||
                               summary.includes('/approve') || summary.includes('/reject');
      const isAppointmentRequest = summary.includes('appointment') || summary.includes('book') || 
                                    summary.includes('/approve_') || summary.includes('/reject_');
      
      // Also exclude appointment details (Name: X, Reason: Y format)
      const hasNameReason = (summary.includes('name:') && summary.includes('reason:')) || 
                           (summary.includes('name') && summary.includes('raason')) || // typo variant
                           summary.includes('full name:') || summary.includes('reason for');
      
      // Exclude time-only or date-only messages (often from calendar interactions)
      const isMetaQuery = /^\d{1,2}:\d{2}\s*(am|pm)?$/i.test(summary.trim()) || 
                          /^\d{2}\/\d{2}\/\d{4}$/.test(summary.trim()) ||
                          summary.includes('today schedule');

      // Only show messages that are NOT meeting/appointment requests or appointment details
      return dateMatch && hourMatch && !isMeetingRequest && !isAppointmentRequest && !hasNameReason && !isMetaQuery;
    });
  }, [messages, selectedDate, selectedHour]);

  const filteredCalendar = useMemo(() => {
    return calendar.filter(e => {
      const eventDate = new Date(e.start);
      const day = eventDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      const hour = eventDate.getHours().toString();
      const dateMatch = day === selectedDate;
      const hourMatch = selectedHour === 'all' || hour === selectedHour;
      return dateMatch && hourMatch;
    }).sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());
  }, [calendar, selectedDate, selectedHour]);

  const unifiedSchedule = useMemo(() => {
    const unified = [
      ...filteredCalendar.map(e => ({ ...e, type: 'event' as const })),
      ...appointments.filter(a => {
        const apptDate = new Date(a.start);
        const day = apptDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        const hour = apptDate.getHours().toString();
        return day === selectedDate && (selectedHour === 'all' || hour === selectedHour);
      }).map(a => ({ ...a, type: 'appointment' as const }))
    ];
    return unified.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());
  }, [filteredCalendar, appointments, selectedDate, selectedHour]);

  const stats = useMemo(() => {
    const now = new Date();
    const msgDateStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    const isPastDate = selectedDate < msgDateStr;
    const isFutureDate = selectedDate > msgDateStr;
    const isCurrentDate = selectedDate === msgDateStr;

    const totalMsgs = filteredMessages.length;
    const todayMeetings = filteredCalendar.length;
    
    let pendingMeetings = 0;
    let completedMeetings = 0;

    if (isPastDate) {
      completedMeetings = todayMeetings;
    } else if (isFutureDate) {
      pendingMeetings = todayMeetings;
    } else {
      // For Today: Pending includes ongoing (ends in future), Completed is strictly ones that ended
      pendingMeetings = filteredCalendar.filter(e => new Date(e.end) >= now).length;
      completedMeetings = filteredCalendar.filter(e => new Date(e.end) < now).length;
    }

    // Count appointments from dedicated collection
    const approvedAppointments = appointments.filter(a => {
      const apptDate = new Date(a.start);
      const day = apptDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      const hour = apptDate.getHours().toString();
      const dateMatch = day === selectedDate;
      const hourMatch = selectedHour === 'all' || hour === selectedHour;
      return dateMatch && hourMatch;
    }).length;
    
    return [
      { id: 'active', label: 'Active Messages', value: totalMsgs, border: 'border-blue-600', color: 'text-blue-600' },
      { id: 'meetings_today', label: 'Today Meetings & Schedule', value: todayMeetings, border: 'border-red-600', color: 'text-red-600' },
      { id: 'meetings_pending', label: 'Pending Meetings', value: pendingMeetings, border: 'border-amber-600', color: 'text-amber-600' },
      { id: 'meetings_completed', label: 'Completed Meetings', value: completedMeetings, border: 'border-emerald-600', color: 'text-emerald-600' },
      { id: 'appointments_approved', label: 'Approved Appointments', value: approvedAppointments, border: 'border-purple-600', color: 'text-purple-600' },
    ];
  }, [filteredMessages, filteredCalendar, selectedDate]);

  const listItems = useMemo(() => {
    const now = new Date();
    const msgDateStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
    const isPastDate = selectedDate < msgDateStr;
    const isFutureDate = selectedDate > msgDateStr;
    const isCurrentDate = selectedDate === msgDateStr;

    if (activeFilter === 'appointments_approved') {
      // Return appointments from dedicated collection
      return appointments.filter(a => {
        const apptDate = new Date(a.start);
        const day = apptDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
        const hour = apptDate.getHours().toString();
        const dateMatch = day === selectedDate;
        const hourMatch = selectedHour === 'all' || hour === selectedHour;
        return dateMatch && hourMatch;
      });
    }
    if (activeFilter === 'meetings_today') return filteredCalendar;
    if (activeFilter === 'meetings_pending') {
      // Shows upcoming AND ongoing meetings
      return filteredCalendar.filter(e => isFutureDate || (isCurrentDate && new Date(e.end) >= now));
    }
    if (activeFilter === 'meetings_completed') {
      // Shows strictly finished meetings
      return filteredCalendar.filter(e => isPastDate || (isCurrentDate && new Date(e.end) < now));
    }
    return filteredMessages;
  }, [activeFilter, filteredMessages, filteredCalendar, selectedDate]);

  if (!isInitialized || !district) return null;

  return (
    <>
      <div className="min-h-screen bg-[#F1F5F9] pb-12 animate-fade-in">
        {/* Government Header */}
        <header className="bg-gradient-to-r from-[#003366] to-[#004080] text-white shadow-2xl sticky top-0 z-[100] border-b-4 border-[#FF9933]">
          <div className="max-w-[1800px] mx-auto px-4 md:px-8 py-3 flex items-center justify-between">
              {/* Left: Government Branding */}
              <div 
                className="flex items-center space-x-3 cursor-pointer hover:opacity-90 transition-all active:scale-95"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleShowDetail({
                    label: 'Platform Information',
                    value: 'RTGS AI v2.4',
                    details: 'The Real-Time Governance Society AI Assistant is a state-of-the-art decision support system designed for high-ranking government officials in Andhra Pradesh.'
                  }, 'stat', 'Platform Overview');
                }}
              >
              <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 relative flex items-center justify-center">
                    <Image 
                      src="/ap_logo.png" 
                      alt="Govt of AP Logo" 
                      width={48} 
                      height={48} 
                      className="object-contain"
                      priority
                    />
                  </div>
                  <div className="h-8 w-[1px] bg-white/20"></div>
                  <div>
                    <h1 className="text-xl font-black tracking-tighter leading-none text-white">AI ASSISTANT</h1>
                    <p className="text-[10px] font-bold text-blue-200 uppercase tracking-widest mt-0.5">Govt. of Andhra Pradesh</p>
                  </div>
                </div>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden lg:flex items-center space-x-5">
                <div 
                  className="hidden xl:flex items-center space-x-3 bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/30 cursor-pointer hover:bg-white/20 transition-all shadow-sm"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleShowDetail({
                      label: 'District Profile',
                      value: district?.name || 'NTR District',
                      details: `Currently monitoring ${district?.name || 'NTR District'}. Headquarters: Vijayawada. Population: 2,218,591.`,
                      bgImage: "/prakasam-barrage.jpg"
                    }, 'stat', 'District Profile');
                  }}
                >
                  <div className="text-right">
                    <p className="text-[9px] font-black text-blue-100 uppercase leading-none mb-1">District</p>
                    <p className="text-sm font-black text-white">{district?.name || 'NTR District'}</p>
                  </div>
                </div>


                {/* Right: User Profiles */}
                <div className="flex items-center space-x-6">
                  <div className="hidden xl:flex flex-col items-end border-r border-white/20 pr-6">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full animate-pulse ${isOnline ? 'bg-emerald-400' : 'bg-red-400'}`}></div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-blue-100">
                          {isOnline ? 'System Live' : 'Link Interrupted'}
                        </span>
                      </div>
                      {lastSync && (
                        <span className="text-[10px] text-white font-black uppercase tracking-wider">
                          Sync: {lastSync.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                      )}
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <p className="text-sm font-black text-white uppercase leading-none text-right mb-1">Dr. G. Lakshmisha, IAS</p>
                      <p className="text-[10px] font-black text-blue-100 uppercase tracking-widest">District Collector</p>
                    </div>
                     <div className="w-14 h-14 rounded-full bg-white/20 border-2 border-white/30 overflow-hidden relative shadow-inner ml-2">
                        <Image src="/collector_avatar.jpg" alt="Collector" fill className="object-cover" priority />
                     </div>
                  </div>

                  <div className="h-8 w-[1px] bg-white/30"></div>

                  <button 
                    onClick={() => { useDistrictStore.getState().logout(); router.push('/login'); }}
                    className="h-10 px-5 bg-red-600/20 border-2 border-red-500/40 rounded-xl flex items-center space-x-2 hover:bg-red-600 hover:border-red-600 transition-all font-black text-white shadow-lg active:scale-95"
                  >
                    <span className="text-xs uppercase tracking-tighter">Logout</span>
                  </button>
                </div>
              </div>

              {/* Mobile Toggle */}
              <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="lg:hidden w-8 h-8 bg-white/10 rounded-lg border border-white/20 flex items-center justify-center">
                <div className="space-y-1">
                  <div className="w-4 h-0.5 bg-white"></div>
                  <div className="w-4 h-0.5 bg-white"></div>
                  <div className="w-4 h-0.5 bg-white"></div>
                </div>
              </button>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
              <div className="lg:hidden p-6 bg-[#003366] border-t border-white/10 space-y-6 animate-slide-down">
                 <div className="space-y-4">
                    <div className="bg-white/10 p-4 rounded-2xl border border-white/10">
                       <p className="text-[10px] font-black text-blue-200 uppercase tracking-widest mb-1">Active District</p>
                       <p className="text-base font-black text-white">{district?.name || 'NTR District'}</p>
                    </div>
                    
                    <div className="flex items-center space-x-5 bg-white/10 p-5 rounded-2xl border border-white/10">
                       <div className="w-16 h-16 rounded-full bg-white/20 border-2 border-white/30 overflow-hidden relative flex-shrink-0">
                          <Image src="/collector_avatar.jpg" alt="Collector" fill className="object-cover" />
                       </div>
                       <div>
                          <p className="text-base font-black text-white uppercase leading-tight">Dr. G. Lakshmisha, IAS</p>
                          <p className="text-[10px] font-black text-blue-200 uppercase tracking-widest">District Collector</p>
                       </div>
                    </div>
                 </div>
                 
                 <button 
                  onClick={() => { useDistrictStore.getState().logout(); router.push('/login'); }} 
                  className="w-full h-12 bg-red-600 hover:bg-red-700 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg transition-all active:scale-95"
                 >
                   Logout Session
                 </button>
              </div>
            )}
        </header>

        <main className="max-w-[1800px] mx-auto p-4 md:p-6 lg:p-8 space-y-8 min-h-[1200px]">
          {/* KPI Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {stats.map((stat) => (
              <div 
                key={stat.id} 
                onClick={() => {
                  setActiveFilter(stat.id as any);
                }}
                className={`bg-white border border-slate-200 border-l-4 ${stat.border} p-4 rounded-xl cursor-pointer hover:shadow-lg transition-all ${activeFilter === stat.id ? 'ring-2 ring-blue-500/20 bg-blue-50/5' : ''}`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-[8px] font-black text-slate-400 gap-2 uppercase tracking-widest mb-1 flex items-center">
                      {stat.label}
                      {stat.id === 'active' && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); fetchData(); }}
                          className="p-1 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-600 hover:text-white transition-all transform active:scale-95"
                          title="Sync Now"
                        >
                          <svg className="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                        </button>
                      )}
                    </p>
                    <h3 className={`text-2xl font-black ${stat.color}`}>{isLoading ? '...' : stat.value.toString().padStart(2, '0')}</h3>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Modern Filter Suite */}
          <div className="bg-white/90 backdrop-blur-xl border border-slate-200/60 p-2.5 rounded-[28px] shadow-lg flex flex-wrap items-center gap-3 sticky top-[80px] z-[90]">
            
            {/* Custom Date Picker Control */}
            <div className="relative">
              <div 
                onClick={() => { setIsDatePickerOpen(!isDatePickerOpen); setIsHourPickerOpen(false); }}
                className={`flex items-center px-4 py-2.5 rounded-2xl cursor-pointer transition-all border-2 ${isDatePickerOpen ? 'bg-blue-50 border-blue-900 shadow-inner' : 'bg-slate-50 border-transparent hover:bg-slate-100 hover:border-slate-200'}`}
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center mr-4 shadow-sm transition-colors ${isDatePickerOpen ? 'bg-blue-900 text-white' : 'bg-white text-blue-900'}`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                </div>
                <div className="flex flex-col">
                  <span className="text-[9px] font-black text-slate-400 tracking-tighter uppercase mb-0.5">Observation Day</span>
                  <p className="text-sm font-black text-slate-900 uppercase">
                    {new Date(selectedDate).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
                  </p>
                </div>
                <svg className={`w-4 h-4 ml-4 text-slate-400 transition-transform ${isDatePickerOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 9l-7 7-7-7" /></svg>
              </div>

              {isDatePickerOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setIsDatePickerOpen(false)}></div>
                  <div className="absolute top-full left-0 mt-3 w-72 bg-white rounded-3xl shadow-2xl border border-slate-100 p-5 z-20 animate-scale-in">
                    
                    {/* Month/Year Selection Navigation */}
                    <div className="flex items-center justify-between mb-2">
                       <button 
                        onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1))}
                        className="w-8 h-8 rounded-full border border-slate-100 flex items-center justify-center text-slate-400 hover:text-blue-900 hover:bg-slate-50 transition-all active:scale-90"
                       >
                         <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M15 19l-7-7 7-7"/></svg>
                       </button>
                       <div className="text-center">
                         <h4 className="text-[10px] font-black text-blue-900 uppercase tracking-widest">
                           {viewDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                         </h4>
                       </div>
                       <button 
                        onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1))}
                        className="w-8 h-8 rounded-full border border-slate-100 flex items-center justify-center text-slate-400 hover:text-blue-900 hover:bg-slate-50 transition-all active:scale-90"
                       >
                         <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M9 5l7 7-7 7"/></svg>
                       </button>
                    </div>

                    <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-50">
                      <p className="text-[8px] font-black text-slate-300 uppercase tracking-tighter">Navigate Operations</p>
                      <button onClick={() => { 
                        const today = new Date();
                        setSelectedDate(today.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' })); 
                        setViewDate(today);
                        setIsDatePickerOpen(false); 
                      }} className="text-[10px] font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-full hover:bg-blue-600 hover:text-white transition-all">TODAY</button>
                    </div>

                    <div className="grid grid-cols-7 gap-1 text-center mb-2">
                      {['Ｓ','Ｍ','Ｔ','Ｗ','Ｔ','Ｆ','Ｓ'].map(d => <span key={d} className="text-[10px] font-black text-slate-300">{d}</span>)}
                    </div>

                    {/* Dynamic Calendar Grid */}
                    <div className="grid grid-cols-7 gap-1">
                      {/* Empty slots for month start offset */}
                      {Array.from({ length: getStartDayOfMonth(viewDate.getMonth(), viewDate.getFullYear()) }).map((_, i) => (
                        <div key={`empty-${i}`} className="aspect-square"></div>
                      ))}
                      
                      {/* Actual Days */}
                      {Array.from({ length: getDaysInMonth(viewDate.getMonth(), viewDate.getFullYear()) }).map((_, i) => {
                        const dayNum = i + 1;
                        const dateObj = new Date(viewDate.getFullYear(), viewDate.getMonth(), dayNum);
                        const dateStr = dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
                        const isActive = selectedDate === dateStr;
                        const isCurrentDay = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' }) === dateStr;

                        return (
                          <button 
                            key={i} 
                            onClick={() => { setSelectedDate(dateStr); setIsDatePickerOpen(false); }}
                            className={`aspect-square rounded-xl text-xs font-black flex items-center justify-center transition-all relative ${
                              isActive ? 'bg-blue-900 text-white shadow-lg shadow-blue-900/40' : 
                              isCurrentDay ? 'bg-blue-50 text-blue-900 border border-blue-200' :
                              'hover:bg-slate-100 text-slate-700'
                            }`}
                          >
                            {dayNum}
                            {isCurrentDay && !isActive && <div className="absolute bottom-1 w-1 h-1 bg-blue-600 rounded-full"></div>}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="h-10 w-[1px] bg-slate-200 hidden md:block mx-1"></div>

            {/* Custom Hour Picker Control */}
            <div className="relative">
              <div 
                onClick={() => { setIsHourPickerOpen(!isHourPickerOpen); setIsDatePickerOpen(false); }}
                className={`flex items-center px-4 py-2.5 rounded-2xl cursor-pointer transition-all border-2 ${isHourPickerOpen ? 'bg-amber-50 border-amber-600 shadow-inner' : 'bg-slate-50 border-transparent hover:bg-slate-100 hover:border-slate-200'}`}
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center mr-4 shadow-sm transition-colors ${isHourPickerOpen ? 'bg-amber-600 text-white' : 'bg-white text-amber-600'}`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div className="flex flex-col">
                  <span className="text-[9px] font-black text-slate-400 tracking-tighter uppercase mb-0.5">Time Slot</span>
                  <p className="text-sm font-black text-slate-900 uppercase">
                    {selectedHour === 'all' ? 'FULL 24H CYCLE' : `${selectedHour.padStart(2, '0')}:00 Window`}
                  </p>
                </div>
                <svg className={`w-4 h-4 ml-4 text-slate-400 transition-transform ${isHourPickerOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 9l-7 7-7-7" /></svg>
              </div>

              {isHourPickerOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setIsHourPickerOpen(false)}></div>
                  <div className="absolute top-full left-0 mt-3 w-64 bg-white rounded-3xl shadow-2xl border border-slate-100 p-3 z-20 animate-scale-in">
                    <div className="max-h-[300px] overflow-y-auto custom-scrollbar pr-1">
                      <button 
                        onClick={() => { setSelectedHour('all'); setIsHourPickerOpen(false); }}
                        className={`w-full text-left p-4 rounded-2xl mb-1 text-xs font-black uppercase transition-all ${selectedHour === 'all' ? 'bg-amber-500 text-white shadow-lg' : 'hover:bg-slate-50 text-slate-600'}`}
                      >
                        All Day Review
                      </button>
                      <div className="h-[1px] bg-slate-50 my-2 mx-2"></div>
                      {Array.from({ length: 24 }).map((_, i) => {
                        const h = i.toString();
                        const isActive = selectedHour === h;
                        return (
                          <button 
                            key={i} 
                            onClick={() => { setSelectedHour(h); setIsHourPickerOpen(false); }}
                            className={`w-full text-left p-3 px-4 rounded-xl mb-1 text-xs font-black transition-all flex justify-between items-center ${isActive ? 'bg-blue-900 text-white shadow-md' : 'hover:bg-slate-50 text-slate-500'}`}
                          >
                            <span>{h.padStart(2, '0')}:00 - {h.padStart(2, '0')}:59</span>
                            {isActive && <div className="w-1.5 h-1.5 rounded-full bg-blue-300 animate-pulse"></div>}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Live Data Summary Chip */}
            <div className="ml-auto hidden xl:flex items-center space-x-6 mr-4">
              <div className="flex flex-col items-end">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Live Telemetry</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                  <p className="text-base font-black text-blue-900 italic">{listItems.length.toString().padStart(2, '0')}<span className="text-[10px] ml-1 not-italic font-bold text-slate-400">ACTIVITIES</span></p>
                </div>
              </div>
              <button 
                onClick={() => { setSelectedDate(new Date().toLocaleDateString('en-CA')); setSelectedHour('all'); }}
                className="w-11 h-11 bg-slate-900 text-white rounded-full flex items-center justify-center hover:scale-110 active:scale-90 transition-all shadow-xl shadow-slate-900/20"
                title="Force Resync"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              </button>
            </div>
          </div>

          {/* Centerpiece */}
          <div className="grid grid-cols-12 gap-6 lg:gap-8">
            <div className="col-span-12 lg:col-span-7 xl:col-span-9 space-y-6">
              {/* Communication Center moved to top primary position */}
              <div id="operational-center" className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden scroll-mt-[200px]">
                 <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <h2 className="text-xs font-black text-black uppercase tracking-widest">
                      {activeFilter === 'active' ? 'Operational Communications' : 
                       activeFilter === 'meetings_today' ? 'Full Schedule Review' :
                       activeFilter === 'meetings_pending' ? 'Upcoming Sessions' :
                       activeFilter === 'appointments_approved' ? 'Verified Citizen Appointments' : 'Completed Briefings'}
                    </h2>
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full">
                      {activeFilter.replace('_', ' ').toUpperCase()}
                    </span>
                 </div>
                  <div className="divide-y divide-slate-50 max-h-[700px] overflow-y-auto custom-scrollbar">
                    {isLoading ? (
                      <div className="p-10 text-center animate-pulse text-xs font-black text-slate-300 uppercase">Synchronizing...</div>
                    ) : listItems.length > 0 ? (
                      listItems.map((item: any) => (
                        <div 
                          key={item.id} 
                          className="p-4 flex items-start justify-between hover:bg-slate-50 transition-all cursor-pointer group active:bg-slate-100"
                          onClick={() => handleShowDetail(item, activeFilter.includes('meetings') ? 'event' : 'message', 'Detail Review')}
                        >
                          <div className="flex items-start space-x-4">
                             <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center border border-slate-200 text-lg shadow-sm group-hover:bg-blue-50 transition-colors">
                               {(() => {
                                 const dept = (item.department || '').toLowerCase();
                                 if (dept.includes('electricity')) return '⚡';
                                 if (dept.includes('water')) return '💧';
                                 if (dept.includes('infrastructure') || dept.includes('road')) return '🏗️';
                                 if (dept.includes('disaster')) return '🚨';
                                 if (dept.includes('health') || dept.includes('medical')) return '🏥';
                                 return '🏛️';
                               })()}
                             </div>
                             <div>
                                <h4 className="text-sm font-black text-slate-800 tracking-tight leading-tight group-hover:text-blue-900 transition-colors">{item.summary || item.title}</h4>
                                <div className="space-y-0.5 mt-1.5">
                                  <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest flex items-center">
                                    <span className="w-1 h-1 bg-slate-300 rounded-full mr-2"></span>
                                    {item.from || activeFilter === 'appointments_approved' ? `FROM: ${item.title || 'CITIZEN'}` : item.location ? `LOC: ${item.location}` : ''} 
                                    {((item.timestamp || item.start) && !isNaN(new Date(item.timestamp || item.start).getTime())) ? ` • ${new Date(item.timestamp || item.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''}
                                  </p>
                                  {item.description && activeFilter === 'appointments_approved' && (
                                    <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest flex items-center">
                                      <span className="w-1 h-1 bg-slate-400 rounded-full mr-2"></span>
                                      REASON: {item.description}
                                    </p>
                                  )}
                                  {!activeFilter.includes('meetings') && (
                                    <p className="text-[9px] font-black text-blue-500 uppercase tracking-widest flex items-center">
                                      {activeFilter === 'appointments_approved' ? (
                                        <>
                                          <span className="w-1 h-1 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                                          STATUS: VERIFIED BY RTGS
                                        </>
                                      ) : item.department ? (
                                        <>
                                          <span className="w-1 h-1 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
                                          FORWARDED TO: {item.department}
                                        </>
                                      ) : null}
                                    </p>
                                  )}
                                </div>
                             </div>
                          </div>
                          <span className={`px-3 py-1 rounded-lg text-[8px] font-black uppercase tracking-widest border ${
                            item.priority?.toLowerCase() === 'high' ? 'bg-red-50 text-red-600 border-red-100' : 'bg-slate-50 text-slate-500 border-slate-100'
                          }`}>{item.priority || ''}</span>
                        </div>
                      ))
                    ) : (
                      <div className="p-10 text-center space-y-4">
                        <div className="text-xs font-black text-slate-300 uppercase tracking-widest">No Active Feedback</div>
                      </div>
                    )}
                 </div>
              </div>
            </div>

            <div className="col-span-12 lg:col-span-5 xl:col-span-3 space-y-6">
              <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
                 <h2 className="text-[10px] font-black text-black uppercase tracking-widest mb-6">Today's Schedule</h2>
                  <div className="space-y-6 border-l border-slate-100 pl-6 ml-1">
                     {unifiedSchedule.length > 0 ? unifiedSchedule.map((item: any) => (
                      <div key={item.id} className="relative group cursor-pointer" onClick={() => handleShowDetail(item, item.type === 'event' ? 'event' : 'message', 'Schedule Detail')}>
                        <div className={`absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-white border-2 transition-all ${
                          item.type === 'appointment' ? 'border-purple-400 group-hover:bg-purple-50' : 'border-slate-200 group-hover:border-blue-500 group-hover:bg-blue-50'
                        }`}></div>
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{new Date(item.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                          {item.type === 'appointment' && (
                            <span className="text-[8px] font-black bg-purple-50 text-purple-600 px-1.5 rounded uppercase border border-purple-100 italic">Appt</span>
                          )}
                        </div>
                        <h4 className="text-xs font-black text-slate-800 group-hover:text-blue-600 transition-colors text-ellipsis overflow-hidden line-clamp-1">
                          {item.title || item.citizen_name || 'Meeting'}
                        </h4>
                        {item.description && <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">{item.description}</p>}
                      </div>
                    )) : (
                      <p className="text-[10px] font-bold text-slate-300 uppercase italic">No schedule for selected day</p>
                    )}
                  </div>
              </div>

              {/* Map shifted here below schedule */}
              <div className="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-200">
                <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                  <h2 className="text-[10px] font-black text-black uppercase tracking-widest">DISTRICT MAP</h2>
                </div>
                <div className="h-[300px] relative w-full">
                  <DistrictMap districtName={district?.id || 'ntr-district'} />
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>


      <DetailModal 
        isOpen={modalOpen} onClose={() => setModalOpen(false)} 
        title={modalTitle} data={modalData} type={modalType}
      />

      <AIChatBot 
        messages={messages}
        calendar={calendar}
        appointments={appointments}
      />
    </>
  );
}
