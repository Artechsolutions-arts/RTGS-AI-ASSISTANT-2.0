import Link from 'next/link';
import { Header } from '@/components/Header';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gov-bg">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="gov-card text-center">
          <h1 className="text-4xl font-bold text-gov-primary mb-4">404</h1>
          <p className="text-xl text-gray-600 mb-8">Page Not Found</p>
          <Link href="/home" className="btn-primary">
            Go to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
