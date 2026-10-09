import { useEffect, useState } from 'react';
import { getSummary } from '../api/analytics';

interface AdminStats {
  total_students: number;
  total_teachers: number;
  total_courses: number;
  sessions_today: number;
  defaulter_count: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSummary()
      .then(setStats)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-gray-500">Loading…</p>;
  if (!stats) return <p className="text-sm text-red-500">Failed to load summary.</p>;

  const cards = [
    { label: 'Total Students', value: stats.total_students, color: 'text-blue-700' },
    { label: 'Total Teachers', value: stats.total_teachers, color: 'text-green-700' },
    { label: 'Total Courses', value: stats.total_courses, color: 'text-purple-700' },
    { label: 'Sessions Today', value: stats.sessions_today, color: 'text-yellow-700' },
    { label: 'Defaulters', value: stats.defaulter_count, color: 'text-red-700' },
  ];

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Admin Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-500 mb-1">{c.label}</p>
            <p className={`text-2xl font-bold ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
