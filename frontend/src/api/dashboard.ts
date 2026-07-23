import { request } from "./client";
import type { AdminDashboardData, DoctorDashboardData, FrontdeskDashboardData } from "../types/dashboard";

export function getAdminDashboard(): Promise<AdminDashboardData> {
  return request<AdminDashboardData>("/api/v1/admin/dashboard", { auth: true });
}

export function getFrontdeskDashboard(doctorUserId?: number): Promise<FrontdeskDashboardData> {
  const suffix = doctorUserId ? `?doctor_user_id=${doctorUserId}` : "";
  return request<FrontdeskDashboardData>(`/api/v1/frontdesk/dashboard${suffix}`, { auth: true });
}

export function getDoctorDashboard(): Promise<DoctorDashboardData> {
  return request<DoctorDashboardData>("/api/v1/doctor/dashboard", { auth: true });
}
