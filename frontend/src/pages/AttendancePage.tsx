import { useEffect, useState } from 'react';
import { getCourses } from '../api/courses';
import { getStudentRecords } from '../api/attendance';
import type { Course, AttendanceRecord } from '../types';

export default function AttendancePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCourses().then(setCourses);
  }, []);

  const statusColor = (status: string) => {
    if (status === 'present') return 'text-green-700 bg-green-50';
    if (status === 'late') return 'text-yellow-700 bg-yellow-50';
    if (status === 'absent') return 'text-red-700 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Attendance Records</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Course</label>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">All courses</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {records.length === 0 ? (
        <p className="text-sm text-gray-400">No records to display.</p>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-2 text-xs text-gray-500">Session</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Date</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Status</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Notes</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b border-gray-100">
                  <td className="px-4 py-2">{r.session_id}</td>
                  <td className="px-4 py-2">{new Date(r.marked_at).toLocaleDateString()}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded capitalize ${statusColor(r.status)}`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{r.notes ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
