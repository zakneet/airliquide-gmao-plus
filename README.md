# AirLiquide GMAO+

> Système intelligent de gestion de maintenance des dispositifs médicaux.

## Description

AirLiquide GMAO+ est une plateforme web et mobile destinée au département Maintenance d'Air Liquide.

Elle permet de gérer le cycle de vie complet d'un dispositif médical :

- Réception
- Désinfection
- Diagnostic
- Réparation
- Contrôle qualité
- Stock
- Livraison

L'objectif est de remplacer les formulaires papier, Google Forms et Google Sheets par une solution centralisée, moderne et sécurisée.

---

## Fonctionnalités

- Gestion des retours
- Gestion des équipements
- Diagnostic
- Réparation
- Contrôle qualité
- Stock
- Historique complet
- Tableau de bord
- Rapports (export CSV)
- Authentification

---

## Aperçu de la plateforme

Captures réalisées avec des **données de démonstration fictives**.

| | |
|---|---|
| ![Connexion](docs/screenshots/01-connexion.png) **Connexion** | ![Tableau de bord](docs/screenshots/02-tableau-de-bord.png) **Tableau de bord** |
| ![Retours annoncés](docs/screenshots/03-retours-annonces.png) **Retours annoncés** | ![Réception](docs/screenshots/04-reception.png) **Réception** |
| ![Dossiers](docs/screenshots/05-dossiers.png) **Dossiers SAV** | ![Contrôle qualité](docs/screenshots/06-dossier-controle-qualite.png) **Dossier : contrôle qualité** |
| ![Diagnostic](docs/screenshots/07-dossier-diagnostic.png) **Dossier : diagnostic** | ![Dossier livré](docs/screenshots/08-dossier-livre.png) **Dossier livré** |
| ![Appareils](docs/screenshots/09-appareils.png) **Appareils** | ![Fiche de vie](docs/screenshots/10-fiche-de-vie.png) **Fiche de vie** |
| ![Stock](docs/screenshots/11-stock-livrable.png) **Stock livrable** | ![Journal](docs/screenshots/12-journal-de-maintenance.png) **Journal de maintenance** |
| ![Rapports](docs/screenshots/13-rapports.png) **Rapports** | ![Palette](docs/screenshots/14-palette-de-commandes.png) **Recherche rapide (Ctrl+K)** |
| ![Mobile tableau de bord](docs/screenshots/15-mobile-tableau-de-bord.png) **Mobile : tableau de bord** | ![Mobile dossier](docs/screenshots/16-mobile-dossier.png) **Mobile : dossier** |

---

## Stack

Backend

- Django
- Django REST Framework
- PostgreSQL

Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui (voir `frontend/DESIGN.md`)

Mobile

- Flutter

---

## Documentation

- [Démarrage local](docs/08_DEMARRAGE.md)
- [API REST](docs/07_API.md)
- [Questionnaire de retour et journal](docs/09_QUESTIONNAIRE_ET_JOURNAL.md)
- [Workflow](docs/03_WORKFLOW.md) · [Base de données](docs/06_BASE_DE_DONNEES.md)

---

## Auteur

Zakaria Fekih Ahmed

Institut Supérieur des Technologies Médicales de Tunis

Cycle Ingénieur TTIS

2026