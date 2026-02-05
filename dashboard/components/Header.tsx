'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { useDistrictStore } from '@/store/districtStore';

export function Header() {
  const pathname = usePathname();
  const district = useDistrictStore((state) => state.district);

  if (pathname === '/login') return null;

  return (
    <header className="bg-slate-900 text-white shadow-2xl sticky top-0 z-[100] border-b border-slate-800">
      <div className="max-w-[1800px] mx-auto px-6 flex items-center justify-between h-20">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-4">
             {/* Dynamic Emblem Placeholder */}
             <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center p-0.5 shadow-[0_0_15px_rgba(255,255,255,0.2)]">
                <div className="w-full h-full rounded-full bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200">
                    <span className="text-[10px] font-black text-blue-900 leading-none text-center">GOVT OF AP</span>
                </div>
             </div>
             <div className="h-8 w-[1px] bg-slate-700"></div>
             <div>
                <h1 className="text-lg font-extrabold tracking-tight leading-none text-white uppercase italic">
                  RTGS AI Assistant
                </h1>
                <p className="text-[10px] font-black text-blue-400 uppercase tracking-[0.3em] mt-1">
                  National Informatics Centre
                </p>
             </div>
          </div>
        </div>

        <div className="flex items-center space-x-8">
          <div className="hidden xl:flex items-center space-x-4 bg-slate-800/50 px-5 py-2 rounded-xl border border-slate-700">
             <div className="text-right">
                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Authenticated District</p>
                <p className="text-sm font-bold text-white">{district?.name || 'NTR District (Vijayawada)'}</p>
             </div>
          </div>

          <div className="flex items-center space-x-3 bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-xl">
             <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.8)]"></div>
             <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Live: Secure Link</span>
          </div>

          <div className="h-10 w-[1px] bg-slate-700"></div>

          <div className="flex items-center gap-4">
             <div className="flex flex-col items-end">
                <h2 className="text-lg font-black text-white uppercase tracking-tight leading-none">Dr. G. Lakshmisha, IAS</h2>
                <p className="text-[10px] font-black text-blue-300 uppercase tracking-[0.2em] leading-none mt-1">District Collector</p>
             </div>
             <div className="w-12 h-12 rounded-full border-2 border-slate-600 overflow-hidden relative shadow-lg">
                <Image 
                  src="/collector_logo.jpg?v=2" 
                  alt="District Collector" 
                  fill 
                  className="object-cover"
                  priority
                  unoptimized // Bypass optimization to ensure raw file is loaded if needed
                />
             </div>
          </div>
        </div>
      </div>
    </header>
  );
}
