const BOOKING_SESSION_TOKEN_KEY = "public_booking_session_token";
const BOOKING_SESSION_EXPIRES_AT_KEY = "public_booking_session_expires_at";
const BOOKING_SESSION_PHONE_KEY = "public_booking_session_phone";

export function setPublicBookingSession(token: string, phone: string, expiresInMinutes: number): void {
  const expiresAt = Date.now() + expiresInMinutes * 60 * 1000;
  localStorage.setItem(BOOKING_SESSION_TOKEN_KEY, token);
  localStorage.setItem(BOOKING_SESSION_EXPIRES_AT_KEY, String(expiresAt));
  localStorage.setItem(BOOKING_SESSION_PHONE_KEY, phone);
}

export function getPublicBookingSessionToken(): string | null {
  const token = localStorage.getItem(BOOKING_SESSION_TOKEN_KEY);
  const expiresAtRaw = localStorage.getItem(BOOKING_SESSION_EXPIRES_AT_KEY);
  if (!token || !expiresAtRaw) {
    return null;
  }
  const expiresAt = Number(expiresAtRaw);
  if (!Number.isFinite(expiresAt) || Date.now() >= expiresAt) {
    clearPublicBookingSession();
    return null;
  }
  return token;
}

export function getPublicBookingSessionPhone(): string | null {
  const token = getPublicBookingSessionToken();
  if (!token) {
    return null;
  }
  return localStorage.getItem(BOOKING_SESSION_PHONE_KEY);
}

export function getPublicBookingSessionRemainingSeconds(): number {
  const expiresAtRaw = localStorage.getItem(BOOKING_SESSION_EXPIRES_AT_KEY);
  if (!expiresAtRaw) {
    return 0;
  }
  const expiresAt = Number(expiresAtRaw);
  if (!Number.isFinite(expiresAt)) {
    clearPublicBookingSession();
    return 0;
  }
  const remainingMs = expiresAt - Date.now();
  if (remainingMs <= 0) {
    clearPublicBookingSession();
    return 0;
  }
  return Math.floor(remainingMs / 1000);
}

export function clearPublicBookingSession(): void {
  localStorage.removeItem(BOOKING_SESSION_TOKEN_KEY);
  localStorage.removeItem(BOOKING_SESSION_EXPIRES_AT_KEY);
  localStorage.removeItem(BOOKING_SESSION_PHONE_KEY);
}
