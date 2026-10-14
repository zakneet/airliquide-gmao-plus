"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState, type ReactNode } from "react";
import { api, auth } from "@/lib/api";
import type { User } from "@/lib/types";

const NAV = [
  { href: "/", label: "Tableau de bord" },
  { href: "/reception", label: "Nouveau retour" },
  { href: "/dossiers", label: "Dossiers SAV" },
  { href: "/devices", label: "Appareils" },
  { href: "/stock", label: "Stock livrable" },
  { href: "/reports", label: "Rapports", responsable: true },
];

function Shell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const path = usePathname();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    auth.setUnauthorizedHandler(() => router.replace("/login"));
    api<User>("/auth/me/").then(setUser).catch(() => {});
    return () => auth.setUnauthorizedHandler(null);
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-50 md:flex">
      <aside className="border-b border-slate-200 bg-white md:w-60 md:border-b-0 md:border-r">
        <div className="px-4 py-4">
          <p className="text-lg font-bold text-sky-800">AirLiquide GMAO+</p>
          <p className="text-xs text-slate-500">{user ? user.first_name || user.email : "…"}</p>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-2 pb-2 md:flex-col md:overflow-visible">
          {NAV.filter((n) => !n.responsable || user?.role === "RESPONSABLE_SAV").map((n) => {
            const active = n.href === "/" ? path === "/" : path.startsWith(n.href);
            return (
              <Link key={n.href} href={n.href}
                className={`whitespace-nowrap rounded-md px-3 py-2 text-sm ${active ? "bg-sky-50 font-medium text-sky-800" : "text-slate-700 hover:bg-slate-100"}`}>
                {n.label}
              </Link>
            );
          })}
          <button onClick={async () => { await auth.logout(); router.replace("/login"); }}
            className="rounded-md px-3 py-2 text-left text-sm text-slate-600 hover:bg-slate-100">
            Déconnexion
          </button>
        </nav>
      </aside>
      <main className="mx-auto w-full max-w-5xl flex-1 space-y-4 p-4 md:p-6">{children}</main>
    </div>
  );
}

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<p className="p-8 text-slate-600">Chargement…</p>}>
      <Shell>{children}</Shell>
    </Suspense>
  );
}
