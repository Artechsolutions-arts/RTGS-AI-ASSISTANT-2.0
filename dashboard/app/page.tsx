'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/login');
  }, [router]);

  return (
    <div className="min-h-screen bg-[#F0F2F5] flex items-center justify-center font-sans">
      <div className="text-slate-400 font-black uppercase tracking-[0.2em] text-sm animate-pulse">
        Initializing System...
      </div>
    </div>
  );
}
