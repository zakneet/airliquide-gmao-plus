# Design : AirLiquide GMAO+

Contexte et choix de design du frontend. Sources d'inspiration lues : frontend-design (Anthropic), Impeccable,
ui-ux-pro-max, Emil Kowalski (détails d'interaction), taste-skill (contre-exemples de templates génériques).

## Sujet et utilisateurs
Atelier SAV de dispositifs médicaux. Utilisateurs : techniciens (gants possibles, éclairage variable, nombreux
dossiers par jour) et Responsable SAV (suivi, rapports). L'écran sert à **savoir quoi faire ensuite**, pas à séduire.

## Direction
« Instrument clinique » : fond blanc bleuté très léger, bleu pétrole sobre, aucune ombre, aucun dégradé,
rayon unique de 8 px, séparation par filets fins. Le contenu (identifiants, statuts, prochaine action) porte l'interface.

## Règles
- **Prochaine action d'abord** : le tableau de bord liste les dossiers ouverts avec l'étape suivante et l'ancienneté.
- **Statut = libellé + icône**, jamais la couleur seule (daltonisme, éclairage). Contrastes ≥ 4,5:1.
- **Cibles tactiles ≥ 44 px** pour tous les boutons et champs (gants, tablette d'atelier).
- **Identifiants en police monospace à chiffres alignés** (`.ident`) : numéros de série, codes internes, références.
- **Un seul mouvement utile** : retour de pression sur les boutons (`scale 0.97`, 120 ms), pas d'animation décorative.
  Respect de `prefers-reduced-motion`.
- **Libellés visibles** sur chaque champ, erreurs près du champ, `role="alert"` pour les erreurs globales.
- **Pas de gabarit générique** : pas d'étiquettes en capitales espacées, pas de cartes identiques en rafale pour le contenu en liste
  (listes en lignes denses avec filets), pas de numérotation décorative (le stepper représente une vraie séquence).

## Jetons (voir `src/app/globals.css`)
| Jeton | Usage |
|---|---|
| `primary` bleu pétrole | actions principales, navigation active |
| `ok` / `warn` / `danger` / `info` (+ `-soft`) | états métier (stock, QC non conforme, risque biologique, étape) |
| `border`, `input` | filets et contours de champs |
| `font-sans` Geist, `font-mono` Geist Mono | texte et identifiants |

## Composants
`src/components/ui/*` : primitives shadcn/ui (Button, Input, Textarea, Card, Badge, Label).
`src/components/kit.tsx` : composition métier (Card titrée, Field, Select natif, StatusBadge, Stepper, EmptyState).
Les `<select>` restent natifs : compatibles `FormData`, accessibles, clavier et mobile corrects.

## Limites
- Thème clair uniquement (atelier éclairé) ; le thème sombre n'est pas implémenté.
- Pas de bibliothèque d'icônes de marque : icônes `lucide-react` pour les états.
