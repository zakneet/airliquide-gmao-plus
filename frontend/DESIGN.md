# Design : AirLiquide GMAO+

Contexte et choix de design du frontend. Sources lues et appliquées : frontend-design (Anthropic), Impeccable
(craft floor, polish, layout, delight), ui-ux-pro-max, Emil Kowalski (design engineering et mouvement), dataviz.

## Sujet, utilisateurs, mode
Atelier SAV de dispositifs médicaux. Utilisateurs : techniciens (gants possibles, éclairage variable, nombreux
dossiers par jour) et Responsable SAV. Mode **Operate** : la fiabilité et la prévisibilité priment ; le plaisir
se concentre sur les moments qui le méritent (étape validée, circuit de connexion).

## Monde visuel : « banc d'atelier médical »
- **Encre bleue** pour la navigation (`--ink`), **papier froid** pour le contenu, un seul bleu d'action (`--primary`).
- **Police** : IBM Plex Sans (texte) et IBM Plex Mono (identifiants uniquement). Chiffres tabulaires partout.
- **Profondeur** par filets de 1 px, pas d'ombre, pas de dégradé, rayon 8 px (12 px pour les dialogues).
- **États** : libellé + icône + couleur sémantique (`ok`, `warn`, `danger`, `info`), jamais la couleur seule.

## Structure
- **Tableau de bord** : pas de cartes de métriques. « Charge de l'atelier » = barres par poste, nommées par
  l'action attendue (À désinfecter, À diagnostiquer…), puis la file « À traiter en premier » (plus ancien d'abord),
  puis des faits en liste et les pannes les plus fréquentes.
- **Dossier** : un **parcours vertical** unique (réception → livraison). Les étapes faites se résument en place ;
  le formulaire de l'étape en cours s'ouvre à sa position. Colonne latérale : photos et historique.
- **Listes** : tableaux denses, identifiants en monospace, ancienneté lisible.
- **Palette de commandes** (Ctrl/Cmd + K) : retrouver un appareil par n° de série ou aller à une page.

## Mouvement (un moment signé par écran)
| Où | Quoi | Pourquoi |
|---|---|---|
| Tableau de bord | les barres montent depuis la ligne de base (`clip-path`, 640 ms, décalage 55 ms) | données qui arrivent |
| Dossier | la coche se dessine, l'étape suivante s'ouvre (`grid-template-rows`, 280 ms) | confirmation d'une action |
| Connexion | le circuit se trace une fois | identité du produit |
| Boutons | `scale(0.97)` à l'appui, 100 ms | réponse immédiate |
| Palette | aucune animation | déclenchée au clavier, répétée |

Courbe `cubic-bezier(0.23, 1, 0.32, 1)` ; jamais d'ease-in ; seulement `transform`, `opacity`, `clip-path`.
`prefers-reduced-motion` coupe tout.

## Accessibilité et ergonomie
Cibles ≥ 44 px, contrastes ≥ 4,5:1, libellés visibles, `aria-current` sur navigation et parcours,
lien d'évitement, focus visible, squelettes à dimensions réelles, toasts (Sonner) pour confirmer.
Surfaces du navigateur thématisées : sélection, curseur, barres de défilement, focus, soulignements.

## Limites
- Thème clair uniquement (atelier éclairé) ; les variantes `dark:` de shadcn sont neutralisées.
- Logo et couleurs de marque officiels non reproduits : charte graphique à fournir.
- Seuil « dossier ancien » = 72 h, hypothèse à valider avec le service.
