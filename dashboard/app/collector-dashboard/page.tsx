'use client';

import React from 'react';

// Static Data based on the visual spec
const STATS = [
  { label: 'Active Messages', value: '124', color: 'border-blue-500' },
  { label: 'High Priority', value: '18', color: 'border-red-500' },
  { label: 'Pending Tasks', value: '42', color: 'border-orange-500' },
  { label: 'Today Meetings', value: '06', color: 'border-emerald-500' },
];

const COMMUNICATIONS = [
  { dept: 'Health', title: 'Emergency supply chain report for NTR District', time: '10:45 AM', priority: 'High' },
  { dept: 'Revenue', title: 'Land acquisition status – Amaravati outer ring road', time: '09:30 AM', priority: 'Medium' },
  { dept: 'Disaster', title: 'Flood warning response protocol update', time: '08:15 AM', priority: 'High' },
  { dept: 'Home', title: 'Security arrangements for upcoming VIP visit', time: '07:45 AM', priority: 'Low' },
];

const TASKS = [
  { task: 'Approve monthly expenditure report', completed: true },
  { task: 'Sign off on disaster relief funds allocation', completed: false },
  { task: 'Review new health infrastructure proposal', completed: false },
  { task: 'Update departmental contact directory', completed: true },
];

const SCHEDULE = [
  { time: '09:00 AM', event: 'Internal Review Meeting' },
  { time: '11:30 AM', event: 'Video Conference with Secretariat' },
  { time: '02:00 PM', event: 'Site Inspection – Vijayawada West' },
  { time: '04:30 PM', event: 'Budget Planning Session' },
];

export default function CollectorDashboard() {
  return (
    <div className="min-h-screen bg-[#F0F2F5] font-sans text-slate-800">
      {/* Top Header */}
      <header className="bg-[#003366] text-white p-4 shadow-md flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center p-1">
            {/* AP Govt Emblem Placeholder */}
            <span className="text-[#003366] font-bold text-xs text-center leading-tight">AP<br/>GOVT</span>
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-wide">
              Government of Andhra Pradesh – AI Personal Assistant System
            </h1>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 bg-[#004080] px-3 py-1 rounded-full border border-blue-400/30">
            <span className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]"></span>
            <span className="text-xs font-medium text-emerald-100 uppercase tracking-wider">System Ready</span>
          </div>
          <div className="text-right">
            <p className="text-xs text-blue-200 uppercase font-bold tracking-widest">District Collector</p>
            <p className="text-sm font-medium">Administrative Role</p>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-[1600px] mx-auto space-y-6">
        {/* KPI Cards Row */}
        <div className="grid grid-cols-4 gap-6">
          {STATS.map((stat, i) => (
            <div key={i} className={`bg-white p-5 rounded-lg shadow-sm border-l-4 ${stat.color} flex flex-col justify-between h-28 hover:shadow-md transition-shadow`}>
              <span className="text-slate-500 text-sm font-semibold uppercase tracking-wider">{stat.label}</span>
              <span className="text-3xl font-bold text-slate-800">{stat.value}</span>
            </div>
          ))}
        </div>

        {/* Operational Activity Map Placeholder */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <div className="bg-slate-50 px-5 py-3 border-b border-slate-200">
            <h2 className="text-sm font-bold text-slate-600 uppercase tracking-widest">Operational Activity Map</h2>
          </div>
          <div className="h-[400px] bg-slate-100 flex items-center justify-center relative group">
            <div className="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:20px_20px] opacity-50"></div>
            <div className="z-10 bg-white/80 backdrop-blur-sm px-8 py-4 rounded-full border border-slate-300 shadow-xl group-hover:scale-105 transition-transform cursor-pointer">
              <span className="text-slate-500 font-bold tracking-widest">Operational Activity Map Placeholder</span>
            </div>
          </div>
        </div>

        {/* Lower Sections */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left: Operational Communications */}
          <div className="col-span-12 lg:col-span-7 bg-white rounded-lg shadow-sm border border-slate-200 flex flex-col">
            <div className="bg-slate-50 px-5 py-3 border-b border-slate-200 flex justify-between items-center">
              <h2 className="text-sm font-bold text-slate-600 uppercase tracking-widest">Operational Communications</h2>
              <button className="text-[10px] font-bold text-blue-600 hover:text-blue-800 uppercase tracking-tighter">View All Items</button>
            </div>
            <div className="divide-y divide-slate-100">
              {COMMUNICATIONS.map((comm, i) => (
                <div key={i} className="px-5 py-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="bg-slate-100 flex-shrink-0 w-16 h-10 rounded flex items-center justify-center border border-slate-200">
                      <span className="text-[10px] font-black text-slate-600 uppercase tracking-tighter">{comm.dept}</span>
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-800 mb-0.5">{comm.title}</h3>
                      <p className="text-[11px] font-medium text-slate-400">{comm.time}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-[10px] font-black uppercase tracking-widest ${
                    comm.priority === 'High' ? 'bg-red-50 text-red-600 border border-red-200' :
                    comm.priority === 'Medium' ? 'bg-orange-50 text-orange-600 border border-orange-200' :
                    'bg-slate-50 text-slate-600 border border-slate-200'
                  }`}>
                    {comm.priority}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-auto p-4 bg-slate-50/50 border-t border-slate-100 text-center">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">End of active feed</p>
            </div>
          </div>

          {/* Right: Administrative & Schedule */}
          <div className="col-span-12 lg:col-span-5 space-y-6">
            {/* Administrative Tasks */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200">
              <div className="bg-slate-50 px-5 py-3 border-b border-slate-200">
                <h2 className="text-sm font-bold text-slate-600 uppercase tracking-widest">Administrative Tasks</h2>
              </div>
              <div className="p-5 space-y-3">
                {TASKS.map((task, i) => (
                  <div key={i} className="flex items-center space-x-3 py-1">
                    <div className={`w-5 h-5 rounded border ${task.completed ? 'bg-emerald-500 border-emerald-600 flex items-center justify-center' : 'border-slate-300'}`}>
                      {task.completed && <div className="w-1.5 h-3 border-r-2 border-b-2 border-white rotate-45 mb-1"></div>}
                    </div>
                    <span className={`text-sm font-medium ${task.completed ? 'text-slate-400 line-through' : 'text-slate-700'}`}>{task.task}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Today's Schedule */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200">
              <div className="bg-slate-50 px-5 py-3 border-b border-slate-200 flex justify-between items-center">
                <h2 className="text-sm font-bold text-slate-600 uppercase tracking-widest">Today’s Schedule</h2>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Jan 29, 2026</span>
              </div>
              <div className="p-5">
                <div className="space-y-6 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-100">
                  {SCHEDULE.map((item, i) => (
                    <div key={i} className="relative pl-8 flex flex-col group">
                      <div className="absolute left-0 top-1 w-6 h-6 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center z-10 group-hover:bg-blue-600 group-hover:scale-110 transition-all">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-600 group-hover:bg-white"></div>
                      </div>
                      <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">{item.time}</span>
                      <h3 className="text-sm font-bold text-slate-800">{item.event}</h3>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer / Info Bar */}
      <footer className="mt-12 mb-6 text-center">
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">
          RTGS AI Personal Assistant System v1.2.0 • Government of Andhra Pradesh
        </p>
      </footer>
    </div>
  );
}
