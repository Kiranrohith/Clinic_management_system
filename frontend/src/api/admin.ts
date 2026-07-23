import { request } from "./client";

export type ManagementRole = "ADMIN" | "DOCTOR" | "FRONTDESK";

export type ManagementUser = {
  user_id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role_name: ManagementRole;
  status: string;
  created_at: string | null;
};

export type DoctorProfileInput = {
  qualification?: string;
  experience_years?: number;
  consultation_fee?: number;
  about?: string;
  specialization_ids?: number[];
};

export type ManagementUserCreatePayload = {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
  role_name: ManagementRole;
  doctor_profile?: DoctorProfileInput;
};

export type ManagementUserUpdatePayload = {
  full_name: string;
  phone?: string;
};

export type Specialization = {
  specialization_id: number;
  specialization_name: string;
};

export type Slot = {
  slot_id: number;
  slot_start_time: string;
  slot_end_time: string;
};

export type ClinicSettings = {
  id: number;
  clinic_name: string;
  clinic_phone: string | null;
  clinic_email: string | null;
  clinic_address: string | null;
  opening_time: string;
  closing_time: string;
  slot_duration_minutes: number;
  booking_window_days: number;
  appointment_limit_per_day: number;
  morning_break_start: string | null;
  morning_break_end: string | null;
  lunch_break_start: string | null;
  lunch_break_end: string | null;
  evening_break_start: string | null;
  evening_break_end: string | null;
  slot_generation_done: boolean;
};

export type ClinicSettingsUpsertPayload = {
  clinic_name: string;
  clinic_phone?: string;
  clinic_email?: string;
  clinic_address?: string;
  opening_time: string;
  closing_time: string;
  slot_duration_minutes: number;
  booking_window_days: number;
  appointment_limit_per_day: number;
  morning_break_start?: string;
  morning_break_end?: string;
  lunch_break_start?: string;
  lunch_break_end?: string;
  evening_break_start?: string;
  evening_break_end?: string;
  slot_generation_done: boolean;
};

export type ContactQueryStatus = "NEW" | "IN_PROGRESS" | "CLOSED";

export type ContactQueryItem = {
  contact_id: number;
  full_name: string;
  phone: string;
  email: string | null;
  subject: string | null;
  message: string;
  status: ContactQueryStatus;
  handled_by: number | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type PatientListItem = {
  patient_id: number;
  full_name: string;
  phone: string;
  gender: string | null;
  dob: string | null;
  blood_group: string | null;
  appointment_count: number;
  created_at: string | null;
};

export type AdminProfile = {
  user_id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role_name: string;
};

export type AdminDashboard = {
  management_users: number;
  doctors: number;
  frontdesk: number;
  patients: number;
  appointments: number;
};

export function listManagementUsers(): Promise<ManagementUser[]> {
  return request<ManagementUser[]>("/api/v1/admin/users", { auth: true });
}

export function createManagementUser(payload: ManagementUserCreatePayload): Promise<ManagementUser> {
  return request<ManagementUser>("/api/v1/admin/users", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function updateManagementUser(userId: number, payload: ManagementUserUpdatePayload): Promise<ManagementUser> {
  return request<ManagementUser>(`/api/v1/admin/users/${userId}`, {
    method: "PUT",
    auth: true,
    body: payload
  });
}

export function setUserStatus(userId: number, status: "ACTIVE" | "INACTIVE"): Promise<ManagementUser> {
  return request<ManagementUser>(`/api/v1/admin/users/${userId}/status`, {
    method: "PUT",
    auth: true,
    body: { status }
  });
}

export function listAdminSpecializations(): Promise<Specialization[]> {
  return request<Specialization[]>("/api/v1/admin/specializations", { auth: true });
}

export function createSpecialization(specialization_name: string): Promise<Specialization> {
  return request<Specialization>("/api/v1/admin/specializations", {
    method: "POST",
    auth: true,
    body: { specialization_name }
  });
}

export function listAdminSlots(): Promise<Slot[]> {
  return request<Slot[]>("/api/v1/admin/slots", { auth: true });
}

export function createSlot(payload: { slot_start_time: string; slot_end_time: string }): Promise<Slot> {
  return request<Slot>("/api/v1/admin/slots", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function generateSlots(): Promise<Slot[]> {
  return request<Slot[]>("/api/v1/admin/slots/generate", {
    method: "POST",
    auth: true,
  });
}

export function deleteSlot(slotId: number): Promise<void> {
  return request<void>(`/api/v1/admin/slots/${slotId}`, {
    method: "DELETE",
    auth: true,
  });
}

export async function getClinicSettings(): Promise<ClinicSettings | null> {
  const data = await request<Record<string, unknown>>("/api/v1/admin/clinic-settings", { auth: true });
  if (!("id" in data)) {
    return null;
  }
  return {
    id: Number(data.id),
    clinic_name: String(data.clinic_name ?? ""),
    clinic_phone: typeof data.clinic_phone === "string" ? data.clinic_phone : null,
    clinic_email: typeof data.clinic_email === "string" ? data.clinic_email : null,
    clinic_address: typeof data.clinic_address === "string" ? data.clinic_address : null,
    opening_time: String(data.opening_time ?? ""),
    closing_time: String(data.closing_time ?? ""),
    slot_duration_minutes: Number(data.slot_duration_minutes ?? 0),
    booking_window_days: Number(data.booking_window_days ?? 0),
    appointment_limit_per_day: Number(data.appointment_limit_per_day ?? 0),
    morning_break_start: typeof data.morning_break_start === "string" ? data.morning_break_start : null,
    morning_break_end: typeof data.morning_break_end === "string" ? data.morning_break_end : null,
    lunch_break_start: typeof data.lunch_break_start === "string" ? data.lunch_break_start : null,
    lunch_break_end: typeof data.lunch_break_end === "string" ? data.lunch_break_end : null,
    evening_break_start: typeof data.evening_break_start === "string" ? data.evening_break_start : null,
    evening_break_end: typeof data.evening_break_end === "string" ? data.evening_break_end : null,
    slot_generation_done: Boolean(data.slot_generation_done)
  };
}

export function upsertClinicSettings(payload: ClinicSettingsUpsertPayload): Promise<ClinicSettings> {
  return request<ClinicSettings>("/api/v1/admin/clinic-settings", {
    method: "PUT",
    auth: true,
    body: payload
  });
}

export function listAdminPatients(): Promise<PatientListItem[]> {
  return request<PatientListItem[]>("/api/v1/admin/patients", { auth: true });
}

export function getAdminProfile(): Promise<AdminProfile> {
  return request<AdminProfile>("/api/v1/admin/profile", { auth: true });
}

export function updateAdminProfile(payload: { full_name: string; phone?: string }): Promise<AdminProfile> {
  return request<AdminProfile>("/api/v1/admin/profile", {
    method: "PUT",
    auth: true,
    body: payload
  });
}

export function listAdminContactQueries(status?: ContactQueryStatus): Promise<ContactQueryItem[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<ContactQueryItem[]>(`/api/v1/admin/contact-queries${query}`, { auth: true });
}

export function updateAdminContactQuery(
  contactId: number,
  payload: { status: ContactQueryStatus; notes?: string; handled_by_user_id?: number }
): Promise<ContactQueryItem> {
  return request<ContactQueryItem>(`/api/v1/admin/contact-queries/${contactId}`, {
    method: "PUT",
    auth: true,
    body: payload
  });
}
