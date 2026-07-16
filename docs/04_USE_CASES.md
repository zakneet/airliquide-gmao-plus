# Cas d'utilisation (Use Cases)

**Projet :** AirLiquide GMAO+

**Version :** 1.0

---

# 1. Introduction

Ce document décrit les interactions entre les utilisateurs et le système AirLiquide GMAO+.

L'objectif est de définir les fonctionnalités accessibles selon chaque rôle.

---

# 2. Acteurs

## Technicien Maintenance

Utilisateur principal.

Responsabilités :

- Réceptionner les machines
- Désinfecter les machines
- Réaliser les diagnostics
- Ajouter les pannes
- Effectuer les réparations
- Réaliser le contrôle qualité
- Envoyer les machines au stock
- Consulter l'historique

---

## Responsable SAV

Responsable du suivi.

Responsabilités :

- Consulter toutes les machines
- Rechercher une machine
- Consulter les statistiques
- Exporter les rapports
- Gérer les utilisateurs
- Gérer les catalogues

---

# 3. Cas d'utilisation

## UC-01

### Connexion

Acteur

- Technicien
- Responsable SAV

Description

L'utilisateur se connecte à l'application.

Préconditions

Compte valide.

Résultat

Accès au tableau de bord.

---

## UC-02

### Enregistrer un retour

Acteur

Technicien

Description

Créer la fiche d'une nouvelle machine.

Informations

- Numéro de série
- Commercial
- État visuel
- Biohazard
- Accessoires manquants
- Photos
- Commentaires

Résultat

Machine créée.

Statut :

RECU

---

## UC-03

### Rechercher une machine

Acteur

Technicien

Recherche par :

- Numéro de série
- QR Code
- Modèle
- Marque

Résultat

Ouverture immédiate de la fiche.

---

## UC-04

### Désinfecter

Acteur

Technicien

Action

Valider la désinfection.

Résultat

Statut

DESINFECTE

Historique mis à jour.

---

## UC-05

### Diagnostic

Acteur

Technicien

Actions

Ajouter

- Pannes
- Commentaires
- Photos

Résultat

Diagnostic enregistré.

---

## UC-06

### Réparation

Acteur

Technicien

Actions

Ajouter

- Pièces remplacées
- Temps d'intervention
- Commentaires

Résultat

Machine réparée.

---

## UC-07

### Contrôle Qualité

Acteur

Technicien

Checklist

- Fonctionnement
- Alarmes
- Débit
- Pression
- Batterie
- Affichage

Résultat

QC validé.

---

## UC-08

### Stock

Acteur

Technicien

Actions

Ajouter

- Emplacement
- Disponibilité

Résultat

Machine prête.

---

## UC-09

### Consulter l'historique

Acteur

Technicien

Description

Consulter toutes les opérations réalisées sur une machine.

Résultat

Chronologie complète.

---

## UC-10

### Tableau de bord

Acteur

Responsable SAV

Visualiser

- Nombre de machines
- Machines en diagnostic
- Machines en réparation
- Machines prêtes
- Temps moyen de réparation

---

## UC-11

### Générer un rapport

Acteur

Responsable SAV

Formats

- PDF
- Excel

---

## UC-12

### Administration

Acteur

Responsable SAV

Gestion

- Utilisateurs
- Types de machines
- Marques
- Modèles
- Catalogue des pannes
- Catalogue des pièces

---

# 4. Cas d'utilisation futurs

Version 2

- Scan QR Code automatique
- Signature numérique
- Notifications
- Maintenance préventive
- IA d'aide au diagnostic
- Gestion des pièces détachées
- Application mobile Flutter

---

# 5. Synthèse

Le système est conçu autour d'un acteur principal :

**Le Technicien Maintenance.**

Toutes les fonctionnalités doivent être optimisées afin de réduire le temps de saisie et garantir une traçabilité complète des dispositifs médicaux.
