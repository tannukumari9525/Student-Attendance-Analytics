import { useEffect, useState } from 'react';
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '../../api/courses';
import type { Department } from '../../types';
import toast from 'react-hot-toast';
import Modal from '../../components/Modal';

export default function DepartmentPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', code: '' });
  const [editId, setEditId] = useState<number | null>(null);

  const load = () => {
    getDepartments()
      .then(setDepartments)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editId) {
        await updateDepartment(editId, form);
        toast.success('Updated');
      } else {
        await createDepartment(form);
        toast.success('Created');
      }
      setShowModal(false);
      setEditId(null);
      setForm({ name: '', code: '' });
      load();
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this department?')) return;
    try {
      await deleteDepartment(id);
      toast.success('Deleted');
      load();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const openEdit = (d: Department) => {
    setEditId(d.id);
    setForm({ name: d.name, code: d.code });
    setShowModal(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Departments</h2>
        <button
          onClick={() => { setEditId(null); setForm({ name: '', code: '' }); setShowModal(true); }}
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700"
        >
          + Add Department
        </button>
      </div>

      {loading ? <p className="text-sm text-gray-500">Loading…</p> : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-2 text-xs text-gray-500">Name</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Code</th>
                <th className="text-left px-4 py-2 text-xs text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((d) => (
                <tr key={d.id} className="border-b border-gray-100">
                  <td className="px-4 py-2 font-medium text-gray-800">{d.name}</td>
                  <td className="px-4 py-2">{d.code}</td>
                  <td className="px-4 py-2 flex gap-3">
                    <button onClick={() => openEdit(d)} className="text-xs text-blue-600 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(d.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal isOpen={showModal} title={editId ? 'Edit Department' : 'Add Department'} onClose={() => setShowModal(false)}>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Code</label>
            <input
              value={form.code}
              onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" className="flex-1 bg-blue-600 text-white text-sm py-2 rounded hover:bg-blue-700">
              {editId ? 'Save' : 'Create'}
            </button>
            <button type="button" onClick={() => setShowModal(false)} className="flex-1 border border-gray-300 text-sm py-2 rounded">
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
