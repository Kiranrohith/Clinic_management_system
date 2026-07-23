import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { listNotifications, markAllNotificationsAsRead, markNotificationAsRead } from "../api/notifications";
import { useAuth } from "./useAuth";

export function useNotifications() {
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [unreadOnly, setUnreadOnly] = useState(false);

  const notificationsQuery = useQuery({
    queryKey: ["notifications", unreadOnly],
    queryFn: () => listNotifications(unreadOnly),
    enabled: Boolean(token)
  });

  useEffect(() => {
    if (!token) {
      return;
    }
    const eventSource = new EventSource(`/api/v1/events?access_token=${encodeURIComponent(token)}`, {
      withCredentials: false
    });
    const refresh = () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    };
    eventSource.onmessage = refresh;
    [
      "APPOINTMENT_BOOKED",
      "APPOINTMENT_CANCELLED",
      "APPOINTMENT_COMPLETED",
      "DOCTOR_EMERGENCY",
      "NEW_CONTACT_REQUEST",
      "FOLLOW_UP_REMINDER",
      "WAITING_LIST_AVAILABLE"
    ].forEach((eventName) => {
      eventSource.addEventListener(eventName, refresh);
    });
    eventSource.onerror = () => {
      eventSource.close();
    };
    return () => {
      eventSource.close();
    };
  }, [queryClient, token]);

  const markReadMutation = useMutation({
    mutationFn: (notificationId: number) => markNotificationAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    }
  });

  const markAllMutation = useMutation({
    mutationFn: () => markAllNotificationsAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    }
  });

  const notifications = notificationsQuery.data ?? [];
  const unreadCount = notifications.filter((item) => !item.is_read).length;

  return {
    notifications,
    isLoading: notificationsQuery.isLoading,
    unreadOnly,
    setUnreadOnly,
    unreadCount,
    markAsRead: markReadMutation.mutateAsync,
    markAllAsRead: markAllMutation.mutateAsync
  };
}
