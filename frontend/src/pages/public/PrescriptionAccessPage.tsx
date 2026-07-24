import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import {
  getPublicClinicSettings,
  requestPublicPrescriptionOtp,
  verifyPublicPrescriptionOtp,
  type PublicPrescriptionItem
} from "../../api/public";
import { isValidOtpCode, isValidPhoneNumber } from "../../utils/validators";
import {
  buildPrescriptionArtifactContent,
  downloadTextArtifact,
  prescriptionFileName,
  printTextArtifact
} from "../../utils/patientArtifacts";

export function PrescriptionAccessPage() {
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [otpPreview, setOtpPreview] = useState<string | null>(null);
  const [records, setRecords] = useState<PublicPrescriptionItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const clinicSettingsQuery = useQuery({
    queryKey: ["public", "clinic-settings"],
    queryFn: getPublicClinicSettings
  });
  const clinicName = clinicSettingsQuery.data?.clinic_name || "CarePoint Clinic";

  const requestOtpMutation = useMutation({
    mutationFn: () => requestPublicPrescriptionOtp(phone.trim()),
    onSuccess: (data) => {
      setOtpRequested(true);
      setOtpPreview(data.otp_preview);
      setError(null);
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : "Failed to request OTP.");
    }
  });

  const verifyOtpMutation = useMutation({
    mutationFn: () => verifyPublicPrescriptionOtp(phone.trim(), otp.trim()),
    onSuccess: (data) => {
      setRecords(data);
      setError(null);
    },
    onError: (err) => {
      setRecords([]);
      setError(err instanceof Error ? err.message : "Failed to verify OTP.");
    }
  });

  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <header className="mb-4 flex items-center justify-between rounded-xl border bg-white px-4 py-3 shadow-sm">
        <Link className="text-sm font-medium text-emerald-700 hover:underline" to="/">
          ← Back to home
        </Link>
      </header>
      <section className="mt-4 rounded-2xl border bg-white p-6 shadow-sm md:p-8">
        <h1 className="text-2xl font-bold text-slate-900">View your prescriptions</h1>
        <p className="mt-2 text-sm text-slate-600">
          Enter your phone number to receive OTP verification and access prescription history.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
            placeholder="Phone number"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
          />
          <button
            className="rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
            type="button"
            disabled={requestOtpMutation.isPending || !isValidPhoneNumber(phone)}
            onClick={() => {
              if (!isValidPhoneNumber(phone)) {
                setError("Enter a valid phone number.");
                return;
              }
              requestOtpMutation.mutate();
            }}
          >
            {requestOtpMutation.isPending ? "Sending OTP..." : "Send OTP"}
          </button>
        </div>
        {otpRequested ? (
          <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3">
            <p className="text-sm text-slate-700">OTP sent. Enter it below to fetch records.</p>
            {otpPreview ? <p className="mt-1 text-xs text-emerald-700">Demo OTP: {otpPreview}</p> : null}
            <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
              <input
                className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
                placeholder="Enter OTP"
                value={otp}
                onChange={(event) => setOtp(event.target.value)}
              />
              <button
                className="rounded-md border border-slate-300 px-4 py-2 font-medium text-slate-800 hover:bg-slate-100 disabled:opacity-60"
                type="button"
                disabled={verifyOtpMutation.isPending || !isValidOtpCode(otp)}
                onClick={() => {
                  if (!isValidOtpCode(otp)) {
                    setError("Enter a valid OTP code.");
                    return;
                  }
                  verifyOtpMutation.mutate();
                }}
              >
                {verifyOtpMutation.isPending ? "Verifying..." : "Verify & View"}
              </button>
            </div>
          </div>
        ) : null}
        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      </section>

      <section className="mt-6 rounded-2xl border bg-white p-6 shadow-sm md:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Prescription history</h2>
        {records.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No records loaded yet.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {records.map((item) => (
              <article key={item.prescription_id} className="rounded-lg border border-slate-200 p-4">
                <p className="font-medium text-slate-900">
                  Prescription #{item.prescription_id} • Dr. {item.doctor_name}
                </p>
                <p className="mt-2 text-xs text-slate-500">Appointment #{item.appointment_id}</p>
                <p className="mt-1 text-sm text-slate-600">Diagnosis: {item.diagnosis ?? "N/A"}</p>
                <p className="text-sm text-slate-600">Medicines: {item.medicines ?? "N/A"}</p>
                <p className="text-sm text-slate-600">Advice: {item.doctor_advice ?? "N/A"}</p>
                <div className="mt-3 flex gap-2">
                  <button
                    className="rounded border px-3 py-1.5 text-xs font-medium hover:bg-slate-100"
                    type="button"
                    onClick={() => {
                      const content = buildPrescriptionArtifactContent({
                        clinicName,
                        prescriptionId: item.prescription_id,
                        appointmentId: item.appointment_id,
                        doctorName: item.doctor_name,
                        diagnosis: item.diagnosis,
                        medicines: item.medicines,
                        dosage: item.dosage,
                        frequency: item.frequency,
                        duration: item.duration,
                        doctorAdvice: item.doctor_advice,
                        followUpDate: item.follow_up_date,
                        issuedAt: item.created_at
                      });
                      downloadTextArtifact(prescriptionFileName(item.prescription_id), content);
                    }}
                  >
                    Download
                  </button>
                  <button
                    className="rounded border px-3 py-1.5 text-xs font-medium hover:bg-slate-100"
                    type="button"
                    onClick={() => {
                      const content = buildPrescriptionArtifactContent({
                        clinicName,
                        prescriptionId: item.prescription_id,
                        appointmentId: item.appointment_id,
                        doctorName: item.doctor_name,
                        diagnosis: item.diagnosis,
                        medicines: item.medicines,
                        dosage: item.dosage,
                        frequency: item.frequency,
                        duration: item.duration,
                        doctorAdvice: item.doctor_advice,
                        followUpDate: item.follow_up_date,
                        issuedAt: item.created_at
                      });
                      printTextArtifact(`Prescription #${item.prescription_id}`, content);
                    }}
                  >
                    Print
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
