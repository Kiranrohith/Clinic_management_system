export interface NotificationItem {
  notification_id: number;
  notification_type: string | null;
  title: string | null;
  message: string | null;
  is_read: boolean;
  created_at: string | null;
}
