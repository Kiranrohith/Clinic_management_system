import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { listPublicDoctors, listPublicSpecializations } from "../../api/public";

export function DoctorsListPage() {
  const [selectedSpecializationId, setSelectedSpecializationId] = useState<number | null>(null);

  const doctorsQuery = useQuery({
    queryKey: ["public", "doctors"],
    queryFn: listPublicDoctors
  });
  const specializationsQuery = useQuery({
    queryKey: ["public", "specializations"],
    queryFn: listPublicSpecializations
  });

  const filteredDoctors = useMemo(() => {
    const doctors = doctorsQuery.data ?? [];
    if (selectedSpecializationId === null) {
      return doctors;
    }
    return doctors.filter((doctor) => doctor.specialization_ids.includes(selectedSpecializationId));
  }, [doctorsQuery.data, selectedSpecializationId]);

  return (
    <main className="mx-auto max-w-7xl p-4 md:p-8">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Find Specialists</p>
          <h1 className="text-2xl font-bold text-slate-900 md:text-3xl">Book with the right doctor</h1>
        </div>
        <Link className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100" to="/">
          Back to Home
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-[280px_1fr]">
        <aside className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Specializations</h2>
            <button
              className="text-sm font-medium text-emerald-700 hover:underline"
              type="button"
              onClick={() => setSelectedSpecializationId(null)}
            >
              Clear
            </button>
          </div>
          <div className="space-y-2">
            {(specializationsQuery.data ?? []).map((item) => (
              <button
                key={item.specialization_id}
                className={`w-full rounded-md border px-3 py-2 text-left text-sm ${selectedSpecializationId === item.specialization_id ? "border-emerald-500 bg-emerald-50 text-emerald-800" : "border-slate-200 hover:border-emerald-300"}`}
                type="button"
                onClick={() => setSelectedSpecializationId(item.specialization_id)}
              >
                {item.specialization_name}
              </button>
            ))}
          </div>
        </aside>

        <section>
          {doctorsQuery.isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <article key={index} className="animate-pulse rounded-xl border bg-white p-5 shadow-sm">
                  <div className="h-5 w-36 rounded bg-slate-200" />
                  <div className="mt-2 h-4 w-28 rounded bg-slate-200" />
                  <div className="mt-2 h-3 w-44 rounded bg-slate-200" />
                  <div className="mt-4 h-9 w-36 rounded bg-slate-200" />
                </article>
              ))}
            </div>
          ) : null}
          {doctorsQuery.isError ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Could not load doctors right now.
            </div>
          ) : null}
          {!doctorsQuery.isLoading && !doctorsQuery.isError && filteredDoctors.length === 0 ? (
            <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
              No doctors found for this specialization. Click <span className="font-semibold">Clear</span> to view all doctors.
            </div>
          ) : null}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredDoctors.map((doctor) => (
              <article key={doctor.doctor_user_id} className="rounded-xl border bg-white p-5 shadow-sm">
                <p className="font-semibold text-slate-900">{doctor.full_name}</p>
                <p className="mt-1 text-sm text-slate-600">{doctor.qualification ?? "Consultant"}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {doctor.specialization_names.join(", ") || "General Care"}
                </p>
                <p className="mt-2 text-sm text-slate-600">
                  {doctor.experience_years ? `${doctor.experience_years} years experience` : "Experienced specialist"}
                </p>
                <div className="mt-4">
                  <Link
                    className="inline-flex rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                    to={`/doctors/${doctor.doctor_user_id}`}
                  >
                    View Profile & Slots
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
