import type { Notification } from '../types';
import { formatDistanceToNow } from 'date-fns';

const typeIcon: Record<string, string> = {
  threshold_alert: '⚠️',
  leave_update: '📋',
  general: '🔔',
};

interface Props {
  notification: Notification;
  onMarkRead: (id: number) => void;
}

export default function NotificationItem({ notification: n, onMarkRead }: Props) {
  return (
    <div
      className={`flex gap-3 p-3 rounded-lg border ${n.is_read ? 'border-gray-100 bg-white' : 'border-blue-200 bg-blue-50'}`}
    >
      <span className="text-lg leading-none mt-0.5">{typeIcon[n.notification_type] ?? '🔔'}</span>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${n.is_read ? 'text-gray-700' : 'text-gray-900'}`}>{n.title}</p>
        <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>
        <p className="text-xs text-gray-400 mt-1">
          {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
        </p>
      </div>
      {!n.is_read && (
        <button
          onClick={() => onMarkRead(n.id)}
          className="text-xs text-blue-600 hover:underline shrink-0"
        >
          Mark read
        </button>
      )}
    </div>
  );
}
