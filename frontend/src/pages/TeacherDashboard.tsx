import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSummary } from '../api/analytics';

interface TeacherCourseStat {
  course_id: number;
  course_name: string;
  course_code: string;
  student_count: number;
  total_sessions: number;
  defaulter_count: number;
}

export default function TeacherDashboard() {
  const [data, setData] = useState<{ courses: TeacherCourseStat[]; total_defaulters: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getSummary()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-gray-500">Loading…</p>;
  if (!data) return <p className="text-sm text-red-500">Failed to load.</p>;

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-2">Teacher Dashboard</h2>
      <p className="text-sm text-gray-500 mb-4">
        Total defaulters across all courses: <span className="text-red-600 font-semibold">{data.total_defaulters}</span>
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.courses.map((c) => (
          <div
            key={c.course_id}
            className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-400"
            onClick={() => navigate(`/attendance?course_id=${c.course_id}`)}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-gray-800">{c.course_name}</p>
                <p className="text-xs text-gray-400">{c.course_code}</p>
              </div>
              {c.defaulter_count > 0 && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                  {c.defaulter_count} defaulters
                </span>
              )}
            </div>
            <div className="mt-3 text-sm text-gray-600 grid grid-cols-2 gap-2">
              <span>{c.student_count} students</span>
              <span>{c.total_sessions} sessions</span>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/mark-attendance?course_id=${c.course_id}`);
              }}
              className="mt-3 text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
            >
              Mark Attendance
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
