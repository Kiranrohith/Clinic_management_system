export function isValidPhoneNumber(value: string): boolean {
  return /^[0-9]{10}$/.test(value.trim());
}

export function isValidOptionalPhoneNumber(value: string): boolean {
  const normalized = value.trim();
  return normalized.length === 0 || isValidPhoneNumber(normalized);
}

function formatDateForInput(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function getDobMaxDate(): string {
  const maxDob = new Date();
  maxDob.setDate(maxDob.getDate() - 1);
  return formatDateForInput(maxDob);
}

export function isDobBeforeToday(value: string): boolean {
  const normalized = value.trim();
  if (normalized.length === 0) {
    return true;
  }

  const parts = normalized.split("-");
  if (parts.length !== 3) {
    return false;
  }
  const [year, month, day] = parts.map(Number);
  if (!Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day)) {
    return false;
  }

  const dob = new Date(year, month - 1, day);
  if (
    dob.getFullYear() !== year ||
    dob.getMonth() !== month - 1 ||
    dob.getDate() !== day
  ) {
    return false;
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dob < today;
}

export function isValidOtpCode(value: string): boolean {
  return /^[0-9]{4,10}$/.test(value.trim());
}
