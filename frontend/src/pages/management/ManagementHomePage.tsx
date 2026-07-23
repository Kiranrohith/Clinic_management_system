import { Link } from "react-router-dom";

export function ManagementHomePage() {
  return (
    <main className="mx-auto mt-14 max-w-4xl px-4 md:px-0">
      <section className="rounded-2xl border bg-white p-8 shadow-sm md:p-10">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-emerald-700">Clinic Management Portal</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900 md:text-4xl">Operations workspace for clinic staff</h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          This area is restricted to management users (admin, doctor, and frontdesk). Patients should continue on the public pages for booking and prescription access.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            className="inline-flex items-center rounded-md bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-700"
            to="/management/login"
          >
            Login to Management
          </Link>
          <Link className="inline-flex items-center rounded-md border border-slate-300 px-4 py-2 font-semibold text-slate-700 hover:bg-slate-100" to="/">
            Back to Public Website
          </Link>
        </div>
      </section>
      <div className="mt-6 grid gap-3 md:grid-cols-3">
        <article className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wider text-slate-500">Role</p>
          <p className="mt-1 text-sm font-semibold text-slate-900">Admin</p>
          <p className="mt-1 text-xs text-slate-600">Manage users, settings, slots, and clinic controls.</p>
        </article>
        <article className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wider text-slate-500">Role</p>
          <p className="mt-1 text-sm font-semibold text-slate-900">Frontdesk</p>
          <p className="mt-1 text-xs text-slate-600">Handle patients, bookings, cancellations, and walk-ins.</p>
        </article>
        <article className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wider text-slate-500">Role</p>
          <p className="mt-1 text-sm font-semibold text-slate-900">Doctor</p>
          <p className="mt-1 text-xs text-slate-600">Manage availability, appointments, and prescriptions.</p>
        </article>
      </div>
    </main>
  );
}
