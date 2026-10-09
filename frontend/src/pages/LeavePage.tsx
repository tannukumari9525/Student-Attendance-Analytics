import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getLeaves, submitLeave, reviewLeave } from '../api/leaves';
import { getCourses } from '../api/courses';
import type { LeaveRequest, Course } from '../types';
import LeaveStatusBadge from '../components/LeaveStatusBadge';
import toast from 'react-hot-toast';

export default function LeavePage() {
  const { user } = useAuth();
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  // Form state (student only)
  const [form, setForm] = useState({
    course_id: '',
    from_date: '',
    to_date: '',
    reason: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const role = user?.role;

  useEffect(() => {
    Promise.all([getLeaves(), getCourses()])
      .then(([leaveData, courseData]) => {
        setLeaves(leaveData);
        setCourses(courseData);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const newLeave = await submitLeave({
        course_id: Number(form.course_id),
        from_date: form.from_date,
        to_date: form.to_date,
        reason: form.reason,
      });
      setLeaves((prev) => [newLeave, ...prev]);
      setForm({ course_id: '', from_date: '', to_date: '', reason: '' });
      toast.success('Leave request submitted');
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReview = async (id: number, status: 'approved' | 'rejected') => {
    try {
      const updated = await reviewLeave(id, status);
      setLeaves((prev) => prev.map((l) => (l.id === id ? updated : l)));
      toast.success(`Leave ${status}`);
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed');
    }
  };

  if (loading) return <p className="text-sm text-gray-500">Loading…</p>;

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Leave Requests</h2>

      {/* Student submission form */}
      {role === 'student' && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Apply for Leave</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Course</label>
              <select
                value={form.course_id}
                onChange={(e) => setForm((f) => ({ ...f, course_id: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="">Select course</option>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">From Date</label>
              <input
                type="date"
                value={form.from_date}
                onChange={(e) => setForm((f) => ({ ...f, from_date: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">To Date</label>
              <input
                type="date"
                value={form.to_date}
                onChange={(e) => setForm((f) => ({ ...f, to_date: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Reason</label>
              <textarea
                value={form.reason}
                onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
                required
                rows={3}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-600 text-white text-sm px-5 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting…' : 'Submit Request'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Leave table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {role !== 'student' && <th className="text-left px-4 py-2 text-xs text-gray-500">Student</th>}
              <th className="text-left px-4 py-2 text-xs text-gray-500">Course</th>
              <th className="text-left px-4 py-2 text-xs text-gray-500">From</th>
              <th className="text-left px-4 py-2 text-xs text-gray-500">To</th>
              <th className="text-left px-4 py-2 text-xs text-gray-500">Reason</th>
              <th className="text-left px-4 py-2 text-xs text-gray-500">Status</th>
              {(role === 'teacher' || role === 'admin') && (
                <th className="text-left px-4 py-2 text-xs text-gray-500">Actions</th>
              )}
            </tr>
          </thead>
          <tbody>
            {leaves.map((l) => {
              const course = courses.find((c) => c.id === l.course_id);
              return (
                <tr key={l.id} className="border-b border-gray-100">
                  {role !== 'student' && (
                    <td className="px-4 py-2 text-gray-700">{l.student_id}</td>
                  )}
                  <td className="px-4 py-2">{course?.name ?? l.course_id}</td>
                  <td className="px-4 py-2">{l.from_date}</td>
                  <td className="px-4 py-2">{l.to_date}</td>
                  <td className="px-4 py-2 text-gray-500 max-w-xs truncate">{l.reason}</td>
                  <td className="px-4 py-2">
                    <LeaveStatusBadge status={l.status} />
                  </td>
                  {(role === 'teacher' || role === 'admin') && (
                    <td className="px-4 py-2">
                      {l.status === 'pending' ? (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleReview(l.id, 'approved')}
                            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleReview(l.id, 'rejected')}
                            className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200"
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">Reviewed</span>
                      )}
                    </td>
                  )}
                </tr>
              );
            })}
            {leaves.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-6 text-center text-sm text-gray-400">
                  No leave requests found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
