import { request } from "./client";

export type DoctorSlotOption = {
  slot_id: number;
  slot_start_time: string;
  slot_end_time: string;
};

export type DoctorAvailability = {
  availability_id: number;
  available_date: string;
  slot_id: number;
  slot_start_time: string;
  slot_end_time: string;
  slot_status: "AVAILABLE" | "BOOKED" | "CANCELLED_BY_DOCTOR" | "BLOCKED";
  cancellation_reason: string | null;
};

export type DoctorAvailabilityWindowResult = {
  available_date: string;
  start_time: string;
  end_time: string;
  enabled_count: number;
  disabled_count: number;
  skipped_booked_count: number;
};

export type DoctorAppointment = {
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  available_date: string;
  slot_start_time: string;
  slot_end_time: string;
  appointment_status: string;
  booking_source: string | null;
  cancellation_reason: string | null;
  completed_at: string | null;
};

export type DoctorPrescription = {
  prescription_id: number;
  appointment_id: number;
  patient_id: number;
  doctor_user_id: number;
  diagnosis: string | null;
  medicines: string | null;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
  doctor_advice: string | null;
  internal_notes: string | null;
  follow_up_date: string | null;
  follow_up_reminder_sent: boolean;
};

export type DoctorPrescriptionHistoryItem = {
  prescription_id: number;
  appointment_id: number;
  appointment_date: string;
  slot_start_time: string;
  slot_end_time: string;
  doctor_user_id: number;
  doctor_name: string;
  diagnosis: string | null;
  medicines: string | null;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
  doctor_advice: string | null;
  internal_notes: string | null;
  follow_up_date: string | null;
};

export type DoctorPatientSummary = {
  patient_id: number;
  full_name: string;
  phone: string;
  gender: "MALE" | "FEMALE" | "OTHER" | null;
  dob: string | null;
  age: number | null;
  blood_group: string | null;
  address: string | null;
  emergency_contact: string | null;
};

export type DoctorAppointmentDetail = {
  appointment_id: number;
  patient: DoctorPatientSummary;
  available_date: string;
  slot_start_time: string;
  slot_end_time: string;
  appointment_status: string;
  booking_source: string | null;
  cancellation_reason: string | null;
  completed_at: string | null;
  reason_for_visit: string | null;
  can_edit_prescription: boolean;
  current_prescription: DoctorPrescription | null;
  previous_prescriptions: DoctorPrescriptionHistoryItem[];
};

export type DoctorProfile = {
  user_id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role_name: string;
  status: "ACTIVE" | "INACTIVE";
  qualification: string | null;
  experience_years: number | null;
  about: string | null;
  specialization_names: string[];
};

export function listDoctorSlots(): Promise<DoctorSlotOption[]> {
  return request<DoctorSlotOption[]>("/api/v1/doctor/slots", { auth: true });
}

export function listDoctorAvailabilities(availableDate?: string): Promise<DoctorAvailability[]> {
  const suffix = availableDate ? `?available_date=${encodeURIComponent(availableDate)}` : "";
  return request<DoctorAvailability[]>(`/api/v1/doctor/availabilities${suffix}`, { auth: true });
}

export function createDoctorAvailability(payload: { available_date: string; slot_id: number }): Promise<DoctorAvailability> {
  return request<DoctorAvailability>("/api/v1/doctor/availabilities", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function cancelDoctorAvailability(availabilityId: number, cancellation_reason: string): Promise<DoctorAvailability> {
  return request<DoctorAvailability>(`/api/v1/doctor/availabilities/${availabilityId}/cancel`, {
    method: "POST",
    auth: true,
    body: { cancellation_reason }
  });
}

export function applyDoctorAvailabilityTimeWindow(payload: {
  available_date: string;
  start_time: string;
  end_time: string;
}): Promise<DoctorAvailabilityWindowResult> {
  return request<DoctorAvailabilityWindowResult>("/api/v1/doctor/availabilities/time-window", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function emergencyCancelDoctorAvailabilities(payload: {
  available_date: string;
  from_slot_id: number;
  cancellation_reason: string;
}): Promise<{
  available_date: string;
  from_slot_id: number;
  cancelled_availability_ids: number[];
  cancelled_appointment_ids: number[];
}> {
  return request("/api/v1/doctor/availabilities/emergency-cancel", {
    method: "POST",
    auth: true,
    body: payload
  });
}

export function listDoctorAppointments(params?: {
  available_date?: string;
  appointment_status?: string;
}): Promise<DoctorAppointment[]> {
  const query = new URLSearchParams();
  if (params?.available_date) {
    query.set("available_date", params.available_date);
  }
  if (params?.appointment_status) {
    query.set("appointment_status", params.appointment_status);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return request<DoctorAppointment[]>(`/api/v1/doctor/appointments${suffix}`, { auth: true });
}

export function getDoctorAppointmentDetail(appointmentId: number): Promise<DoctorAppointmentDetail> {
  return request<DoctorAppointmentDetail>(`/api/v1/doctor/appointments/${appointmentId}`, { auth: true });
}

export function completeDoctorAppointment(appointmentId: number): Promise<DoctorAppointment> {
  return request<DoctorAppointment>(`/api/v1/doctor/appointments/${appointmentId}/complete`, {
    method: "POST",
    auth: true
  });
}

export function cancelDoctorAppointment(appointmentId: number, cancellation_reason: string): Promise<DoctorAppointment> {
  return request<DoctorAppointment>(`/api/v1/doctor/appointments/${appointmentId}/cancel`, {
    method: "POST",
    auth: true,
    body: { cancellation_reason }
  });
}

export function getDoctorPrescription(appointmentId: number): Promise<DoctorPrescription> {
  return request<DoctorPrescription>(`/api/v1/doctor/appointments/${appointmentId}/prescription`, { auth: true });
}

export function upsertDoctorPrescription(
  appointmentId: number,
  payload: {
    diagnosis?: string;
    medicines?: string;
    dosage?: string;
    frequency?: string;
    duration?: string;
    doctor_advice?: string;
    internal_notes?: string;
    follow_up_date?: string;
  }
): Promise<DoctorPrescription> {
  return request<DoctorPrescription>(`/api/v1/doctor/appointments/${appointmentId}/prescription`, {
    method: "PUT",
    auth: true,
    body: payload
  });
}

export function getDoctorProfile(): Promise<DoctorProfile> {
  return request<DoctorProfile>("/api/v1/doctor/profile", { auth: true });
}

export function updateDoctorProfile(payload: {
  full_name: string;
  phone?: string;
  qualification?: string;
  experience_years?: number;
  about?: string;
}): Promise<DoctorProfile> {
  return request<DoctorProfile>("/api/v1/doctor/profile", {
    method: "PUT",
    auth: true,
    body: payload
  });
}
