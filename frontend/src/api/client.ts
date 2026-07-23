import type { ApiResponse } from "../types/api";
import { getStoredAccessToken } from "../utils/storage";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean;
  signal?: AbortSignal;
};

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = false, signal } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };

  if (auth) {
    const token = getStoredAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal
  });

  const responseText = await response.text();
  let json: ApiResponse<T> | null = null;

  if (responseText) {
    try {
      json = JSON.parse(responseText) as ApiResponse<T>;
    } catch {
      if (!response.ok) {
        throw new Error(responseText);
      }
      throw new Error("Server returned an invalid JSON response.");
    }
  }

  if (!response.ok) {
    const message = json?.message || responseText || `Request failed with status ${response.status}.`;
    throw new Error(message);
  }

  if (!json) {
    throw new Error("Server returned an empty response.");
  }

  if (!json.success) {
    throw new Error(json.message || "Request failed.");
  }

  return json.data;
}
