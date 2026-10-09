import type { LeaveRequest } from '../types';

const statusClasses: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

export default function LeaveStatusBadge({ status }: { status: LeaveRequest['status'] }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full capitalize font-medium ${statusClasses[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
}
