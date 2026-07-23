import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";

import { logout } from "../api/auth";
import { useAuth } from "../hooks/useAuth";

type Props = {
  title: string;
  children?: ReactNode;
};

export function DashboardLayout({ title, children }: Props) {
  const navigate = useNavigate();
  const { clearSession, user } = useAuth();

  const onLogout = async () => {
    try {
      await logout();
    } finally {
      clearSession();
      navigate("/management/login");
    }
  };

  return (
    <main className="mx-auto max-w-5xl space-y-4 p-4">
      <header className="flex items-center justify-between rounded border bg-white p-4">
        <div>
          <h1 className="text-xl font-semibold">{title}</h1>
          <p className="text-sm text-slate-600">{user?.full_name}</p>
        </div>
        <button className="rounded border px-3 py-1 text-sm" onClick={onLogout} type="button">
          Logout
        </button>
      </header>
      {children}
    </main>
  );
}
