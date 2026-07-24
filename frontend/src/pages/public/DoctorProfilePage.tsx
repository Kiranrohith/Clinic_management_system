import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getPublicDoctor, listPublicAvailabilitiesByDoctor } from "../../api/public";

function dateToYmd(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function nextFiveDates(): string[] {
  const today = new Date();
  return Array.from({ length: 5 }).map((_, index) => {
    const d = new Date(today);
    d.setDate(today.getDate() + index);
    return dateToYmd(d);
  });
}

function dateChipLabel(dateValue: string, index: number): string {
  if (index === 0) {
    return "Today";
  }
  if (index === 1) {
    return "Tomorrow";
  }
  const date = new Date(dateValue);
  return date.toLocaleDateString(undefined, { weekday: "short", day: "2-digit", month: "short" });
}

function formatTimeLabel(value: string): string {
  const [hours, minutes] = value.split(":");
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
}

export function DoctorProfilePage() {
  const navigate = useNavigate();
  const { doctorId } = useParams();
  const parsedDoctorId = Number(doctorId);
  const dates = useMemo(() => nextFiveDates(), []);
  const [selectedDate, setSelectedDate] = useState<string>(dates[0] ?? "");

  const doctorQuery = useQuery({
    queryKey: ["public", "doctor", parsedDoctorId],
    queryFn: () => getPublicDoctor(parsedDoctorId),
    enabled: Number.isInteger(parsedDoctorId) && parsedDoctorId > 0
  });

  const slotsQuery = useQuery({
    queryKey: ["public", "doctor-slots", parsedDoctorId, selectedDate],
    queryFn: () => listPublicAvailabilitiesByDoctor(parsedDoctorId, selectedDate, true),
    enabled: Number.isInteger(parsedDoctorId) && parsedDoctorId > 0 && selectedDate.length > 0
  });

  return (
    <main className="mx-auto max-w-6xl p-4 md:p-8">
      <div className="mb-5 flex items-center justify-between">
        <Link className="text-sm font-medium text-emerald-700 hover:underline" to="/doctors">
          ← Back to Doctors
        </Link>
      </div>

      {doctorQuery.isLoading ? (
        <section className="animate-pulse rounded-2xl border bg-white p-6 shadow-sm">
          <div className="h-8 w-64 rounded bg-slate-200" />
          <div className="mt-3 h-4 w-40 rounded bg-slate-200" />
          <div className="mt-2 h-4 w-48 rounded bg-slate-200" />
          <div className="mt-4 h-4 w-full rounded bg-slate-200" />
        </section>
      ) : null}
      {doctorQuery.isError ? (
        <section className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
          Unable to load doctor details.
        </section>
      ) : null}
      {doctorQuery.data ? (
        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-slate-900">{doctorQuery.data.full_name}</h1>
          <p className="mt-2 text-slate-600">{doctorQuery.data.qualification ?? "Consultant"}</p>
          <p className="mt-1 text-sm text-slate-500">
            {doctorQuery.data.specialization_names.join(", ") || "General Care"}
          </p>
          <p className="mt-4 text-sm text-slate-700">
            {doctorQuery.data.about?.trim() ? doctorQuery.data.about : "Doctor profile details will be updated soon."}
          </p>
        </section>
      ) : null}

      <section className="mt-6 rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Select date (next 5 days)</h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {dates.map((date, index) => (
            <button
              key={date}
              className={`rounded-md border px-4 py-2 text-sm ${selectedDate === date ? "border-emerald-500 bg-emerald-50 text-emerald-800" : "border-slate-300 hover:border-emerald-300"}`}
              type="button"
              onClick={() => setSelectedDate(date)}
            >
              {dateChipLabel(date, index)}
            </button>
          ))}
        </div>

        <h3 className="mt-6 text-lg font-semibold text-slate-900">Slots</h3>
        {slotsQuery.isLoading ? (
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <article key={index} className="animate-pulse rounded-lg border p-4">
                <div className="h-5 w-32 rounded bg-slate-200" />
                <div className="mt-2 h-4 w-24 rounded bg-slate-200" />
                <div className="mt-3 h-9 w-28 rounded bg-slate-200" />
              </article>
            ))}
          </div>
        ) : null}
        {slotsQuery.isError ? (
          <p className="mt-2 text-sm text-red-600">Could not load slots for this doctor right now.</p>
        ) : null}
        {!slotsQuery.isLoading && (slotsQuery.data ?? []).length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No slots available for this day.</p>
        ) : null}
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {(slotsQuery.data ?? []).map((slot) => (
            <article key={slot.availability_id} className="rounded-lg border p-4">
              <p className="font-medium text-slate-900">
                {formatTimeLabel(slot.slot_start_time)} - {formatTimeLabel(slot.slot_end_time)}
              </p>
              <p className="mt-1 text-sm text-slate-600">{slot.available_date}</p>
              <p
                className={`mt-2 inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                  slot.slot_status === "AVAILABLE"
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {slot.slot_status === "AVAILABLE" ? "Available" : "Booked"}
              </p>
              <button
                className={`mt-3 rounded-md px-3 py-2 text-sm font-medium text-white ${
                  slot.slot_status === "AVAILABLE"
                    ? "bg-emerald-600 hover:bg-emerald-700"
                    : "bg-amber-600 hover:bg-amber-700"
                }`}
                type="button"
                onClick={() =>
                  navigate(`/book?availabilityId=${slot.availability_id}&doctorId=${slot.doctor_user_id}`)
                }
              >
                {slot.slot_status === "AVAILABLE" ? "Book this slot" : "Join Waiting List"}
              </button>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
