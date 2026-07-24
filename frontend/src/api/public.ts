import { request } from "./client";

export type PublicDoctor = {
  doctor_user_id: number;
  full_name: string;
  qualification: string | null;
  experience_years: number | null;
  consultation_fee: number | null;
  about: string | null;
  specialization_ids: number[];
  specialization_names: string[];
};

export type PublicAvailability = {
  availability_id: number;
  doctor_user_id: number;
  doctor_name: string;
  available_date: string;
  slot_id: number;
  slot_start_time: string;
  slot_end_time: string;
  slot_status: string;
};

export type PublicSpecialization = {
  specialization_id: number;
  specialization_name: string;
};

export type PublicClinicSettings = {
  clinic_name: string;
  clinic_phone: string | null;
  clinic_email: string | null;
  clinic_address: string | null;
  opening_time: string;
  closing_time: string;
};

export type PublicBookingPatientInput = {
  full_name: string;
  phone: string;
  gender?: "MALE" | "FEMALE" | "OTHER";
  dob?: string;
  blood_group?: string;
  address?: string;
  emergency_contact?: string;
};

export type PublicBookAppointmentRequest = {
  availability_id: number;
  patient: PublicBookingPatientInput;
};

export type PublicBookAppointmentResponse = {
  appointment_id: number;
  patient_id: number;
  availability_id: number;
  appointment_status: string;
  booking_source: string;
};

export type PublicJoinWaitingListResponse = {
  waiting_id: number;
  patient_id: number;
  availability_id: number;
  position: number;
  status: string;
};

export type PublicContactQueryCreateRequest = {
  full_name: string;
  phone: string;
  email?: string;
  subject?: string;
  message: string;
};

export type PublicContactQueryResponse = {
  contact_id: number;
  full_name: string;
  phone: string;
  email: string | null;
  subject: string | null;
  message: string;
  status: string;
};

export type PublicPrescriptionOtpResponse = {
  message: string;
  expires_in_minutes: number;
  otp_preview: string | null;
};

export type PublicBookingSessionResponse = {
  booking_session_token: string;
  expires_in_minutes: number;
};

export type PublicPatientProfile = {
  patient_id: number;
  full_name: string;
  phone: string;
  gender: "MALE" | "FEMALE" | "OTHER" | null;
  dob: string | null;
  blood_group: string | null;
  address: string | null;
  emergency_contact: string | null;
};

export type PublicPrescriptionItem = {
  prescription_id: number;
  appointment_id: number;
  doctor_name: string;
  diagnosis: string | null;
  medicines: string | null;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
  doctor_advice: string | null;
  follow_up_date: string | null;
  created_at: string | null;
};

export type PublicAppointmentHistoryItem = {
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string; 
  doctor_user_id: number;
  doctor_name: string; 
  availability_id: number;
  available_date: string;
  slot_start_time: string;
  slot_end_time: string;
  appointment_status: string;
  booking_source: string | null;
  cancellation_reason: string | null;
  completed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export function listPublicDoctors(): Promise<PublicDoctor[]> {
  return request<PublicDoctor[]>("/api/v1/public/doctors");
}

export function getPublicDoctor(doctorUserId: number): Promise<PublicDoctor> {
  return request<PublicDoctor>(`/api/v1/public/doctors/${doctorUserId}`);
}

export function listPublicSpecializations(): Promise<PublicSpecialization[]> {
  return request<PublicSpecialization[]>("/api/v1/public/specializations");
}

export async function getPublicClinicSettings(): Promise<PublicClinicSettings | null> {
  const data = await request<Record<string, unknown>>("/api/v1/public/clinic-settings");
  if (!("clinic_name" in data)) {
    return null;
  }
  return {
    clinic_name: String(data.clinic_name ?? ""),
    clinic_phone: typeof data.clinic_phone === "string" ? data.clinic_phone : null,
    clinic_email: typeof data.clinic_email === "string" ? data.clinic_email : null,
    clinic_address: typeof data.clinic_address === "string" ? data.clinic_address : null,
    opening_time: String(data.opening_time ?? ""),
    closing_time: String(data.closing_time ?? ""),
  };
}

export function listPublicAvailabilities(): Promise<PublicAvailability[]> {
  return request<PublicAvailability[]>("/api/v1/public/availabilities");
}

export function listPublicAvailabilitiesByDoctor(
  doctorUserId: number,
  availableDate?: string,
  includeBooked = false
): Promise<PublicAvailability[]> {
  const params = new URLSearchParams();
  params.set("doctor_user_id", String(doctorUserId));
  if (availableDate) {
    params.set("available_date", availableDate);
  }
  if (includeBooked) {
    params.set("include_booked", "true");
  }
  return request<PublicAvailability[]>(`/api/v1/public/availabilities?${params.toString()}`);
}

export function bookPublicAppointment(payload: PublicBookAppointmentRequest): Promise<PublicBookAppointmentResponse> {
  return request<PublicBookAppointmentResponse>("/api/v1/public/appointments/book", {
    method: "POST",
    body: payload
  });
}

export function submitPublicContactQuery(payload: PublicContactQueryCreateRequest): Promise<PublicContactQueryResponse> {
  return request<PublicContactQueryResponse>("/api/v1/public/contact-queries", {
    method: "POST",
    body: payload
  });
}

export function requestPublicPrescriptionOtp(phone: string): Promise<PublicPrescriptionOtpResponse> {
  return request<PublicPrescriptionOtpResponse>("/api/v1/public/prescriptions/request-otp", {
    method: "POST",
    body: { phone }
  });
}

export function verifyPublicPrescriptionOtp(phone: string, otp_code: string): Promise<PublicPrescriptionItem[]> {
  return request<PublicPrescriptionItem[]>("/api/v1/public/prescriptions/verify-otp", {
    method: "POST",
    body: { phone, otp_code }
  });
}

export function requestPublicBookingOtp(phone: string): Promise<PublicPrescriptionOtpResponse> {
  return request<PublicPrescriptionOtpResponse>("/api/v1/public/bookings/request-otp", {
    method: "POST",
    body: { phone }
  });
}

export function verifyPublicBookingOtp(phone: string, otp_code: string): Promise<PublicBookingSessionResponse> {
  return request<PublicBookingSessionResponse>("/api/v1/public/bookings/verify-otp", {
    method: "POST",
    body: { phone, otp_code }
  });
}

export function getPublicBookingPatientByPhone(bookingSessionToken: string, patientPhone: string): Promise<PublicPatientProfile> {
  const params = new URLSearchParams();
  params.set("booking_session_token", bookingSessionToken);
  params.set("patient_phone", patientPhone);
  return request<PublicPatientProfile>(`/api/v1/public/bookings/patients/by-phone?${params.toString()}`);
}

export function bookPublicAppointmentAuthenticated(payload: {
  booking_session_token: string;
  availability_id: number;
  patient_phone: string;
  patient?: PublicBookingPatientInput;
}): Promise<PublicBookAppointmentResponse> {
  return request<PublicBookAppointmentResponse>("/api/v1/public/appointments/book-authenticated", {
    method: "POST",
    body: payload
  });
}

export function listPublicBookingHistory(bookingSessionToken: string): Promise<PublicAppointmentHistoryItem[]> {
  const params = new URLSearchParams();
  params.set("booking_session_token", bookingSessionToken);
  return request<PublicAppointmentHistoryItem[]>(`/api/v1/public/appointments/history?${params.toString()}`);
}

export function cancelPublicAppointment(
  appointmentId: number,
  bookingSessionToken: string,
  cancellationReason: string
): Promise<PublicBookAppointmentResponse> {
  return request<PublicBookAppointmentResponse>(`/api/v1/public/appointments/${appointmentId}/cancel`, {
    method: "POST",
    body: {
      booking_session_token: bookingSessionToken,
      cancellation_reason: cancellationReason
    }
  });
}

export function reschedulePublicAppointment(
  appointmentId: number,
  bookingSessionToken: string,
  newAvailabilityId: number
): Promise<PublicBookAppointmentResponse> {
  return request<PublicBookAppointmentResponse>(`/api/v1/public/appointments/${appointmentId}/reschedule`, {
    method: "POST",
    body: {
      booking_session_token: bookingSessionToken,
      new_availability_id: newAvailabilityId
    }
  });
}

export function joinPublicWaitingList(payload: {
  availability_id: number;
  patient: PublicBookingPatientInput;
}): Promise<PublicJoinWaitingListResponse> {
  return request<PublicJoinWaitingListResponse>("/api/v1/public/waiting-list/join", {
    method: "POST",
    body: payload
  });
}
