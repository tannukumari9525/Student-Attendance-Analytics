import { useState } from 'react';
import { useNotifications } from '../hooks/useNotifications';
import { markRead } from '../api/notifications';
import NotificationItem from '../components/NotificationItem';

export default function NotificationsPage() {
  const { notifications, markAll, refresh } = useNotifications();
  const [marking, setMarking] = useState(false);

  const handleMarkRead = async (id: number) => {
    await markRead(id);
    refresh();
  };

  const handleMarkAll = async () => {
    setMarking(true);
    await markAll();
    setMarking(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Notifications</h2>
        <button
          onClick={handleMarkAll}
          disabled={marking}
          className="text-xs text-blue-600 border border-blue-300 px-3 py-1 rounded hover:bg-blue-50 disabled:opacity-50"
        >
          Mark all read
        </button>
      </div>

      {notifications.length === 0 ? (
        <p className="text-sm text-gray-400">No notifications.</p>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <NotificationItem key={n.id} notification={n} onMarkRead={handleMarkRead} />
          ))}
        </div>
      )}
    </div>
  );
}
