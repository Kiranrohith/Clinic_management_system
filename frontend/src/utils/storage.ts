const ACCESS_TOKEN_KEY = "clinic_access_token";
const REFRESH_TOKEN_KEY = "clinic_refresh_token";
const USER_KEY = "clinic_auth_user";

export function setStoredSession(accessToken: string, refreshToken: string, userJson: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  localStorage.setItem(USER_KEY, userJson);
}

export function clearStoredSession(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getStoredUserJson(): string | null {
  return localStorage.getItem(USER_KEY);
}
