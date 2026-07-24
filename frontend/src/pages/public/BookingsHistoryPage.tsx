import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import {
  cancelPublicAppointment,
  getPublicClinicSettings,
  listPublicAvailabilitiesByDoctor,
  listPublicBookingHistory,
  requestPublicBookingOtp,
  reschedulePublicAppointment,
  verifyPublicBookingOtp
} from "../../api/public";
import {
  clearPublicBookingSession,
  getPublicBookingSessionPhone,
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

function timelineFromAppointment(item: {
  appointment_status: string;
  created_at: string | null;
  completed_at: string | null;
  updated_at: string | null;
  cancellation_reason: string | null;
}): Array<{ label: string; time: string | null; detail?: string }> {
  const timeline = [
    { label: "Booked", time: item.created_at, detail: undefined as string | undefined }
  ];
  if (item.appointment_status === "COMPLETED") {
    timeline.push({ label: "Completed", time: item.completed_at, detail: undefined });
  }
  if (item.appointment_status.startsWith("CANCELLED")) {
    timeline.push({
      label: "Cancelled",
      time: item.updated_at,
      detail: item.cancellation_reason ?? undefined
    });
  }
  return timeline;
}

export function BookingsHistoryPage() {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const [authPhone, setAuthPhone] = useState(getPublicBookingSessionPhone() ?? "");
  const [otp, setOtp] = useState("");
  const [sessionToken, setSessionToken] = useState<string | null>(() => getPublicBookingSessionToken());
  const [cancelReason, setCancelReason] = useState<Record<number, string>>({});
  const [rescheduleAvailability, setRescheduleAvailability] = useState<Record<number, string>>({});
  const clinicSettingsQuery = useQuery({
    queryKey: ["public", "clinic-settings"],
    queryFn: getPublicClinicSettings
  });
  const clinicName = clinicSettingsQuery.data?.clinic_name || "CarePoint Clinic";

  const historyQuery = useQuery({
    queryKey: ["public", "booking-history", sessionToken],
    queryFn: () => listPublicBookingHistory(sessionToken!),
    enabled: Boolean(sessionToken)
  });

  const requestOtpMutation = useMutation({
    mutationFn: () => requestPublicBookingOtp(authPhone.trim()),
    onSuccess: (data) => {
      setMessage(data.otp_preview ? `OTP sent. Demo OTP: ${data.otp_preview}` : "OTP sent.");
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to request OTP.")
  });

  const verifyOtpMutation = useMutation({
    mutationFn: () => verifyPublicBookingOtp(authPhone.trim(), otp.trim()),
    onSuccess: (data) => {
      setPublicBookingSession(data.booking_session_token, authPhone.trim(), data.expires_in_minutes);
      setSessionToken(data.booking_session_token);
      setMessage(`Session active for ${data.expires_in_minutes} minutes.`);
      void queryClient.invalidateQueries({ queryKey: ["public", "booking-history"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to verify OTP.")
  });

  const cancelMutation = useMutation({
    mutationFn: ({ appointmentId, reason }: { appointmentId: number; reason: string }) =>
      cancelPublicAppointment(appointmentId, sessionToken!, reason),
    onSuccess: (data) => {
      setMessage(`Appointment #${data.appointment_id} cancelled.`);
      void queryClient.invalidateQueries({ queryKey: ["public", "booking-history"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to cancel appointment.")
  });

  const rescheduleMutation = useMutation({
    mutationFn: ({ appointmentId, newAvailabilityId }: { appointmentId: number; newAvailabilityId: number }) =>
      reschedulePublicAppointment(appointmentId, sessionToken!, newAvailabilityId),
    onSuccess: (data) => {
      setMessage(`Appointment #${data.appointment_id} rescheduled.`);
      void queryClient.invalidateQueries({ queryKey: ["public", "booking-history"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to reschedule appointment.")
  });

  return (
    <main className="mx-auto max-w-6xl p-4 md:p-8">
      <div className="mb-4 flex items-center justify-between">
        <Link className="text-sm font-medium text-emerald-700 hover:underline" to="/">
          ← Back to Home
        </Link>
        <button
          className="rounded border px-3 py-1.5 text-sm hover:bg-slate-100"
          type="button"
          onClick={() => {
            clearPublicBookingSession();
            setSessionToken(null);
            setMessage("Booking session cleared.");
          }}
        >
          Clear Session
        </button>
      </div>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">My Bookings</h1>
        <p className="mt-2 text-sm text-slate-600">Authenticate once to view, cancel, or reschedule your bookings.</p>
        {!sessionToken ? (
          <>
            <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
              <input className="rounded border px-3 py-2" placeholder="Your phone number" value={authPhone} onChange={(e) => setAuthPhone(e.target.value)} />
              <button
                className="rounded bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                type="button"
                disabled={requestOtpMutation.isPending || !isValidPhoneNumber(authPhone)}
                onClick={() => {
                  if (!isValidPhoneNumber(authPhone)) {
                    setMessage("Enter a valid phone number.");
                    return;
                  }
                  requestOtpMutation.mutate();
                }}
              >
                {requestOtpMutation.isPending ? "Sending..." : "Send OTP"}
              </button>
            </div>
            <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
              <input className="rounded border px-3 py-2" placeholder="OTP code" value={otp} onChange={(e) => setOtp(e.target.value)} />
              <button
                className="rounded border px-4 py-2 text-sm font-medium hover:bg-slate-100 disabled:opacity-60"
                type="button"
                disabled={verifyOtpMutation.isPending || !isValidOtpCode(otp)}
                onClick={() => {
                  if (!isValidOtpCode(otp)) {
                    setMessage("Enter a valid OTP.");
                    return;
                  }
                  verifyOtpMutation.mutate();
                }}
              >
                {verifyOtpMutation.isPending ? "Verifying..." : "Verify OTP"}
              </button>
            </div>
          </>
        ) : (
          <p className="mt-3 text-sm text-emerald-700">Session active for: {getPublicBookingSessionPhone() ?? authPhone}</p>
        )}
        {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
      </section>

      <section className="mt-5 rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Booking history</h2>
        {!sessionToken ? <p className="mt-2 text-sm text-slate-600">Verify OTP to load your bookings.</p> : null}
        {historyQuery.isLoading ? <p className="mt-2 text-sm text-slate-600">Loading bookings...</p> : null}
        {historyQuery.isError ? <p className="mt-2 text-sm text-red-600">Could not load booking history.</p> : null}
        {!historyQuery.isLoading && sessionToken && (historyQuery.data ?? []).length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No bookings found.</p>
        ) : null}
        <div className="mt-3 space-y-3">
          {(historyQuery.data ?? []).map((item) => (
            <article key={item.appointment_id} className="rounded-lg border p-4">
              <p className="font-medium text-slate-900">
                #{item.appointment_id} • {item.doctor_name}
              </p>
              <p className="mt-1 text-sm text-slate-600">
                Patient: {item.patient_name} ({item.patient_phone})
              </p>
              <p className="text-sm text-slate-600">
                {item.available_date} • {item.slot_start_time} - {item.slot_end_time}
              </p>
              <p className="text-sm text-slate-600">Status: {item.appointment_status}</p>
              {item.cancellation_reason ? <p className="text-sm text-slate-600">Reason: {item.cancellation_reason}</p> : null}
              <div className="mt-2 rounded border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Status timeline</p>
                <ol className="mt-2 space-y-1 text-xs text-slate-700">
                  {timelineFromAppointment(item).map((step, index) => (
                    <li key={index}>
                      • {step.label}
                      {step.time ? ` at ${new Date(step.time).toLocaleString()}` : ""}
                      {step.detail ? ` (${step.detail})` : ""}
                    </li>
                  ))}
                </ol>
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                <button
                  className="rounded border px-3 py-1.5 text-xs font-medium hover:bg-slate-100"
                  type="button"
                  onClick={() => {
                    const content = buildBookingConfirmationArtifactContent({
                      clinicName,
                      appointmentId: item.appointment_id,
                      patientPhone: item.patient_phone,
                      doctorName: item.doctor_name,
                      date: item.available_date,
                      startTime: item.slot_start_time,
                      endTime: item.slot_end_time,
                      status: item.appointment_status,
                      bookingSource: item.booking_source
                    });
                    downloadTextArtifact(bookingConfirmationFileName(item.appointment_id), content);
                  }}
                >
                  Download Confirmation
                </button>
                <button
                  className="rounded border px-3 py-1.5 text-xs font-medium hover:bg-slate-100"
                  type="button"
                  onClick={() => {
                    const content = buildBookingConfirmationArtifactContent({
                      clinicName,
                      appointmentId: item.appointment_id,
                      patientPhone: item.patient_phone,
                      doctorName: item.doctor_name,
                      date: item.available_date,
                      startTime: item.slot_start_time,
                      endTime: item.slot_end_time,
                      status: item.appointment_status,
                      bookingSource: item.booking_source
                    });
                    printTextArtifact(`Appointment #${item.appointment_id}`, content);
                  }}
                >
                  Print Confirmation
                </button>
              </div>
              {item.appointment_status === "BOOKED" ? (
                <div className="mt-3 grid gap-3 md:grid-cols-[1fr_1fr_auto]">
                  <input
                    className="rounded border px-3 py-2 text-sm"
                    placeholder="Cancellation reason"
                    value={cancelReason[item.appointment_id] ?? ""}
                    onChange={(e) =>
                      setCancelReason((prev) => ({ ...prev, [item.appointment_id]: e.target.value }))
                    }
                  />
                  <RescheduleSelector
                    doctorUserId={item.doctor_user_id}
                    selectedValue={rescheduleAvailability[item.appointment_id] ?? ""}
                    onChange={(value) =>
                      setRescheduleAvailability((prev) => ({ ...prev, [item.appointment_id]: value }))
                    }
                  />
                  <div className="flex gap-2">
                    <button
                      className="rounded border px-3 py-2 text-sm hover:bg-slate-100 disabled:opacity-60"
                      type="button"
                      disabled={cancelMutation.isPending}
                      onClick={() => {
                        const reason = (cancelReason[item.appointment_id] ?? "").trim();
                        if (reason.length < 1) {
                          setMessage("Please provide cancellation reason.");
                          return;
                        }
                        cancelMutation.mutate({ appointmentId: item.appointment_id, reason });
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      className="rounded bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                      type="button"
                      disabled={rescheduleMutation.isPending}
                      onClick={() => {
                        const newId = Number(rescheduleAvailability[item.appointment_id] ?? "");
                        if (!Number.isInteger(newId) || newId < 1) {
                          setMessage("Please select a valid new slot.");
                          return;
                        }
                        rescheduleMutation.mutate({ appointmentId: item.appointment_id, newAvailabilityId: newId });
                      }}
                    >
                      Reschedule
                    </button>
                  </div>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function RescheduleSelector({
  doctorUserId,
  selectedValue,
  onChange
}: {
  doctorUserId: number;
  selectedValue: string;
  onChange: (value: string) => void;
}) {
  const slotsQuery = useQuery({
    queryKey: ["public", "reschedule-slots", doctorUserId],
    queryFn: () => listPublicAvailabilitiesByDoctor(doctorUserId)
  });

  return (
    <select className="rounded border px-3 py-2 text-sm" value={selectedValue} onChange={(e) => onChange(e.target.value)}>
      <option value="">Select new slot</option>
      {(slotsQuery.data ?? []).map((slot) => (
        <option key={slot.availability_id} value={String(slot.availability_id)}>
          #{slot.availability_id} • {slot.available_date} {slot.slot_start_time}-{slot.slot_end_time}
        </option>
      ))}
    </select>
  );
}
