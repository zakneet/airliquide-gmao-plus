"use client";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { CornerDownLeft, Search } from "lucide-react";
import { api } from "@/lib/api";
import type { Device } from "@/lib/types";

interface Props {
  open: boolean;
  onClose: () => void;
  pages: { href: string; label: string }[];
}

type Item = { key: string; label: string; hint: string; href: string; ident?: boolean };

/**
 * Palette de commandes : retrouver un appareil par n° de série ou aller à une page.
 * Action déclenchée au clavier, donc volontairement sans animation (Emil Kowalski).
 */
export function CommandPalette({ open, onClose, pages }: Props) {
  const router = useRouter();
  const ref = useRef<HTMLDialogElement>(null);
  const [q, setQ] = useState("");
  const [devices, setDevices] = useState<Device[]>([]);
  const [cursor, setCursor] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);

  useEffect(() => {
    const term = q.trim();
    if (term.length < 2) return;
    let alive = true;
    const t = setTimeout(() => {
      api<Device[]>(`/devices/?search=${encodeURIComponent(term)}`)
        .then((d) => alive && setDevices(d.slice(0, 6)))
        .catch(() => alive && setDevices([]));
    }, 180);
    return () => { alive = false; clearTimeout(t); };
  }, [q]);

  const items: Item[] = useMemo(() => {
    const term = q.trim().toLowerCase();
    const found: Item[] = (term.length >= 2 ? devices : []).map((d) => ({
      key: `d${d.id}`, label: d.serial_number, hint: `${d.type_name} · fiche de vie`,
      href: `/devices/${d.id}`, ident: true,
    }));
    const nav: Item[] = pages
      .filter((p) => !term || p.label.toLowerCase().includes(term))
      .map((p) => ({ key: p.href, label: p.label, hint: "Page", href: p.href }));
    return [...found, ...nav];
  }, [q, devices, pages]);

  function close() {
    setQ(""); setDevices([]); setCursor(0);
    onClose();
  }

  function go(item: Item | undefined) {
    if (!item) return;
    close();
    router.push(item.href);
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") { e.preventDefault(); setCursor((c) => Math.min(c + 1, items.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setCursor((c) => Math.max(c - 1, 0)); }
    else if (e.key === "Enter") { e.preventDefault(); go(items[cursor]); }
  }

  return (
    <dialog
      ref={ref}
      onClose={close}
      onClick={(e) => { if (e.target === ref.current) close(); }}
      aria-label="Recherche rapide"
      className="m-auto mt-[12vh] w-[min(92vw,560px)] rounded-xl border border-border bg-popover p-0 text-popover-foreground backdrop:bg-[oklch(0.2_0.05_258/0.45)]"
    >
      <div onKeyDown={onKeyDown}>
        <div className="flex items-center gap-3 border-b border-border px-4">
          <Search className="size-4 shrink-0 text-muted-foreground" aria-hidden />
          <input
            autoFocus
            value={q}
            onChange={(e) => { setQ(e.target.value); setCursor(0); }}
            placeholder="N° de série ou page…"
            aria-label="Rechercher un appareil ou une page"
            className="h-14 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground"
          />
          <kbd className="rounded border border-border px-1.5 py-0.5 text-xs text-muted-foreground">Échap</kbd>
        </div>
        <ul role="listbox" className="max-h-[50vh] overflow-y-auto p-2">
          {items.length === 0 && (
            <li className="px-3 py-6 text-center text-sm text-muted-foreground">Aucun résultat.</li>
          )}
          {items.map((it, i) => (
            <li key={it.key} role="option" aria-selected={i === cursor}>
              <button
                type="button"
                onMouseMove={() => setCursor(i)}
                onClick={() => go(it)}
                className={`flex min-h-11 w-full items-center justify-between gap-3 rounded-md px-3 text-left text-sm ${
                  i === cursor ? "bg-accent text-accent-foreground" : ""
                }`}
              >
                <span className={it.ident ? "ident font-medium" : "font-medium"}>{it.label}</span>
                <span className="flex items-center gap-2 text-xs text-muted-foreground">
                  {it.hint}
                  {i === cursor && <CornerDownLeft className="size-3.5" aria-hidden />}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </dialog>
  );
}
