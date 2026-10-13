# API REST : AirLiquide GMAO+

Documentation interactive : `http://localhost:8000/api/docs/` (Swagger, générée par drf-spectacular).
Authentification : `Authorization: Bearer <access>` (JWT, obtenu sur `/api/auth/login/`).

| Méthode | Endpoint | Rôle | Description |
|---|---|---|---|
| POST | `/api/auth/login/` | public | e-mail + mot de passe → access/refresh |
| GET | `/api/auth/me/` | connecté | profil |
| CRUD | `/api/users/` | Responsable | administration utilisateurs |
| CRUD | `/api/device-types/`, `/brands/`, `/device-models/`, `/faults/`, `/parts/` | lecture : tous, écriture : Responsable | catalogues |
| GET | `/api/devices/?search=` | connecté | appareils |
| GET | `/api/devices/{id}/life-sheet/` | connecté | fiche de vie complète |
| GET | `/api/dossiers/?status=&device=` | connecté | liste des dossiers |
| GET | `/api/dossiers/{id}/` | connecté | dossier détaillé (toutes les étapes) |
| POST | `/api/dossiers/reception/` | connecté | retour SAV (crée ou retrouve l'appareil) |
| POST | `/api/dossiers/{id}/disinfection/` | connecté | RECU → DESINFECTE |
| POST | `/api/dossiers/{id}/diagnosis/` | connecté | DESINFECTE → DIAGNOSTIC_TERMINE |
| POST | `/api/dossiers/{id}/repair/` | connecté | DIAGNOSTIC_TERMINE → REPARE |
| POST | `/api/dossiers/{id}/quality-control/` | connecté | REPARE → QC_VALIDE (si conforme) |
| POST | `/api/dossiers/{id}/stock-entry/` | connecté | QC_VALIDE → EN_STOCK |
| POST | `/api/dossiers/{id}/delivery/` | connecté | EN_STOCK → LIVRE |
| POST | `/api/dossiers/{id}/transition/` | connecté / Responsable pour reculer | transition manuelle contrôlée |
| POST | `/api/dossiers/{id}/photos/` | connecté | téléversement (JPEG/PNG/WebP, 5 Mo) |
| GET | `/api/stock-movements/` | connecté | mouvements de stock |
| GET | `/api/dashboard/` | connecté | indicateurs |
| GET | `/api/reports/dossiers.csv` | Responsable | export CSV |

## Règles métier
- Chaque étape ne peut être enregistrée qu'au statut précédent ; aucun saut possible.
- Un contrôle qualité non conforme exige un commentaire, laisse le dossier à `REPARE` et bloque le stock ; un nouveau contrôle est possible.
- La checklist QC est fixe : Fonctionnement, Alarmes, Débit, Pression, Batterie, Affichage, Nettoyage.
- Le recul d'un statut est réservé au Responsable SAV (commentaire obligatoire) ; un dossier livré ne se rouvre pas.
- Les pannes du diagnostic doivent appartenir au type de l'appareil.
- Les entrées/sorties de stock sont déduites des étapes (une entrée et une sortie par dossier).

## Hypothèses provisoires
- Le contrôle qualité non conforme ne recule pas le statut automatiquement : le technicien corrige puis refait un contrôle.
- Une livraison enregistre le destinataire et un n° de bon libre.
- Les stocks de pièces détachées ne sont pas gérés (hors périmètre MVP).
