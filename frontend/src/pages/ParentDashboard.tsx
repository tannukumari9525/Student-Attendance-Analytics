import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getStudentCourses } from '../api/analytics';
import { getUsers } from '../api/users';
import type { User } from '../types';

interface CourseStat {
  course_id: number;
  course_name: string;
  course_code: string;
  total_sessions: number;
  attendance_percentage: number;
  threshold: number;
}

function ProgressRing({ pct, threshold }: { pct: number; threshold: number }) {
  const r = 30;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  const color = pct >= 85 ? '#16a34a' : pct >= threshold ? '#ca8a04' : '#dc2626';
  return (
    <svg width="80" height="80">
      <circle cx="40" cy="40" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" transform="rotate(-90 40 40)" />
      <circle
        cx="40"
        cy="40"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeDasharray={`${circ}`}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 40 40)"
      />
      <text x="40" y="45" textAnchor="middle" fontSize="13" fontWeight="bold" fill={color}>
        {pct.toFixed(0)}%
      </text>
    </svg>
  );
}

export default function ParentDashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<CourseStat[]>([]);
  const [childName, setChildName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.linked_student_id) return;
    Promise.all([
      getStudentCourses(user.linked_student_id),
      getUsers('student'),
    ]).then(([courseData, students]) => {
      setCourses(courseData);
      const child = students.find((s: User) => s.id === user.linked_student_id);
      setChildName(child?.name ?? `Student #${user.linked_student_id}`);
    }).finally(() => setLoading(false));
  }, [user]);

  if (!user?.linked_student_id)
    return <p className="text-sm text-gray-500">No linked student account.</p>;
  if (loading) return <p className="text-sm text-gray-500">Loading…</p>;

  const warnings = courses.filter((c) => c.attendance_percentage < c.threshold);

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Parent Dashboard</h2>
      <p className="text-sm text-gray-500 mb-4">Viewing attendance for: <strong>{childName}</strong></p>

      {warnings.length > 0 && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
          ⚠️ {childName} is below attendance threshold in:{' '}
          {warnings.map((c) => c.course_name).join(', ')}
        </div>
      )}

      {courses.length === 0 ? (
        <p className="text-sm text-gray-400">Not enrolled in any courses.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((c) => (
            <div key={c.course_id} className="bg-white border border-gray-200 rounded-lg p-4 flex items-center gap-4">
              <ProgressRing pct={c.attendance_percentage} threshold={c.threshold} />
              <div>
                <p className="font-medium text-gray-800">{c.course_name}</p>
                <p className="text-xs text-gray-400">{c.course_code}</p>
                <p className="text-xs text-gray-500 mt-1">{c.total_sessions} sessions</p>
                <p className="text-xs text-gray-400">Threshold: {c.threshold}%</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
