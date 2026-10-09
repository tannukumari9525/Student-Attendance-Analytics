import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getCourses, getCourseStudents, getSessions, createSession } from '../api/courses';
import { markBulk } from '../api/attendance';
import type { Course } from '../types';
import toast from 'react-hot-toast';

interface StudentRow {
  id: number;
  name: string;
  status: 'present' | 'absent' | 'late';
}

export default function MarkAttendancePage() {
  const [searchParams] = useSearchParams();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>(searchParams.get('course_id') ?? '');
  const [date, setDate] = useState<string>(new Date().toISOString().slice(0, 10));
  const [students, setStudents] = useState<StudentRow[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getCourses().then(setCourses);
  }, []);

  const loadStudents = async () => {
    if (!selectedCourse) return;
    setLoadingStudents(true);
    try {
      const enrolled = await getCourseStudents(Number(selectedCourse));
      setStudents(enrolled.map((s: any) => ({ id: s.id, name: s.name, status: 'present' as const })));

      // Find or create session for this course+date
      const allSessions = await getSessions(Number(selectedCourse));
      let session = allSessions.find((s: any) => s.date === date);
      if (!session) {
        session = await createSession({
          course_id: Number(selectedCourse),
          date,
          start_time: '09:00:00',
          end_time: '10:00:00',
          session_type: 'lecture',
        });
      }
      setSessionId(session.id);
    } finally {
      setLoadingStudents(false);
    }
  };

  const setStatus = (studentId: number, status: StudentRow['status']) => {
    setStudents((prev) => prev.map((s) => (s.id === studentId ? { ...s, status } : s)));
  };

  const markAllPresent = () => {
    setStudents((prev) => prev.map((s) => ({ ...s, status: 'present' })));
  };

  const handleSubmit = async () => {
    if (!sessionId) return;
    setSubmitting(true);
    try {
      await markBulk({
        session_id: sessionId,
        records: students.map((s) => ({ student_id: s.id, status: s.status })),
      });
      toast.success('Attendance marked successfully');
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to mark attendance');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Mark Attendance</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Course</label>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">Select course</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <button
            onClick={loadStudents}
            disabled={!selectedCourse || loadingStudents}
            className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loadingStudents ? 'Loading…' : 'Load Students'}
          </button>
        </div>
      </div>

      {students.length > 0 && (
        <>
          <div className="flex justify-between items-center mb-3">
            <p className="text-sm text-gray-600">{students.length} students</p>
            <button
              onClick={markAllPresent}
              className="text-xs text-blue-600 border border-blue-300 px-3 py-1 rounded hover:bg-blue-50"
            >
              Mark All Present
            </button>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Student</th>
                  <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b border-gray-100">
                    <td className="px-4 py-2 text-gray-800">{s.name}</td>
                    <td className="px-4 py-2">
                      <div className="flex gap-2">
                        {(['present', 'late', 'absent'] as const).map((st) => (
                          <button
                            key={st}
                            onClick={() => setStatus(s.id, st)}
                            className={`text-xs px-3 py-1 rounded capitalize ${
                              s.status === st
                                ? st === 'present'
                                  ? 'bg-green-600 text-white'
                                  : st === 'late'
                                  ? 'bg-yellow-500 text-white'
                                  : 'bg-red-500 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {st}
                          </button>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="mt-4 bg-green-600 text-white text-sm px-6 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            {submitting ? 'Submitting…' : 'Submit Attendance'}
          </button>
        </>
      )}
    </div>
  );
}
