export function isValidPhoneNumber(value: string): boolean {
  const normalized = value.trim();
  return /^\+?[0-9]{7,15}$/.test(normalized);
}

export function isValidOtpCode(value: string): boolean {
  return /^[0-9]{4,10}$/.test(value.trim());
}
