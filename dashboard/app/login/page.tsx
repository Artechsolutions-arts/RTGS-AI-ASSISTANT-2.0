'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useDistrictStore } from '@/store/districtStore';
import { DISTRICTS } from '@/lib/auth';
import Image from 'next/image';

export default function LoginPage() {
  const router = useRouter();
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [isMounted, setIsMounted] = useState(false);
  const setDistrict = useDistrictStore((state) => state.setDistrict);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDistrict) return;

    const district = DISTRICTS.find((d) => d.id === selectedDistrict);
    if (district) {
      setDistrict(district);
      router.push('/home');
    }
  };

  if (!isMounted) return null;

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#001A33]">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <Image 
          src="/login_bg.png" 
          alt="Government Background" 
          fill 
          className="object-cover opacity-40 scale-105 animate-pulse-slow"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#001A33]/90 via-transparent to-[#001A33]/90"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500/10 via-transparent to-transparent"></div>
      </div>

      {/* Decorative Elements */}
      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#FF9933] via-white to-[#128807]"></div>
      
      <main className="relative z-10 w-full max-w-[1200px] px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        {/* Left Side: Government Info */}
        <div className="hidden lg:block space-y-8 animate-fade-in-left">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center p-2 shadow-2xl border-4 border-blue-900/20">
              <div className="w-full h-full rounded-full bg-slate-50 flex items-center justify-center overflow-hidden border border-slate-200">
                <span className="text-[12px] font-black text-blue-900 leading-none text-center">GOVT<br/>OF AP</span>
              </div>
            </div>
            <div className="h-20 w-[2px] bg-gradient-to-b from-transparent via-white/30 to-transparent"></div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight leading-none mb-2">
                RTGS AI ASSISTANT
              </h1>
              <p className="text-lg font-bold text-blue-300 uppercase tracking-[0.2em]">
                Real-Time Governance Society
              </p>
            </div>
          </div>

          <div className="space-y-6 max-w-lg">
            <h2 className="text-2xl font-bold text-slate-100 leading-snug">
              Secure Administrative Command Center for Government Officials
            </h2>
            <p className="text-slate-400 text-lg leading-relaxed">
              Experience the next generation of governance with AI-powered insights, real-time situational awareness, and automated departmental orchestration.
            </p>
            
            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10">
                <p className="text-2xl font-black text-white">26+</p>
                <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Districts Digitized</p>
              </div>
              <div className="bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10">
                <p className="text-2xl font-black text-white">LIVE</p>
                <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Systems Synchronized</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-6 pt-8 opacity-50 grayscale hover:grayscale-0 transition-all">
             <div className="text-[10px] font-black text-white border border-white/20 px-3 py-1 rounded">NIC INDIA</div>
             <div className="text-[10px] font-black text-white border border-white/20 px-3 py-1 rounded">DIGITAL INDIA</div>
             <div className="text-[10px] font-black text-white border border-white/20 px-3 py-1 rounded">AP FIBERNET</div>
          </div>
        </div>

        {/* Right Side: Login Form */}
        <div className="flex justify-center lg:justify-end animate-fade-in-right">
          <div className="w-full max-w-[480px] bg-white rounded-[40px] shadow-[0_30px_100px_rgba(0,0,0,0.5)] overflow-hidden">
            <div className="bg-gradient-to-br from-blue-900 to-[#001A33] p-10 text-white text-center">
              <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mx-auto mb-6 backdrop-blur-xl border border-white/10">
                <svg className="w-8 h-8 text-blue-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black tracking-tight mb-2">Internal Access</h3>
              <p className="text-blue-300 text-xs font-bold uppercase tracking-[0.2em] opacity-80">Authorized Personnel Only</p>
            </div>

            <form onSubmit={handleLogin} className="p-10 space-y-8">
              <div className="space-y-3">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-1">Administrative District</label>
                <div className="relative group">
                  <select
                    value={selectedDistrict}
                    onChange={(e) => setSelectedDistrict(e.target.value)}
                    className="w-full h-14 bg-slate-50 border-2 border-slate-100 rounded-2xl px-6 text-sm font-bold text-slate-700 appearance-none focus:outline-none focus:border-blue-900 transition-all"
                  >
                    <option value="" disabled>Select your jurisdiction</option>
                    {DISTRICTS.map((district) => (
                      <option key={district.id} value={district.id}>
                        {district.name}
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-hover:text-blue-900 transition-colors">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}><path d="M19 9l-7 7-7-7" /></svg>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-1">Officer Credentials</label>
                <div className="relative group">
                   <div className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-blue-900 transition-colors">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                   </div>
                   <input 
                    type="text" 
                    placeholder="Collector / Admin ID" 
                    className="w-full h-14 bg-slate-50 border-2 border-slate-100 rounded-2xl pl-14 pr-6 text-sm font-bold text-slate-700 focus:outline-none focus:border-blue-900 transition-all placeholder:text-slate-300"
                    disabled
                    value="DISTRICT_ADMIN_SECURE"
                   />
                </div>
              </div>

              <button
                type="submit"
                disabled={!selectedDistrict}
                className="group relative w-full h-14 bg-[#001A33] hover:bg-black text-white rounded-2xl font-black text-sm uppercase tracking-[0.2em] transition-all overflow-hidden disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <span className="relative z-10">Access Dashboard</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </button>

              <div className="pt-4 flex flex-col items-center space-y-6">
                <div className="flex items-center space-x-2">
                   <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                   <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Secure 256-bit Encrypted Session</p>
                </div>
                
                <p className="text-[9px] text-slate-300 text-center leading-relaxed">
                   By logging in, you agree to the terms of the Government of Andhra Pradesh IT & Cybersecurity Policy. All actions are logged for auditing purposes.
                </p>
              </div>
            </form>
          </div>
        </div>
      </main>

      {/* Footer Branding */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center space-x-4 opacity-30">
        <p className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Cyber Security Integrated</p>
        <div className="h-3 w-[1px] bg-white"></div>
        <p className="text-[10px] font-black text-white uppercase tracking-[0.3em]">© 2026 AP RTGS</p>
      </div>
      
      <style jsx global>{`
        @keyframes fadeInRight {
          from { opacity: 0; transform: translateX(30px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeInLeft {
          from { opacity: 0; transform: translateX(-30px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseSlow {
          0%, 100% { opacity: 0.35; transform: scale(1.05); }
          50% { opacity: 0.45; transform: scale(1.1); }
        }
        .animate-fade-in-right {
          animation: fadeInRight 1s ease-out forwards;
        }
        .animate-fade-in-left {
          animation: fadeInLeft 1s ease-out forwards;
        }
        .animate-pulse-slow {
          animation: pulseSlow 10s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
