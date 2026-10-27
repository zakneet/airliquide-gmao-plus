"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState, type ReactNode } from "react";
import {
  BookOpen, Boxes, ClipboardPlus, FileText, FolderOpen, LayoutDashboard, LogOut, Menu, Package,
  Search, Truck, X, type LucideIcon,
} from "lucide-react";
import { CommandPalette } from "@/components/command-palette";
import { api, auth } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { User } from "@/lib/types";

const NAV: { href: string; label: string; Icon: LucideIcon; responsable?: boolean }[] = [
  { href: "/", label: "Tableau de bord", Icon: LayoutDashboard },
  { href: "/returns", label: "Retours annoncés", Icon: Truck },
  { href: "/reception", label: "Réception", Icon: ClipboardPlus },
  { href: "/dossiers", label: "Dossiers SAV", Icon: FolderOpen },
  { href: "/devices", label: "Appareils", Icon: Boxes },
  { href: "/stock", label: "Stock livrable", Icon: Package },
  { href: "/journal", label: "Journal", Icon: BookOpen },
  { href: "/reports", label: "Rapports", Icon: FileText, responsable: true },
];

function Shell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const path = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    auth.setUnauthorizedHandler(() => router.replace("/login"));
    api<User>("/auth/me/").then(setUser).catch(() => {});
    return () => auth.setUnauthorizedHandler(null);
  }, [router]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const items = NAV.filter((n) => !n.responsable || user?.role === "RESPONSABLE_SAV");
  const initials = user ? (user.first_name?.[0] ?? user.email[0]).toUpperCase() : "";

  const nav = (
    <nav aria-label="Navigation principale" className="flex flex-col gap-0.5 px-3">
      {items.map(({ href, label, Icon }) => {
        const active = href === "/" ? path === "/" : path.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={() => setMenuOpen(false)}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex min-h-11 items-center gap-3 rounded-md px-3 text-sm transition-colors duration-150",
              active
                ? "bg-ink-active font-medium text-ink-foreground"
                : "text-ink-muted hover:bg-ink-active/60 hover:text-ink-foreground",
            )}
          >
            <Icon className="size-[18px] shrink-0" aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );

  const account = (
    <div className="mt-auto space-y-1 border-t border-white/10 p-3">
      <div className="flex items-center gap-3 px-3 py-2">
        <span
          aria-hidden
          className="grid size-8 shrink-0 place-items-center rounded-full bg-ink-active text-sm font-semibold text-ink-foreground"
        >
          {initials}
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-ink-foreground">
            {user ? user.first_name || user.email : "…"}
          </p>
          <p className="truncate text-xs text-ink-muted">
            {user?.role === "RESPONSABLE_SAV" ? "Responsable SAV" : user ? "Technicien" : ""}
          </p>
        </div>
      </div>
      <button
        onClick={async () => { await auth.logout(); router.replace("/login"); }}
        className="flex min-h-11 w-full items-center gap-3 rounded-md px-3 text-sm text-ink-muted transition-colors hover:bg-ink-active/60 hover:text-ink-foreground"
      >
        <LogOut className="size-[18px]" aria-hidden />Déconnexion
      </button>
    </div>
  );

  return (
    <div className="min-h-screen lg:flex">
      <a href="#contenu" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-card focus:p-3">
        Aller au contenu
      </a>

      {/* Barre mobile */}
      <header className="sticky top-0 z-30 flex h-14 items-center justify-between bg-ink px-4 text-ink-foreground lg:hidden print:hidden">
        <span className="font-semibold">AirLiquide GMAO+</span>
        <div className="flex items-center gap-1">
          <button aria-label="Rechercher" onClick={() => setPaletteOpen(true)}
            className="grid size-11 place-items-center rounded-md hover:bg-ink-active/60">
            <Search className="size-5" aria-hidden />
          </button>
          <button aria-label={menuOpen ? "Fermer le menu" : "Ouvrir le menu"} aria-expanded={menuOpen}
            onClick={() => setMenuOpen((o) => !o)}
            className="grid size-11 place-items-center rounded-md hover:bg-ink-active/60">
            {menuOpen ? <X className="size-5" aria-hidden /> : <Menu className="size-5" aria-hidden />}
          </button>
        </div>
      </header>
      {menuOpen && (
        <div className="z-20 flex flex-col bg-ink pb-2 lg:hidden print:hidden">
          {nav}
          {account}
        </div>
      )}

      {/* Barre latérale */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col bg-ink py-5 lg:flex print:hidden">
        <div className="px-6 pb-5">
          <p className="text-[1.05rem] font-semibold tracking-tight text-ink-foreground">AirLiquide GMAO+</p>
          <p className="text-xs text-ink-muted">Maintenance et SAV</p>
        </div>
        <div className="px-3 pb-4">
          <button
            onClick={() => setPaletteOpen(true)}
            className="flex h-10 w-full items-center gap-2.5 rounded-md border border-white/15 px-3 text-sm text-ink-muted transition-colors hover:border-white/30 hover:text-ink-foreground"
          >
            <Search className="size-4" aria-hidden />
            <span className="flex-1 text-left">Rechercher</span>
            <kbd className="rounded border border-white/20 px-1.5 text-[11px]">Ctrl K</kbd>
          </button>
        </div>
        {nav}
        {account}
      </aside>

      <main id="contenu" className="mx-auto w-full max-w-[1100px] flex-1 space-y-6 px-4 py-6 md:px-8 md:py-9">
        {children}
      </main>

      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        pages={items.map((n) => ({ href: n.href, label: n.label }))}
      />
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
