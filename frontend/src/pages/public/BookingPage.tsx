import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import {
  bookPublicAppointmentAuthenticated,
  getPublicBookingPatientByPhone,
  getPublicDoctor,
  listPublicAvailabilitiesByDoctor,
  requestPublicBookingOtp,
  verifyPublicBookingOtp
} from "../../api/public";
import {
  clearPublicBookingSession,
  getPublicBookingSessionPhone,
  getPublicBookingSessionRemainingSeconds,
  getPublicBookingSessionToken,
  setPublicBookingSession
} from "../../utils/publicBookingSession";
import { isValidOtpCode, isValidPhoneNumber } from "../../utils/validators";
import {
  bookingConfirmationFileName,
  buildBookingConfirmationArtifactContent,
  downloadTextArtifact,
  printTextArtifact
} from "../../utils/patientArtifacts";

function formatTimeLabel(value: string): string {
  const [hours, minutes] = value.split(":");
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
}

export function BookingPage() {
  const [searchParams] = useSearchParams();
  const availabilityId = Number(searchParams.get("availabilityId") ?? "");
  const doctorId = Number(searchParams.get("doctorId") ?? "");

  const [message, setMessage] = useState<string | null>(null);
  const [authPhone, setAuthPhone] = useState(getPublicBookingSessionPhone() ?? "");
  const [authOtp, setAuthOtp] = useState("");
  const [sessionToken, setSessionToken] = useState<string | null>(() => getPublicBookingSessionToken());
  const [sessionRemainingSeconds, setSessionRemainingSeconds] = useState<number>(() =>
    getPublicBookingSessionRemainingSeconds()
  );
  const [patientPhone, setPatientPhone] = useState("");
  const [existingPatient, setExistingPatient] = useState<{
    patient_id: number;
    full_name: string;
    phone: string;
    gender: "MALE" | "FEMALE" | "OTHER" | null;
    dob: string | null;
    blood_group: string | null;
    address: string | null;
    emergency_contact: string | null;
  } | null>(null);
  const [newPatient, setNewPatient] = useState({
    full_name: "",
    gender: "" as "" | "MALE" | "FEMALE" | "OTHER",
    dob: "",
    blood_group: "",
    address: "",
    emergency_contact: ""
  });
  const [lastBookedAppointment, setLastBookedAppointment] = useState<{
    appointment_id: number;
    patient_phone: string;
  } | null>(null);

  const doctorQuery = useQuery({
    queryKey: ["public", "doctor", doctorId],
    queryFn: () => getPublicDoctor(doctorId),
    enabled: Number.isInteger(doctorId) && doctorId > 0
  });
  const availabilityQuery = useQuery({
    queryKey: ["public", "doctor-slots", doctorId],
    queryFn: () => listPublicAvailabilitiesByDoctor(doctorId),
    enabled: Number.isInteger(doctorId) && doctorId > 0
  });

  const selectedSlot = useMemo(
    () => (availabilityQuery.data ?? []).find((slot) => slot.availability_id === availabilityId),
    [availabilityQuery.data, availabilityId]
  );

  useEffect(() => {
    const timer = setInterval(() => {
      const remaining = getPublicBookingSessionRemainingSeconds();
      setSessionRemainingSeconds(remaining);
      if (remaining <= 0) {
        setSessionToken(null);
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const requestOtpMutation = useMutation({
    mutationFn: () => requestPublicBookingOtp(authPhone.trim()),
    onSuccess: (data) => {
      setMessage(data.otp_preview ? `OTP sent. Demo OTP: ${data.otp_preview}` : "OTP sent.");
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to request OTP.")
  });

  const verifyOtpMutation = useMutation({
    mutationFn: () => verifyPublicBookingOtp(authPhone.trim(), authOtp.trim()),
    onSuccess: (data) => {
      setPublicBookingSession(data.booking_session_token, authPhone.trim(), data.expires_in_minutes);
      setSessionToken(data.booking_session_token);
      setSessionRemainingSeconds(data.expires_in_minutes * 60);
      setMessage(`Authentication successful. Session active for ${data.expires_in_minutes} minutes.`);
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to verify OTP.")
  });

  const lookupPatientMutation = useMutation({
    mutationFn: ({ token, phone }: { token: string; phone: string }) => getPublicBookingPatientByPhone(token, phone),
    onSuccess: (patient) => {
      setExistingPatient(patient);
      setNewPatient({
        full_name: patient.full_name,
        gender: patient.gender ?? "",
        dob: patient.dob ?? "",
        blood_group: patient.blood_group ?? "",
        address: patient.address ?? "",
        emergency_contact: patient.emergency_contact ?? ""
      });
      setMessage(`Existing patient found: ${patient.full_name}`);
    },
    onError: (error) => {
      setExistingPatient(null);
      setMessage(error instanceof Error ? `${error.message} Please fill new patient details.` : "Patient not found.");
    }
  });

  const bookMutation = useMutation({
    mutationFn: (payload: {
      booking_session_token: string;
      availability_id: number;
      patient_phone: string;
      patient?: {
        full_name: string;
        phone: string;
        gender?: "MALE" | "FEMALE" | "OTHER";
        dob?: string;
        blood_group?: string;
        address?: string;
        emergency_contact?: string;
      };
    }) => bookPublicAppointmentAuthenticated(payload),
    onSuccess: (data) => {
      setMessage(`Appointment booked successfully. Appointment ID #${data.appointment_id}`);
      setLastBookedAppointment({
        appointment_id: data.appointment_id,
        patient_phone: patientPhone.trim()
      });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to book appointment.")
  });

  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <div className="mb-4 flex items-center justify-between">
        <Link className="text-sm font-medium text-emerald-700 hover:underline" to={doctorId ? `/doctors/${doctorId}` : "/doctors"}>
          ← Back
        </Link>
        <div className="flex items-center gap-2">
          <Link className="rounded border px-3 py-1.5 text-sm font-medium hover:bg-slate-100" to="/bookings">
            My Bookings
          </Link>
          <button
            className="rounded border px-3 py-1.5 text-sm font-medium hover:bg-slate-100"
            type="button"
            onClick={() => {
              clearPublicBookingSession();
              setSessionToken(null);
              setSessionRemainingSeconds(0);
              setMessage("Booking session cleared.");
            }}
          >
            Clear Session
          </button>
        </div>
      </div>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">Book appointment</h1>
        <p className="mt-2 text-sm text-slate-600">Follow OTP verification once, then book multiple slots for 15 minutes.</p>

        <div className="mt-4 rounded-lg border bg-slate-50 p-4 text-sm text-slate-700">
          <p><span className="font-semibold">Doctor:</span> {doctorQuery.data?.full_name ?? "Loading..."}</p>
          <p className="mt-1">
            <span className="font-semibold">Selected slot:</span>{" "}
            {selectedSlot
              ? `${selectedSlot.available_date} ${formatTimeLabel(selectedSlot.slot_start_time)} - ${formatTimeLabel(selectedSlot.slot_end_time)}`
              : "Invalid or unavailable slot"}
          </p>
          {doctorQuery.isError || availabilityQuery.isError ? (
            <p className="mt-2 text-red-600">Unable to load doctor/slot details fully. Please go back and retry.</p>
          ) : null}
        </div>
      </section>

      <section className="mt-5 rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Step 1: Public OTP authentication</h2>
        {sessionToken ? (
          <p className="mt-2 text-sm text-emerald-700">
            Session active for phone: {getPublicBookingSessionPhone() ?? authPhone} • Time left:{" "}
            {Math.floor(sessionRemainingSeconds / 60)
              .toString()
              .padStart(2, "0")}
            :
            {(sessionRemainingSeconds % 60).toString().padStart(2, "0")}
          </p>
        ) : (
          <>
            <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
              <input className="rounded border px-3 py-2" placeholder="Your phone number" value={authPhone} onChange={(e) => setAuthPhone(e.target.value)} />
              <button
                className="rounded bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                type="button"
                disabled={requestOtpMutation.isPending || !isValidPhoneNumber(authPhone)}
                onClick={() => {
                  if (!isValidPhoneNumber(authPhone)) {
                    setMessage("Enter a valid phone number with 7 to 15 digits.");
                    return;
                  }
                  requestOtpMutation.mutate();
                }}
              >
                {requestOtpMutation.isPending ? "Sending..." : "Send OTP"}
              </button>
            </div>
            <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
              <input className="rounded border px-3 py-2" placeholder="Enter OTP" value={authOtp} onChange={(e) => setAuthOtp(e.target.value)} />
              <button
                className="rounded border px-4 py-2 text-sm font-medium hover:bg-slate-100 disabled:opacity-60"
                type="button"
                disabled={verifyOtpMutation.isPending || !isValidOtpCode(authOtp)}
                onClick={() => {
                  if (!isValidOtpCode(authOtp)) {
                    setMessage("Enter a valid OTP code.");
                    return;
                  }
                  verifyOtpMutation.mutate();
                }}
              >
                {verifyOtpMutation.isPending ? "Verifying..." : "Verify OTP"}
              </button>
            </div>
          </>
        )}
      </section>

      <section className="mt-5 rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Step 2: Select patient</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
          <input className="rounded border px-3 py-2" placeholder="Patient phone number" value={patientPhone} onChange={(e) => setPatientPhone(e.target.value)} />
          <button
            className="rounded border px-4 py-2 text-sm font-medium hover:bg-slate-100 disabled:opacity-60"
            type="button"
            disabled={!sessionToken || lookupPatientMutation.isPending || !isValidPhoneNumber(patientPhone)}
            onClick={() => {
              if (!sessionToken) {
                setMessage("Please complete OTP authentication first.");
                return;
              }
              if (!isValidPhoneNumber(patientPhone)) {
                setMessage("Enter a valid patient phone number.");
                return;
              }
              lookupPatientMutation.mutate({ token: sessionToken, phone: patientPhone.trim() });
            }}
          >
            {lookupPatientMutation.isPending ? "Checking..." : "Check Patient"}
          </button>
        </div>

        {!existingPatient ? (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <input className="rounded border px-3 py-2" placeholder="Full name" value={newPatient.full_name} onChange={(e) => setNewPatient((p) => ({ ...p, full_name: e.target.value }))} />
            <select className="rounded border px-3 py-2" value={newPatient.gender} onChange={(e) => setNewPatient((p) => ({ ...p, gender: e.target.value as "" | "MALE" | "FEMALE" | "OTHER" }))}>
              <option value="">Gender (optional)</option>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
            <input className="rounded border px-3 py-2" type="date" value={newPatient.dob} onChange={(e) => setNewPatient((p) => ({ ...p, dob: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Blood group" value={newPatient.blood_group} onChange={(e) => setNewPatient((p) => ({ ...p, blood_group: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Emergency contact" value={newPatient.emergency_contact} onChange={(e) => setNewPatient((p) => ({ ...p, emergency_contact: e.target.value }))} />
            <input className="rounded border px-3 py-2" placeholder="Address" value={newPatient.address} onChange={(e) => setNewPatient((p) => ({ ...p, address: e.target.value }))} />
          </div>
        ) : (
          <div className="mt-4 rounded-lg border bg-emerald-50 p-3 text-sm text-emerald-800">
            Existing patient detected: {existingPatient.full_name} (#{existingPatient.patient_id})
          </div>
        )}
      </section>

      <section className="mt-5 rounded-2xl border bg-white p-6 shadow-sm">
        <button
          className="rounded bg-emerald-600 px-5 py-2.5 font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          type="button"
          disabled={bookMutation.isPending}
          onClick={() => {
            if (!sessionToken) {
              setMessage("Please complete OTP authentication first.");
              return;
            }
            if (!selectedSlot) {
              setMessage("Selected slot is not available.");
              return;
            }
            if (!isValidPhoneNumber(patientPhone)) {
              setMessage("Enter a valid patient phone number.");
              return;
            }

            if (existingPatient) {
              bookMutation.mutate({
                booking_session_token: sessionToken,
                availability_id: selectedSlot.availability_id,
                patient_phone: patientPhone.trim()
              });
              return;
            }

            if (newPatient.full_name.trim().length < 2) {
              setMessage("Please provide new patient full name.");
              return;
            }

            bookMutation.mutate({
              booking_session_token: sessionToken,
              availability_id: selectedSlot.availability_id,
              patient_phone: patientPhone.trim(),
              patient: {
                full_name: newPatient.full_name.trim(),
                phone: patientPhone.trim(),
                gender: newPatient.gender || undefined,
                dob: newPatient.dob || undefined,
                blood_group: newPatient.blood_group.trim() || undefined,
                address: newPatient.address.trim() || undefined,
                emergency_contact: newPatient.emergency_contact.trim() || undefined
              }
            });
          }}
        >
          {bookMutation.isPending ? "Booking..." : "Confirm Booking"}
        </button>
        {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
        {lastBookedAppointment && selectedSlot ? (
          <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <p className="text-sm font-semibold text-emerald-800">
              Booking confirmation ready for appointment #{lastBookedAppointment.appointment_id}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                className="rounded border border-emerald-600 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100"
                type="button"
                onClick={() => {
                  const content = buildBookingConfirmationArtifactContent({
                    clinicName: "CarePoint Clinic",
                    appointmentId: lastBookedAppointment.appointment_id,
                    patientPhone: lastBookedAppointment.patient_phone,
                    doctorName: doctorQuery.data?.full_name ?? selectedSlot.doctor_name,
                    date: selectedSlot.available_date,
                    startTime: selectedSlot.slot_start_time,
                    endTime: selectedSlot.slot_end_time,
                    status: "BOOKED",
                    bookingSource: "ONLINE"
                  });
                  downloadTextArtifact(
                    bookingConfirmationFileName(lastBookedAppointment.appointment_id),
                    content
                  );
                }}
              >
                Download Confirmation
              </button>
              <button
                className="rounded border border-emerald-600 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100"
                type="button"
                onClick={() => {
                  const content = buildBookingConfirmationArtifactContent({
                    clinicName: "CarePoint Clinic",
                    appointmentId: lastBookedAppointment.appointment_id,
                    patientPhone: lastBookedAppointment.patient_phone,
                    doctorName: doctorQuery.data?.full_name ?? selectedSlot.doctor_name,
                    date: selectedSlot.available_date,
                    startTime: selectedSlot.slot_start_time,
                    endTime: selectedSlot.slot_end_time,
                    status: "BOOKED",
                    bookingSource: "ONLINE"
                  });
                  printTextArtifact(`Appointment #${lastBookedAppointment.appointment_id}`, content);
                }}
              >
                Print Confirmation
              </button>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
