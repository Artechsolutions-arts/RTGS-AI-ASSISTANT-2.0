'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDistrictStore } from '@/store/districtStore';
import { Header } from '@/components/Header';
import { n8nClient, Department } from '@/lib/n8nClient';

export default function DepartmentsPage() {
  const router = useRouter();
  const district = useDistrictStore((state) => state.district);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    useDistrictStore.getState().initialize();
    const currentDistrict = useDistrictStore.getState().district;
    if (!currentDistrict) {
      router.push('/login');
      return;
    }

    const fetchDepartments = async () => {
      try {
        setLoading(true);
        const data = await n8nClient.getDepartments({
          district: currentDistrict.name,
          slug: currentDistrict.slug,
        });
        setDepartments(data);
      } catch (error) {
        console.error('Error fetching departments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDepartments();
    const interval = setInterval(fetchDepartments, 30000);
    return () => clearInterval(interval);
  }, [district, router]);

  const currentDistrict = useDistrictStore((state) => state.district);
  
  if (!currentDistrict) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gov-bg">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="gov-card">
          <h1 className="text-2xl font-bold text-gov-primary mb-6">Departments</h1>

          {loading ? (
            <p className="text-gray-500">Loading departments...</p>
          ) : departments.length === 0 ? (
            <p className="text-gray-500">No departments found</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {departments.map((dept) => (
                <div
                  key={dept.id}
                  className="border border-gov-border rounded-lg p-6 hover:bg-gray-50 transition-colors"
                >
                  <h3 className="text-xl font-semibold text-gov-text mb-4">{dept.name}</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Messages:</span>
                      <span className="font-semibold">{dept.messageCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pending Tasks:</span>
                      <span className="font-semibold">{dept.pendingTasks}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
