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

const store = {
  get: (k: string) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v); } catch {} },
  del: (k: string) => { try { localStorage.removeItem(k); } catch {} },
};

export const auth = {
  isLoggedIn: () => !!store.get("access"),
  logout: () => { store.del("access"); store.del("refresh"); },
};

async function refresh(): Promise<boolean> {
  const r = store.get("refresh");
  if (!r) return false;
  const res = await fetch(`${BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: r }),
  });
  if (!res.ok) return false;
  store.set("access", (await res.json()).access);
  return true;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, data?.detail ? "Identifiants invalides." : data);
  store.set("access", data.access);
  store.set("refresh", data.refresh);
}

export async function api<T = unknown>(path: string, init: RequestInit & { json?: unknown } = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  const token = store.get("access");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  const res = await fetch(`${BASE}${path}`, { ...init, headers, body });
  if (res.status === 401 && retry && (await refresh())) return api<T>(path, init, false);
  if (res.status === 401) {
    auth.logout();
    if (typeof window !== "undefined") window.location.href = "/login";
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, data);
  return data as T;
}

export async function downloadCsv(path: string, filename: string) {
  const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${store.get("access")}` } });
  if (!res.ok) throw new ApiError(res.status, "Export refusé.");
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
