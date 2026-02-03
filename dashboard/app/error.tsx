'use client';

import { useEffect } from 'react';
import { Header } from '@/components/Header';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Dashboard error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gov-bg">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="gov-card text-center">
          <h1 className="text-2xl font-bold text-gov-primary mb-4">Something went wrong</h1>
          <p className="text-gray-600 mb-8">{error.message || 'An unexpected error occurred'}</p>
          <button onClick={reset} className="btn-primary">
            Try again
          </button>
        </div>
      </main>
    </div>
  );
}
