import { request } from "./client";
import type { AuthUser, LoginPayload, LoginResponse } from "../types/auth";

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  return request<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: payload
  });
}

export async function getMe(): Promise<AuthUser> {
  return request<AuthUser>("/api/v1/auth/me", { auth: true });
}

export async function logout(): Promise<void> {
  await request<{}>("/api/v1/auth/logout", { method: "POST", auth: true });
}

export async function changePassword(payload: { current_password: string; new_password: string }): Promise<void> {
  await request<{}>("/api/v1/auth/change-password", {
    method: "POST",
    auth: true,
    body: payload
  });
}
