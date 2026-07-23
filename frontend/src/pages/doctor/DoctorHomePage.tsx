import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { useNavigate } from "react-router-dom";

import { changePassword, logout } from "../../api/auth";
import { getDoctorDashboard } from "../../api/dashboard";
import {
  applyDoctorAvailabilityTimeWindow,
  cancelDoctorAppointment,
  cancelDoctorAvailability,
  completeDoctorAppointment,
  createDoctorAvailability,
  emergencyCancelDoctorAvailabilities,
  getDoctorAppointmentDetail,
  getDoctorProfile,
  listDoctorAppointments,
  listDoctorAvailabilities,
  listDoctorSlots,
  updateDoctorProfile,
  upsertDoctorPrescription,
  type DoctorAppointment,
  type DoctorAppointmentDetail,
  type DoctorAvailability,
  type DoctorAvailabilityWindowResult,
  type DoctorProfile,
  type DoctorPrescription
} from "../../api/doctor";
import { NotificationPanel } from "../../components/NotificationPanel";
import { useAuth } from "../../hooks/useAuth";

type DoctorTab = "dashboard" | "availability" | "appointments" | "prescriptions" | "profile";

type ToastItem = { id: number; text: string; kind: "success" | "error" };

type PrescriptionFormState = {
  diagnosis: string;
  medicines: string;
  dosage: string;
  frequency: string;
  duration: string;
  doctor_advice: string;
  internal_notes: string;
  follow_up_date: string;
};

function toDateInputValue(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDateLabel(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" });
}

function formatShortDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString([], { weekday: "short", day: "numeric", month: "short" });
}

function formatTimeLabel(value: string): string {
  const [hours, minutes] = value.split(":");
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function toTimeInputValue(value: string): string {
  return value.slice(0, 5);
}

function toApiTimeValue(value: string): string {
  return value.length === 5 ? `${value}:00` : value;
}

function statusClasses(status: string): string {
  if (status === "BOOKED") return "bg-blue-50 text-blue-700";
  if (status === "COMPLETED") return "bg-emerald-50 text-emerald-700";
  if (status === "AVAILABLE") return "bg-emerald-50 text-emerald-700";
  if (status === "BLOCKED") return "bg-amber-50 text-amber-700";
  if (status.includes("CANCELLED")) return "bg-rose-50 text-rose-700";
  return "bg-slate-100 text-slate-700";
}

function emptyPrescriptionForm(): PrescriptionFormState {
  return {
    diagnosis: "",
    medicines: "",
    dosage: "",
    frequency: "",
    duration: "",
    doctor_advice: "",
    internal_notes: "",
    follow_up_date: ""
  };
}

function mapPrescriptionToForm(prescription: DoctorPrescription | null | undefined): PrescriptionFormState {
  return {
    diagnosis: prescription?.diagnosis ?? "",
    medicines: prescription?.medicines ?? "",
    dosage: prescription?.dosage ?? "",
    frequency: prescription?.frequency ?? "",
    duration: prescription?.duration ?? "",
    doctor_advice: prescription?.doctor_advice ?? "",
    internal_notes: prescription?.internal_notes ?? "",
    follow_up_date: prescription?.follow_up_date ?? ""
  };
}

const NAV_ICONS: Record<DoctorTab, string> = {
  dashboard:
    "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  availability:
    "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
  appointments:
    "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01",
  prescriptions:
    "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  profile:
    "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
};

function SidebarButton({
  active,
  label,
  tab,
  badge,
  onClick
}: {
  active: boolean;
  label: string;
  tab: DoctorTab;
  badge?: number;
  onClick: () => void;
}) {
  return (
    <button
      className={`group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
        active
          ? "bg-blue-600 text-white shadow-md shadow-blue-900/30"
          : "text-slate-300 hover:bg-white/10 hover:text-white"
      }`}
      type="button"
      onClick={onClick}
    >
      <svg className="h-4 w-4 shrink-0 opacity-80" fill="none" stroke="currentColor" strokeWidth={1.75} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d={NAV_ICONS[tab]} />
      </svg>
      <span className="flex-1">{label}</span>
      {badge !== undefined && badge > 0 ? (
        <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${active ? "bg-white/20 text-white" : "bg-blue-500/30 text-blue-200"}`}>
          {badge}
        </span>
      ) : null}
    </button>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/60 px-6 py-10 text-center">
      <svg className="mb-3 h-8 w-8 text-slate-300" fill="none" stroke="currentColor" strokeWidth={1.25} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p className="text-sm text-slate-500">{text}</p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-2">
          <div className="h-3.5 w-16 rounded bg-slate-200" />
          <div className="h-4 w-32 rounded bg-slate-200" />
          <div className="h-3 w-24 rounded bg-slate-200" />
        </div>
        <div className="h-6 w-16 rounded-full bg-slate-200" />
      </div>
    </div>
  );
}

function ToastStack({ toasts, onDismiss }: { toasts: ToastItem[]; onDismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-start gap-3 rounded-2xl border px-4 py-3 shadow-lg ${
            toast.kind === "error"
              ? "border-rose-200 bg-rose-50 text-rose-800"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
        >
          <svg className="mt-0.5 h-4 w-4 shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            {toast.kind === "error" ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            )}
          </svg>
          <p className="flex-1 text-sm">{toast.text}</p>
          <button className="ml-1 opacity-60 hover:opacity-100" type="button" onClick={() => onDismiss(toast.id)}>
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}

const STATUS_LEFT_BORDER: Record<string, string> = {
  BOOKED: "border-l-blue-400",
  COMPLETED: "border-l-emerald-400",
  CANCELLED_BY_DOCTOR: "border-l-rose-400",
  CANCELLED_BY_FRONTDESK: "border-l-rose-400",
  CANCELLED_BY_PATIENT: "border-l-rose-400",
  NO_SHOW: "border-l-slate-400"
};

function getStatusBorder(status: string): string {
  return STATUS_LEFT_BORDER[status] ?? "border-l-slate-300";
}

function AppointmentList({
  appointments,
  selectedAppointmentId,
  onSelect,
  showDate = false
}: {
  appointments: DoctorAppointment[];
  selectedAppointmentId: number | null;
  onSelect: (appointmentId: number) => void;
  showDate?: boolean;
}) {
  if (appointments.length === 0) {
    return <EmptyState text="No appointments found." />;
  }

  return (
    <div className="space-y-2.5">
      {appointments.map((appointment, index) => {
        const selected = selectedAppointmentId === appointment.appointment_id;
        return (
          <button
            key={appointment.appointment_id}
            className={`w-full rounded-2xl border-l-4 border border-slate-200 text-left transition ${getStatusBorder(appointment.appointment_status)} ${
              selected
                ? "bg-blue-50 shadow-sm ring-1 ring-blue-300"
                : "bg-white hover:bg-slate-50 hover:shadow-sm"
            }`}
            type="button"
            onClick={() => onSelect(appointment.appointment_id)}
          >
            <div className="flex items-start gap-3 px-4 py-3.5">
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                selected ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600"
              }`}>
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-slate-900">{formatTimeLabel(appointment.slot_start_time)}</p>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${statusClasses(appointment.appointment_status)}`}>
                    {appointment.appointment_status}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-sm font-medium text-slate-800">{appointment.patient_name}</p>
                <p className="text-xs text-slate-400">{appointment.patient_phone}</p>
                {showDate ? <p className="mt-1 text-xs text-slate-400">{formatDateLabel(appointment.available_date)}</p> : null}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

function PatientInitials({ name }: { name: string }) {
  const parts = name.trim().split(/\s+/);
  const initials = parts.length >= 2 ? `${parts[0][0]}${parts[1][0]}` : parts[0].slice(0, 2);
  return (
    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-sm font-bold uppercase tracking-wide text-white shadow-md">
      {initials.toUpperCase()}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 px-3 py-3">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-medium text-slate-800">{value}</p>
    </div>
  );
}

function CollapsiblePrescription({ item }: { item: { prescription_id: number; appointment_date: string; slot_start_time: string; slot_end_time: string; doctor_name: string; diagnosis: string | null; medicines: string | null; dosage: string | null; frequency: string | null; duration: string | null; doctor_advice: string | null; internal_notes: string | null; follow_up_date: string | null } }) {
  const [open, setOpen] = useState(false);
  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <button
        className="flex w-full items-start justify-between gap-3 px-4 py-3.5 text-left hover:bg-slate-50"
        type="button"
        onClick={() => setOpen((prev) => !prev)}
      >
        <div>
          <p className="font-semibold text-slate-900">{formatDateLabel(item.appointment_date)}</p>
          <p className="text-sm text-slate-500">{item.doctor_name} • {formatTimeLabel(item.slot_start_time)}</p>
          {!open && item.diagnosis ? (
            <p className="mt-1 max-w-xs truncate text-xs text-slate-400">{item.diagnosis}</p>
          ) : null}
        </div>
        <svg
          className={`mt-0.5 h-4 w-4 shrink-0 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open ? (
        <div className="border-t border-slate-100 px-4 py-3 space-y-2 text-sm text-slate-700">
          {([
            ["Diagnosis", item.diagnosis],
            ["Medicines", item.medicines],
            ["Dosage", item.dosage],
            ["Frequency", item.frequency],
            ["Duration", item.duration],
            ["Doctor Advice", item.doctor_advice],
            ["Consultation Notes", item.internal_notes],
            ["Follow-up Date", item.follow_up_date]
          ] as [string, string | null][]).map(([label, value]) =>
            value ? (
              <div key={label}>
                <span className="font-medium text-slate-900">{label}: </span>
                <span>{value}</span>
              </div>
            ) : null
          )}
        </div>
      ) : null}
    </article>
  );
}

function ConsultationWorkspace({
  detail,
  form,
  setForm,
  onSave,
  onComplete,
  onCancelAppointment,
  savePending
}: {
  detail: DoctorAppointmentDetail;
  form: PrescriptionFormState;
  setForm: Dispatch<SetStateAction<PrescriptionFormState>>;
  onSave: () => void;
  onComplete: (appointmentId: number) => void;
  onCancelAppointment: (appointmentId: number) => void;
  savePending: boolean;
}) {
  const canManageAppointment = detail.appointment_status === "BOOKED";

  return (
    <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr]">
      <section className="rounded-3xl bg-white p-5 shadow-sm">
        {/* Header */}
        <div className="flex flex-wrap items-start gap-3">
          <PatientInitials name={detail.patient.full_name} />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-xl font-semibold text-slate-900">{detail.patient.full_name}</h3>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusClasses(detail.appointment_status)}`}>
                {detail.appointment_status}
              </span>
            </div>
            <p className="mt-1 text-sm text-slate-500">
              {formatDateLabel(detail.available_date)} • {formatTimeLabel(detail.slot_start_time)} – {formatTimeLabel(detail.slot_end_time)}
            </p>
          </div>
          {canManageAppointment ? (
            <div className="flex flex-wrap gap-2">
              <button
                className="flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100"
                type="button"
                onClick={() => onComplete(detail.appointment_id)}
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                Complete
              </button>
              <button
                className="flex items-center gap-1.5 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700 hover:bg-rose-100"
                type="button"
                onClick={() => onCancelAppointment(detail.appointment_id)}
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                Cancel
              </button>
            </div>
          ) : null}
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <DetailRow label="Name" value={detail.patient.full_name} />
          <DetailRow label="Age" value={detail.patient.age !== null ? `${detail.patient.age} years` : "Not available"} />
          <DetailRow label="Gender" value={detail.patient.gender ?? "Not available"} />
          <DetailRow label="Phone" value={detail.patient.phone} />
          <DetailRow
            label="Appointment time"
            value={`${formatDateLabel(detail.available_date)} • ${formatTimeLabel(detail.slot_start_time)} – ${formatTimeLabel(detail.slot_end_time)}`}
          />
          <DetailRow label="Reason for visit" value={detail.reason_for_visit ?? "Not recorded"} />
        </div>

        <div className="mt-6">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Prescription workspace</p>
              <h4 className="mt-1 text-lg font-semibold text-slate-900">
                {detail.can_edit_prescription ? "Edit today's prescription" : "Read-only prescription record"}
              </h4>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Diagnosis</span>
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                value={form.diagnosis}
                onChange={(event) => setForm((prev) => ({ ...prev, diagnosis: event.target.value }))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Medicines</span>
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                value={form.medicines}
                onChange={(event) => setForm((prev) => ({ ...prev, medicines: event.target.value }))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Dosage</span>
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                value={form.dosage}
                onChange={(event) => setForm((prev) => ({ ...prev, dosage: event.target.value }))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Frequency</span>
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                value={form.frequency}
                onChange={(event) => setForm((prev) => ({ ...prev, frequency: event.target.value }))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Duration</span>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                value={form.duration}
                onChange={(event) => setForm((prev) => ({ ...prev, duration: event.target.value }))}
              />
            </label>
            <label className="text-sm text-slate-700">
              <span className="mb-1 block font-medium">Follow-up date</span>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
                disabled={!detail.can_edit_prescription}
                type="date"
                value={form.follow_up_date}
                onChange={(event) => setForm((prev) => ({ ...prev, follow_up_date: event.target.value }))}
              />
            </label>
          </div>

          <label className="mt-3 block text-sm text-slate-700">
            <span className="mb-1 block font-medium">Doctor advice</span>
            <textarea
              className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
              disabled={!detail.can_edit_prescription}
              value={form.doctor_advice}
              onChange={(event) => setForm((prev) => ({ ...prev, doctor_advice: event.target.value }))}
            />
          </label>

          <label className="mt-3 block text-sm text-slate-700">
            <span className="mb-1 block font-medium">Consultation notes</span>
            <textarea
              className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring disabled:bg-slate-50"
              disabled={!detail.can_edit_prescription}
              value={form.internal_notes}
              onChange={(event) => setForm((prev) => ({ ...prev, internal_notes: event.target.value }))}
            />
          </label>

          {detail.can_edit_prescription ? (
            <button
              className="mt-4 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
              disabled={savePending}
              type="button"
              onClick={onSave}
            >
              {savePending ? "Saving..." : "Save Prescription"}
            </button>
          ) : (
            <p className="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              Older consultations are read-only. Prescription editing is allowed only on the appointment day.
            </p>
          )}
        </div>
      </section>

      <section className="rounded-3xl bg-white p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Previous prescriptions</p>
        <p className="mt-0.5 text-sm text-slate-400">{detail.previous_prescriptions.length} record{detail.previous_prescriptions.length !== 1 ? "s" : ""} found</p>
        <div className="mt-4 space-y-2">
          {detail.previous_prescriptions.length === 0 ? (
            <EmptyState text="No previous prescriptions found for this patient." />
          ) : (
            detail.previous_prescriptions.map((item) => (
              <CollapsiblePrescription key={item.prescription_id} item={item} />
            ))
          )}
        </div>
      </section>
    </div>
  );
}

function ProfileEditor({
  profile,
  profileForm,
  onProfileChange,
  onSaveProfile,
  savingProfile,
  passwordForm,
  onPasswordChange,
  onChangePassword,
  changingPassword
}: {
  profile: DoctorProfile;
  profileForm: {
    full_name: string;
    phone: string;
    qualification: string;
    experience_years: string;
    about: string;
  };
  onProfileChange: (field: "full_name" | "phone" | "qualification" | "experience_years" | "about", value: string) => void;
  onSaveProfile: () => void;
  savingProfile: boolean;
  passwordForm: { current_password: string; new_password: string; confirm_password: string };
  onPasswordChange: (field: "current_password" | "new_password" | "confirm_password", value: string) => void;
  onChangePassword: () => void;
  changingPassword: boolean;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <section className="rounded-3xl bg-white p-5 shadow-sm">
        {/* Doctor identity header */}
        <div className="flex items-center gap-4 border-b border-slate-100 pb-5">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-lg font-bold uppercase text-white shadow-md">
            {profile.full_name.trim().split(/\s+/).slice(0, 2).map((p) => p[0]).join("").toUpperCase()}
          </div>
          <div>
            <p className="text-lg font-bold text-slate-900">{profile.full_name}</p>
            <p className="text-sm text-slate-500">{profile.email}</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {profile.specialization_names.length === 0 ? (
                <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-500">No specialization assigned</span>
              ) : profile.specialization_names.map((spec) => (
                <span key={spec} className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">{spec}</span>
              ))}
            </div>
          </div>
        </div>
        <p className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Edit profile</p>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Name</span>
            <input
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
              value={profileForm.full_name}
              onChange={(event) => onProfileChange("full_name", event.target.value)}
            />
          </label>
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Phone</span>
            <input
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
              value={profileForm.phone}
              onChange={(event) => onProfileChange("phone", event.target.value)}
            />
          </label>
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Email</span>
            <input className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5" readOnly value={profile.email} />
          </label>
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Role</span>
            <input className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5" readOnly value={profile.role_name} />
          </label>
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Qualification</span>
            <input
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
              value={profileForm.qualification}
              onChange={(event) => onProfileChange("qualification", event.target.value)}
            />
          </label>
          <label className="text-sm text-slate-700">
            <span className="mb-1 block font-medium">Experience (years)</span>
            <input
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
              type="number"
              min="0"
              max="80"
              value={profileForm.experience_years}
              onChange={(event) => onProfileChange("experience_years", event.target.value)}
            />
          </label>
        </div>
        <label className="mt-3 block text-sm text-slate-700">
          <span className="mb-1 block font-medium">About / Profile information</span>
          <textarea
            className="min-h-32 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
            value={profileForm.about}
            onChange={(event) => onProfileChange("about", event.target.value)}
          />
        </label>
        <button
          className="mt-5 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
          disabled={savingProfile}
          type="button"
          onClick={onSaveProfile}
        >
          {savingProfile ? "Saving..." : "Save Profile"}
        </button>
      </section>

      <section className="space-y-4">
        <div className="rounded-3xl bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Password</p>
          <div className="mt-4 space-y-3">
            <label className="block text-sm text-slate-700">
              <span className="mb-1 block font-medium">Current password</span>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                type="password"
                value={passwordForm.current_password}
                onChange={(event) => onPasswordChange("current_password", event.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-700">
              <span className="mb-1 block font-medium">New password</span>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                type="password"
                value={passwordForm.new_password}
                onChange={(event) => onPasswordChange("new_password", event.target.value)}
              />
            </label>
            <label className="block text-sm text-slate-700">
              <span className="mb-1 block font-medium">Confirm password</span>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                type="password"
                value={passwordForm.confirm_password}
                onChange={(event) => onPasswordChange("confirm_password", event.target.value)}
              />
            </label>
          </div>
          <button
            className="mt-5 rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50 disabled:opacity-60"
            disabled={changingPassword}
            type="button"
            onClick={onChangePassword}
          >
            {changingPassword ? "Updating..." : "Update Password"}
          </button>
        </div>

        <NotificationPanel />
      </section>
    </div>
  );
}

export function DoctorHomePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { clearSession, user } = useAuth();
  const today = useMemo(() => toDateInputValue(new Date()), []);
  const availabilityWindow = useMemo(
    () =>
      Array.from({ length: 5 }, (_, index) => {
        const nextDate = new Date();
        nextDate.setDate(nextDate.getDate() + index);
        return toDateInputValue(nextDate);
      }),
    []
  );

  const [activeTab, setActiveTab] = useState<DoctorTab>("dashboard");
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const toastIdRef = useRef(0);
  const [dashboardAppointmentId, setDashboardAppointmentId] = useState<number | null>(null);
  const [historyDate, setHistoryDate] = useState(today);
  const [historyAppointmentId, setHistoryAppointmentId] = useState<number | null>(null);
  const [prescriptionAppointmentId, setPrescriptionAppointmentId] = useState<number | null>(null);
  const [availabilityDate, setAvailabilityDate] = useState(today);
  const [prescriptionForm, setPrescriptionForm] = useState<PrescriptionFormState>(emptyPrescriptionForm);
  const [profileForm, setProfileForm] = useState({
    full_name: "",
    phone: "",
    qualification: "",
    experience_years: "",
    about: ""
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });
  const [availabilityStartTime, setAvailabilityStartTime] = useState("");
  const [availabilityEndTime, setAvailabilityEndTime] = useState("");
  const [emergencySlotId, setEmergencySlotId] = useState("");
  const [emergencyReason, setEmergencyReason] = useState("");

  const dashboardQuery = useQuery({
    queryKey: ["dashboard", "doctor"],
    queryFn: getDoctorDashboard,
    refetchInterval: 30000
  });
  const slotsQuery = useQuery({ queryKey: ["doctor", "slots"], queryFn: listDoctorSlots });
  const availabilityQuery = useQuery({
    queryKey: ["doctor", "availabilities", availabilityDate],
    queryFn: () => listDoctorAvailabilities(availabilityDate)
  });
  const todaysAppointmentsQuery = useQuery({
    queryKey: ["doctor", "appointments", "today", today],
    queryFn: () => listDoctorAppointments({ available_date: today }),
    refetchInterval: 30000
  });
  const historyAppointmentsQuery = useQuery({
    queryKey: ["doctor", "appointments", "history", historyDate],
    queryFn: () => listDoctorAppointments({ available_date: historyDate })
  });
  const profileQuery = useQuery({
    queryKey: ["doctor", "profile"],
    queryFn: getDoctorProfile
  });

  const selectedAppointmentId =
    activeTab === "dashboard"
      ? dashboardAppointmentId
      : activeTab === "appointments"
        ? historyAppointmentId
        : activeTab === "prescriptions"
          ? prescriptionAppointmentId
          : null;

  const appointmentDetailQuery = useQuery({
    queryKey: ["doctor", "appointment-detail", selectedAppointmentId],
    queryFn: () => getDoctorAppointmentDetail(selectedAppointmentId as number),
    enabled: selectedAppointmentId !== null && ["dashboard", "appointments", "prescriptions"].includes(activeTab)
  });

  const createAvailabilityMutation = useMutation({
    mutationFn: createDoctorAvailability,
    onSuccess: () => {
      addToast("Slot enabled successfully.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "availabilities"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to enable slot.", "error")
  });

  const cancelAvailabilityMutation = useMutation({
    mutationFn: ({ availabilityId, reason }: { availabilityId: number; reason: string }) =>
      cancelDoctorAvailability(availabilityId, reason),
    onSuccess: () => {
      addToast("Slot marked unavailable.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "availabilities"] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to update slot.", "error")
  });

  const applyAvailabilityWindowMutation = useMutation({
    mutationFn: applyDoctorAvailabilityTimeWindow,
    onSuccess: (data: DoctorAvailabilityWindowResult) => {
      addToast(
        `Window applied. Enabled: ${data.enabled_count}, Disabled: ${data.disabled_count}, Booked kept: ${data.skipped_booked_count}.`
      );
      void queryClient.invalidateQueries({ queryKey: ["doctor", "availabilities"] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
    },
    onError: (error) =>
      addToast(error instanceof Error ? error.message : "Failed to apply availability window.", "error")
  });

  const emergencyCancelMutation = useMutation({
    mutationFn: emergencyCancelDoctorAvailabilities,
    onSuccess: (data) => {
      addToast(`Emergency cancellation completed. ${data.cancelled_appointment_ids.length} appointment(s) and ${data.cancelled_availability_ids.length} slot(s) affected.`
      );
      setEmergencyReason("");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "availabilities"] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard", "doctor"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to cancel remaining slots.", "error")
  });

  const completeAppointmentMutation = useMutation({
    mutationFn: completeDoctorAppointment,
    onSuccess: (_, appointmentId) => {
      addToast("Appointment marked completed.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointment-detail", appointmentId] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard", "doctor"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to complete appointment.", "error")
  });

  const cancelAppointmentMutation = useMutation({
    mutationFn: ({ appointmentId, reason }: { appointmentId: number; reason: string }) =>
      cancelDoctorAppointment(appointmentId, reason),
    onSuccess: (_, variables) => {
      addToast("Appointment cancelled.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointment-detail", variables.appointmentId] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard", "doctor"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to cancel appointment.", "error")
  });

  const savePrescriptionMutation = useMutation({
    mutationFn: ({ appointmentId, payload }: { appointmentId: number; payload: Parameters<typeof upsertDoctorPrescription>[1] }) =>
      upsertDoctorPrescription(appointmentId, payload),
    onSuccess: (_, variables) => {
      addToast("Prescription saved successfully.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointment-detail", variables.appointmentId] });
      void queryClient.invalidateQueries({ queryKey: ["doctor", "appointments"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to save prescription.", "error")
  });

  const updateProfileMutation = useMutation({
    mutationFn: updateDoctorProfile,
    onSuccess: () => {
      addToast("Profile updated successfully.");
      void queryClient.invalidateQueries({ queryKey: ["doctor", "profile"] });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to update profile.", "error")
  });

  const changePasswordMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      addToast("Password updated successfully.");
      setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
    },
    onError: (error) => addToast(error instanceof Error ? error.message : "Failed to update password.", "error")
  });

  const todaysAppointments = todaysAppointmentsQuery.data ?? [];
  const historyAppointments = historyAppointmentsQuery.data ?? [];
  const todaysPrescriptionAppointments = todaysAppointments.filter((appointment) =>
    ["BOOKED", "COMPLETED"].includes(appointment.appointment_status)
  );

  useEffect(() => {
    if (todaysAppointments.length === 0) {
      setDashboardAppointmentId(null);
      return;
    }
    if (!todaysAppointments.some((appointment) => appointment.appointment_id === dashboardAppointmentId)) {
      setDashboardAppointmentId(todaysAppointments[0].appointment_id);
    }
  }, [dashboardAppointmentId, todaysAppointments]);

  useEffect(() => {
    if (historyAppointments.length === 0) {
      setHistoryAppointmentId(null);
      return;
    }
    if (!historyAppointments.some((appointment) => appointment.appointment_id === historyAppointmentId)) {
      setHistoryAppointmentId(historyAppointments[0].appointment_id);
    }
  }, [historyAppointmentId, historyAppointments]);

  useEffect(() => {
    if (todaysPrescriptionAppointments.length === 0) {
      setPrescriptionAppointmentId(null);
      return;
    }
    if (!todaysPrescriptionAppointments.some((appointment) => appointment.appointment_id === prescriptionAppointmentId)) {
      setPrescriptionAppointmentId(todaysPrescriptionAppointments[0].appointment_id);
    }
  }, [prescriptionAppointmentId, todaysPrescriptionAppointments]);

  useEffect(() => {
    setPrescriptionForm(mapPrescriptionToForm(appointmentDetailQuery.data?.current_prescription));
  }, [appointmentDetailQuery.data]);

  useEffect(() => {
    if (!profileQuery.data) return;
    setProfileForm({
      full_name: profileQuery.data.full_name,
      phone: profileQuery.data.phone ?? "",
      qualification: profileQuery.data.qualification ?? "",
      experience_years: profileQuery.data.experience_years !== null ? String(profileQuery.data.experience_years) : "",
      about: profileQuery.data.about ?? ""
    });
  }, [profileQuery.data]);

  useEffect(() => {
    const slots = slotsQuery.data ?? [];
    if (slots.length === 0) {
      setAvailabilityStartTime("");
      setAvailabilityEndTime("");
      return;
    }
    setAvailabilityStartTime(toTimeInputValue(slots[0].slot_start_time));
    setAvailabilityEndTime(toTimeInputValue(slots[slots.length - 1].slot_end_time));
  }, [availabilityDate, slotsQuery.data]);

  useEffect(() => {
    const activeRows = availabilityQuery.data ?? [];
    const activeRowsForEmergency = activeRows.filter((row) =>
      row.slot_status === "AVAILABLE" || row.slot_status === "BOOKED"
    );
    if (activeRowsForEmergency.length === 0) {
      setEmergencySlotId("");
      return;
    }
    if (!activeRowsForEmergency.some((row) => String(row.slot_id) === emergencySlotId)) {
      setEmergencySlotId(String(activeRowsForEmergency[0].slot_id));
    }
  }, [availabilityQuery.data, emergencySlotId]);

  const availabilityBySlotId = useMemo(() => {
    const map = new Map<number, DoctorAvailability>();
    for (const item of availabilityQuery.data ?? []) {
      map.set(item.slot_id, item);
    }
    return map;
  }, [availabilityQuery.data]);

  const addToast = (text: string, kind: "success" | "error" = "success") => {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { id, text, kind }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000);
  };
  const dismissToast = (id: number) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const onLogout = async () => {
    try {
      await logout();
    } finally {
      clearSession();
      navigate("/management");
    }
  };

  const handleCancelAppointment = (appointmentId: number) => {
    const reason = window.prompt("Enter cancellation reason");
    if (!reason || !reason.trim()) return;
    cancelAppointmentMutation.mutate({ appointmentId, reason: reason.trim() });
  };

  const handleDisableAvailability = (availabilityId: number) => {
    const reason = window.prompt("Enter unavailability reason");
    if (!reason || !reason.trim()) return;
    cancelAvailabilityMutation.mutate({ availabilityId, reason: reason.trim() });
  };

  const handleApplyAvailabilityWindow = () => {
    if (!availabilityStartTime || !availabilityEndTime) {
      addToast("Choose both start and end times.", "error");
      return;
    }
    if (availabilityStartTime >= availabilityEndTime) {
      addToast("Start time must be earlier than end time.", "error");
      return;
    }
    applyAvailabilityWindowMutation.mutate({
      available_date: availabilityDate,
      start_time: toApiTimeValue(availabilityStartTime),
      end_time: toApiTimeValue(availabilityEndTime)
    });
  };

  const handleSavePrescription = () => {
    if (!appointmentDetailQuery.data) return;
    savePrescriptionMutation.mutate({
      appointmentId: appointmentDetailQuery.data.appointment_id,
      payload: {
        diagnosis: formValueOrUndefined(prescriptionForm.diagnosis),
        medicines: formValueOrUndefined(prescriptionForm.medicines),
        dosage: formValueOrUndefined(prescriptionForm.dosage),
        frequency: formValueOrUndefined(prescriptionForm.frequency),
        duration: formValueOrUndefined(prescriptionForm.duration),
        doctor_advice: formValueOrUndefined(prescriptionForm.doctor_advice),
        internal_notes: formValueOrUndefined(prescriptionForm.internal_notes),
        follow_up_date: formValueOrUndefined(prescriptionForm.follow_up_date)
      }
    });
  };

  const handleSaveProfile = () => {
    if (profileForm.full_name.trim().length < 2) {
      addToast("Doctor name must contain at least 2 characters.", "error");
      return;
    }
    const normalizedExperience = profileForm.experience_years.trim();
    const experienceYears =
      normalizedExperience.length === 0 ? undefined : Number.parseInt(normalizedExperience, 10);
    if (normalizedExperience.length > 0 && Number.isNaN(experienceYears)) {
      addToast("Experience must be a valid number.", "error");
      return;
    }
    updateProfileMutation.mutate({
      full_name: profileForm.full_name.trim(),
      phone: formValueOrUndefined(profileForm.phone),
      qualification: formValueOrUndefined(profileForm.qualification),
      experience_years: experienceYears,
      about: formValueOrUndefined(profileForm.about)
    });
  };

  const handleChangePassword = () => {
    if (passwordForm.new_password.length < 8) {
      addToast("New password must be at least 8 characters.", "error");
      return;
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      addToast("New password and confirmation do not match.", "error");
      return;
    }
    changePasswordMutation.mutate({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    });
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] md:grid-cols-[18rem_1fr]">
        <aside className="flex flex-col gap-5 bg-gradient-to-b from-slate-950 via-slate-900 to-blue-950 px-5 py-6">
          {/* Clinic brand */}
          <div className="flex items-center gap-3 rounded-2xl bg-white/10 px-4 py-3 text-white">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-500/30">
              <svg className="h-4 w-4 text-blue-300" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <p className="text-xs font-semibold tracking-[0.2em] text-blue-300">CAREPOINT</p>
              <p className="text-sm font-semibold text-white">Doctor Workspace</p>
            </div>
          </div>

          <nav className="space-y-1">
            <SidebarButton active={activeTab === "dashboard"} tab="dashboard" label="Dashboard" badge={dashboardQuery.data?.pending_appointments} onClick={() => setActiveTab("dashboard")} />
            <SidebarButton active={activeTab === "availability"} tab="availability" label="Availability" onClick={() => setActiveTab("availability")} />
            <SidebarButton active={activeTab === "appointments"} tab="appointments" label="Appointment History" onClick={() => setActiveTab("appointments")} />
            <SidebarButton active={activeTab === "prescriptions"} tab="prescriptions" label="Prescriptions" onClick={() => setActiveTab("prescriptions")} />
            <SidebarButton active={activeTab === "profile"} tab="profile" label="Profile" onClick={() => setActiveTab("profile")} />
          </nav>

          <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-xs font-bold uppercase text-white">
                {(user?.full_name ?? "D").trim().split(/\s+/).slice(0, 2).map((p) => p[0]).join("").toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="truncate font-semibold text-white">{user?.full_name ?? "Doctor"}</p>
                <p className="truncate text-xs text-slate-400">{user?.email ?? ""}</p>
              </div>
            </div>
            <button
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-white/15 px-3 py-2 text-sm font-medium text-white hover:bg-white/10"
              type="button"
              onClick={onLogout}
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </aside>

        <main className="p-4 md:p-6">
          <header className="rounded-3xl bg-white px-5 py-5 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <span className="inline-flex rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold tracking-[0.16em] text-white">
                    DOCTOR PANEL
                  </span>
                  <span className="hidden text-sm text-slate-400 lg:block">{new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</span>
                </div>
                <h2 className="mt-3 text-2xl font-semibold text-slate-900">
                  {activeTab === "dashboard"
                    ? "Today's Appointments"
                    : activeTab === "availability"
                      ? "Availability Planner"
                      : activeTab === "appointments"
                        ? "Appointment History"
                        : activeTab === "prescriptions"
                          ? "Prescription Management"
                          : "Doctor Profile"}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {activeTab === "dashboard"
                    ? "Select a patient to open the consultation workspace."
                    : activeTab === "availability"
                      ? "Manage the next five days of slots; use emergency cancel when needed."
                      : activeTab === "appointments"
                        ? "Browse older consultations and view their prescription records."
                        : activeTab === "prescriptions"
                          ? "Review and edit today's prescription records."
                          : "Update your professional information and change your password."}
                </p>
              </div>
            </div>
          </header>

          <div className="mt-4">
            {activeTab === "dashboard" ? (
              <div className="grid gap-4 xl:grid-cols-[0.95fr_1.55fr]">
                <div className="space-y-4">
                  <section className="rounded-3xl bg-white p-5 shadow-sm">
                    <div className="grid gap-3 sm:grid-cols-3">
                      <div className="rounded-2xl bg-blue-50 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-blue-600">Today</p>
                        <p className="mt-2 text-3xl font-bold text-blue-700">{dashboardQuery.data?.todays_appointments ?? "—"}</p>
                        <p className="mt-1 text-xs text-blue-500/70">Appointments</p>
                      </div>
                      <div className="rounded-2xl bg-emerald-50 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-600">Done</p>
                        <p className="mt-2 text-3xl font-bold text-emerald-700">{dashboardQuery.data?.completed_appointments ?? "—"}</p>
                        <p className="mt-1 text-xs text-emerald-500/70">Completed</p>
                      </div>
                      <div className="rounded-2xl bg-amber-50 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-600">Left</p>
                        <p className="mt-2 text-3xl font-bold text-amber-700">{dashboardQuery.data?.pending_appointments ?? "—"}</p>
                        <p className="mt-1 text-xs text-amber-500/70">Pending</p>
                      </div>
                    </div>
                  </section>

                  <section className="rounded-3xl bg-white p-5 shadow-sm">
                    <div className="mb-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Consultation queue</p>
                      <h3 className="mt-1 text-lg font-semibold text-slate-900">Today's appointments</h3>
                    </div>
                    {todaysAppointmentsQuery.isLoading ? (
                      <div className="space-y-2.5">
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                      </div>
                    ) : (
                      <AppointmentList
                        appointments={todaysAppointments}
                        selectedAppointmentId={dashboardAppointmentId}
                        onSelect={setDashboardAppointmentId}
                      />
                    )}
                  </section>
                </div>

                <div>
                  {appointmentDetailQuery.isLoading ? (
                    <section className="rounded-3xl bg-white p-5 shadow-sm">
                      <div className="animate-pulse space-y-4">
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-full bg-slate-200" />
                          <div className="space-y-2">
                            <div className="h-4 w-36 rounded bg-slate-200" />
                            <div className="h-3 w-24 rounded bg-slate-200" />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          {[...Array(6)].map((_, i) => <div key={i} className="h-14 rounded-xl bg-slate-100" />)}
                        </div>
                      </div>
                    </section>
                  ) : appointmentDetailQuery.data ? (
                    <ConsultationWorkspace
                      detail={appointmentDetailQuery.data}
                      form={prescriptionForm}
                      setForm={setPrescriptionForm}
                      onSave={handleSavePrescription}
                      onComplete={(appointmentId) => completeAppointmentMutation.mutate(appointmentId)}
                      onCancelAppointment={handleCancelAppointment}
                      savePending={savePrescriptionMutation.isPending}
                    />
                  ) : (
                    <EmptyState text="Select an appointment from the queue to open the consultation workspace." />
                  )}
                </div>
              </div>
            ) : null}

            {activeTab === "availability" ? (
              <div className="space-y-4">
                {/* Day picker */}
                <section className="rounded-3xl bg-white p-5 shadow-sm">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Select day</p>
                  <div className="flex flex-wrap gap-2">
                    {availabilityWindow.map((windowDate, index) => (
                      <button
                        key={windowDate}
                        className={`rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                          availabilityDate === windowDate
                            ? "bg-blue-600 text-white shadow-sm"
                            : "border border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:text-blue-700"
                        }`}
                        type="button"
                        onClick={() => setAvailabilityDate(windowDate)}
                      >
                        <span className="font-semibold">{index === 0 ? "Today" : index === 1 ? "Tomorrow" : `Day ${index + 1}`}</span>
                        <span className={`ml-1.5 text-xs ${availabilityDate === windowDate ? "text-blue-200" : "text-slate-400"}`}>{formatShortDate(windowDate)}</span>
                      </button>
                    ))}
                  </div>
                </section>

                <section className="rounded-3xl bg-white p-5 shadow-sm">
                  <div className="mb-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Daily time window</p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-900">Enable slots by time range</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Choose start and end time for {formatDateLabel(availabilityDate)}. Slots inside this range are enabled, others are disabled.
                    </p>
                  </div>
                  <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-end">
                    <label className="block text-sm text-slate-700">
                      <span className="mb-1 block font-medium">Start time</span>
                      <input
                        className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                        type="time"
                        value={availabilityStartTime}
                        onChange={(event) => setAvailabilityStartTime(event.target.value)}
                      />
                    </label>
                    <label className="block text-sm text-slate-700">
                      <span className="mb-1 block font-medium">End time</span>
                      <input
                        className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                        type="time"
                        value={availabilityEndTime}
                        onChange={(event) => setAvailabilityEndTime(event.target.value)}
                      />
                    </label>
                    <button
                      className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                      type="button"
                      disabled={
                        applyAvailabilityWindowMutation.isPending ||
                        !availabilityStartTime ||
                        !availabilityEndTime
                      }
                      onClick={handleApplyAvailabilityWindow}
                    >
                      {applyAvailabilityWindowMutation.isPending ? "Applying..." : "Apply Window"}
                    </button>
                  </div>
                </section>

                <div className="grid gap-4 xl:grid-cols-[1.35fr_0.95fr]">
                  <section className="rounded-3xl bg-white p-5 shadow-sm">
                    <div className="mb-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Clinic slots</p>
                      <h3 className="mt-1 text-lg font-semibold text-slate-900">{formatDateLabel(availabilityDate)}</h3>
                    </div>
                    {slotsQuery.isLoading ? (
                      <div className="space-y-3">
                        {[...Array(5)].map((_, i) => <div key={i} className="animate-pulse h-16 rounded-2xl bg-slate-100" />)}
                      </div>
                    ) : (
                      <div className="space-y-2.5">
                        {(slotsQuery.data ?? []).map((slot) => {
                          const availability = availabilityBySlotId.get(slot.slot_id);
                          const isEnabled = availability
                            ? availability.slot_status === "AVAILABLE" || availability.slot_status === "BOOKED"
                            : false;
                          return (
                            <article key={slot.slot_id} className={`flex flex-col gap-3 rounded-2xl border p-4 md:flex-row md:items-center md:justify-between ${isEnabled ? "border-emerald-200 bg-emerald-50/40" : "border-slate-200 bg-white"}`}>
                              <div>
                                <div className="flex items-center gap-2">
                                  <div className={`h-2 w-2 rounded-full ${isEnabled ? "bg-emerald-500" : "bg-slate-300"}`} />
                                  <p className="font-semibold text-slate-900">
                                    {formatTimeLabel(slot.slot_start_time)} – {formatTimeLabel(slot.slot_end_time)}
                                  </p>
                                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${statusClasses(availability?.slot_status ?? "DISABLED")}`}>
                                    {availability?.slot_status ?? "DISABLED"}
                                  </span>
                                </div>
                                {availability?.cancellation_reason ? (
                                  <p className="mt-1 ml-4 text-xs text-rose-600">Reason: {availability.cancellation_reason}</p>
                                ) : null}
                              </div>
                              <div className="flex items-center gap-2">
                                {isEnabled && availability ? (
                                  <button
                                    className="flex items-center gap-1.5 rounded-xl border border-rose-200 bg-white px-3 py-2 text-sm font-medium text-rose-700 hover:bg-rose-50"
                                    type="button"
                                    onClick={() => handleDisableAvailability(availability.availability_id)}
                                  >
                                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                                    Disable
                                  </button>
                                ) : (
                                  <button
                                    className="flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-white px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
                                    type="button"
                                    onClick={() => createAvailabilityMutation.mutate({ available_date: availabilityDate, slot_id: slot.slot_id })}
                                  >
                                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                    Enable
                                  </button>
                                )}
                              </div>
                            </article>
                          );
                        })}
                      </div>
                    )}
                  </section>

                  <section className="rounded-3xl bg-white p-5 shadow-sm">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-100">
                        <svg className="h-4 w-4 text-rose-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      </div>
                      <p className="font-semibold text-slate-900">Emergency Cancel</p>
                    </div>
                    <p className="mt-2 text-sm text-slate-500">
                      Cancel all remaining appointments from a given slot onward. Affected slots stay closed for new bookings.
                    </p>

                    <label className="mt-4 block text-sm text-slate-700">
                      <span className="mb-1 block font-medium">Date</span>
                      <input className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-slate-600" readOnly value={availabilityDate} />
                    </label>
                    <label className="mt-3 block text-sm text-slate-700">
                      <span className="mb-1 block font-medium">Cancel from slot</span>
                      <select
                        className="w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                        value={emergencySlotId}
                        onChange={(event) => setEmergencySlotId(event.target.value)}
                      >
                        {(availabilityQuery.data ?? [])
                          .filter((item) => item.slot_status === "AVAILABLE" || item.slot_status === "BOOKED")
                          .map((item) => (
                          <option key={item.availability_id} value={item.slot_id}>
                            {formatTimeLabel(item.slot_start_time)} – {formatTimeLabel(item.slot_end_time)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="mt-3 block text-sm text-slate-700">
                      <span className="mb-1 block font-medium">Reason</span>
                      <textarea
                        className="min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                        value={emergencyReason}
                        onChange={(event) => setEmergencyReason(event.target.value)}
                      />
                    </label>
                    <button
                      className="mt-4 rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
                      disabled={emergencyCancelMutation.isPending || !emergencySlotId || emergencyReason.trim().length === 0}
                      type="button"
                      onClick={() =>
                        emergencyCancelMutation.mutate({
                          available_date: availabilityDate,
                          from_slot_id: Number(emergencySlotId),
                          cancellation_reason: emergencyReason.trim()
                        })
                      }
                    >
                      {emergencyCancelMutation.isPending ? "Cancelling..." : "Cancel Remaining Slots"}
                    </button>
                  </section>
                </div>
              </div>
            ) : null}

            {activeTab === "appointments" ? (
              <div className="grid gap-4 xl:grid-cols-[0.95fr_1.55fr]">
                <section className="rounded-3xl bg-white p-5 shadow-sm">
                  <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Calendar</p>
                      <h3 className="mt-1 text-lg font-semibold text-slate-900">Appointment history</h3>
                    </div>
                    <input
                      className="rounded-xl border border-slate-200 px-3 py-2.5 outline-none ring-blue-500 focus:ring"
                      type="date"
                      value={historyDate}
                      onChange={(event) => setHistoryDate(event.target.value)}
                    />
                  </div>
                  {historyAppointmentsQuery.isLoading ? (
                    <div className="space-y-2.5">
                      <SkeletonCard />
                      <SkeletonCard />
                    </div>
                  ) : (
                    <AppointmentList
                      appointments={historyAppointments}
                      selectedAppointmentId={historyAppointmentId}
                      onSelect={setHistoryAppointmentId}
                    />
                  )}
                </section>

                <div>
                  {appointmentDetailQuery.isLoading ? (
                    <section className="animate-pulse rounded-3xl bg-white p-5 shadow-sm">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-full bg-slate-200" />
                        <div className="space-y-2"><div className="h-4 w-32 rounded bg-slate-200" /><div className="h-3 w-20 rounded bg-slate-200" /></div>
                      </div>
                      <div className="mt-4 grid grid-cols-2 gap-3">{[...Array(4)].map((_, i) => <div key={i} className="h-14 rounded-xl bg-slate-100" />)}</div>
                    </section>
                  ) : appointmentDetailQuery.data ? (
                    <ConsultationWorkspace
                      detail={appointmentDetailQuery.data}
                      form={prescriptionForm}
                      setForm={setPrescriptionForm}
                      onSave={handleSavePrescription}
                      onComplete={(appointmentId) => completeAppointmentMutation.mutate(appointmentId)}
                      onCancelAppointment={handleCancelAppointment}
                      savePending={savePrescriptionMutation.isPending}
                    />
                  ) : (
                    <EmptyState text="Select a dated appointment to review the consultation history." />
                  )}
                </div>
              </div>
            ) : null}

            {activeTab === "prescriptions" ? (
              <div className="grid gap-4 xl:grid-cols-[0.95fr_1.55fr]">
                <section className="rounded-3xl bg-white p-5 shadow-sm">
                  <div className="mb-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Today's patients</p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-900">Prescription queue</h3>
                  </div>
                  {todaysAppointmentsQuery.isLoading ? (
                    <div className="space-y-2.5">
                      <SkeletonCard />
                      <SkeletonCard />
                    </div>
                  ) : (
                    <AppointmentList
                      appointments={todaysPrescriptionAppointments}
                      selectedAppointmentId={prescriptionAppointmentId}
                      onSelect={setPrescriptionAppointmentId}
                    />
                  )}
                </section>

                <div>
                  {appointmentDetailQuery.isLoading ? (
                    <section className="animate-pulse rounded-3xl bg-white p-5 shadow-sm">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-full bg-slate-200" />
                        <div className="space-y-2"><div className="h-4 w-32 rounded bg-slate-200" /><div className="h-3 w-20 rounded bg-slate-200" /></div>
                      </div>
                      <div className="mt-4 space-y-2">{[...Array(6)].map((_, i) => <div key={i} className="h-20 rounded-xl bg-slate-100" />)}</div>
                    </section>
                  ) : appointmentDetailQuery.data ? (
                    <ConsultationWorkspace
                      detail={appointmentDetailQuery.data}
                      form={prescriptionForm}
                      setForm={setPrescriptionForm}
                      onSave={handleSavePrescription}
                      onComplete={(appointmentId) => completeAppointmentMutation.mutate(appointmentId)}
                      onCancelAppointment={handleCancelAppointment}
                      savePending={savePrescriptionMutation.isPending}
                    />
                  ) : (
                    <EmptyState text="Select one of today's patients to review or update the prescription." />
                  )}
                </div>
              </div>
            ) : null}

            {activeTab === "profile" ? (
              profileQuery.isLoading || !profileQuery.data ? (
                <section className="animate-pulse rounded-3xl bg-white p-5 shadow-sm">
                  <div className="flex items-center gap-4">
                    <div className="h-16 w-16 rounded-full bg-slate-200" />
                    <div className="space-y-2"><div className="h-5 w-40 rounded bg-slate-200" /><div className="h-3 w-32 rounded bg-slate-200" /></div>
                  </div>
                  <div className="mt-6 grid grid-cols-2 gap-3">{[...Array(6)].map((_, i) => <div key={i} className="h-12 rounded-xl bg-slate-100" />)}</div>
                </section>
              ) : (
                <ProfileEditor
                  profile={profileQuery.data}
                  profileForm={profileForm}
                  onProfileChange={(field, value) => setProfileForm((prev) => ({ ...prev, [field]: value }))}
                  onSaveProfile={handleSaveProfile}
                  savingProfile={updateProfileMutation.isPending}
                  passwordForm={passwordForm}
                  onPasswordChange={(field, value) => setPasswordForm((prev) => ({ ...prev, [field]: value }))}
                  onChangePassword={handleChangePassword}
                  changingPassword={changePasswordMutation.isPending}
                />
              )
            ) : null}
          </div>
        </main>
      </div>
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

function formValueOrUndefined(value: string): string | undefined {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}
