import { useMutation, useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";

import { listPublicDoctors, submitPublicContactQuery } from "../../api/public";

export function PublicHomePage() {
  const [contactForm, setContactForm] = useState({ full_name: "", phone: "", email: "", subject: "", message: "" });
  const [contactMessage, setContactMessage] = useState<string | null>(null);

  const doctorsQuery = useQuery({
    queryKey: ["public", "doctors"],
    queryFn: listPublicDoctors
  });

  const contactMutation = useMutation({
    mutationFn: () =>
      submitPublicContactQuery({
        full_name: contactForm.full_name.trim(),
        phone: contactForm.phone.trim(),
        email: contactForm.email.trim() || undefined,
        subject: contactForm.subject.trim() || undefined,
        message: contactForm.message.trim()
      }),
    onSuccess: () => {
      setContactMessage("Your message has been sent to our frontdesk team.");
      setContactForm({ full_name: "", phone: "", email: "", subject: "", message: "" });
    },
    onError: (error) => {
      setContactMessage(error instanceof Error ? error.message : "Failed to send contact request.");
    }
  });

  return (
    <main className="pb-20">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 md:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">CarePoint Clinic</p>
            <p className="text-sm text-slate-600">Modern outpatient care</p>
          </div>
          <div className="flex items-center gap-2">
            <Link className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100" to="/doctors">
              Book Appointment
            </Link>
            <Link className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100" to="/prescriptions">
              Prescriptions
            </Link>
            <Link className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100" to="/bookings">
              My Bookings
            </Link>
          </div>
        </div>
      </header>

      <section className="bg-gradient-to-r from-emerald-700 via-emerald-600 to-teal-700 px-4 py-16 text-white md:px-8">
        <div className="mx-auto grid max-w-6xl items-center gap-8 md:grid-cols-[1.2fr_1fr]">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-emerald-100">Clinic Appointment System</p>
            <h1 className="mt-3 text-4xl font-bold leading-tight md:text-5xl">Trusted specialists. Structured booking. Better care.</h1>
            <p className="mt-4 max-w-2xl text-emerald-50">
              Discover doctors by specialization, choose your preferred slot, and complete booking with secure OTP verification.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link className="rounded-md bg-white px-5 py-2.5 font-semibold text-emerald-800 hover:bg-emerald-50" to="/doctors">
                Start Booking
              </Link>
              <Link className="rounded-md border border-emerald-200 px-5 py-2.5 font-semibold text-white hover:bg-emerald-800/60" to="/prescriptions">
                Access Prescriptions
              </Link>
            </div>
          </div>
          <div className="grid gap-3 rounded-2xl border border-emerald-300/30 bg-white/10 p-5 text-sm backdrop-blur">
            <p className="font-semibold text-white">Patient-first workflow</p>
            <p className="text-emerald-50">• Filter doctors by specialization</p>
            <p className="text-emerald-50">• View next 5 days slot availability</p>
            <p className="text-emerald-50">• One-time OTP, 15-min booking session</p>
            <p className="text-emerald-50">• Existing/new patient smart handling</p>
          </div>
        </div>
      </section>

      <section className="mx-auto -mt-6 grid max-w-6xl gap-4 px-4 md:grid-cols-3 md:px-8">
        <article className="rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-semibold">Clinic Hours</h3>
          <p className="mt-2 text-sm text-slate-600">Mon - Sat: 08:00 AM to 08:00 PM</p>
        </article>
        <article className="rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-semibold">Location</h3>
          <p className="mt-2 text-sm text-slate-600">12, Health Avenue, City Center</p>
        </article>
        <article className="rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-semibold">Emergency Contact</h3>
          <p className="mt-2 text-sm text-slate-600">+91 98765 43210</p>
        </article>
      </section>

      <section className="mx-auto mt-10 max-w-6xl px-4 md:px-8">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">Featured Specialists</h2>
            <p className="mt-2 text-sm text-slate-600">Choose from our experienced doctors.</p>
          </div>
          <Link className="rounded-md border border-emerald-600 px-4 py-2 text-sm font-semibold text-emerald-700 hover:bg-emerald-50" to="/doctors">
            View All Doctors
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {doctorsQuery.isLoading
            ? Array.from({ length: 6 }).map((_, index) => (
                <article key={index} className="animate-pulse rounded-xl border bg-white p-5 shadow-sm">
                  <div className="h-5 w-36 rounded bg-slate-200" />
                  <div className="mt-2 h-4 w-28 rounded bg-slate-200" />
                  <div className="mt-2 h-3 w-44 rounded bg-slate-200" />
                  <div className="mt-3 h-8 w-24 rounded bg-slate-200" />
                </article>
              ))
            : (doctorsQuery.data ?? []).slice(0, 6).map((doctor) => (
                <article key={doctor.doctor_user_id} className="rounded-xl border bg-white p-5 shadow-sm transition hover:shadow">
                  <p className="font-semibold text-slate-900">{doctor.full_name}</p>
                  <p className="mt-1 text-sm text-slate-600">{doctor.qualification ?? "Consultant"}</p>
                  <p className="mt-1 text-xs text-slate-500">{doctor.specialization_names.join(", ") || "General Care"}</p>
                  <Link
                    className="mt-3 inline-flex rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                    to={`/doctors/${doctor.doctor_user_id}`}
                  >
                    View Profile
                  </Link>
                </article>
              ))}
        </div>
        {doctorsQuery.isError ? (
          <p className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            We could not load doctors right now. Please try again.
          </p>
        ) : null}
      </section>

      <section className="mx-auto mt-10 max-w-6xl px-4 md:px-8">
        <div className="rounded-2xl border bg-white p-6 shadow-sm md:p-8">
          <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">Contact us</h2>
          <p className="mt-2 text-sm text-slate-600">
            Have a question about booking or treatment? Our frontdesk will respond quickly.
          </p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <input
              className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
              placeholder="Full name"
              value={contactForm.full_name}
              onChange={(event) => setContactForm((prev) => ({ ...prev, full_name: event.target.value }))}
            />
            <input
              className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
              placeholder="Phone"
              value={contactForm.phone}
              onChange={(event) => setContactForm((prev) => ({ ...prev, phone: event.target.value }))}
            />
            <input
              className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
              placeholder="Email (optional)"
              value={contactForm.email}
              onChange={(event) => setContactForm((prev) => ({ ...prev, email: event.target.value }))}
            />
            <input
              className="rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
              placeholder="Subject (optional)"
              value={contactForm.subject}
              onChange={(event) => setContactForm((prev) => ({ ...prev, subject: event.target.value }))}
            />
          </div>
          <textarea
            className="mt-3 min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
            placeholder="Message"
            value={contactForm.message}
            onChange={(event) => setContactForm((prev) => ({ ...prev, message: event.target.value }))}
          />
          <button
            className="mt-4 rounded-md bg-slate-900 px-5 py-2.5 font-semibold text-white hover:bg-slate-700 disabled:opacity-60"
            type="button"
            disabled={contactMutation.isPending}
            onClick={() => {
              if (
                contactForm.full_name.trim().length < 2 ||
                contactForm.phone.trim().length < 7 ||
                contactForm.message.trim().length < 1
              ) {
                setContactMessage("Please fill in required contact details.");
                return;
              }
              setContactMessage(null);
              contactMutation.mutate();
            }}
          >
            {contactMutation.isPending ? "Sending..." : "Send message"}
          </button>
          {contactMessage ? <p className="mt-3 text-sm text-slate-700">{contactMessage}</p> : null}
        </div>
      </section>
    </main>
  );
}
