"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState, type ReactNode } from "react";
import { Boxes, ClipboardPlus, FileText, FolderOpen, LayoutDashboard, LogOut, Package, type LucideIcon } from "lucide-react";
import { api, auth } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { User } from "@/lib/types";

const NAV: { href: string; label: string; Icon: LucideIcon; responsable?: boolean }[] = [
  { href: "/", label: "Tableau de bord", Icon: LayoutDashboard },
  { href: "/reception", label: "Nouveau retour", Icon: ClipboardPlus },
  { href: "/dossiers", label: "Dossiers SAV", Icon: FolderOpen },
  { href: "/devices", label: "Appareils", Icon: Boxes },
  { href: "/stock", label: "Stock livrable", Icon: Package },
  { href: "/reports", label: "Rapports", Icon: FileText, responsable: true },
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
    <div className="min-h-screen md:flex">
      <a href="#contenu" className="sr-only focus:not-sr-only focus:absolute focus:z-10 focus:bg-card focus:p-3">
        Aller au contenu
      </a>
      <aside className="border-b border-border bg-card md:sticky md:top-0 md:h-screen md:w-64 md:shrink-0 md:border-b-0 md:border-r">
        <div className="px-4 py-4">
          <p className="text-lg font-semibold text-primary">AirLiquide GMAO+</p>
          <p className="min-h-5 text-sm text-muted-foreground">
            {user ? user.first_name || user.email : ""}
            {user?.role === "RESPONSABLE_SAV" && " · Responsable SAV"}
          </p>
        </div>
        <nav aria-label="Navigation principale" className="flex gap-1 overflow-x-auto px-2 pb-2 md:flex-col md:overflow-visible">
          {NAV.filter((n) => !n.responsable || user?.role === "RESPONSABLE_SAV").map(({ href, label, Icon }) => {
            const active = href === "/" ? path === "/" : path.startsWith(href);
            return (
              <Link key={href} href={href} aria-current={active ? "page" : undefined}
                className={cn(
                  "flex min-h-11 items-center gap-2.5 whitespace-nowrap rounded-md px-3 text-sm",
                  active ? "bg-accent font-medium text-accent-foreground" : "text-foreground hover:bg-muted",
                )}>
                <Icon className="size-4 shrink-0" aria-hidden />{label}
              </Link>
            );
          })}
          <button
            onClick={async () => { await auth.logout(); router.replace("/login"); }}
            className="flex min-h-11 items-center gap-2.5 whitespace-nowrap rounded-md px-3 text-left text-sm text-muted-foreground hover:bg-muted md:mt-4">
            <LogOut className="size-4 shrink-0" aria-hidden />Déconnexion
          </button>
        </nav>
      </aside>
      <main id="contenu" className="mx-auto w-full max-w-5xl flex-1 space-y-5 px-4 py-5 md:px-8 md:py-8">{children}</main>
    </div>
  );
}

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<p className="p-8 text-muted-foreground">Chargement…</p>}>
      <Shell>{children}</Shell>
    </Suspense>
  );
}
