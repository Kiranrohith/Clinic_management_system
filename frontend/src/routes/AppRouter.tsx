import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { AdminHomePage } from "../pages/admin/AdminHomePage";
import { LoginPage } from "../pages/auth/LoginPage";
import { DoctorHomePage } from "../pages/doctor/DoctorHomePage";
import { FrontdeskHomePage } from "../pages/frontdesk/FrontdeskHomePage";
import { BookingPage } from "../pages/public/BookingPage";
import { BookingsHistoryPage } from "../pages/public/BookingsHistoryPage";
import { DoctorProfilePage } from "../pages/public/DoctorProfilePage";
import { DoctorsListPage } from "../pages/public/DoctorsListPage";
import { PrescriptionAccessPage } from "../pages/public/PrescriptionAccessPage";
import { PublicHomePage } from "../pages/public/PublicHomePage";
import type { UserRole } from "../types/auth";

type ProtectedRouteProps = {
  allow: UserRole[];
  children: ReactNode;
};

function ProtectedRoute({ allow, children }: ProtectedRouteProps) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/management/login" replace />;
  if (!allow.includes(user.role_name)) return <Navigate to="/management/login" replace />;
  return children;
}

export function AppRouter() {
  const { user } = useAuth();
  const homePath =
    user?.role_name === "ADMIN"
      ? "/management/admin"
      : user?.role_name === "FRONTDESK"
        ? "/management/frontdesk"
        : user?.role_name === "DOCTOR"
          ? "/management/doctor"
          : "/";

  return (
    <Routes>
      <Route path="/" element={<PublicHomePage />} />
      <Route path="/doctors" element={<DoctorsListPage />} />
      <Route path="/doctors/:doctorId" element={<DoctorProfilePage />} />
      <Route path="/book" element={<BookingPage />} />
      <Route path="/bookings" element={<BookingsHistoryPage />} />
      <Route path="/prescriptions" element={<PrescriptionAccessPage />} />
      <Route path="/management" element={user ? <Navigate to={homePath} replace /> : <LoginPage />} />
      <Route path="/management/login" element={<Navigate to="/management" replace />} />
      <Route
        path="/management/admin"
        element={
          <ProtectedRoute allow={["ADMIN"]}>
            <AdminHomePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/management/frontdesk"
        element={
          <ProtectedRoute allow={["FRONTDESK"]}>
            <FrontdeskHomePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/management/doctor"
        element={
          <ProtectedRoute allow={["DOCTOR"]}>
            <DoctorHomePage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to={user ? homePath : "/"} replace />} />
    </Routes>
  );
}
