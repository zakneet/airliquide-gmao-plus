# Questionnaire de retour et journal de maintenance

Deux documents papier / Google Forms existants sont repris dans l'application.

## 1. Questionnaire de retour (avant l'arrivée de l'appareil)

Source : formulaire en ligne (Serial Number, Visual Condition, Missing Accessories, Return ID, Biohazard Status).

| Champ du formulaire | Champ GMAO+ | Valeurs |
|---|---|---|
| Serial Number | `serial_number` (normalisé : majuscules, sans espaces) | texte |
| Visual Condition | `visual_condition` | Bon état · Dégâts mineurs · Réparation nécessaire · Risque biologique |
| Missing Accessories | `missing_accessories` | texte libre |
| Return ID | `return_id` (unique) | texte |
| Biohazard Status | `biohazard_status` | Normal · Contamination importante · Inconnu |

Fonctionnement :
1. Un utilisateur connecté annonce le retour (menu **Retours annoncés**). L'annonce n'est pas encore un dossier SAV.
2. À l'arrivée, le technicien ouvre **Réception**, choisit le retour annoncé : les réponses sont reprises (modifiables). Le numéro de série est verrouillé sur celui annoncé.
3. Le dossier SAV est créé et rattaché à l'annonce. Une annonce ne peut être réceptionnée qu'une seule fois.
4. Le dossier est marqué **à risque biologique** si le statut biologique n'est pas « Normal » (« Inconnu » compte comme un risque) ou si l'état visuel est « Risque biologique ».

## 2. Journal de maintenance

Source : « Journal de maintenance des équipements O2, VNI, CPAP et respirateur » (registre papier, Réf. 404, Rév. 1).

| Colonne papier | Origine dans GMAO+ |
|---|---|
| Année, Mois | date de réception du dossier |
| Équip. / type | type d'appareil + modèle |
| N° série | appareil |
| C.H (compteur horaire) | saisi à la réception |
| Pureté | contrôle qualité (pureté O₂ en %, 0 à 100) |
| Débit / pression | contrôle qualité |
| Alarme sonore | contrôle qualité (conforme / non conforme / non testée) |
| Pannes | diagnostic (liste du catalogue, séparées par « + ») |
| Doc de sortie PR | réparation (référence du document de sortie des pièces) |
| Technicien | technicien de la réparation (à défaut, de la désinfection) |
| Date sortie | date de livraison |

Une ligne par dossier SAV, calculée à la volée : le journal ne peut donc pas diverger des dossiers.
Écran **Journal** : filtres année / mois / type / n° de série, impression, export CSV (`/api/reports/journal.csv`).

## Hypothèses à valider avec le service
- « C.H » = compteur horaire de l'appareil ; « Doc de sortie PR » = document de sortie de pièces de rechange.
- Pureté, débit/pression et alarme sont relevés lors du contrôle qualité final (le dernier contrôle fait foi).
- L'ID de retour est fourni par l'émetteur de l'annonce ; il doit être unique.
- Le formulaire en ligne semblait contenir d'autres questions sous « Biohazard Status » : à compléter si besoin.
- Les annonces sont créées par des utilisateurs connectés ; un lien public sans compte demanderait une conception sécurisée dédiée (anti-spam, validation).
