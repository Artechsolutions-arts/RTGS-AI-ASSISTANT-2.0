'use client';

import React from 'react';
import Image from 'next/image';
import { N8nMessage, N8nCalendarEvent } from '@/lib/n8nClient';

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  data: N8nMessage | N8nCalendarEvent | any;
  type: 'message' | 'event' | 'stat';
  location?: string;
  department?: string;
  description?: string;
}

export const DetailModal: React.FC<DetailModalProps> = ({ isOpen, onClose, title, data, type }) => {
  if (!isOpen) return null;

  const renderContent = () => {
    if (type === 'message') {
      const msg = data as N8nMessage;
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Source</p>
              <p className="text-sm font-bold text-slate-800">{msg.from}</p>
            </div>
            <div className="text-right">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Time</p>
              <p className="text-sm font-bold text-slate-800">{new Date(msg.timestamp).toLocaleString()}</p>
            </div>
          </div>
          
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Summary</p>
            <p className="text-lg font-black text-blue-900 leading-tight">{msg.summary}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-white shadow-sm flex items-center justify-center text-xl shrink-0">
                {(() => {
                  const dept = (msg.department || '').toLowerCase();
                  if (dept.includes('electricity')) return '⚡';
                  if (dept.includes('water')) return '💧';
                  if (dept.includes('infrastructure') || dept.includes('road')) return '🏗️';
                  if (dept.includes('disaster')) return '🚨';
                  if (dept.includes('health') || dept.includes('medical')) return '🏥';
                  return '🏛️';
                })()}
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Forwarded To</p>
                <p className="text-xs font-black text-blue-600">{msg.department || 'General RTGS'}</p>
              </div>
            </div>
            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Priority</p>
              <span className={`inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                msg.priority?.toLowerCase() === 'high' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
              }`}>
                {msg.priority || 'Normal'}
              </span>
            </div>
          </div>

        </div>
      );
    }

    if (type === 'event') {
      const event = data as N8nCalendarEvent;
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Location</p>
              <p className="text-sm font-bold text-slate-800">{event.location || 'Collectorate Hall'}</p>
            </div>
            <div className="text-right">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Time</p>
              <p className="text-sm font-bold text-slate-800">
                {new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>

          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Event Title</p>
            <p className="text-xl font-black text-blue-900 leading-tight">{event.title}</p>
          </div>

          <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Description / Agenda</p>
            <p className="text-sm text-slate-600 leading-relaxed font-medium">
              {event.description || 'Routine administrative review and departmental briefing organized by the District Collectorate Office.'}
            </p>
          </div>

          <div className="space-y-3">
             <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Attendees</p>
             <div className="flex -space-x-2">
                {[1,2,3,4].map(i => (
                  <div key={i} className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-600 uppercase">
                    P{i}
                  </div>
                ))}
                <div className="w-8 h-8 rounded-full bg-blue-100 border-2 border-white flex items-center justify-center text-[10px] font-bold text-blue-600">
                  +12
                </div>
             </div>
          </div>

          <button className="w-full bg-slate-900 hover:bg-slate-800 text-white py-4 rounded-2xl text-xs font-black uppercase tracking-widest transition-all">
            Join Meeting / View Brief
          </button>
        </div>
      );
    }

    if (type === 'stat') {
      if (data.list && Array.isArray(data.list)) {
        return (
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
            <div className="text-center mb-6">
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">{data.label}</p>
              <h4 className="text-2xl font-black text-slate-900">{data.value} Total Items</h4>
            </div>
            {data.list.length > 0 ? (
              data.list.map((item: any, idx: number) => (
                <div key={idx} className="bg-slate-50 p-4 rounded-2xl border border-slate-100 hover:border-blue-200 transition-all">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">
                      {item.department || item.location || 'General'}
                    </span>
                    <span className="text-[10px] font-bold text-slate-400">
                      {new Date(item.timestamp || item.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-sm font-bold text-slate-800 leading-tight">
                    {item.summary || item.title}
                  </p>
                  {item.from && <p className="text-[10px] font-bold text-slate-500 mt-2 uppercase tracking-tight">From: {item.from}</p>}
                </div>
              ))
            ) : (
              <div className="text-center py-10">
                <p className="text-sm font-bold text-slate-300 uppercase italic">No items found in this category</p>
              </div>
            )}
          </div>
        );
      }
      return (
        <div className="text-center py-10 space-y-4">
          <h4 className={`text-4xl font-black ${hasBgImage ? 'text-white' : 'text-slate-900'}`}>{data.value}</h4>
          <p className={`text-sm font-bold uppercase tracking-widest ${hasBgImage ? 'text-white/60' : 'text-slate-500'}`}>{data.label}</p>
          <div className="h-1.5 w-24 bg-blue-500 mx-auto rounded-full shadow-lg shadow-blue-500/20"></div>
          <p className={`text-base font-medium max-w-sm mx-auto pt-4 leading-relaxed ${hasBgImage ? 'text-white/90' : 'text-slate-600'}`}>
            {data.details || `Detailed analytical breakdown for ${data.label} is being processed by the AI engine.`}
          </p>
        </div>
      );
    }

    return null;
  };

  const hasBgImage = data && data.bgImage;

  return (
    <div className="fixed top-0 left-0 w-full h-full z-[1000] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div 
        className={`w-full max-w-[95%] md:max-w-lg rounded-[24px] md:rounded-[32px] shadow-2xl overflow-hidden animate-scale-in border border-white/20 flex flex-col max-h-[90vh] relative ${hasBgImage ? 'text-white' : 'bg-white'}`}
        onClick={(e) => e.stopPropagation()}
      >
        {hasBgImage && (
          <div className="absolute inset-0 z-0">
            <Image 
              src={data.bgImage} 
              alt="Modal Background" 
              fill 
              className="object-cover"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900/80 via-slate-900/60 to-slate-900/90 z-10"></div>
          </div>
        )}
        
        <div className={`p-5 md:p-6 border-b flex items-center justify-between shrink-0 z-20 ${hasBgImage ? 'border-white/10' : 'border-slate-100'}`}>
          <h2 className={`text-[10px] md:text-xs font-black uppercase tracking-[0.2em] ${hasBgImage ? 'text-white/60' : 'text-black'}`}>{title}</h2>
          <button 
            onClick={onClose}
            className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${hasBgImage ? 'bg-white/10 text-white hover:bg-white/20' : 'bg-slate-100 text-slate-400 hover:bg-red-50 hover:text-red-500'}`}
          >
            ✕
          </button>
        </div>
        <div className="p-5 md:p-8 overflow-y-auto custom-scrollbar z-20">
          {renderContent()}
        </div>
      </div>
      <div className="absolute inset-0 -z-10" onClick={onClose}></div>
    </div>
  );
};
