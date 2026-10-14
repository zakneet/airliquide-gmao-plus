const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, public data: unknown) {
    super(formatError(data));
  }
}

export function formatError(data: unknown): string {
  if (!data) return "Erreur inconnue.";
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.map(formatError).join(" ");
  if (typeof data === "object") {
    const o = data as Record<string, unknown>;
    if (typeof o.detail === "string") return o.detail;
    return Object.entries(o)
      .map(([k, v]) => `${k === "non_field_errors" ? "" : k + " : "}${formatError(v)}`)
      .join(" · ");
  }
  return String(data);
}

// L'access token reste en mémoire ; le refresh token est dans un cookie HttpOnly
// inaccessible au JavaScript (protection contre le vol de jeton par XSS).
let accessToken: string | null = null;
let onUnauthorized: (() => void) | null = null;

export const auth = {
  /** Tente de restaurer la session depuis le cookie (après rechargement de page). */
  async restore(): Promise<boolean> {
    return accessToken ? true : refresh();
  },
  async logout() {
    accessToken = null;
    await fetch(`${BASE}/auth/logout/`, { method: "POST", credentials: "include" }).catch(() => {});
  },
  setUnauthorizedHandler(fn: (() => void) | null) { onUnauthorized = fn; },
};

async function refresh(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/auth/refresh/`, { method: "POST", credentials: "include" });
    if (!res.ok) return false;
    accessToken = (await res.json()).access;
    return true;
  } catch {
    return false;
  }
}

export async function login(email: string, password: string) {
  const res = await fetch(`${BASE}/auth/login/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => null);
  if (res.status === 429) throw new ApiError(429, "Trop de tentatives. Réessayez dans une minute.");
  if (!res.ok) throw new ApiError(res.status, data?.detail ? "Identifiants invalides." : data);
  accessToken = data.access;
}

export async function api<T = unknown>(path: string, init: RequestInit & { json?: unknown } = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  const res = await fetch(`${BASE}${path}`, { ...init, headers, body, credentials: "include" });
  if (res.status === 401 && retry && (await refresh())) return api<T>(path, init, false);
  if (res.status === 401) {
    accessToken = null;
    onUnauthorized?.();
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, data);
  return data as T;
}

export async function downloadCsv(path: string, filename: string) {
  const res = await fetch(`${BASE}${path}`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    credentials: "include",
  });
  if (!res.ok) throw new ApiError(res.status, "Export refusé.");
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
