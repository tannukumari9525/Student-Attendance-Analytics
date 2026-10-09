import { useEffect, useState } from 'react';
import { getCourses, createCourse, updateCourse, deleteCourse, getDepartments } from '../../api/courses';
import { getUsers } from '../../api/users';
import type { Course, Department, User } from '../../types';
import Modal from '../../components/Modal';
import toast from 'react-hot-toast';

export default function CourseManagementPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [teachers, setTeachers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    name: '', code: '', department_id: '', teacher_id: '',
    credits: '3', semester: '1', academic_year: '2024-25',
  });

  const load = () => {
    Promise.all([getCourses(), getDepartments(), getUsers('teacher')])
      .then(([c, d, t]) => { setCourses(c); setDepartments(d); setTeachers(t); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createCourse({
        name: form.name, code: form.code,
        department_id: Number(form.department_id),
        teacher_id: Number(form.teacher_id),
        credits: Number(form.credits),
        semester: form.semester,
        academic_year: form.academic_year,
        attendance_threshold: 75,
      });
      toast.success('Course created');
      setShowModal(false);
      load();
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this course?')) return;
    try {
      await deleteCourse(id);
      toast.success('Deleted');
      load();
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Course Management</h2>
        <button onClick={() => setShowModal(true)} className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700">
          + Add Course
        </button>
      </div>

      {loading ? <p className="text-sm text-gray-500">Loading…</p> : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-2 text-xs text-gray-500">Name</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Code</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Semester</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Credits</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((c) => (
                <tr key={c.id} className="border-b border-gray-100">
                  <td className="px-4 py-2 font-medium text-gray-800">{c.name}</td>
                  <td className="px-4 py-2">{c.code}</td>
                  <td className="px-4 py-2">{c.semester}</td>
                  <td className="px-4 py-2">{c.credits}</td>
                  <td className="px-4 py-2">
                    <button onClick={() => handleDelete(c.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={showModal} title="Add Course" onClose={() => setShowModal(false)}>
        <form onSubmit={handleCreate} className="space-y-3">
          {([['name', 'Course Name'], ['code', 'Course Code'], ['academic_year', 'Academic Year'], ['semester', 'Semester'], ['credits', 'Credits']] as Array<[string, string]>).map(([field, label]) => (
            <div key={field}>
              <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
              <input
                value={(form as any)[field]}
                onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Department</label>
            <select value={form.department_id} onChange={(e) => setForm((f) => ({ ...f, department_id: e.target.value }))} required className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="">Select</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Teacher</label>
            <select value={form.teacher_id} onChange={(e) => setForm((f) => ({ ...f, teacher_id: e.target.value }))} required className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="">Select</option>
              {teachers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" className="flex-1 bg-blue-600 text-white text-sm py-2 rounded hover:bg-blue-700">Create</button>
            <button type="button" onClick={() => setShowModal(false)} className="flex-1 border border-gray-300 text-sm py-2 rounded">Cancel</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
