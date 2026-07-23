export interface AdminDashboardData {
  management_users: number;
  doctors: number;
  frontdesk: number;
  patients: number;
  appointments: number;
}

export interface FrontdeskDashboardData {
  todays_appointments: number;
  todays_walkin_tokens: number;
  waiting_patients: number;
}

export interface DoctorDashboardData {
  todays_appointments: number;
  completed_appointments: number;
  pending_appointments: number;
  todays_walkin_tokens: number;
}
