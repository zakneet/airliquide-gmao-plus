# Base de Données

**Projet :** AirLiquide GMAO+

Version : 1.0

---

# Objectif

Cette base de données permet de gérer le cycle de vie complet des dispositifs médicaux, depuis leur réception jusqu'à leur remise en stock.

---

# Vue d'ensemble

Le système est organisé autour d'une entité principale :

Machine

Toutes les autres informations sont rattachées à cette machine.

---

# Entités principales

## Utilisateur

Responsable de l'authentification.

Attributs

- id
- prénom
- nom
- email
- mot_de_passe
- rôle
- actif
- date_creation

---

## Machine

Entité principale.

Attributs

- id
- numéro_serie
- code_interne
- type_machine
- marque
- modèle
- état_actuel
- commercial
- biohazard
- état_visuel
- commentaire
- date_retour
- créé_par
- créé_le

---

## HistoriqueMachine

Chaque changement est enregistré.

Attributs

- id
- machine
- utilisateur
- ancienne_étape
- nouvelle_étape
- commentaire
- date

---

## Diagnostic

Attributs

- id
- machine
- technicien
- commentaire
- date

---

## CataloguePanne

Liste officielle des pannes.

Exemple

- Compresseur
- Batterie
- Turbine
- Carte mère
- Electrovanne
- Carte O₂
- Afficheur

---

## PanneDétectée

Attributs

- id
- diagnostic
- panne
- gravité
- commentaire

---

## CataloguePièce

Liste officielle des pièces.

- référence
- nom
- fabricant
- compatible

---

## PièceRemplacée

Attributs

- id
- réparation
- pièce
- quantité

---

## Réparation

Attributs

- id
- machine
- technicien
- début
- fin
- durée
- commentaire

---

## ContrôleQualité

Attributs

- id
- machine
- technicien
- résultat
- commentaire
- date

---

## Stock

Attributs

- id
- machine
- emplacement
- disponible
- date

---

## Photo

Toutes les images sont centralisées.

- id
- machine
- type
- chemin
- date

---

# Relations

Utilisateur

↓

Machine

↓

Diagnostic

↓

Pannes

↓

Réparation

↓

Pièces remplacées

↓

Contrôle Qualité

↓

Stock

---

# Principe

Une machine possède UNE SEULE fiche.

Toutes les interventions viennent enrichir cette fiche.

Aucune donnée n'est dupliquée.

---

# Traçabilité

Chaque modification est enregistrée.

Le système doit toujours répondre à ces questions :

- Qui ?
- Quand ?
- Pourquoi ?
- Quelle machine ?
- Quelle intervention ?
- Quel résultat ?

---

# Évolutions futures

Cette base permet d'ajouter sans modification majeure :

- Maintenance préventive
- QR Code
- IA
- Notifications
- Pièces détachées
- Gestion multi-sites
- Gestion multi-pays

---

# Mise à jour (étape 2) : Appareil vs Dossier SAV

Le modèle implémenté sépare l'appareil physique de ses retours :

- `Device` (app `inventory`) : une seule fiche par numéro de série (normalisé en majuscules, sans espaces), code interne `APP-000001`.
- `DossierSAV` (app `maintenance`) : un retour SAV (`SAV-2026-00001`). Un seul dossier ouvert par appareil (contrainte en base).
- `StatusHistory` : journal immuable (utilisateur, date/heure, ancien/nouveau statut, commentaire).

Statuts, dans l'ordre : `RECU → DESINFECTE → DIAGNOSTIC_TERMINE → REPARE → QC_VALIDE → EN_STOCK → LIVRE`.
Seule l'avancée d'une étape est permise ; le retour d'une étape est réservé au Responsable SAV avec commentaire obligatoire.
Hypothèse provisoire : les prérequis métier de chaque transition (désinfection renseignée, QC validé, etc.) seront ajoutés avec les étapes 4 à 8.
