import { useEffect, useState } from 'react';
import { getCourses } from '../api/courses';
import type { Course } from '../types';
import client from '../api/client';

export default function ReportsPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [courseId, setCourseId] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [studentId, setStudentId] = useState('');

  useEffect(() => {
    getCourses().then(setCourses);
  }, []);

  const buildParams = () => {
    const params = new URLSearchParams({ course_id: courseId });
    if (fromDate) params.set('from_date', fromDate);
    if (toDate) params.set('to_date', toDate);
    if (studentId) params.set('student_id', studentId);
    return params.toString();
  };

  const downloadCSV = async () => {
    const response = await client.get(`/reports/export/csv?${buildParams()}`, {
      responseType: 'blob',
    });
    const url = URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_report.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPDF = async () => {
    const params = new URLSearchParams({ course_id: courseId });
    if (studentId) params.set('student_id', studentId);
    const response = await client.get(`/reports/export/pdf?${params}`, {
      responseType: 'blob',
    });
    const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_report.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Reports & Export</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Course *</label>
            <select
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">Select course</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Student ID (optional)</label>
            <input
              type="number"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              placeholder="Leave empty for all students"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">From Date</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">To Date</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={downloadCSV}
            disabled={!courseId}
            className="bg-green-600 text-white text-sm px-5 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            Export CSV
          </button>
          <button
            onClick={downloadPDF}
            disabled={!courseId}
            className="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Export PDF
          </button>
        </div>
      </div>
    </div>
  );
}
