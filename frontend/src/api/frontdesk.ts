import { request } from "./client";

export type FrontdeskPatient = {
  patient_id: number;
  full_name: string;
  phone: string;
  gender: "MALE" | "FEMALE" | "OTHER" | null;
  dob: string | null;
  blood_group: string | null;
  address: string | null;
  emergency_contact: string | null;
};

export type FrontdeskPatientUpsertPayload = {
  full_name: string;
  phone: string;
  gender?: "MALE" | "FEMALE" | "OTHER";
  dob?: string;
  blood_group?: string;
  address?: string;
  emergency_contact?: string;
};

export type FrontdeskPatientSearchItem = {
  patient_id: number;
  full_name: string;
  phone: string;
};

export type FrontdeskDoctorOption = {
  doctor_user_id: number;
  doctor_name: string;
  specializations: string[];
};

export type FrontdeskAvailability = {
  availability_id: number;
  doctor_user_id: number;
  doctor_name: string;
  available_date: string;
  slot_id: number;
  slot_start_time: string;
  slot_end_time: string;
  slot_status: string;
};

export type FrontdeskAppointment = {
  appointment_id: number;
  patient_id: number;
  availability_id: number;
  appointment_status: string;
  booking_source: string;
};

export type FrontdeskAppointmentListItem = {
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  doctor_user_id: number;
  doctor_name: string;
  availability_id: number;
  appointment_date: string;
  slot_start_time: string;
  slot_end_time: string;
  appointment_status: string;
  booking_source: string | null;
  cancellation_reason: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type FrontdeskWalkIn = {
  token_id: number;
  token_number: number;
  token_date: string;
  patient_id: number;
  doctor_user_id: number;
  status: "WAITING" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  notes: string | null;
};

export type FrontdeskWalkInListItem = {
  token_id: number;
  token_number: number;
  token_date: string;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  doctor_user_id: number;
  doctor_name: string;
  status: "WAITING" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type FrontdeskProfile = {
  user_id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role_name: string;
  status: string;
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

export function listFrontdeskDoctors(): Promise<FrontdeskDoctorOption[]> {
  return request<FrontdeskDoctorOption[]>("/api/v1/frontdesk/doctors", { auth: true });
}

export function getPatientByPhone(phone: string): Promise<FrontdeskPatient> {
  return request<FrontdeskPatient>(`/api/v1/frontdesk/patients/by-phone?phone=${encodeURIComponent(phone)}`, { auth: true });
}

export function searchFrontdeskPatients(query: string, limit = 10): Promise<FrontdeskPatientSearchItem[]> {
  return request<FrontdeskPatientSearchItem[]>(
    `/api/v1/frontdesk/patients/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    { auth: true }
  );
}

export function upsertPatient(payload: FrontdeskPatientUpsertPayload): Promise<FrontdeskPatient> {
  return request<FrontdeskPatient>("/api/v1/frontdesk/patients", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function listFrontdeskAvailabilities(params?: {
  doctor_user_id?: number;
  available_date?: string;
}): Promise<FrontdeskAvailability[]> {
  const query = new URLSearchParams();
  if (params?.doctor_user_id) {
    query.set("doctor_user_id", String(params.doctor_user_id));
  }
  if (params?.available_date) {
    query.set("available_date", params.available_date);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return request<FrontdeskAvailability[]>(`/api/v1/frontdesk/availabilities${suffix}`, { auth: true });
}

export function listTodayAppointments(doctorUserId?: number): Promise<FrontdeskAppointmentListItem[]> {
  const suffix = doctorUserId ? `?doctor_user_id=${doctorUserId}` : "";
  return request<FrontdeskAppointmentListItem[]>(`/api/v1/frontdesk/appointments/today${suffix}`, { auth: true });
}

export function listAppointmentsByDate(appointmentDate: string, doctorUserId?: number): Promise<FrontdeskAppointmentListItem[]> {
  const query = new URLSearchParams({ appointment_date: appointmentDate });
  if (doctorUserId) {
    query.set("doctor_user_id", String(doctorUserId));
  }
  return request<FrontdeskAppointmentListItem[]>(`/api/v1/frontdesk/appointments?${query.toString()}`, { auth: true });
}

export function getFrontdeskAppointment(appointmentId: number): Promise<FrontdeskAppointmentListItem> {
  return request<FrontdeskAppointmentListItem>(`/api/v1/frontdesk/appointments/${appointmentId}`, { auth: true });
}

export function bookFrontdeskAppointment(payload: { availability_id: number; patient_phone: string }): Promise<FrontdeskAppointment> {
  return request<FrontdeskAppointment>("/api/v1/frontdesk/appointments/book", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function cancelFrontdeskAppointment(appointmentId: number, cancellation_reason: string): Promise<FrontdeskAppointment> {
  return request<FrontdeskAppointment>(`/api/v1/frontdesk/appointments/${appointmentId}/cancel`, {
    method: "POST",
    auth: true,
    body: { cancellation_reason }
  });
}

export function createWalkinToken(payload: {
  doctor_user_id: number;
  token_date: string;
  patient_phone: string;
  notes?: string;
}): Promise<FrontdeskWalkIn> {
  return request<FrontdeskWalkIn>("/api/v1/frontdesk/walkin-tokens", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function listTodayWalkinTokens(doctorUserId?: number): Promise<FrontdeskWalkInListItem[]> {
  const suffix = doctorUserId ? `?doctor_user_id=${doctorUserId}` : "";
  return request<FrontdeskWalkInListItem[]>(`/api/v1/frontdesk/walkin-tokens/today${suffix}`, { auth: true });
}

export function listWalkinHistory(tokenDate: string, doctorUserId?: number): Promise<FrontdeskWalkInListItem[]> {
  const query = new URLSearchParams({ token_date: tokenDate });
  if (doctorUserId) {
    query.set("doctor_user_id", String(doctorUserId));
  }
  return request<FrontdeskWalkInListItem[]>(`/api/v1/frontdesk/walkin-tokens?${query.toString()}`, { auth: true });
}

export function getWalkinToken(tokenId: number): Promise<FrontdeskWalkInListItem> {
  return request<FrontdeskWalkInListItem>(`/api/v1/frontdesk/walkin-tokens/${tokenId}`, { auth: true });
}

export function updateWalkinTokenStatus(
  tokenId: number,
  payload: { status: "WAITING" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED"; notes?: string }
): Promise<FrontdeskWalkInListItem> {
  return request<FrontdeskWalkInListItem>(`/api/v1/frontdesk/walkin-tokens/${tokenId}/status`, {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function getFrontdeskProfile(): Promise<FrontdeskProfile> {
  return request<FrontdeskProfile>("/api/v1/frontdesk/profile", { auth: true });
}

export function updateFrontdeskProfile(payload: { full_name: string; phone?: string }): Promise<FrontdeskProfile> {
  return request<FrontdeskProfile>("/api/v1/frontdesk/profile", {
    method: "PUT",
    auth: true,
    body: payload
  });
}

export function listFrontdeskContactQueries(status?: ContactQueryStatus): Promise<ContactQueryItem[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<ContactQueryItem[]>(`/api/v1/frontdesk/contact-queries${query}`, { auth: true });
}

export function updateFrontdeskContactQuery(
  contactId: number,
  payload: { status: ContactQueryStatus; notes?: string; handled_by_user_id?: number }
): Promise<ContactQueryItem> {
  return request<ContactQueryItem>(`/api/v1/frontdesk/contact-queries/${contactId}`, {
    method: "PUT",
    auth: true,
    body: payload
  });
}
