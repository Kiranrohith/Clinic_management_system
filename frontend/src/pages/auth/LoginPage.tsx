import { useQuery } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { getPublicClinicSettings } from "../../api/public";
import { login } from "../../api/auth";
import { useAuth } from "../../hooks/useAuth";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required")
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const { setSession } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const clinicSettingsQuery = useQuery({
    queryKey: ["public", "clinic-settings"],
    queryFn: getPublicClinicSettings
  });
  const clinicName = clinicSettingsQuery.data?.clinic_name || "CarePoint Clinic";
  const clinicHours =
    clinicSettingsQuery.data?.opening_time && clinicSettingsQuery.data?.closing_time
      ? `${clinicSettingsQuery.data.opening_time} to ${clinicSettingsQuery.data.closing_time}`
      : "08:00 AM to 08:00 PM";
  const clinicSupport = [
    clinicSettingsQuery.data?.clinic_phone || "+91 98765 43210",
    clinicSettingsQuery.data?.clinic_email || "support@carepointclinic.com"
  ].join(" • ");
  const clinicAddress = clinicSettingsQuery.data?.clinic_address || "12 Health Avenue, City Center";
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  });

  const onSubmit = async (values: LoginFormValues) => {
    setError(null);

    try {
      const result = await login(values);
      setSession(result.access_token, result.refresh_token, result.user);

      const role = result.user.role_name;
      if (role === "ADMIN") navigate("/management/admin");
      else if (role === "FRONTDESK") navigate("/management/frontdesk");
      else if (role === "DOCTOR") navigate("/management/doctor");
      else throw new Error("Unsupported role.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-emerald-50 px-4 py-10 md:px-8">
      <section className="mx-auto grid w-full max-w-5xl overflow-hidden rounded-2xl border bg-white shadow-lg md:grid-cols-[1.1fr_1fr]">
        <div className="bg-gradient-to-br from-emerald-700 via-emerald-600 to-teal-700 p-8 text-white md:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100">{clinicName}</p>
          <h1 className="mt-3 text-3xl font-bold leading-tight">Compassion in care. Precision in every appointment.</h1>
          <p className="mt-4 text-sm text-emerald-50">
            Welcome to the clinic management portal. Please sign in with your official credentials to continue.
          </p>
          <div className="mt-8 grid gap-3 text-sm">
            <article className="rounded-lg border border-white/25 bg-white/10 p-3 backdrop-blur-sm">
              <p className="font-semibold">Clinic Timings</p>
              <p className="text-emerald-50">Mon - Sat • {clinicHours}</p>
            </article>
            <article className="rounded-lg border border-white/25 bg-white/10 p-3 backdrop-blur-sm">
              <p className="font-semibold">Support Desk</p>
              <p className="text-emerald-50">{clinicSupport}</p>
            </article>
            <article className="rounded-lg border border-white/25 bg-white/10 p-3 backdrop-blur-sm">
              <p className="font-semibold">Location</p>
              <p className="text-emerald-50">{clinicAddress}</p>
            </article>
          </div>
        </div>
        <div className="p-8 md:p-10">
          <h2 className="mb-1 text-2xl font-semibold text-slate-900">Management Login</h2>
          <p className="mb-5 text-sm text-slate-600">Enter your email and password to access your dashboard.</p>
          <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <input
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
                placeholder="Email"
                type="email"
                {...register("email")}
              />
              {errors.email ? <p className="mt-1 text-sm text-red-600">{errors.email.message}</p> : null}
            </div>
            <div>
              <input
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none ring-emerald-500 focus:ring"
                placeholder="Password"
                type="password"
                {...register("password")}
              />
              {errors.password ? <p className="mt-1 text-sm text-red-600">{errors.password.message}</p> : null}
            </div>
            <button
              className="w-full rounded-md bg-emerald-600 px-3 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign In"}
            </button>
          </form>
          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        </div>
      </section>
    </main>
  );
}
