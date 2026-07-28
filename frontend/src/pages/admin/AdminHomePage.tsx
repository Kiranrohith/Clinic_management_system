import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  createManagementUser,
  createSlot,
  createSpecialization,
  deleteSlot,
  generateSlots,
  getAdminProfile,
  getClinicSettings,
  listAdminContactQueries,
  listAdminPatients,
  listAdminSlots,
  listAdminSpecializations,
  listManagementUsers,
  setUserStatus,
  updateAdminContactQuery,
  updateAdminProfile,
  updateManagementUser,
  upsertClinicSettings,
  type ClinicSettingsUpsertPayload,
  type ContactQueryStatus,
  type ManagementRole,
  type ManagementUser,
  type PatientListItem,
  type Specialization,
} from "../../api/admin";
import { changePassword, logout } from "../../api/auth";
import { getAdminDashboard } from "../../api/dashboard";
import { NotificationPanel } from "../../components/NotificationPanel";
import { useAuth } from "../../hooks/useAuth";
import { isValidOptionalPhoneNumber } from "../../utils/validators";

type AdminTab = "dashboard" | "accounts" | "settings" | "profile";
type AccountSubTab = "doctors" | "frontdesk" | "patients";
type ToastItem = { id: number; text: string; kind: "success" | "error" };

type CreateDoctorForm = {
  full_name: string; email: string; password: string; phone: string;
  qualification: string; experience_years: string; consultation_fee: string;
  about: string; specialization_ids: number[];
};

type CreateFrontdeskForm = { full_name: string; email: string; password: string; phone: string };
type EditUserForm = { full_name: string; phone: string };

const defaultClinicSettings: ClinicSettingsUpsertPayload = {
  clinic_name: "", clinic_phone: "", clinic_email: "", clinic_address: "",
  opening_time: "08:00", closing_time: "20:00", slot_duration_minutes: 20,
  booking_window_days: 5, appointment_limit_per_day: 2,
  morning_break_start: "", morning_break_end: "",
  lunch_break_start: "13:00", lunch_break_end: "14:00",
  evening_break_start: "", evening_break_end: "", slot_generation_done: false,
};

function generatePassword(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#";
  return Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
}

const NAV_ICONS: Record<AdminTab, string> = {
  dashboard: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  accounts: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
  settings: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
  profile: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
};

function SidebarButton({ active, tab, label, badge, onClick }: { active: boolean; tab: AdminTab; label: string; badge?: number; onClick: () => void }) {
  return (
    <button className={`group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium transition ${active ? "bg-indigo-600 text-white shadow-md shadow-indigo-900/30" : "text-slate-300 hover:bg-white/10 hover:text-white"}`} type="button" onClick={onClick}>
      <svg className="h-4 w-4 shrink-0 opacity-80" fill="none" stroke="currentColor" strokeWidth={1.75} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d={NAV_ICONS[tab]} /></svg>
      <span className="flex-1">{label}</span>
      {badge !== undefined && badge > 0 && (<span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${active ? "bg-white/20 text-white" : "bg-indigo-500/30 text-indigo-200"}`}>{badge}</span>)}
    </button>
  );
}

function ToastStack({ toasts, onDismiss }: { toasts: ToastItem[]; onDismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div key={t.id} className={`flex items-start gap-3 rounded-2xl border px-4 py-3 shadow-lg ${t.kind === "error" ? "border-rose-200 bg-rose-50 text-rose-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`}>
          <svg className="mt-0.5 h-4 w-4 shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            {t.kind === "error" ? <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /> : <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />}
          </svg>
          <p className="flex-1 text-sm">{t.text}</p>
          <button className="ml-1 opacity-60 hover:opacity-100" type="button" onClick={() => onDismiss(t.id)}>
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/60 px-6 py-10 text-center">
      <svg className="mb-3 h-8 w-8 text-slate-300" fill="none" stroke="currentColor" strokeWidth={1.25} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
      <p className="text-sm text-slate-500">{text}</p>
    </div>
  );
}

function SkeletonRow() {
  return (
    <div className="animate-pulse flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4">
      <div className="h-10 w-10 rounded-full bg-slate-200 shrink-0" />
      <div className="flex-1 space-y-2"><div className="h-4 w-36 rounded bg-slate-200" /><div className="h-3 w-48 rounded bg-slate-200" /></div>
      <div className="h-6 w-16 rounded-full bg-slate-200" />
    </div>
  );
}

function StatCard({ label, value, color, icon, loading }: { label: string; value: number | undefined; color: string; icon?: string; loading?: boolean }) {
  const bg: Record<string, string> = { indigo: "bg-indigo-50", blue: "bg-blue-50", purple: "bg-purple-50", emerald: "bg-emerald-50", amber: "bg-amber-50" };
  const num: Record<string, string> = { indigo: "text-indigo-700", blue: "text-blue-700", purple: "text-purple-700", emerald: "text-emerald-700", amber: "text-amber-700" };
  const lbl: Record<string, string> = { indigo: "text-indigo-600", blue: "text-blue-600", purple: "text-purple-600", emerald: "text-emerald-600", amber: "text-amber-600" };
  const icoBg: Record<string, string> = { indigo: "bg-indigo-100 text-indigo-600", blue: "bg-blue-100 text-blue-600", purple: "bg-purple-100 text-purple-600", emerald: "bg-emerald-100 text-emerald-600", amber: "bg-amber-100 text-amber-600" };
  return (
    <div className={`rounded-2xl p-5 ${bg[color] ?? "bg-slate-50"}`}>
      <div className="flex items-start justify-between">
        <p className={`text-xs font-semibold uppercase tracking-[0.14em] ${lbl[color] ?? "text-slate-600"}`}>{label}</p>
        {icon && <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${icoBg[color] ?? "bg-slate-100 text-slate-600"}`}><svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={1.75} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d={icon} /></svg></div>}
      </div>
      {loading ? <div className="mt-2 h-10 w-20 animate-pulse rounded-xl bg-current opacity-10" /> : <p className={`mt-2 text-4xl font-bold ${num[color] ?? "text-slate-900"}`}>{value !== undefined ? value.toLocaleString() : "—"}</p>}
    </div>
  );
}

function statusBadge(status: string) {
  return status === "ACTIVE" ? "rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700" : "rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-500";
}

function initials(name: string) {
  return name.trim().split(/\s+/).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
}

function formatSlotLabel(startTime: string, endTime: string) {
  return `${startTime.slice(0, 5)} - ${endTime.slice(0, 5)}`;
}

function SlidePanel({ open, title, subtitle, onClose, children }: { open: boolean; title: string; subtitle?: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/30 backdrop-blur-sm" onClick={onClose} />}
      <aside className={`fixed inset-y-0 right-0 z-40 flex w-full max-w-lg flex-col bg-white shadow-2xl transition-transform duration-300 ${open ? "translate-x-0" : "translate-x-full"}`}>
        <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-5">
          <button className="mr-1 rounded-xl border border-slate-200 p-2 hover:bg-slate-50" type="button" onClick={onClose}>
            <svg className="h-4 w-4 text-slate-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
          <div><h3 className="font-semibold text-slate-900">{title}</h3>{subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}</div>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
      </aside>
    </>
  );
}

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <label className="block text-sm text-slate-700">
      <span className="mb-1 block font-medium">{label}</span>
      {children}
      {hint && <span className="mt-0.5 block text-xs text-slate-400">{hint}</span>}
    </label>
  );
}

const inputCls = "w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none ring-indigo-400 focus:ring disabled:bg-slate-50";
const textareaCls = "w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none ring-indigo-400 focus:ring min-h-24";
export function AdminHomePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { clearSession, user } = useAuth();
  const toastIdRef = useRef(0);

  const [activeTab, setActiveTab] = useState<AdminTab>("dashboard");
  const [accountSubTab, setAccountSubTab] = useState<AccountSubTab>("doctors");
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [createDoctorOpen, setCreateDoctorOpen] = useState(false);
  const [createFrontdeskOpen, setCreateFrontdeskOpen] = useState(false);
  const [editUserId, setEditUserId] = useState<number | null>(null);

  const [doctorForm, setDoctorForm] = useState<CreateDoctorForm>({
    full_name: "", email: "", password: generatePassword(), phone: "",
    qualification: "", experience_years: "", consultation_fee: "", about: "", specialization_ids: [],
  });
  const [frontdeskForm, setFrontdeskForm] = useState<CreateFrontdeskForm>({ full_name: "", email: "", password: generatePassword(), phone: "" });
  const [editForm, setEditForm] = useState<EditUserForm>({ full_name: "", phone: "" });
  const [clinicForm, setClinicForm] = useState<ClinicSettingsUpsertPayload>(defaultClinicSettings);
  const [pwForm, setPwForm] = useState({ current: "", next: "", confirm: "" });
  const [profileForm, setProfileForm] = useState({ full_name: "", phone: "" });
  const [newSpecName, setNewSpecName] = useState("");
  const [newSlotTime, setNewSlotTime] = useState("08:00");
  const [newSlotIsBreak, setNewSlotIsBreak] = useState(false);

  const dashboardQuery = useQuery({ queryKey: ["dashboard", "admin"], queryFn: getAdminDashboard, refetchInterval: 60000 });
  const usersQuery = useQuery({ queryKey: ["admin", "users"], queryFn: listManagementUsers });
  const specsQuery = useQuery({ queryKey: ["admin", "specializations"], queryFn: listAdminSpecializations });
  const slotsQuery = useQuery({ queryKey: ["admin", "slots"], queryFn: listAdminSlots });
  const clinicSettingsQuery = useQuery({ queryKey: ["admin", "clinic-settings"], queryFn: getClinicSettings });
  const patientsQuery = useQuery({ queryKey: ["admin", "patients"], queryFn: listAdminPatients, enabled: accountSubTab === "patients" && activeTab === "accounts" });
  const profileQuery = useQuery({ queryKey: ["admin", "profile"], queryFn: getAdminProfile, enabled: activeTab === "profile" });

  useEffect(() => {
    if (!clinicSettingsQuery.data) return;
    const s = clinicSettingsQuery.data;
    setClinicForm({ clinic_name: s.clinic_name, clinic_phone: s.clinic_phone ?? "", clinic_email: s.clinic_email ?? "", clinic_address: s.clinic_address ?? "", opening_time: s.opening_time, closing_time: s.closing_time, slot_duration_minutes: s.slot_duration_minutes, booking_window_days: s.booking_window_days, appointment_limit_per_day: s.appointment_limit_per_day, morning_break_start: s.morning_break_start ?? "", morning_break_end: s.morning_break_end ?? "", lunch_break_start: s.lunch_break_start ?? "", lunch_break_end: s.lunch_break_end ?? "", evening_break_start: s.evening_break_start ?? "", evening_break_end: s.evening_break_end ?? "", slot_generation_done: s.slot_generation_done });
  }, [clinicSettingsQuery.data]);

  useEffect(() => {
    if (!profileQuery.data) return;
    setProfileForm({ full_name: profileQuery.data.full_name, phone: profileQuery.data.phone ?? "" });
  }, [profileQuery.data]);

  useEffect(() => {
    if (editUserId === null) return;
    const found = usersQuery.data?.find((u) => u.user_id === editUserId);
    if (found) setEditForm({ full_name: found.full_name, phone: found.phone ?? "" });
  }, [editUserId, usersQuery.data]);

  const addToast = (text: string, kind: "success" | "error" = "success") => {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { id, text, kind }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000);
  };

  const createDoctorMutation = useMutation({
    mutationFn: createManagementUser,
    onSuccess: (data) => { addToast(`Doctor "${data.full_name}" created.`); setCreateDoctorOpen(false); setDoctorForm({ full_name: "", email: "", password: generatePassword(), phone: "", qualification: "", experience_years: "", consultation_fee: "", about: "", specialization_ids: [] }); void queryClient.invalidateQueries({ queryKey: ["admin", "users"] }); void queryClient.invalidateQueries({ queryKey: ["dashboard", "admin"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const createFrontdeskMutation = useMutation({
    mutationFn: createManagementUser,
    onSuccess: (data) => { addToast(`Front Desk "${data.full_name}" created.`); setCreateFrontdeskOpen(false); setFrontdeskForm({ full_name: "", email: "", password: generatePassword(), phone: "" }); void queryClient.invalidateQueries({ queryKey: ["admin", "users"] }); void queryClient.invalidateQueries({ queryKey: ["dashboard", "admin"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const editUserMutation = useMutation({
    mutationFn: ({ userId, payload }: { userId: number; payload: { full_name: string; phone?: string } }) => updateManagementUser(userId, payload),
    onSuccess: () => { addToast("User updated."); setEditUserId(null); void queryClient.invalidateQueries({ queryKey: ["admin", "users"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ userId, status }: { userId: number; status: "ACTIVE" | "INACTIVE" }) => setUserStatus(userId, status),
    onSuccess: (data) => { addToast(`${data.full_name} is now ${data.status}.`); void queryClient.invalidateQueries({ queryKey: ["admin", "users"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const saveClinicMutation = useMutation({
    mutationFn: upsertClinicSettings,
    onSuccess: () => { addToast("Clinic settings saved."); void queryClient.invalidateQueries({ queryKey: ["admin", "clinic-settings"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const addSpecMutation = useMutation({
    mutationFn: createSpecialization,
    onSuccess: () => { addToast("Specialization added."); setNewSpecName(""); void queryClient.invalidateQueries({ queryKey: ["admin", "specializations"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const addSlotMutation = useMutation({
    mutationFn: createSlot,
    onSuccess: () => { addToast("Slot added."); void queryClient.invalidateQueries({ queryKey: ["admin", "slots"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const generateSlotsMutation = useMutation({
    mutationFn: generateSlots,
    onSuccess: (data) => { addToast(`${data.length} slots ready.`); void queryClient.invalidateQueries({ queryKey: ["admin", "slots"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed to generate slots.", "error"),
  });

  const deleteSlotMutation = useMutation({
    mutationFn: deleteSlot,
    onSuccess: () => { addToast("Slot deleted."); void queryClient.invalidateQueries({ queryKey: ["admin", "slots"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const saveProfileMutation = useMutation({
    mutationFn: updateAdminProfile,
    onSuccess: () => { addToast("Profile updated."); void queryClient.invalidateQueries({ queryKey: ["admin", "profile"] }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const changePasswordMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => { addToast("Password changed."); setPwForm({ current: "", next: "", confirm: "" }); },
    onError: (err) => addToast(err instanceof Error ? err.message : "Failed.", "error"),
  });

  const allUsers = usersQuery.data ?? [];
  const doctors = allUsers.filter((u) => u.role_name === "DOCTOR");
  const frontdeskUsers = allUsers.filter((u) => u.role_name === "FRONTDESK");
  const patients = patientsQuery.data ?? [];

  const filteredDoctors = useMemo(() => doctors.filter((u) => u.full_name.toLowerCase().includes(searchQuery.toLowerCase()) || u.email.toLowerCase().includes(searchQuery.toLowerCase())), [doctors, searchQuery]);
  const filteredFrontdesk = useMemo(() => frontdeskUsers.filter((u) => u.full_name.toLowerCase().includes(searchQuery.toLowerCase()) || u.email.toLowerCase().includes(searchQuery.toLowerCase())), [frontdeskUsers, searchQuery]);
  const filteredPatients = useMemo(() => patients.filter((p) => p.full_name.toLowerCase().includes(searchQuery.toLowerCase()) || p.phone.includes(searchQuery)), [patients, searchQuery]);

  const onLogout = async () => { try { await logout(); } finally { clearSession(); navigate("/management"); } };

  const handleSaveSettings = () => {
    if (!isValidOptionalPhoneNumber(clinicForm.clinic_phone ?? "")) {
      addToast("Clinic phone must be exactly 10 digits.", "error");
      return;
    }
    saveClinicMutation.mutate(clinicForm);
  };
  const handleAddSpec = () => { if (newSpecName.trim().length < 2) { addToast("Specialization name too short.", "error"); return; } addSpecMutation.mutate(newSpecName.trim()); };
  const handleAddSlot = () => {
    if (!newSlotTime) { addToast("Select a time.", "error"); return; }
    const [h, m] = newSlotTime.split(":").map(Number);
    const dur = clinicForm.slot_duration_minutes || 20;
    const endMin = m + dur;
    const endH = h + Math.floor(endMin / 60);
    const endM = endMin % 60;
    const slot_end_time = `${String(endH).padStart(2, "0")}:${String(endM).padStart(2, "0")}`;
    addSlotMutation.mutate({ slot_start_time: newSlotTime, slot_end_time });
  };

  const handleCreateDoctor = () => {
    if (doctorForm.full_name.trim().length < 2) { addToast("Doctor name required.", "error"); return; }
    if (!doctorForm.email.trim()) { addToast("Email required.", "error"); return; }
    if (doctorForm.password.length < 8) { addToast("Password min 8 chars.", "error"); return; }
    if (!isValidOptionalPhoneNumber(doctorForm.phone)) { addToast("Phone must be exactly 10 digits.", "error"); return; }
    createDoctorMutation.mutate({ full_name: doctorForm.full_name.trim(), email: doctorForm.email.trim(), password: doctorForm.password, phone: doctorForm.phone.trim() || undefined, role_name: "DOCTOR", doctor_profile: { qualification: doctorForm.qualification.trim() || undefined, experience_years: doctorForm.experience_years ? parseInt(doctorForm.experience_years, 10) : undefined, consultation_fee: doctorForm.consultation_fee ? parseFloat(doctorForm.consultation_fee) : undefined, about: doctorForm.about.trim() || undefined, specialization_ids: doctorForm.specialization_ids } });
  };

  const handleCreateFrontdesk = () => {
    if (frontdeskForm.full_name.trim().length < 2) { addToast("Name required.", "error"); return; }
    if (!frontdeskForm.email.trim()) { addToast("Email required.", "error"); return; }
    if (frontdeskForm.password.length < 8) { addToast("Password min 8 chars.", "error"); return; }
    if (!isValidOptionalPhoneNumber(frontdeskForm.phone)) { addToast("Phone must be exactly 10 digits.", "error"); return; }
    createFrontdeskMutation.mutate({ full_name: frontdeskForm.full_name.trim(), email: frontdeskForm.email.trim(), password: frontdeskForm.password, phone: frontdeskForm.phone.trim() || undefined, role_name: "FRONTDESK" });
  };

  const handleEditUser = () => {
    if (!editUserId || editForm.full_name.trim().length < 2) { addToast("Name required.", "error"); return; }
    if (!isValidOptionalPhoneNumber(editForm.phone)) { addToast("Phone must be exactly 10 digits.", "error"); return; }
    editUserMutation.mutate({ userId: editUserId, payload: { full_name: editForm.full_name.trim(), phone: editForm.phone.trim() || undefined } });
  };

  const handleSaveProfile = () => {
    if (profileForm.full_name.trim().length < 2) { addToast("Name required.", "error"); return; }
    if (!isValidOptionalPhoneNumber(profileForm.phone)) { addToast("Phone must be exactly 10 digits.", "error"); return; }
    saveProfileMutation.mutate({ full_name: profileForm.full_name.trim(), phone: profileForm.phone.trim() || undefined });
  };

  const handleChangePassword = () => {
    if (pwForm.next.length < 8) { addToast("New password min 8 chars.", "error"); return; }
    if (pwForm.next !== pwForm.confirm) { addToast("Passwords do not match.", "error"); return; }
    changePasswordMutation.mutate({ current_password: pwForm.current, new_password: pwForm.next });
  };

  function UserCard({ u }: { u: ManagementUser }) {
    const isDoctor = u.role_name === "DOCTOR";
    return (
      <article className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white px-4 py-3.5 hover:shadow-sm transition">
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white ${isDoctor ? "bg-gradient-to-br from-blue-500 to-blue-700" : "bg-gradient-to-br from-purple-500 to-purple-700"}`}>{initials(u.full_name)}</div>
        <div className="flex-1 min-w-0">
          <p className="truncate font-semibold text-slate-900">{u.full_name}</p>
          <p className="truncate text-sm text-slate-500">{u.email}</p>
          {u.phone && <p className="text-xs text-slate-400">{u.phone}</p>}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className={statusBadge(u.status)}>{u.status}</span>
          <button className="rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" type="button" onClick={() => setEditUserId(u.user_id)}>Edit</button>
          <button className={`rounded-xl border px-3 py-1.5 text-xs font-medium transition ${u.status === "ACTIVE" ? "border-rose-200 text-rose-700 hover:bg-rose-50" : "border-emerald-200 text-emerald-700 hover:bg-emerald-50"}`} type="button" disabled={toggleStatusMutation.isPending} onClick={() => toggleStatusMutation.mutate({ userId: u.user_id, status: u.status === "ACTIVE" ? "INACTIVE" : "ACTIVE" })}>{u.status === "ACTIVE" ? "Deactivate" : "Activate"}</button>
        </div>
      </article>
    );
  }

  function PatientCard({ p }: { p: PatientListItem }) {
    return (
      <article className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white px-4 py-3.5 hover:shadow-sm transition">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 text-sm font-bold text-white">{initials(p.full_name)}</div>
        <div className="flex-1 min-w-0">
          <p className="truncate font-semibold text-slate-900">{p.full_name}</p>
          <p className="text-sm text-slate-500">{p.phone}{p.gender ? ` · ${p.gender}` : ""}{p.dob ? ` · DOB: ${p.dob}` : ""}</p>
          {p.blood_group && <p className="text-xs text-slate-400">Blood: {p.blood_group}</p>}
        </div>
        <span className="shrink-0 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700">{p.appointment_count} appts</span>
      </article>
    );
  }

  function SpecializationPicker({ selected, onChange, specs }: { selected: number[]; onChange: (ids: number[]) => void; specs: Specialization[] }) {
    return (
      <div className="flex flex-wrap gap-2">
        {specs.map((spec) => {
          const on = selected.includes(spec.specialization_id);
          return <button key={spec.specialization_id} className={`rounded-full px-3 py-1 text-xs font-medium transition ${on ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-700 hover:border-indigo-300"}`} type="button" onClick={() => onChange(on ? selected.filter((id) => id !== spec.specialization_id) : [...selected, spec.specialization_id])}>{spec.specialization_name}</button>;
        })}
      </div>
    );
  }
  const editUser = useMemo(() => (editUserId ? (usersQuery.data ?? []).find((u) => u.user_id === editUserId) : null), [editUserId, usersQuery.data]);

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] md:grid-cols-[18rem_1fr]">

        {/* Sidebar */}
        <aside className="flex flex-col gap-5 bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950 px-5 py-6">
          <div className="flex items-center gap-3 rounded-2xl bg-white/10 px-4 py-3 text-white">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-500/30">
              <svg className="h-4 w-4 text-indigo-300" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" /></svg>
            </div>
            <div>
              <p className="text-xs font-semibold tracking-[0.2em] text-indigo-300">CAREPOINT</p>
              <p className="text-sm font-semibold text-white">Admin Panel</p>
            </div>
          </div>
          <nav className="space-y-1">
            <SidebarButton active={activeTab === "dashboard"} tab="dashboard" label="Dashboard" onClick={() => setActiveTab("dashboard")} />
            <SidebarButton active={activeTab === "accounts"} tab="accounts" label="Manage Accounts" badge={dashboardQuery.data?.management_users} onClick={() => setActiveTab("accounts")} />
            <SidebarButton active={activeTab === "settings"} tab="settings" label="Clinic Settings" onClick={() => setActiveTab("settings")} />
            <SidebarButton active={activeTab === "profile"} tab="profile" label="Profile" onClick={() => setActiveTab("profile")} />
          </nav>
          <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-xs font-bold uppercase text-white">{initials(user?.full_name ?? "A")}</div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">{user?.full_name ?? "Admin"}</p>
                <p className="truncate text-xs text-slate-400">{user?.email ?? ""}</p>
              </div>
            </div>
            <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-white/15 px-3 py-2 text-sm font-medium text-white hover:bg-white/10" type="button" onClick={onLogout}>
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
              Logout
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex flex-col overflow-y-auto">
          <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/80 px-8 py-4 backdrop-blur">
            <div>
              <p className="text-xs font-medium uppercase tracking-widest text-indigo-500">
                {clinicSettingsQuery.data?.clinic_name || "CarePoint Clinic"}
              </p>
              <h1 className="text-xl font-bold text-slate-900">
                {activeTab === "dashboard" && "Dashboard"}
                {activeTab === "accounts" && "Manage Accounts"}
                {activeTab === "settings" && "Clinic Settings"}
                {activeTab === "profile" && "My Profile"}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="hidden text-sm text-slate-500 sm:block">{new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}</span>
              <NotificationPanel />
            </div>
          </header>

          <div className="flex-1 space-y-8 p-8">

            {/* DASHBOARD TAB */}
            {activeTab === "dashboard" && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                  <StatCard label="Total Staff" value={dashboardQuery.data?.management_users} color="indigo" icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" loading={dashboardQuery.isLoading} />
                  <StatCard label="Doctors" value={dashboardQuery.data?.doctors} color="blue" icon="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z" loading={dashboardQuery.isLoading} />
                  <StatCard label="Front Desk" value={dashboardQuery.data?.frontdesk} color="purple" icon="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 00-1-1h-2a1 1 0 00-1 1v5m4 0H9" loading={dashboardQuery.isLoading} />
                  <StatCard label="Patients" value={dashboardQuery.data?.patients} color="emerald" icon="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" loading={dashboardQuery.isLoading} />
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-4 text-base font-semibold text-slate-800">Quick Actions</h2>
                  <div className="flex flex-wrap gap-3">
                    <button className="flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition" type="button" onClick={() => { setActiveTab("accounts"); setAccountSubTab("doctors"); setCreateDoctorOpen(true); }}>
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                      Create Doctor
                    </button>
                    <button className="flex items-center gap-2 rounded-xl bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-purple-700 transition" type="button" onClick={() => { setActiveTab("accounts"); setAccountSubTab("frontdesk"); setCreateFrontdeskOpen(true); }}>
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                      Create Front Desk
                    </button>
                    <button className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition" type="button" onClick={() => setActiveTab("settings")}>
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                      Clinic Settings
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="mb-4 flex items-center justify-between">
                      <h2 className="text-base font-semibold text-slate-800">Doctors</h2>
                      <button className="text-xs font-medium text-indigo-600 hover:underline" type="button" onClick={() => { setActiveTab("accounts"); setAccountSubTab("doctors"); }}>View all</button>
                    </div>
                    {usersQuery.isLoading ? (
                      <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <SkeletonRow key={i} />)}</div>
                    ) : (usersQuery.data ?? []).filter(u => u.role_name === "DOCTOR").slice(0, 5).length === 0 ? (
                      <EmptyState text="No doctors yet" />
                    ) : (
                      <ul className="divide-y divide-slate-100">
                        {(usersQuery.data ?? []).filter(u => u.role_name === "DOCTOR").slice(0, 5).map((u) => (
                          <li key={u.user_id} className="flex items-center gap-3 py-2.5">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-500/15 text-xs font-bold text-blue-700">{initials(u.full_name)}</div>
                            <div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-slate-900">{u.full_name}</p><p className="truncate text-xs text-slate-500">{u.email}</p></div>
                            <span className={statusBadge(u.status)}>{u.status}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="mb-4 flex items-center justify-between">
                      <h2 className="text-base font-semibold text-slate-800">Front Desk</h2>
                      <button className="text-xs font-medium text-indigo-600 hover:underline" type="button" onClick={() => { setActiveTab("accounts"); setAccountSubTab("frontdesk"); }}>View all</button>
                    </div>
                    {usersQuery.isLoading ? (
                      <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <SkeletonRow key={i} />)}</div>
                    ) : (usersQuery.data ?? []).filter(u => u.role_name === "FRONTDESK").slice(0, 5).length === 0 ? (
                      <EmptyState text="No front desk staff yet" />
                    ) : (
                      <ul className="divide-y divide-slate-100">
                        {(usersQuery.data ?? []).filter(u => u.role_name === "FRONTDESK").slice(0, 5).map((u) => (
                          <li key={u.user_id} className="flex items-center gap-3 py-2.5">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-500/15 text-xs font-bold text-purple-700">{initials(u.full_name)}</div>
                            <div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-slate-900">{u.full_name}</p><p className="truncate text-xs text-slate-500">{u.email}</p></div>
                            <span className={statusBadge(u.status)}>{u.status}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ACCOUNTS TAB */}
            {activeTab === "accounts" && (
              <div className="space-y-6">
                <div className="flex items-center gap-1 rounded-2xl border border-slate-200 bg-white p-1.5">
                  {(["doctors", "frontdesk", "patients"] as AccountSubTab[]).map((t) => (
                    <button key={t} className={`flex-1 rounded-xl py-2 text-sm font-semibold capitalize transition ${accountSubTab === t ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"}`} type="button" onClick={() => { setAccountSubTab(t); setSearchQuery(""); }}>{t === "frontdesk" ? "Front Desk" : t.charAt(0).toUpperCase() + t.slice(1)}</button>
                  ))}
                </div>
                <div className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    <input className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm placeholder:text-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100" placeholder={`Search ${accountSubTab === "frontdesk" ? "front desk" : accountSubTab}...`} value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                  </div>
                  {accountSubTab !== "patients" && (
                    <button className="flex shrink-0 items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition" type="button" onClick={() => accountSubTab === "doctors" ? setCreateDoctorOpen(true) : setCreateFrontdeskOpen(true)}>
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                      {accountSubTab === "doctors" ? "New Doctor" : "New Front Desk"}
                    </button>
                  )}
                </div>
                {accountSubTab !== "patients" ? (
                  <div className="space-y-3">
                    {usersQuery.isLoading ? Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />) : (accountSubTab === "doctors" ? filteredDoctors : filteredFrontdesk).length === 0 ? <EmptyState text={`No ${accountSubTab === "frontdesk" ? "front desk staff" : accountSubTab} found`} /> : (accountSubTab === "doctors" ? filteredDoctors : filteredFrontdesk).map((u) => <UserCard key={u.user_id} u={u} />)}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {patientsQuery.isLoading ? Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />) : filteredPatients.length === 0 ? <EmptyState text="No patients found" /> : filteredPatients.map((p) => <PatientCard key={p.patient_id} p={p} />)}
                  </div>
                )}
              </div>
            )}

            {/* SETTINGS TAB */}
            {activeTab === "settings" && (
              <div className="space-y-8">
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-5 text-base font-semibold text-slate-800">Clinic Identity</h2>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <Field label="Clinic Name"><input className={inputCls} value={clinicForm.clinic_name} onChange={(e) => setClinicForm((f) => ({ ...f, clinic_name: e.target.value }))} /></Field>
                    <Field label="Clinic Phone"><input className={inputCls} value={clinicForm.clinic_phone ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, clinic_phone: e.target.value }))} inputMode="numeric" pattern="[0-9]{10}" minLength={10} maxLength={10} /></Field>
                    <Field label="Clinic Email"><input className={inputCls} type="email" value={clinicForm.clinic_email ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, clinic_email: e.target.value }))} /></Field>
                    <Field label="Address"><input className={inputCls} value={clinicForm.clinic_address ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, clinic_address: e.target.value }))} /></Field>
                  </div>
                </section>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-5 text-base font-semibold text-slate-800">Hours &amp; Scheduling</h2>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <Field label="Opening Time"><input className={inputCls} type="time" value={clinicForm.opening_time} onChange={(e) => setClinicForm((f) => ({ ...f, opening_time: e.target.value }))} /></Field>
                    <Field label="Closing Time"><input className={inputCls} type="time" value={clinicForm.closing_time} onChange={(e) => setClinicForm((f) => ({ ...f, closing_time: e.target.value }))} /></Field>
                    <Field label="Slot Duration (min)"><input className={inputCls} type="number" min={5} max={60} value={clinicForm.slot_duration_minutes} onChange={(e) => setClinicForm((f) => ({ ...f, slot_duration_minutes: Number(e.target.value) }))} /></Field>
                    <Field label="Booking Window (days)"><input className={inputCls} type="number" min={1} max={30} value={clinicForm.booking_window_days} onChange={(e) => setClinicForm((f) => ({ ...f, booking_window_days: Number(e.target.value) }))} /></Field>
                    <Field label="Max Appts/Patient/Day"><input className={inputCls} type="number" min={1} max={10} value={clinicForm.appointment_limit_per_day} onChange={(e) => setClinicForm((f) => ({ ...f, appointment_limit_per_day: Number(e.target.value) }))} /></Field>
                  </div>
                </section>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-5 text-base font-semibold text-slate-800">Break Times</h2>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div className="space-y-3">
                      <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Morning Break</p>
                      <Field label="Start"><input className={inputCls} type="time" value={clinicForm.morning_break_start ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, morning_break_start: e.target.value }))} /></Field>
                      <Field label="End"><input className={inputCls} type="time" value={clinicForm.morning_break_end ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, morning_break_end: e.target.value }))} /></Field>
                    </div>
                    <div className="space-y-3">
                      <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Lunch Break</p>
                      <Field label="Start"><input className={inputCls} type="time" value={clinicForm.lunch_break_start ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, lunch_break_start: e.target.value }))} /></Field>
                      <Field label="End"><input className={inputCls} type="time" value={clinicForm.lunch_break_end ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, lunch_break_end: e.target.value }))} /></Field>
                    </div>
                    <div className="space-y-3">
                      <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">Evening Break</p>
                      <Field label="Start"><input className={inputCls} type="time" value={clinicForm.evening_break_start ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, evening_break_start: e.target.value }))} /></Field>
                      <Field label="End"><input className={inputCls} type="time" value={clinicForm.evening_break_end ?? ""} onChange={(e) => setClinicForm((f) => ({ ...f, evening_break_end: e.target.value }))} /></Field>
                    </div>
                  </div>
                </section>
                <div className="flex justify-end">
                  <button className="flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition" type="button" disabled={saveClinicMutation.isPending} onClick={handleSaveSettings}>
                    {saveClinicMutation.isPending ? "Saving…" : "Save Settings"}
                  </button>
                </div>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-4 text-base font-semibold text-slate-800">Specializations</h2>
                  <div className="flex flex-wrap gap-2">
                    {(specsQuery.data ?? []).map((s) => (
                      <span key={s.specialization_id} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700">{s.specialization_name}</span>
                    ))}
                  </div>
                  <div className="mt-4 flex gap-2">
                    <input className={`${inputCls} flex-1`} placeholder="Add specialization…" value={newSpecName} onChange={(e) => setNewSpecName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleAddSpec()} />
                    <button className="shrink-0 rounded-xl bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 transition" type="button" disabled={addSpecMutation.isPending} onClick={handleAddSpec}>Add</button>
                  </div>
                </section>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <h2 className="text-base font-semibold text-slate-800">Time Slots</h2>
                      <p className="mt-0.5 text-xs text-slate-500">{(slotsQuery.data ?? []).length} slots configured</p>
                    </div>
                    <button
                      className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition"
                      type="button"
                      disabled={generateSlotsMutation.isPending || saveClinicMutation.isPending}
                      title="Auto-generate slots from clinic hours and breaks"
                      onClick={() => generateSlotsMutation.mutate()}
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                      {generateSlotsMutation.isPending ? "Generating…" : "Auto-Generate"}
                    </button>
                  </div>
                  {slotsQuery.isLoading ? (
                    <div className="flex flex-wrap gap-2">{Array.from({ length: 8 }).map((_, i) => <div key={i} className="h-7 w-20 animate-pulse rounded-full bg-slate-200" />)}</div>
                  ) : (slotsQuery.data ?? []).length === 0 ? (
                    <div className="rounded-xl border-2 border-dashed border-slate-200 py-8 text-center">
                      <p className="text-sm text-slate-500">No slots yet. Save clinic settings first, then click <strong>Auto-Generate</strong>.</p>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2 max-h-64 overflow-y-auto">
                      {(slotsQuery.data ?? []).slice().sort((a, b) => a.slot_start_time.localeCompare(b.slot_start_time)).map((s) => (
                        <span key={s.slot_id} className="group flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 pl-3 pr-1.5 py-1 text-xs font-medium text-indigo-700">
                          {formatSlotLabel(s.slot_start_time, s.slot_end_time)}
                          <button
                            className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-indigo-200 text-indigo-700 opacity-0 transition hover:bg-rose-500 hover:text-white group-hover:opacity-100"
                            type="button"
                            title="Delete slot"
                            disabled={deleteSlotMutation.isPending}
                            onClick={() => deleteSlotMutation.mutate(s.slot_id)}
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                  <p className="mt-3 text-xs text-slate-400">Hover a slot to reveal the delete button. Auto-Generate skips break periods and won't duplicate existing slots.</p>
                </section>
              </div>
            )}

            {/* PROFILE TAB */}
            {activeTab === "profile" && (
              <div className="space-y-6 max-w-2xl">
                <div className="flex items-center gap-5 rounded-2xl border border-slate-200 bg-white p-6">
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-xl font-bold uppercase text-white">{initials(user?.full_name ?? "A")}</div>
                  <div>
                    <p className="text-lg font-bold text-slate-900">{profileQuery.data?.full_name ?? user?.full_name}</p>
                    <p className="text-sm text-slate-500">{profileQuery.data?.email ?? user?.email}</p>
                    <span className="mt-1 inline-block rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">Administrator</span>
                  </div>
                </div>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-5 text-base font-semibold text-slate-800">Personal Information</h2>
                  <div className="space-y-4">
                    <Field label="Full Name"><input className={inputCls} value={profileForm.full_name} onChange={(e) => setProfileForm((f) => ({ ...f, full_name: e.target.value }))} /></Field>
                    <Field label="Email"><input className={`${inputCls} bg-slate-50 cursor-not-allowed`} value={profileQuery.data?.email ?? user?.email ?? ""} readOnly /></Field>
                    <Field label="Phone"><input className={inputCls} value={profileForm.phone} onChange={(e) => setProfileForm((f) => ({ ...f, phone: e.target.value }))} inputMode="numeric" pattern="[0-9]{10}" minLength={10} maxLength={10} /></Field>
                  </div>
                  <button className="mt-5 flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition" type="button" disabled={saveProfileMutation.isPending} onClick={handleSaveProfile}>
                    {saveProfileMutation.isPending ? "Saving…" : "Save Changes"}
                  </button>
                </section>
                <section className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h2 className="mb-5 text-base font-semibold text-slate-800">Change Password</h2>
                  <div className="space-y-4">
                    <Field label="Current Password"><input className={inputCls} type="password" value={pwForm.current} onChange={(e) => setPwForm((f) => ({ ...f, current: e.target.value }))} /></Field>
                    <Field label="New Password"><input className={inputCls} type="password" value={pwForm.next} onChange={(e) => setPwForm((f) => ({ ...f, next: e.target.value }))} /></Field>
                    <Field label="Confirm Password"><input className={inputCls} type="password" value={pwForm.confirm} onChange={(e) => setPwForm((f) => ({ ...f, confirm: e.target.value }))} /></Field>
                  </div>
                  <button className="mt-5 flex items-center gap-2 rounded-xl bg-slate-800 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 disabled:opacity-50 transition" type="button" disabled={changePasswordMutation.isPending} onClick={handleChangePassword}>
                    {changePasswordMutation.isPending ? "Updating…" : "Update Password"}
                  </button>
                </section>
                <NotificationPanel />
              </div>
            )}

          </div>
        </main>
      </div>

      {/* Create Doctor Slide Panel */}
      <SlidePanel open={createDoctorOpen} title="Create Doctor Account" onClose={() => setCreateDoctorOpen(false)}>
        <div className="space-y-4">
          <Field label="Full Name *"><input className={inputCls} value={doctorForm.full_name} onChange={(e) => setDoctorForm((f) => ({ ...f, full_name: e.target.value }))} /></Field>
          <Field label="Email *"><input className={inputCls} type="email" value={doctorForm.email} onChange={(e) => setDoctorForm((f) => ({ ...f, email: e.target.value }))} /></Field>
          <Field label="Phone"><input className={inputCls} value={doctorForm.phone} onChange={(e) => setDoctorForm((f) => ({ ...f, phone: e.target.value }))} inputMode="numeric" pattern="[0-9]{10}" minLength={10} maxLength={10} /></Field>
          <Field label="Qualification"><input className={inputCls} value={doctorForm.qualification} onChange={(e) => setDoctorForm((f) => ({ ...f, qualification: e.target.value }))} /></Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Experience (yrs)"><input className={inputCls} type="number" min={0} value={doctorForm.experience_years} onChange={(e) => setDoctorForm((f) => ({ ...f, experience_years: e.target.value }))} /></Field>
            <Field label="Consultation Fee">
              <div className="relative"><span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">â‚¹</span><input className={`${inputCls} pl-7`} type="number" min={0} value={doctorForm.consultation_fee} onChange={(e) => setDoctorForm((f) => ({ ...f, consultation_fee: e.target.value }))} /></div>
            </Field>
          </div>
          <Field label="Specializations">
            <SpecializationPicker selected={doctorForm.specialization_ids} onChange={(ids) => setDoctorForm((f) => ({ ...f, specialization_ids: ids }))} specs={specsQuery.data ?? []} />
          </Field>
          <Field label="About"><textarea className={textareaCls} rows={3} value={doctorForm.about} onChange={(e) => setDoctorForm((f) => ({ ...f, about: e.target.value }))} /></Field>
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
            <p className="mb-1 text-xs font-semibold text-amber-700">Generated Password</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 rounded-lg bg-white px-3 py-1.5 text-sm font-mono text-slate-800 border border-slate-200">{doctorForm.password}</code>
              <button className="shrink-0 rounded-lg bg-amber-500 px-2 py-1 text-xs font-semibold text-white hover:bg-amber-600 transition" type="button" onClick={() => setDoctorForm((f) => ({ ...f, password: generatePassword() }))}>Refresh</button>
            </div>
            <p className="mt-1 text-xs text-amber-600">Share this with the doctor. They can change it after login.</p>
          </div>
          <div className="flex gap-3 pt-2">
            <button className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition" type="button" onClick={() => setCreateDoctorOpen(false)}>Cancel</button>
            <button className="flex-1 rounded-xl bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition" type="button" disabled={createDoctorMutation.isPending} onClick={handleCreateDoctor}>
              {createDoctorMutation.isPending ? "Creating…" : "Create Doctor"}
            </button>
          </div>
        </div>
      </SlidePanel>

      {/* Create Front Desk Slide Panel */}
      <SlidePanel open={createFrontdeskOpen} title="Create Front Desk Account" onClose={() => setCreateFrontdeskOpen(false)}>
        <div className="space-y-4">
          <Field label="Full Name *"><input className={inputCls} value={frontdeskForm.full_name} onChange={(e) => setFrontdeskForm((f) => ({ ...f, full_name: e.target.value }))} /></Field>
          <Field label="Email *"><input className={inputCls} type="email" value={frontdeskForm.email} onChange={(e) => setFrontdeskForm((f) => ({ ...f, email: e.target.value }))} /></Field>
          <Field label="Phone"><input className={inputCls} value={frontdeskForm.phone} onChange={(e) => setFrontdeskForm((f) => ({ ...f, phone: e.target.value }))} inputMode="numeric" pattern="[0-9]{10}" minLength={10} maxLength={10} /></Field>
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
            <p className="mb-1 text-xs font-semibold text-amber-700">Generated Password</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 rounded-lg bg-white px-3 py-1.5 text-sm font-mono text-slate-800 border border-slate-200">{frontdeskForm.password}</code>
              <button className="shrink-0 rounded-lg bg-amber-500 px-2 py-1 text-xs font-semibold text-white hover:bg-amber-600 transition" type="button" onClick={() => setFrontdeskForm((f) => ({ ...f, password: generatePassword() }))}>Refresh</button>
            </div>
            <p className="mt-1 text-xs text-amber-600">Share this with the staff member. They can change it after login.</p>
          </div>
          <div className="flex gap-3 pt-2">
            <button className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition" type="button" onClick={() => setCreateFrontdeskOpen(false)}>Cancel</button>
            <button className="flex-1 rounded-xl bg-purple-600 py-2.5 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 transition" type="button" disabled={createFrontdeskMutation.isPending} onClick={handleCreateFrontdesk}>
              {createFrontdeskMutation.isPending ? "Creating…" : "Create Front Desk"}
            </button>
          </div>
        </div>
      </SlidePanel>

      {/* Edit User Slide Panel */}
      {editUser && (
        <SlidePanel open={editUserId !== null} title={`Edit — ${editUser.full_name}`} onClose={() => setEditUserId(null)}>
          <div className="space-y-4">
            <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-4">
              <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white ${editUser.role_name === "DOCTOR" ? "bg-gradient-to-br from-blue-500 to-blue-700" : "bg-gradient-to-br from-purple-500 to-purple-700"}`}>{initials(editUser.full_name)}</div>
              <div><p className="font-semibold text-slate-900">{editUser.full_name}</p><p className="text-sm text-slate-500">{editUser.email}</p><span className={statusBadge(editUser.status)}>{editUser.status}</span></div>
            </div>
            <Field label="Full Name"><input className={inputCls} value={editForm.full_name} onChange={(e) => setEditForm((f) => ({ ...f, full_name: e.target.value }))} /></Field>
            <Field label="Phone"><input className={inputCls} value={editForm.phone} onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))} inputMode="numeric" pattern="[0-9]{10}" minLength={10} maxLength={10} /></Field>
            <div className="flex gap-3 pt-2">
              <button className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition" type="button" onClick={() => setEditUserId(null)}>Cancel</button>
              <button className="flex-1 rounded-xl bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition" type="button" disabled={editUserMutation.isPending} onClick={handleEditUser}>
                {editUserMutation.isPending ? "Saving…" : "Save Changes"}
              </button>
            </div>
          </div>
        </SlidePanel>
      )}

      <ToastStack toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
}
