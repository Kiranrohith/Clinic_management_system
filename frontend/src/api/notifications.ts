import { request } from "./client";
import type { NotificationItem } from "../types/notification";

export function listNotifications(unreadOnly = false): Promise<NotificationItem[]> {
  const query = unreadOnly ? "?unread_only=true" : "";
  return request<NotificationItem[]>(`/api/v1/notifications${query}`, { auth: true });
}

export function markNotificationAsRead(notificationId: number): Promise<{ updated: boolean }> {
  return request<{ updated: boolean }>(`/api/v1/notifications/${notificationId}/read`, {
    method: "PATCH",
    auth: true
  });
}

export function markAllNotificationsAsRead(): Promise<{ updated_count: number }> {
  return request<{ updated_count: number }>("/api/v1/notifications/read-all", {
    method: "PATCH",
    auth: true
  });
}
