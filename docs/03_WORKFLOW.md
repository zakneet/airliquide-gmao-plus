# Workflow de Maintenance

**Projet :** AirLiquide GMAO+

**Version :** 1.0

**Dernière mise à jour :** 15/07/2026

---

# 1. Objectif

Ce document décrit le cycle de vie complet d'un dispositif médical au sein du département Maintenance d'Air Liquide.

Chaque équipement suit un processus unique garantissant sa traçabilité depuis son retour jusqu'à sa remise en stock.

---

# 2. Workflow Global

```text
Retour Machine
      │
      ▼
Réception
      │
      ▼
Désinfection
      │
      ▼
Diagnostic
      │
      ▼
Réparation
      │
      ▼
Contrôle Qualité
      │
      ▼
Stock
      │
      ▼
Livraison
```

---

# 3. Description des étapes

## 3.1 Réception

Objectif :

Créer la fiche de vie de la machine.

Informations enregistrées :

- Numéro de série
- Type de machine
- Marque
- Modèle
- Commercial
- État visuel
- Accessoires manquants
- Biohazard Status
- Commentaires
- Photos

Statut :

`RECU`

---

## 3.2 Désinfection

Objectif :

Garantir que l'appareil peut être manipulé en sécurité.

Informations :

- Date
- Heure
- Technicien
- Validation

Statut :

`DESINFECTE`

---

## 3.3 Diagnostic

Objectif :

Identifier toutes les défaillances de la machine.

Informations :

- Pannes détectées
- Observations
- Commentaires
- Photos éventuelles

Exemple :

Concentrateur :

- Compresseur
- Carte O₂
- Electrovanne
- Tamis moléculaire
- Débitmètre
- Batterie

VNI / CPAP :

- Turbine
- Carte mère
- Batterie
- Écran
- Tactile
- Ventilateur

Statut :

`DIAGNOSTIC_TERMINE`

---

## 3.4 Réparation

Objectif :

Effectuer toutes les opérations nécessaires.

Informations :

- Pièces remplacées
- Temps d'intervention
- Commentaires
- Tests effectués

Statut :

`REPARE`

---

## 3.5 Contrôle Qualité

Objectif :

Vérifier que la machine respecte les exigences techniques.

Checklist :

- Fonctionnement
- Alarmes
- Débit
- Pression
- Batterie
- Affichage
- Nettoyage

Statut :

`QC_VALIDE`

---

## 3.6 Stock

Objectif :

Préparer la machine pour une future livraison.

Informations :

- Emplacement
- Date d'entrée
- Disponibilité

Statut :

`EN_STOCK`

---

# 4. Règles Métier

- Une machine possède une seule fiche de vie.
- Chaque étape est historisée.
- Aucun retour en arrière n'est possible sans autorisation.
- Toutes les modifications sont tracées.
- Les dates sont enregistrées automatiquement.
- Chaque action est associée à un utilisateur.

---

# 5. Historique

Chaque changement génère automatiquement un événement.

Exemple :

08:12 Réception

08:35 Désinfection

09:10 Diagnostic

09:45 Réparation

10:20 Contrôle Qualité

10:45 Stock

L'historique ne peut jamais être supprimé.

---

# 6. Objectif Final

Permettre à tout moment de répondre aux questions suivantes :

- Où se trouve la machine ?
- Qui travaille dessus ?
- Quelle est la panne ?
- Quelles pièces ont été remplacées ?
- Est-elle prête à être livrée ?
- Combien de temps a duré la réparation ?
