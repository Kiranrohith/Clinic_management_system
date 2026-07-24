import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { logout } from "../../api/auth";
import { getFrontdeskDashboard } from "../../api/dashboard";
import {
  bookFrontdeskAppointment,
  cancelFrontdeskAppointment,
  createWalkinToken,
  getFrontdeskProfile,
  listAppointmentsByDate,
  listFrontdeskAvailabilities,
  listFrontdeskContactQueries,
  listFrontdeskDoctors,
  listTodayAppointments,
  listTodayWalkinTokens,
  listWalkinHistory,
  searchFrontdeskPatients,
  updateFrontdeskContactQuery,
  updateFrontdeskProfile,
  updateWalkinTokenStatus,
  upsertPatient,
  type ContactQueryStatus,
  type FrontdeskAppointmentListItem,
  type FrontdeskPatient,
  type FrontdeskPatientSearchItem,
  type FrontdeskWalkInListItem
} from "../../api/frontdesk";
import { getPublicClinicSettings } from "../../api/public";
import { NotificationPanel } from "../../components/NotificationPanel";
import { useAuth } from "../../hooks/useAuth";

type FrontdeskTab = "dashboard" | "appointments" | "walkins" | "contacts" | "profile";
type WalkinStatus = "WAITING" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
const GENERAL_MEDICINE_SPECIALIZATION = "general medicine";

type PatientDraft = {
  full_name: string;
  phone: string;
  gender: "" | "MALE" | "FEMALE" | "OTHER";
  dob: string;
  blood_group: string;
  address: string;
  emergency_contact: string;
};

function toDateInputValue(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatTimeLabel(value: string): string {
  const [hours, minutes] = value.split(":");
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
}

function formatDateLabel(value: string): string {
  return new Date(value).toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" });
}

function statusClasses(status: string): string {
  if (status === "BOOKED" || status === "CONFIRMED") return "bg-blue-50 text-blue-700";
  if (status === "COMPLETED") return "bg-emerald-50 text-emerald-700";
  if (status === "WAITING" || status === "NOTIFIED") return "bg-amber-50 text-amber-700";
  if (status.includes("CANCELLED")) return "bg-rose-50 text-rose-700";
  if (status === "IN_PROGRESS" || status === "ONGOING") return "bg-violet-50 text-violet-700";
  return "bg-slate-100 text-slate-700";
}

function emptyPatientDraft(): PatientDraft {
  return {
    full_name: "",
    phone: "",
    gender: "",
    dob: "",
    blood_group: "",
    address: "",
    emergency_contact: ""
  };
}

function SidebarButton({
  active,
  label,
  onClick
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className={`w-full rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
        active ? "bg-blue-600 text-white shadow-sm" : "text-slate-200 hover:bg-white/10"
      }`}
      type="button"
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function EmptyState({ text }: { text: string }) {
  return <p className="rounded-xl border border-dashed border-slate-300 px-4 py-8 text-center text-sm text-slate-500">{text}</p>;
}

function AppointmentsTable({
  rows,
  onCancel,
  onRebook
}: {
  rows: FrontdeskAppointmentListItem[];
  onCancel?: (appointmentId: number) => void;
  onRebook?: () => void;
}) {
  if (rows.length === 0) {
    return <EmptyState text="No appointments found for the selected filter." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b text-left text-slate-500">
            <th className="px-3 py-3 font-medium">Time</th>
            <th className="px-3 py-3 font-medium">Patient</th>
            <th className="px-3 py-3 font-medium">Doctor</th>
            <th className="px-3 py-3 font-medium">Status</th>
            <th className="px-3 py-3 font-medium">Source</th>
            {(onCancel || onRebook) ? <th className="px-3 py-3 font-medium">Action</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.appointment_id} className="border-b last:border-b-0">
              <td className="px-3 py-3 font-medium text-slate-900">{formatTimeLabel(item.slot_start_time)}</td>
              <td className="px-3 py-3">
                <p className="font-medium text-slate-900">{item.patient_name}</p>
                <p className="text-xs text-slate-500">{item.patient_phone}</p>
              </td>
              <td className="px-3 py-3 text-slate-700">{item.doctor_name}</td>
              <td className="px-3 py-3">
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClasses(item.appointment_status)}`}>
                  {item.appointment_status}
                </span>
              </td>
              <td className="px-3 py-3 text-slate-600">{item.booking_source ?? "-"}</td>
              {(onCancel || onRebook) ? (
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-2">
                    {onCancel && item.appointment_status === "BOOKED" ? (
                      <button
                        className="rounded-md border border-rose-200 px-3 py-1 text-xs font-medium text-rose-700 hover:bg-rose-50"
                        type="button"
                        onClick={() => onCancel(item.appointment_id)}
                      >
                        Cancel
                      </button>
                    ) : null}
                    {onRebook ? (
                      <button
                        className="rounded-md border border-blue-200 px-3 py-1 text-xs font-medium text-blue-700 hover:bg-blue-50"
                        type="button"
                        onClick={onRebook}
                      >
                        Rebook
                      </button>
                    ) : null}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WalkinTable({
  rows,
  onStatusChange
}: {
  rows: FrontdeskWalkInListItem[];
  onStatusChange?: (tokenId: number, status: WalkinStatus) => void;
}) {
  if (rows.length === 0) {
    return <EmptyState text="No walk-in tokens found for the selected filter." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b text-left text-slate-500">
            <th className="px-3 py-3 font-medium">Token</th>
            <th className="px-3 py-3 font-medium">Patient</th>
            <th className="px-3 py-3 font-medium">Doctor</th>
            <th className="px-3 py-3 font-medium">Status</th>
            {onStatusChange ? <th className="px-3 py-3 font-medium">Action</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.token_id} className="border-b last:border-b-0">
              <td className="px-3 py-3 font-medium text-slate-900">T-{String(item.token_number).padStart(2, "0")}</td>
              <td className="px-3 py-3">
                <p className="font-medium text-slate-900">{item.patient_name}</p>
                <p className="text-xs text-slate-500">{item.patient_phone}</p>
              </td>
              <td className="px-3 py-3 text-slate-700">{item.doctor_name}</td>
              <td className="px-3 py-3">
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClasses(item.status)}`}>{item.status}</span>
              </td>
              {onStatusChange ? (
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-2">
                    {item.status === "WAITING" ? (
                      <button
                        className="rounded-md border border-violet-200 px-3 py-1 text-xs font-medium text-violet-700 hover:bg-violet-50"
                        type="button"
                        onClick={() => onStatusChange(item.token_id, "IN_PROGRESS")}
                      >
                        Start
                      </button>
                    ) : null}
                    {item.status !== "COMPLETED" && item.status !== "CANCELLED" ? (
                      <button
                        className="rounded-md border border-emerald-200 px-3 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-50"
                        type="button"
                        onClick={() => onStatusChange(item.token_id, "COMPLETED")}
                      >
                        Complete
                      </button>
                    ) : null}
                    {item.status !== "COMPLETED" && item.status !== "CANCELLED" ? (
                      <button
                        className="rounded-md border border-rose-200 px-3 py-1 text-xs font-medium text-rose-700 hover:bg-rose-50"
                        type="button"
                        onClick={() => onStatusChange(item.token_id, "CANCELLED")}
                      >
                        Cancel
                      </button>
                    ) : null}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PatientSection({
  search,
  onSearchChange,
  searchResults,
  searchLoading,
  selectedPatient,
  onSelectPatient,
  showForm,
  onToggleForm,
  form,
  onFormChange,
  onSave,
  savePending
}: {
  search: string;
  onSearchChange: (value: string) => void;
  searchResults: FrontdeskPatientSearchItem[];
  searchLoading: boolean;
  selectedPatient: FrontdeskPatientSearchItem | FrontdeskPatient | null;
  onSelectPatient: (patient: FrontdeskPatientSearchItem) => void;
  showForm: boolean;
  onToggleForm: () => void;
  form: PatientDraft;
  onFormChange: (next: PatientDraft) => void;
  onSave: () => void;
  savePending: boolean;
}) {
  return (
    <section className="rounded-3xl border border-slate-200">
      <div className="border-b px-5 py-4">
        <h4 className="text-2xl font-semibold text-slate-900">Patient</h4>
      </div>
      <div className="px-5 py-5">
        <input
          className="w-full rounded-2xl border border-slate-200 px-4 py-3"
          placeholder="Search by patient name or phone"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
        />
        {searchLoading ? <p className="mt-3 text-sm text-slate-500">Searching patients...</p> : null}
        {searchResults.length > 0 ? (
          <div className="mt-3 space-y-2">
            {searchResults.map((patient) => (
              <button
                key={patient.patient_id}
                className="flex w-full items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 text-left hover:bg-slate-50"
                type="button"
                onClick={() => onSelectPatient(patient)}
              >
                <span>
                  <span className="block font-medium text-slate-900">{patient.full_name}</span>
                  <span className="text-xs text-slate-500">{patient.phone}</span>
                </span>
                <span className="text-sm font-medium text-blue-600">Select</span>
              </button>
            ))}
          </div>
        ) : null}
        <button
          className="mt-4 w-full rounded-2xl border border-dashed border-slate-300 px-4 py-3 text-base font-semibold text-emerald-700 hover:bg-emerald-50"
          type="button"
          onClick={onToggleForm}
        >
          {showForm ? "Hide New Patient Form" : "Add New Patient"}
        </button>

        {selectedPatient ? (
          <div className="mt-4 rounded-2xl bg-emerald-50 p-4">
            <p className="font-semibold text-emerald-900">{selectedPatient.full_name}</p>
            <p className="mt-1 text-sm text-emerald-700">{selectedPatient.phone}</p>
          </div>
        ) : null}

        {showForm ? (
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            <input
              className="rounded-2xl border border-slate-200 px-4 py-3"
              placeholder="Full name"
              value={form.full_name}
              onChange={(event) => onFormChange({ ...form, full_name: event.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 px-4 py-3"
              placeholder="Phone"
              value={form.phone}
              onChange={(event) => onFormChange({ ...form, phone: event.target.value })}
            />
            <select
              className="rounded-2xl border border-slate-200 px-4 py-3"
              value={form.gender}
              onChange={(event) => onFormChange({ ...form, gender: event.target.value as PatientDraft["gender"] })}
            >
              <option value="">Gender</option>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
            <input
              className="rounded-2xl border border-slate-200 px-4 py-3"
              type="date"
              value={form.dob}
              onChange={(event) => onFormChange({ ...form, dob: event.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 px-4 py-3"
              placeholder="Blood group"
              value={form.blood_group}
              onChange={(event) => onFormChange({ ...form, blood_group: event.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 px-4 py-3"
              placeholder="Emergency contact"
              value={form.emergency_contact}
              onChange={(event) => onFormChange({ ...form, emergency_contact: event.target.value })}
            />
            <textarea
              className="rounded-2xl border border-slate-200 px-4 py-3 lg:col-span-2"
              placeholder="Address"
              value={form.address}
              onChange={(event) => onFormChange({ ...form, address: event.target.value })}
            />
            <div className="lg:col-span-2">
              <button
                className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
                type="button"
                disabled={savePending}
                onClick={onSave}
              >
                {savePending ? "Saving..." : "Save Patient"}
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

export function FrontdeskHomePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { clearSession, user } = useAuth();

  const today = useMemo(() => toDateInputValue(new Date()), []);
  const tomorrow = useMemo(() => {
    const next = new Date();
    next.setDate(next.getDate() + 1);
    return toDateInputValue(next);
  }, []);

  const [activeTab, setActiveTab] = useState<FrontdeskTab>("dashboard");
  const [message, setMessage] = useState<string | null>(null);
  const [dashboardDoctorFilter, setDashboardDoctorFilter] = useState("ALL");
  const [appointmentDoctorFilter, setAppointmentDoctorFilter] = useState("ALL");
  const [walkinDoctorFilter, setWalkinDoctorFilter] = useState("ALL");
  const [appointmentDate, setAppointmentDate] = useState(today);
  const [walkinDate, setWalkinDate] = useState(today);
  const [appointmentDrawerOpen, setAppointmentDrawerOpen] = useState(false);
  const [walkinDrawerOpen, setWalkinDrawerOpen] = useState(false);
  const [appointmentDoctorUserId, setAppointmentDoctorUserId] = useState("");
  const [appointmentDrawerDate, setAppointmentDrawerDate] = useState(today);
  const [selectedAvailabilityId, setSelectedAvailabilityId] = useState<number | null>(null);
  const [appointmentPatientSearch, setAppointmentPatientSearch] = useState("");
  const [selectedAppointmentPatient, setSelectedAppointmentPatient] = useState<FrontdeskPatientSearchItem | FrontdeskPatient | null>(null);
  const [showAppointmentPatientForm, setShowAppointmentPatientForm] = useState(false);
  const [appointmentPatientForm, setAppointmentPatientForm] = useState<PatientDraft>(emptyPatientDraft());
  const [walkinDoctorUserId, setWalkinDoctorUserId] = useState("");
  const [walkinTokenDate, setWalkinTokenDate] = useState(today);
  const [walkinPatientSearch, setWalkinPatientSearch] = useState("");
  const [selectedWalkinPatient, setSelectedWalkinPatient] = useState<FrontdeskPatientSearchItem | FrontdeskPatient | null>(null);
  const [showWalkinPatientForm, setShowWalkinPatientForm] = useState(false);
  const [walkinPatientForm, setWalkinPatientForm] = useState<PatientDraft>(emptyPatientDraft());
  const [walkinNotes, setWalkinNotes] = useState("");
  const [profileForm, setProfileForm] = useState({ full_name: "", phone: "" });
  const [contactStatusFilter, setContactStatusFilter] = useState<"ALL" | ContactQueryStatus>("NEW");
  const [contactDrafts, setContactDrafts] = useState<Record<number, { status: ContactQueryStatus; notes: string }>>({});
  const [appointmentSpecFilter, setAppointmentSpecFilter] = useState("");

  const dashboardDoctorId = dashboardDoctorFilter === "ALL" ? undefined : Number(dashboardDoctorFilter);
  const appointmentDoctorId = appointmentDoctorFilter === "ALL" ? undefined : Number(appointmentDoctorFilter);
  const walkinDoctorId = walkinDoctorFilter === "ALL" ? undefined : Number(walkinDoctorFilter);
  const appointmentDrawerDoctorId = appointmentDoctorUserId ? Number(appointmentDoctorUserId) : undefined;
  const walkinDrawerDoctorId = walkinDoctorUserId ? Number(walkinDoctorUserId) : undefined;

  const doctorsQuery = useQuery({ queryKey: ["frontdesk", "doctors"], queryFn: listFrontdeskDoctors });
  const dashboardQuery = useQuery({
    queryKey: ["dashboard", "frontdesk", dashboardDoctorId ?? "ALL"],
    queryFn: () => getFrontdeskDashboard(dashboardDoctorId)
  });
  const todayAppointmentsQuery = useQuery({
    queryKey: ["frontdesk", "appointments", "today", dashboardDoctorId ?? "ALL"],
    queryFn: () => listTodayAppointments(dashboardDoctorId)
  });
  const todayWalkinsQuery = useQuery({
    queryKey: ["frontdesk", "walkins", "today", dashboardDoctorId ?? "ALL"],
    queryFn: () => listTodayWalkinTokens(dashboardDoctorId)
  });
  const appointmentHistoryQuery = useQuery({
    queryKey: ["frontdesk", "appointments", appointmentDate, appointmentDoctorId ?? "ALL"],
    queryFn: () => listAppointmentsByDate(appointmentDate, appointmentDoctorId)
  });
  const walkinHistoryQuery = useQuery({
    queryKey: ["frontdesk", "walkins", walkinDate, walkinDoctorId ?? "ALL"],
    queryFn: () => listWalkinHistory(walkinDate, walkinDoctorId)
  });
  const contactQueriesQuery = useQuery({
    queryKey: ["frontdesk", "contact-queries", contactStatusFilter],
    queryFn: () => listFrontdeskContactQueries(contactStatusFilter === "ALL" ? undefined : contactStatusFilter)
  });
  const clinicSettingsQuery = useQuery({
    queryKey: ["public", "clinic-settings"],
    queryFn: getPublicClinicSettings
  });
  const profileQuery = useQuery({ queryKey: ["frontdesk", "profile"], queryFn: getFrontdeskProfile });
  const appointmentPatientSearchQuery = useQuery({
    queryKey: ["frontdesk", "patients", "search", "appointment", appointmentPatientSearch],
    queryFn: () => searchFrontdeskPatients(appointmentPatientSearch, 8),
    enabled: appointmentDrawerOpen && appointmentPatientSearch.trim().length >= 2
  });
  const walkinPatientSearchQuery = useQuery({
    queryKey: ["frontdesk", "patients", "search", "walkin", walkinPatientSearch],
    queryFn: () => searchFrontdeskPatients(walkinPatientSearch, 8),
    enabled: walkinDrawerOpen && walkinPatientSearch.trim().length >= 2
  });
  const availabilitiesQuery = useQuery({
    queryKey: ["frontdesk", "availabilities", appointmentDrawerDoctorId ?? "NONE", appointmentDrawerDate],
    queryFn: () =>
      listFrontdeskAvailabilities({
        doctor_user_id: appointmentDrawerDoctorId,
        available_date: appointmentDrawerDate
      }),
    enabled: appointmentDrawerOpen && Boolean(appointmentDrawerDoctorId) && Boolean(appointmentDrawerDate)
  });

  useEffect(() => {
    if (!profileQuery.data) return;
    setProfileForm({
      full_name: profileQuery.data.full_name,
      phone: profileQuery.data.phone ?? ""
    });
  }, [profileQuery.data]);

  const invalidateFrontdeskViews = () => {
    void queryClient.invalidateQueries({ queryKey: ["dashboard", "frontdesk"] });
    void queryClient.invalidateQueries({ queryKey: ["frontdesk", "appointments"] });
    void queryClient.invalidateQueries({ queryKey: ["frontdesk", "walkins"] });
    void queryClient.invalidateQueries({ queryKey: ["frontdesk", "availabilities"] });
  };

  const upsertPatientMutation = useMutation({
    mutationFn: upsertPatient,
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to save patient.")
  });

  const bookAppointmentMutation = useMutation({
    mutationFn: bookFrontdeskAppointment,
    onSuccess: (appointment) => {
      setMessage(`Appointment #${appointment.appointment_id} booked successfully.`);
      setAppointmentDrawerOpen(false);
      setActiveTab("dashboard");
      setSelectedAvailabilityId(null);
      setSelectedAppointmentPatient(null);
      setAppointmentPatientSearch("");
      setShowAppointmentPatientForm(false);
      setAppointmentPatientForm(emptyPatientDraft());
      invalidateFrontdeskViews();
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to book appointment.")
  });

  const createWalkinMutation = useMutation({
    mutationFn: createWalkinToken,
    onSuccess: (token) => {
      setMessage(`Walk-in token T-${String(token.token_number).padStart(2, "0")} created successfully.`);
      setWalkinDrawerOpen(false);
      setActiveTab("dashboard");
      setSelectedWalkinPatient(null);
      setWalkinPatientSearch("");
      setShowWalkinPatientForm(false);
      setWalkinPatientForm(emptyPatientDraft());
      setWalkinNotes("");
      invalidateFrontdeskViews();
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to create walk-in token.")
  });

  const cancelAppointmentMutation = useMutation({
    mutationFn: ({ appointmentId, reason }: { appointmentId: number; reason: string }) =>
      cancelFrontdeskAppointment(appointmentId, reason),
    onSuccess: (appointment) => {
      setMessage(`Appointment #${appointment.appointment_id} cancelled.`);
      invalidateFrontdeskViews();
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to cancel appointment.")
  });

  const updateWalkinStatusMutation = useMutation({
    mutationFn: ({ tokenId, status }: { tokenId: number; status: WalkinStatus }) => updateWalkinTokenStatus(tokenId, { status }),
    onSuccess: (token) => {
      setMessage(`Walk-in token T-${String(token.token_number).padStart(2, "0")} updated to ${token.status}.`);
      invalidateFrontdeskViews();
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to update walk-in token.")
  });

  const updateProfileMutation = useMutation({
    mutationFn: updateFrontdeskProfile,
    onSuccess: () => {
      setMessage("Profile updated successfully.");
      void queryClient.invalidateQueries({ queryKey: ["frontdesk", "profile"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to update profile.")
  });

  const updateContactMutation = useMutation({
    mutationFn: ({
      contactId,
      payload
    }: {
      contactId: number;
      payload: { status: ContactQueryStatus; notes?: string };
    }) => updateFrontdeskContactQuery(contactId, payload),
    onSuccess: () => {
      setMessage("Contact query updated.");
      void queryClient.invalidateQueries({ queryKey: ["frontdesk", "contact-queries"] });
    },
    onError: (error) => setMessage(error instanceof Error ? error.message : "Failed to update contact query.")
  });

  const sidebarUserName = profileQuery.data?.full_name ?? user?.full_name ?? "Frontdesk User";
  const sidebarEmail = profileQuery.data?.email ?? user?.email ?? "";
  const clinicName = clinicSettingsQuery.data?.clinic_name ?? "CarePoint Clinic";
  const doctorOptions = doctorsQuery.data ?? [];
  const allSpecs = Array.from(new Set(doctorOptions.flatMap((d) => d.specializations))).sort();
  const walkinDoctorOptions = doctorOptions.filter((doctor) =>
    doctor.specializations.some((specialization) => specialization.trim().toLowerCase() === GENERAL_MEDICINE_SPECIALIZATION)
  );
  const filteredDoctorsForAppt = appointmentSpecFilter
    ? doctorOptions.filter((d) => d.specializations.includes(appointmentSpecFilter))
    : doctorOptions;
  const selectedAvailability = (availabilitiesQuery.data ?? []).find((item) => item.availability_id === selectedAvailabilityId) ?? null;

  const openAppointmentDrawer = () => {
    setAppointmentDrawerOpen(true);
    setSelectedAvailabilityId(null);
    setSelectedAppointmentPatient(null);
    setAppointmentPatientSearch("");
    setShowAppointmentPatientForm(false);
    setAppointmentPatientForm(emptyPatientDraft());
    setAppointmentDrawerDate(today);
    setAppointmentSpecFilter("");
    setAppointmentDoctorUserId(
      dashboardDoctorFilter !== "ALL"
        ? dashboardDoctorFilter
        : doctorOptions[0]?.doctor_user_id
          ? String(doctorOptions[0].doctor_user_id)
          : ""
    );
  };

  const openWalkinDrawer = () => {
    setWalkinDrawerOpen(true);
    setSelectedWalkinPatient(null);
    setWalkinPatientSearch("");
    setShowWalkinPatientForm(false);
    setWalkinPatientForm(emptyPatientDraft());
    setWalkinTokenDate(today);
    setWalkinNotes("");
    const dashboardDoctorUserId = dashboardDoctorFilter === "ALL" ? null : Number(dashboardDoctorFilter);
    setWalkinDoctorUserId(
      dashboardDoctorUserId && walkinDoctorOptions.some((doctor) => doctor.doctor_user_id === dashboardDoctorUserId)
        ? String(dashboardDoctorUserId)
        : walkinDoctorOptions[0]?.doctor_user_id
          ? String(walkinDoctorOptions[0].doctor_user_id)
          : ""
    );
  };

  const handleCancelFromTable = (appointmentId: number) => {
    const reason = window.prompt("Enter cancellation reason");
    if (!reason || !reason.trim()) return;
    cancelAppointmentMutation.mutate({ appointmentId, reason: reason.trim() });
  };

  const handleWalkinStatusChange = (tokenId: number, status: WalkinStatus) => {
    updateWalkinStatusMutation.mutate({ tokenId, status });
  };

  const onLogout = async () => {
    try {
      await logout();
    } finally {
      clearSession();
      navigate("/management");
    }
  };

  const saveAppointmentPatient = () => {
    if (appointmentPatientForm.full_name.trim().length < 2 || appointmentPatientForm.phone.trim().length < 7) {
      setMessage("Enter valid patient details before saving.");
      return;
    }
    upsertPatientMutation.mutate(
      {
        full_name: appointmentPatientForm.full_name.trim(),
        phone: appointmentPatientForm.phone.trim(),
        gender: appointmentPatientForm.gender || undefined,
        dob: appointmentPatientForm.dob || undefined,
        blood_group: appointmentPatientForm.blood_group.trim() || undefined,
        address: appointmentPatientForm.address.trim() || undefined,
        emergency_contact: appointmentPatientForm.emergency_contact.trim() || undefined
      },
      {
        onSuccess: (patient) => {
          setSelectedAppointmentPatient(patient);
          setAppointmentPatientSearch(patient.full_name);
          setShowAppointmentPatientForm(false);
          setMessage(`Patient ${patient.full_name} is ready for booking.`);
        }
      }
    );
  };

  const saveWalkinPatient = () => {
    if (walkinPatientForm.full_name.trim().length < 2 || walkinPatientForm.phone.trim().length < 7) {
      setMessage("Enter valid patient details before saving.");
      return;
    }
    upsertPatientMutation.mutate(
      {
        full_name: walkinPatientForm.full_name.trim(),
        phone: walkinPatientForm.phone.trim(),
        gender: walkinPatientForm.gender || undefined,
        dob: walkinPatientForm.dob || undefined,
        blood_group: walkinPatientForm.blood_group.trim() || undefined,
        address: walkinPatientForm.address.trim() || undefined,
        emergency_contact: walkinPatientForm.emergency_contact.trim() || undefined
      },
      {
        onSuccess: (patient) => {
          setSelectedWalkinPatient(patient);
          setWalkinPatientSearch(patient.full_name);
          setShowWalkinPatientForm(false);
          setMessage(`Patient ${patient.full_name} is ready for walk-in token creation.`);
        }
      }
    );
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] md:grid-cols-[18rem_1fr]">
        <aside className="flex flex-col gap-6 bg-gradient-to-b from-slate-950 via-slate-900 to-blue-950 px-5 py-6">
          <div className="rounded-2xl bg-white/10 p-4 text-white">
            <p className="text-xs uppercase tracking-[0.24em] text-blue-200">{clinicName}</p>
            <h1 className="mt-2 text-lg font-semibold">Front Desk</h1>
            <p className="mt-1 text-sm text-slate-300">Appointments, tokens, contact queries, and patient coordination.</p>
          </div>

          <nav className="space-y-2">
            <SidebarButton active={activeTab === "dashboard"} label="Dashboard" onClick={() => setActiveTab("dashboard")} />
            <SidebarButton active={activeTab === "appointments"} label="Appointments" onClick={() => setActiveTab("appointments")} />
            <SidebarButton active={activeTab === "walkins"} label="Walk-in Tokens" onClick={() => setActiveTab("walkins")} />
            <SidebarButton active={activeTab === "contacts"} label="Contact Requests" onClick={() => setActiveTab("contacts")} />
            <SidebarButton active={activeTab === "profile"} label="Profile" onClick={() => setActiveTab("profile")} />
          </nav>

          <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
            <p className="font-semibold text-white">{sidebarUserName}</p>
            <p className="mt-1 text-xs text-slate-400">{sidebarEmail}</p>
            <button
              className="mt-4 w-full rounded-xl border border-white/15 px-3 py-2 font-medium text-white hover:bg-white/10"
              type="button"
              onClick={onLogout}
            >
              Logout
            </button>
          </div>
        </aside>

        <main className="p-4 md:p-6">
          <header className="rounded-3xl bg-white px-5 py-5 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <span className="inline-flex rounded-full bg-blue-600 px-4 py-1 text-xs font-semibold tracking-[0.16em] text-white">
                  FRONT DESK DASHBOARD
                </span>
                <h2 className="mt-3 text-2xl font-semibold text-slate-900">
                  {activeTab === "dashboard"
                    ? "Daily operations overview"
                    : activeTab === "appointments"
                      ? "Appointment history"
                      : activeTab === "walkins"
                        ? "Walk-in token control"
                        : activeTab === "contacts"
                          ? "Contact requests"
                          : "Profile settings"}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Coordinate bookings for callers, issue walk-in tokens, and manage frontdesk follow-up.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
                  type="button"
                  onClick={openAppointmentDrawer}
                >
                  + New Appointment
                </button>
                <button
                  className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700"
                  type="button"
                  onClick={openWalkinDrawer}
                >
                  + Walk-in Token
                </button>
              </div>
            </div>
          </header>

          {message ? (
            <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              {message}
            </div>
          ) : null}

          <div className="mt-4">
            {activeTab === "dashboard" ? (
              <div className="space-y-4">
                <section className="rounded-3xl bg-white p-5 shadow-sm">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div className="grid flex-1 gap-3 sm:grid-cols-3">
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Today's Appointments</p>
                        <p className="mt-3 text-3xl font-semibold text-slate-900">{dashboardQuery.data?.todays_appointments ?? 0}</p>
                      </div>
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Walk-in Tokens</p>
                        <p className="mt-3 text-3xl font-semibold text-slate-900">{dashboardQuery.data?.todays_walkin_tokens ?? 0}</p>
                      </div>
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Waiting Patients</p>
                        <p className="mt-3 text-3xl font-semibold text-slate-900">{dashboardQuery.data?.waiting_patients ?? 0}</p>
                      </div>
                    </div>
                    <div className="min-w-[220px]">
                      <label className="text-sm font-medium text-slate-600">Doctor filter</label>
                      <select
                        className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm"
                        value={dashboardDoctorFilter}
                        onChange={(event) => setDashboardDoctorFilter(event.target.value)}
                      >
                        <option value="ALL">All Doctors</option>
                        {walkinDoctorOptions.map((doctor) => (
                          <option key={doctor.doctor_user_id} value={doctor.doctor_user_id}>
                            {doctor.doctor_name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </section>

                <div className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
                  <div className="space-y-4">
                    <section className="rounded-3xl bg-white p-5 shadow-sm">
                      <div className="mb-4 flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-slate-900">Today's Appointments</h3>
                          <p className="text-sm text-slate-500">Ordered by slot time.</p>
                        </div>
                        <button className="text-sm font-medium text-blue-600" type="button" onClick={() => setActiveTab("appointments")}>
                          View all
                        </button>
                      </div>
                      {todayAppointmentsQuery.isLoading ? <p className="text-sm text-slate-500">Loading appointments...</p> : null}
                      {!todayAppointmentsQuery.isLoading ? (
                        <AppointmentsTable rows={todayAppointmentsQuery.data ?? []} onRebook={openAppointmentDrawer} />
                      ) : null}
                    </section>

                    <section className="rounded-3xl bg-white p-5 shadow-sm">
                      <div className="mb-4 flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-slate-900">Walk-in Tokens</h3>
                          <p className="text-sm text-slate-500">Sorted by token number.</p>
                        </div>
                        <button className="text-sm font-medium text-blue-600" type="button" onClick={() => setActiveTab("walkins")}>
                          View all
                        </button>
                      </div>
                      {todayWalkinsQuery.isLoading ? <p className="text-sm text-slate-500">Loading walk-in list...</p> : null}
                      {!todayWalkinsQuery.isLoading ? <WalkinTable rows={todayWalkinsQuery.data ?? []} /> : null}
                    </section>
                  </div>

                  <div className="space-y-4">
                    <NotificationPanel />
                    <section className="rounded-3xl bg-white p-5 shadow-sm">
                      <div className="mb-3 flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-slate-900">New contact requests</h3>
                        <button className="text-sm font-medium text-blue-600" type="button" onClick={() => setActiveTab("contacts")}>
                          Open queue
                        </button>
                      </div>
                      {(contactQueriesQuery.data ?? []).slice(0, 3).map((item) => (
                        <article key={item.contact_id} className="mb-3 rounded-2xl border border-slate-200 p-3 last:mb-0">
                          <p className="font-medium text-slate-900">{item.full_name}</p>
                          <p className="text-xs text-slate-500">{item.phone}</p>
                          <p className="mt-1 text-sm text-slate-600">{item.subject ?? "General enquiry"}</p>
                        </article>
                      ))}
                      {(contactQueriesQuery.data ?? []).length === 0 ? <EmptyState text="No contact requests pending." /> : null}
                    </section>
                  </div>
                </div>
              </div>
            ) : null}

            {activeTab === "appointments" ? (
              <section className="rounded-3xl bg-white p-5 shadow-sm">
                <div className="mb-5 grid gap-3 lg:grid-cols-[220px_260px_auto]">
                  <label className="text-sm font-medium text-slate-600">
                    Appointment date
                    <input
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
                      type="date"
                      value={appointmentDate}
                      onChange={(event) => setAppointmentDate(event.target.value)}
                    />
                  </label>
                  <label className="text-sm font-medium text-slate-600">
                    Doctor filter
                    <select
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
                      value={appointmentDoctorFilter}
                      onChange={(event) => setAppointmentDoctorFilter(event.target.value)}
                    >
                      <option value="ALL">All Doctors</option>
                      {doctorOptions.map((doctor) => (
                        <option key={doctor.doctor_user_id} value={doctor.doctor_user_id}>
                          {doctor.doctor_name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="flex items-end justify-start lg:justify-end">
                    <button
                      className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                      type="button"
                      onClick={openAppointmentDrawer}
                    >
                      + New Appointment
                    </button>
                  </div>
                </div>
                {appointmentHistoryQuery.isLoading ? <p className="text-sm text-slate-500">Loading appointment history...</p> : null}
                {!appointmentHistoryQuery.isLoading ? (
                  <AppointmentsTable rows={appointmentHistoryQuery.data ?? []} onCancel={handleCancelFromTable} onRebook={openAppointmentDrawer} />
                ) : null}
              </section>
            ) : null}

            {activeTab === "walkins" ? (
              <section className="rounded-3xl bg-white p-5 shadow-sm">
                <div className="mb-5 flex flex-wrap items-end gap-3">
                  <label className="text-sm font-medium text-slate-600">
                    Token date
                    <input
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
                      type="date"
                      value={walkinDate}
                      onChange={(event) => setWalkinDate(event.target.value)}
                    />
                  </label>
                  <label className="text-sm font-medium text-slate-600">
                    Doctor filter
                    <select
                      className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5"
                      value={walkinDoctorFilter}
                      onChange={(event) => setWalkinDoctorFilter(event.target.value)}
                    >
                      <option value="ALL">All Doctors</option>
                      {doctorOptions.map((doctor) => (
                        <option key={doctor.doctor_user_id} value={doctor.doctor_user_id}>
                          {doctor.doctor_name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700"
                    type="button"
                    onClick={openWalkinDrawer}
                  >
                    + New Walk-in Token
                  </button>
                </div>
                {walkinHistoryQuery.isLoading ? <p className="text-sm text-slate-500">Loading walk-in history...</p> : null}
                {!walkinHistoryQuery.isLoading ? (
                  <WalkinTable rows={walkinHistoryQuery.data ?? []} onStatusChange={handleWalkinStatusChange} />
                ) : null}
              </section>
            ) : null}

            {activeTab === "contacts" ? (
              <section className="rounded-3xl bg-white p-5 shadow-sm">
                <div className="mb-5 flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-900">Home page contact requests</h3>
                  <select
                    className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    value={contactStatusFilter}
                    onChange={(event) => setContactStatusFilter(event.target.value as "ALL" | ContactQueryStatus)}
                  >
                    <option value="ALL">All</option>
                    <option value="NEW">New</option>
                    <option value="IN_PROGRESS">In progress</option>
                    <option value="CLOSED">Closed</option>
                  </select>
                </div>
                <div className="space-y-4">
                  {(contactQueriesQuery.data ?? []).map((query) => {
                    const draft = contactDrafts[query.contact_id] ?? { status: query.status, notes: query.notes ?? "" };
                    return (
                      <article key={query.contact_id} className="rounded-2xl border border-slate-200 p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-900">{query.full_name}</p>
                            <p className="text-sm text-slate-500">
                              {query.phone} {query.email ? `• ${query.email}` : ""}
                            </p>
                            <p className="mt-2 text-sm font-medium text-slate-700">{query.subject ?? "General enquiry"}</p>
                          </div>
                          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClasses(query.status)}`}>{query.status}</span>
                        </div>
                        <p className="mt-3 text-sm text-slate-700">{query.message}</p>
                        <div className="mt-4 grid gap-3 md:grid-cols-[200px_1fr_auto]">
                          <select
                            className="rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                            value={draft.status}
                            onChange={(event) =>
                              setContactDrafts((prev) => ({
                                ...prev,
                                [query.contact_id]: { ...draft, status: event.target.value as ContactQueryStatus }
                              }))
                            }
                          >
                            <option value="NEW">NEW</option>
                            <option value="IN_PROGRESS">IN_PROGRESS</option>
                            <option value="CLOSED">CLOSED</option>
                          </select>
                          <textarea
                            className="rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                            placeholder="Notes"
                            value={draft.notes}
                            onChange={(event) =>
                              setContactDrafts((prev) => ({
                                ...prev,
                                [query.contact_id]: { ...draft, notes: event.target.value }
                              }))
                            }
                          />
                          <button
                            className="rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-60"
                            type="button"
                            disabled={updateContactMutation.isPending}
                            onClick={() =>
                              updateContactMutation.mutate({
                                contactId: query.contact_id,
                                payload: { status: draft.status, notes: draft.notes.trim() || undefined }
                              })
                            }
                          >
                            Update
                          </button>
                        </div>
                      </article>
                    );
                  })}
                  {!contactQueriesQuery.isLoading && (contactQueriesQuery.data ?? []).length === 0 ? (
                    <EmptyState text="No contact requests found for the selected filter." />
                  ) : null}
                </div>
              </section>
            ) : null}

            {activeTab === "profile" ? (
              <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
                <article className="rounded-3xl bg-white p-5 shadow-sm">
                  <h3 className="text-lg font-semibold text-slate-900">Basic profile</h3>
                  {profileQuery.isLoading ? <p className="mt-4 text-sm text-slate-500">Loading profile...</p> : null}
                  {profileQuery.data ? (
                    <div className="mt-4 space-y-3 text-sm">
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-slate-500">Email</p>
                        <p className="mt-1 font-medium text-slate-900">{profileQuery.data.email}</p>
                      </div>
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-slate-500">Role</p>
                        <p className="mt-1 font-medium text-slate-900">{profileQuery.data.role_name}</p>
                      </div>
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <p className="text-slate-500">Status</p>
                        <p className="mt-1 font-medium text-slate-900">{profileQuery.data.status}</p>
                      </div>
                    </div>
                  ) : null}
                </article>

                <article className="rounded-3xl bg-white p-5 shadow-sm">
                  <h3 className="text-lg font-semibold text-slate-900">Edit profile</h3>
                  <div className="mt-4 grid gap-3">
                    <input
                      className="rounded-xl border border-slate-200 px-3 py-2.5"
                      placeholder="Full name"
                      value={profileForm.full_name}
                      onChange={(event) => setProfileForm((prev) => ({ ...prev, full_name: event.target.value }))}
                    />
                    <input
                      className="rounded-xl border border-slate-200 px-3 py-2.5"
                      placeholder="Phone"
                      value={profileForm.phone}
                      onChange={(event) => setProfileForm((prev) => ({ ...prev, phone: event.target.value }))}
                    />
                  </div>
                  <button
                    className="mt-4 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                    type="button"
                    disabled={updateProfileMutation.isPending}
                    onClick={() => {
                      if (profileForm.full_name.trim().length < 2) {
                        setMessage("Enter a valid full name.");
                        return;
                      }
                      updateProfileMutation.mutate({
                        full_name: profileForm.full_name.trim(),
                        phone: profileForm.phone.trim() || undefined
                      });
                    }}
                  >
                    {updateProfileMutation.isPending ? "Saving..." : "Save profile"}
                  </button>
                </article>
              </section>
            ) : null}
          </div>
        </main>
      </div>

      {appointmentDrawerOpen ? (
        <>
          <button className="fixed inset-0 z-40 bg-slate-900/40 md:left-72" type="button" onClick={() => setAppointmentDrawerOpen(false)} />
          <section className="fixed inset-y-0 left-0 right-0 z-50 md:left-72">
            <div className="ml-auto h-full w-full max-w-4xl overflow-y-auto bg-white shadow-2xl">
              <div className="sticky top-0 flex items-center justify-between border-b bg-white px-6 py-5">
                <div>
                  <h3 className="text-3xl font-semibold text-slate-900">New Appointment</h3>
                  <p className="mt-1 text-sm text-slate-500">Create a booking on behalf of a calling patient.</p>
                </div>
                <button className="text-3xl text-slate-400 hover:text-slate-700" type="button" onClick={() => setAppointmentDrawerOpen(false)}>
                  ×
                </button>
              </div>

              <div className="space-y-6 px-6 py-6">
                <section className="rounded-3xl border border-slate-200">
                  <div className="border-b px-5 py-4">
                    <h4 className="text-2xl font-semibold text-slate-900">Doctor &amp; Schedule</h4>
                  </div>
                  <div className="grid gap-4 px-5 py-5 lg:grid-cols-2">
                    <label className="text-sm font-medium text-slate-600">
                      Specialization
                      <select
                        className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3"
                        value={appointmentSpecFilter}
                        onChange={(event) => {
                          setAppointmentSpecFilter(event.target.value);
                          setAppointmentDoctorUserId("");
                          setSelectedAvailabilityId(null);
                        }}
                      >
                        <option value="">All Specializations</option>
                        {allSpecs.map((spec) => (
                          <option key={spec} value={spec}>{spec}</option>
                        ))}
                      </select>
                    </label>
                    <label className="text-sm font-medium text-slate-600">
                      Select Doctor
                      {doctorsQuery.isLoading && <span className="ml-2 text-xs text-slate-400">Loading…</span>}
                      <select
                        className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3"
                        value={appointmentDoctorUserId}
                        onChange={(event) => {
                          setAppointmentDoctorUserId(event.target.value);
                          setSelectedAvailabilityId(null);
                        }}
                      >
                        <option value="">Select doctor</option>
                        {filteredDoctorsForAppt.map((doctor) => (
                          <option key={doctor.doctor_user_id} value={doctor.doctor_user_id}>
                            {doctor.doctor_name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="text-sm font-medium text-slate-600 lg:col-span-2">
                      Date
                      <input
                        className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3"
                        type="date"
                        value={appointmentDrawerDate}
                        onChange={(event) => {
                          setAppointmentDrawerDate(event.target.value);
                          setSelectedAvailabilityId(null);
                        }}
                      />
                    </label>
                  </div>
                  <div className="px-5 pb-5">
                    <p className="text-sm font-medium text-slate-600">Available slots</p>
                    {availabilitiesQuery.isLoading ? <p className="mt-3 text-sm text-slate-500">Loading slots...</p> : null}
                    {!appointmentDrawerDoctorId && <p className="mt-3 text-sm text-slate-400">Select a doctor to see available slots.</p>}
                    <div className="mt-3 flex flex-wrap gap-3">
                      {(availabilitiesQuery.data ?? []).map((slot) => (
                        <button
                          key={slot.availability_id}
                          className={`rounded-2xl border px-4 py-3 text-sm font-medium ${
                            selectedAvailabilityId === slot.availability_id
                              ? "border-blue-600 bg-blue-50 text-blue-700"
                              : "border-slate-200 text-slate-700 hover:bg-slate-50"
                          }`}
                          type="button"
                          onClick={() => setSelectedAvailabilityId(slot.availability_id)}
                        >
                          {formatTimeLabel(slot.slot_start_time)} - {formatTimeLabel(slot.slot_end_time)}
                        </button>
                      ))}
                    </div>
                  </div>
                </section>

                <PatientSection
                  search={appointmentPatientSearch}
                  onSearchChange={setAppointmentPatientSearch}
                  searchResults={appointmentPatientSearchQuery.data ?? []}
                  searchLoading={appointmentPatientSearchQuery.isLoading}
                  selectedPatient={selectedAppointmentPatient}
                  onSelectPatient={(patient) => {
                    setSelectedAppointmentPatient(patient);
                    setShowAppointmentPatientForm(false);
                    setAppointmentPatientForm({ ...appointmentPatientForm, full_name: patient.full_name, phone: patient.phone });
                  }}
                  showForm={showAppointmentPatientForm}
                  onToggleForm={() => {
                    setShowAppointmentPatientForm((prev) => !prev);
                    setSelectedAppointmentPatient(null);
                    setAppointmentPatientForm((prev) => ({ ...prev, phone: appointmentPatientSearch.trim() }));
                  }}
                  form={appointmentPatientForm}
                  onFormChange={setAppointmentPatientForm}
                  onSave={saveAppointmentPatient}
                  savePending={upsertPatientMutation.isPending}
                />

                <section className="rounded-3xl border border-slate-200">
                  <div className="border-b px-5 py-4">
                    <h4 className="text-2xl font-semibold text-slate-900">Appointment Details</h4>
                  </div>
                  <div className="grid gap-3 px-5 py-5 lg:grid-cols-3">
                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Doctor</p>
                      <p className="mt-2 font-semibold text-slate-900">
                        {doctorOptions.find((doctor) => doctor.doctor_user_id === appointmentDrawerDoctorId)?.doctor_name ?? "Not selected"}
                      </p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Date</p>
                      <p className="mt-2 font-semibold text-slate-900">{formatDateLabel(appointmentDrawerDate)}</p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Time</p>
                      <p className="mt-2 font-semibold text-slate-900">
                        {selectedAvailability
                          ? `${formatTimeLabel(selectedAvailability.slot_start_time)} - ${formatTimeLabel(selectedAvailability.slot_end_time)}`
                          : "Choose a slot"}
                      </p>
                    </div>
                  </div>
                </section>
              </div>

              <div className="sticky bottom-0 border-t bg-white px-6 py-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-slate-500">Complete booking after selecting doctor, slot, and patient.</p>
                  <button
                    className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                    type="button"
                    disabled={bookAppointmentMutation.isPending}
                    onClick={() => {
                      if (!selectedAvailabilityId || !selectedAppointmentPatient) {
                        setMessage("Select an available slot and patient before booking.");
                        return;
                      }
                      bookAppointmentMutation.mutate({
                        availability_id: selectedAvailabilityId,
                        patient_phone: selectedAppointmentPatient.phone
                      });
                    }}
                  >
                    {bookAppointmentMutation.isPending ? "Booking..." : "Confirm Appointment"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </>
      ) : null}

      {walkinDrawerOpen ? (
        <>
          <button className="fixed inset-0 z-40 bg-slate-900/40 md:left-72" type="button" onClick={() => setWalkinDrawerOpen(false)} />
          <section className="fixed inset-y-0 left-0 right-0 z-50 md:left-72">
            <div className="ml-auto h-full w-full max-w-4xl overflow-y-auto bg-white shadow-2xl">
              <div className="sticky top-0 flex items-center justify-between border-b bg-white px-6 py-5">
                <div>
                  <h3 className="text-3xl font-semibold text-slate-900">New Walk-in Token</h3>
                  <p className="mt-1 text-sm text-slate-500">Register a walk-in patient and create a same-day token.</p>
                </div>
                <button className="text-3xl text-slate-400 hover:text-slate-700" type="button" onClick={() => setWalkinDrawerOpen(false)}>
                  ×
                </button>
              </div>

              <div className="space-y-6 px-6 py-6">
                <section className="rounded-3xl border border-slate-200">
                  <div className="border-b px-5 py-4">
                    <h4 className="text-2xl font-semibold text-slate-900">Doctor &amp; Token Date</h4>
                  </div>
                  <div className="grid gap-4 px-5 py-5 lg:grid-cols-2">
                    <label className="text-sm font-medium text-slate-600">
                      Select Doctor (General Medicine)
                      {doctorsQuery.isLoading && <span className="ml-2 text-xs text-slate-400">Loading…</span>}
                      <select
                        className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3"
                        value={walkinDoctorUserId}
                        onChange={(event) => setWalkinDoctorUserId(event.target.value)}
                      >
                        <option value="">Select doctor</option>
                        {walkinDoctorOptions.map((doctor) => (
                          <option key={doctor.doctor_user_id} value={doctor.doctor_user_id}>
                            {doctor.doctor_name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="text-sm font-medium text-slate-600 lg:col-span-2">
                      Token date
                      <input
                        className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3"
                        type="date"
                        value={walkinTokenDate}
                        onChange={(event) => setWalkinTokenDate(event.target.value)}
                      />
                    </label>
                    {walkinDoctorOptions.length === 0 && !doctorsQuery.isLoading ? (
                      <p className="text-sm text-slate-500 lg:col-span-2">
                        No General Medicine doctor is available for walk-in token creation.
                      </p>
                    ) : null}
                  </div>
                </section>

                <PatientSection
                  search={walkinPatientSearch}
                  onSearchChange={setWalkinPatientSearch}
                  searchResults={walkinPatientSearchQuery.data ?? []}
                  searchLoading={walkinPatientSearchQuery.isLoading}
                  selectedPatient={selectedWalkinPatient}
                  onSelectPatient={(patient) => {
                    setSelectedWalkinPatient(patient);
                    setShowWalkinPatientForm(false);
                    setWalkinPatientForm({ ...walkinPatientForm, full_name: patient.full_name, phone: patient.phone });
                  }}
                  showForm={showWalkinPatientForm}
                  onToggleForm={() => {
                    setShowWalkinPatientForm((prev) => !prev);
                    setSelectedWalkinPatient(null);
                    setWalkinPatientForm((prev) => ({ ...prev, phone: walkinPatientSearch.trim() }));
                  }}
                  form={walkinPatientForm}
                  onFormChange={setWalkinPatientForm}
                  onSave={saveWalkinPatient}
                  savePending={upsertPatientMutation.isPending}
                />

                <section className="rounded-3xl border border-slate-200">
                  <div className="border-b px-5 py-4">
                    <h4 className="text-2xl font-semibold text-slate-900">Token Notes</h4>
                  </div>
                  <div className="px-5 py-5">
                    <textarea
                      className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3"
                      placeholder="Optional notes for this walk-in token"
                      value={walkinNotes}
                      onChange={(event) => setWalkinNotes(event.target.value)}
                    />
                  </div>
                </section>
              </div>

              <div className="sticky bottom-0 border-t bg-white px-6 py-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-slate-500">Create a walk-in token once doctor and patient are selected.</p>
                  <button
                    className="rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
                    type="button"
                    disabled={createWalkinMutation.isPending}
                    onClick={() => {
                      if (!walkinDrawerDoctorId || !selectedWalkinPatient) {
                        setMessage("Select a doctor and patient before creating the token.");
                        return;
                      }
                      createWalkinMutation.mutate({
                        doctor_user_id: walkinDrawerDoctorId,
                        token_date: walkinTokenDate,
                        patient_phone: selectedWalkinPatient.phone,
                        notes: walkinNotes.trim() || undefined
                      });
                    }}
                  >
                    {createWalkinMutation.isPending ? "Creating..." : "Create Walk-in Token"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
