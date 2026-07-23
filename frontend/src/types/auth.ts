export type UserRole = "ADMIN" | "DOCTOR" | "FRONTDESK";

export interface AuthUser {
  user_id: number;
  full_name: string;
  email: string;
  role_name: UserRole;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
}
