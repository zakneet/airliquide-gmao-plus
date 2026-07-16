# Architecture Logicielle

**Projet :** AirLiquide GMAO+

**Version :** 1.0

---

# 1. Introduction

Ce document décrit l'architecture logicielle de l'application AirLiquide GMA+.

L'objectif est de concevoir une plateforme moderne, évolutive et maintenable permettant de gérer le cycle complet de maintenance des dispositifs médicaux.

L'architecture suit une approche client/serveur basée sur une API REST.

---

# 2. Architecture Générale

```
                    Utilisateurs

            ┌────────────────────┐
            │ Technicien         │
            │ Responsable SAV    │
            └─────────┬──────────┘
                      │
             Web / Mobile
                      │
        ┌─────────────▼─────────────┐
        │      Frontend (Next.js)   │
        │      Flutter Mobile       │
        └─────────────┬─────────────┘
                      │ REST API
        ┌─────────────▼─────────────┐
        │ Django REST Framework     │
        │ Business Logic            │
        │ Authentication            │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │ PostgreSQL                │
        └───────────────────────────┘
```

---

# 3. Architecture en couches

Le projet est composé de quatre couches.

## Présentation

Responsable de l'interface utilisateur.

Technologies :

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Flutter

---

## API

Responsable de la communication.

Technologies :

- Django REST Framework
- JWT Authentication

---

## Métier

Contient toutes les règles de gestion.

Exemples :

- Workflow des machines
- Gestion des états
- Validation des diagnostics
- Contrôle qualité
- Gestion des stocks

---

## Données

Responsable du stockage.

Technologies :

- PostgreSQL

---

# 4. Modules

Le backend sera organisé en plusieurs modules Django.

```
backend/

apps/

accounts/

machines/

returns/

diagnostics/

repairs/

quality/

inventory/

reports/

dashboard/

notifications/

common/
```

Chaque module possède :

- modèles
- serializers
- vues
- urls
- services
- permissions
- tests

---

# 5. Frontend

Le frontend sera organisé par fonctionnalités.

```
frontend/

app/

dashboard/

machines/

diagnostics/

repairs/

quality/

inventory/

settings/

components/

services/

hooks/

types/

utils/
```

---

# 6. Mobile

L'application Flutter utilisera la même API REST.

```
mobile/

lib/

features/

authentication/

machines/

diagnostic/

repair/

quality/

stock/

profile/

core/

shared/
```

---

# 7. Authentification

JWT Authentication.

Chaque utilisateur possède un rôle.

- Technicien
- Responsable SAV

Les permissions sont contrôlées côté serveur.

---

# 8. Communication

Toutes les communications passent par l'API REST.

```
Flutter

↓

HTTPS

↓

API Django

↓

PostgreSQL
```

Le frontend Web suit exactement le même principe.

---

# 9. Stockage des fichiers

Les photos seront enregistrées sur le serveur.

Structure :

```
media/

machines/

diagnostics/

repairs/

quality/
```

Les documents PDF seront générés automatiquement.

---

# 10. Journalisation

Chaque action utilisateur sera enregistrée.

Exemple :

- Création d'une machine
- Modification
- Diagnostic
- Réparation
- Contrôle qualité
- Entrée en stock

Le journal permettra une traçabilité complète.

---

# 11. Évolutivité

L'architecture est conçue pour intégrer facilement :

- QR Code
- Scanner Code-barres
- Notifications
- Signature numérique
- Maintenance préventive
- Intelligence Artificielle
- Tableau de bord avancé

sans modifier la structure principale.

---

# 12. Principes d'architecture

Le projet respecte les principes suivants :

- Séparation des responsabilités
- API First
- Modularité
- Réutilisabilité
- Traçabilité
- Évolutivité
- Sécurité
- Simplicité

---

# 13. Objectif

Construire une plateforme robuste, maintenable et évolutive répondant aux besoins du département Maintenance d'Air Liquide.