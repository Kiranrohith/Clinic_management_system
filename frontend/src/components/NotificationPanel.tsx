import { useNotifications } from "../hooks/useNotifications";

function formatCreatedAt(value: string | null): string {
  if (!value) {
    return "Unknown time";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString();
}

export function NotificationPanel() {
  const { notifications, isLoading, unreadOnly, setUnreadOnly, unreadCount, markAsRead, markAllAsRead } =
    useNotifications();

  return (
    <section className="rounded border bg-white p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-lg font-semibold">Notifications</h3>
        <div className="flex items-center gap-2">
          <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">Unread: {unreadCount}</span>
          <button
            className="rounded border px-2 py-1 text-xs hover:bg-slate-100"
            type="button"
            onClick={() => setUnreadOnly(!unreadOnly)}
          >
            {unreadOnly ? "Show all" : "Show unread"}
          </button>
          <button
            className="rounded border px-2 py-1 text-xs hover:bg-slate-100"
            type="button"
            onClick={() => markAllAsRead()}
          >
            Mark all read
          </button>
        </div>
      </div>
      {isLoading ? <p>Loading notifications...</p> : null}
      {!isLoading && notifications.length === 0 ? <p>No notifications yet.</p> : null}
      <ul className="space-y-2">
        {notifications.map((item) => (
          <li key={item.notification_id} className="rounded border p-2">
            <div className="flex items-center justify-between">
              <p className="font-medium">{item.title ?? "Notification"}</p>
              {!item.is_read ? (
                <button
                  className="text-sm text-blue-600"
                  onClick={() => markAsRead(item.notification_id)}
                  type="button"
                >
                  Mark read
                </button>
              ) : (
                <span className="text-xs text-slate-500">Read</span>
              )}
            </div>
            <p className="text-xs text-slate-500">
              {item.notification_type ?? "GENERAL"} • {formatCreatedAt(item.created_at)}
            </p>
            <p className="text-sm text-slate-700">{item.message}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
