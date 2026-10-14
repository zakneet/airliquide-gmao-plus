export type Status =
  | "RECU" | "DESINFECTE" | "DIAGNOSTIC_TERMINE" | "REPARE" | "QC_VALIDE" | "EN_STOCK" | "LIVRE";

export const STATUSES: { value: Status; label: string }[] = [
  { value: "RECU", label: "Reçu" },
  { value: "DESINFECTE", label: "Désinfecté" },
  { value: "DIAGNOSTIC_TERMINE", label: "Diagnostic" },
  { value: "REPARE", label: "Réparé" },
  { value: "QC_VALIDE", label: "Qualité validée" },
  { value: "EN_STOCK", label: "En stock" },
  { value: "LIVRE", label: "Livré" },
];

export const NEXT_STEP: Record<Status, string> = {
  RECU: "Désinfecter l'appareil",
  DESINFECTE: "Réaliser le diagnostic",
  DIAGNOSTIC_TERMINE: "Enregistrer la réparation",
  REPARE: "Effectuer le contrôle qualité",
  QC_VALIDE: "Placer en stock livrable",
  EN_STOCK: "Livrer l'appareil",
  LIVRE: "Dossier terminé",
};

export const QC_CHECKLIST = ["Fonctionnement", "Alarmes", "Débit", "Pression", "Batterie", "Affichage", "Nettoyage"];

export interface User { id: number; email: string; first_name: string; last_name: string; role: "TECHNICIEN" | "RESPONSABLE_SAV" }
export interface Option { id: number; name: string }
export interface DeviceModel { id: number; brand: number; device_type: number; name: string }
export interface Fault { id: number; device_type: number; name: string; active: boolean }
export interface Part { id: number; reference: string; name: string }
export interface Device {
  id: number; internal_code: string; serial_number: string; device_type: number;
  type_name: string; model: number | null; model_name: string | null; created_at: string;
}
export interface HistoryItem {
  id: number; from_status: string; to_status: string; user_name: string; comment: string; at: string; dossier?: number;
}
export interface Dossier {
  id: number; reference: string; device: Device; status: Status; status_label: string;
  commercial: string; biohazard: boolean; visual_state: string; missing_accessories: string;
  comment: string; received_at: string;
  disinfection?: { product: string; validated: boolean; comment: string; technician_name: string; at: string } | null;
  diagnosis?: { comment: string; faults: { name: string; severity: string; comment: string }[] } | null;
  repair?: { started_at: string; ended_at: string; duration_minutes: number; tests: string; comment: string;
             parts: { reference: string; name: string; quantity: number }[] } | null;
  quality_controls?: { id: number; result: string; comment: string; at: string }[];
  stock_movements?: { id: number; kind: string; location: string; at: string }[];
  delivery?: { recipient: string; delivery_note: string; at: string } | null;
  photos?: { id: number; kind: string; image: string }[];
  history?: HistoryItem[];
}
export interface Paged<T> { results: T[] }
export interface DashboardData {
  by_status: Record<Status, number>; open_dossiers: number; in_stock: number; biohazard_open: number;
  avg_repair_minutes: number | null; qc_total: number; qc_failure_rate: number | null;
  top_faults: { name: string; count: number }[];
}
export interface LifeSheet { device: Device; dossiers: Dossier[]; timeline: HistoryItem[] }
