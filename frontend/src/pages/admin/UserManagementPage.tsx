import { useEffect, useState } from 'react';
import { getUsers, createUser, updateUser } from '../../api/users';
import { getDepartments } from '../../api/courses';
import type { User, Department } from '../../types';
import Modal from '../../components/Modal';
import toast from 'react-hot-toast';

const ROLES = ['admin', 'teacher', 'student', 'parent'];

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [filterRole, setFilterRole] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student',
    department_id: '',
    linked_student_id: '',
  });
  const [saving, setSaving] = useState(false);

  const load = () => {
    Promise.all([getUsers(filterRole || undefined), getDepartments()])
      .then(([u, d]) => {
        setUsers(u);
        setDepartments(d);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filterRole]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createUser({
        ...form,
        department_id: form.department_id ? Number(form.department_id) : undefined,
        linked_student_id: form.linked_student_id ? Number(form.linked_student_id) : undefined,
      });
      toast.success('User created');
      setShowModal(false);
      setForm({ name: '', email: '', password: '', role: 'student', department_id: '', linked_student_id: '' });
      load();
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (user: User) => {
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      toast.success(user.is_active ? 'User deactivated' : 'User activated');
      load();
    } catch {
      toast.error('Failed to update user');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">User Management</h2>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add User
        </button>
      </div>

      <div className="mb-4 flex gap-3">
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 text-sm"
        >
          <option value="">All roles</option>
          {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-2 text-xs text-gray-500">Name</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Email</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Role</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Active</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-gray-100">
                  <td className="px-4 py-2 font-medium text-gray-800">{u.name}</td>
                  <td className="px-4 py-2 text-gray-600">{u.email}</td>
                  <td className="px-4 py-2 capitalize">{u.role}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => toggleActive(u)}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={showModal} title="Add New User" onClose={() => setShowModal(false)}>
        <form onSubmit={handleCreate} className="space-y-3">
          {(['name', 'email', 'password'] as const).map((field) => (
            <div key={field}>
              <label className="block text-xs font-medium text-gray-600 mb-1 capitalize">{field}</label>
              <input
                type={field === 'password' ? 'password' : field === 'email' ? 'email' : 'text'}
                value={form[field]}
                onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Role</label>
            <select
              value={form.role}
              onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Department (optional)</label>
            <select
              value={form.department_id}
              onChange={(e) => setForm((f) => ({ ...f, department_id: e.target.value }))}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          {form.role === 'parent' && (
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Linked Student ID</label>
              <input
                type="number"
                value={form.linked_student_id}
                onChange={(e) => setForm((f) => ({ ...f, linked_student_id: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
          )}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 bg-blue-600 text-white text-sm py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Creating…' : 'Create User'}
            </button>
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className="flex-1 border border-gray-300 text-sm py-2 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
