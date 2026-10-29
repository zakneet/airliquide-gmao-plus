# Audit et préparation du rapport de stage : AirLiquide GMAO+

**Étape 1 sur la rédaction du rapport.** Document de préparation, rédigé en français. Aucun chapitre du rapport n'est rédigé ici.
**Date de l'audit :** 28 octobre 2026. **Échéance du rapport :** vendredi 30 octobre 2026 (soit 2 jours).
**Périmètre :** lecture seule du dépôt et des documents. Aucun code, aucune dépendance, aucun schéma ni aucun test n'a été modifié ; rien n'a été supprimé ni committé. Aucune valeur secrète n'a été lue ni recopiée.

> Convention de lecture : **[V]** fait vérifié dans le dépôt ou un document fourni ; **[É]** information donnée par l'étudiant, non vérifiable seule ; **[?]** information manquante ou non confirmée.

---

## 1. Inventaire de l'espace de travail et des références

### 1.1 Dépôt
| Élément | Constat |
|---|---|
| Racine | `C:\Users\GIGABYTE\Documents\AirLiquideGMAO\airliquide-gmao-plus` [V] |
| Dépôt distant | `github.com/zakneet/airliquide-gmao-plus` (branches `main` et `develop` poussées) [V] |
| Branche courante | `develop` ; arbre de travail propre au moment de l'audit [V] |
| Historique | 31 commits (Conventional Commits) ; dates de commits : 15 et 16 juillet 2026 (documentation), puis 14, 27 et 28 octobre 2026 (développement) [V] |
| Branches locales | `main`, `develop`, plusieurs branches `feature/*` et `chore/*` déjà fusionnées [V] |
| Dossiers | `backend/`, `frontend/`, `docs/` ; `mobile/` **absent** [V] |
| Conteneurisation | `docker-compose.yml` ne définit que la base PostgreSQL 16 ; **aucun** `Dockerfile` pour l'application [V] |
| Intégration continue | aucun fichier `.github/workflows` [V] |

### 1.2 Documents du projet présents
| Document | Contenu | Statut |
|---|---|---|
| `README.md` | présentation, galerie de 16 captures, pile technique | [V] |
| `docs/00_VISION.md`, `01_CAHIER_DES_CHARGES.md`, `02_OBJECTIFS.md` | vision, besoins, objectifs | [V] |
| `docs/03_WORKFLOW.md`, `04_USE_CASES.md`, `05_ARCHITECTURE.md`, `06_BASE_DE_DONNEES.md` | workflow, cas d'utilisation, architecture, base de données | [V] ; certains contenus sont des intentions de conception, voir 3 |
| `docs/07_API.md`, `08_DEMARRAGE.md`, `09_QUESTIONNAIRE_ET_JOURNAL.md` | API, démarrage, questionnaire et journal | [V] |
| `frontend/DESIGN.md` | choix de design de l'interface | [V] |
| `docs/diagrams/` | `architecture.puml` (20 lignes), `erd.md` (24 lignes) ; `use_case.puml`, `workflow.puml`, `sequence_reception.puml` **vides (0 ligne)** | [V] |
| `docs/screenshots/` | 16 captures (desktop et mobile), données de démonstration fictives | [V] |
| `AirLiquideGMAO\Documents\cahier des charges vf.pdf` et `cahier des charges.pdf` | cahier des charges fonctionnel (texte extrait) | [V] |
| `AirLiquideGMAO\Documents\1.jpg`, `2.jpg`, `3.jpg` | captures du Google Sheet « GMAO v1 » (onglets RETURNS, DISINFECTION, MAINTENANCE_JOURNAL, LISTS, PM_LOG, CM_LOG et un onglet commençant par « P ») | [V] |
| Photo du « Journal de maintenance des équipements O2, VNI, CPAP et respirateur » (réf. 404, rév. 1, 15/04/2021) et capture du questionnaire de retour en ligne | images transmises dans la conversation, **non présentes dans le dépôt** | [É] à copier dans le dossier du rapport |

### 1.3 Références de mise en forme du rapport
| Fichier attendu | Résultat |
|---|---|
| `docs/rapport-stage/references/version finale du rapport.pdf` | **Absent.** Le dossier `docs/rapport-stage/` n'existait pas (créé avec ce fichier). Aucun PDF de rapport antérieur (ni celui de l'Hôpital La Rabta) n'a été trouvé dans les emplacements inspectés. |
| `docs/rapport-stage/references/rapport_stage_vf.zip` | **Absent à l'emplacement prévu**, mais **trouvé ailleurs** : `C:\Users\GIGABYTE\Documents\rapport-airl\mayssa\Nouveau dossier\rapport_stage_vf.zip` (3,2 Mo) et son dossier décompressé `rapport_stage_vf\`. Il s'agit d'un modèle LaTeX d'un autre étudiant (stage de technicien, juillet 2026, société Smart Med / med.tn). **Utilisé uniquement pour la mise en forme.** |
| Dossier de travail alternatif | `C:\Users\GIGABYTE\Documents\rapport-airl\zakaria-rapport` : existe, **vide**. |
| Autres fichiers candidats, **non ouverts** | `Documents\lettre d affectation\lettre d affectation.pdf` et `Documents\2emec2s\stage\Formulaire-stage-de-technicien-CI-GBM (1).docx` : documents personnels et administratifs pouvant fournir dates, encadrants et exigences. Je ne les ai pas ouverts sans votre accord (voir section 7). |

---

## 2. Architecture réelle du projet [V]

### 2.1 Pile technique (relevée dans `requirements.txt`, `package.json` et `docker-compose.yml`)
| Couche | Technologies et versions |
|---|---|
| Backend | Python 3.10, Django 5.2.16, Django REST Framework 3.17.1, `djangorestframework-simplejwt` 5.5.1, `drf-spectacular` 0.30.0, `django-cors-headers` 4.9.0, Pillow 12.3.0, `psycopg2-binary` 2.9.12, `python-dotenv` 1.2.2 |
| Base de données | PostgreSQL 16 (conteneur Docker) ; SQLite en repli pour le développement (variable `DB_ENGINE`) |
| Frontend | Next.js 16.4.3, React 19.3.0, TypeScript 5, Tailwind CSS 4, shadcn/ui, `@base-ui/react`, `lucide-react`, `sonner`, polices IBM Plex auto-hébergées |
| Authentification | JWT : jeton d'accès en mémoire côté navigateur, jeton de rafraîchissement en cookie `HttpOnly` ; limitation de débit à la connexion |
| Documentation API | OpenAPI / Swagger (`/api/docs/`) |
| Mobile | Flutter **prévu**, aucun code |

Les affirmations « Next.js, TypeScript, Tailwind, Django REST Framework, PostgreSQL 16, Docker » sont donc **confirmées**, avec la nuance que Docker ne sert qu'à la base de données.

### 2.2 Organisation du code
- **Backend** (`backend/`) : applications `accounts` (utilisateurs, rôles, JWT), `inventory` (types, marques, modèles, appareils), `maintenance` (dossiers SAV, étapes, services métier, catalogues), `dashboard` (indicateurs), `reports` (exports et journal) ; `common` existe mais est vide.
- **Principe de conception** : logique métier dans `maintenance/services.py` (transitions, prérequis, atomicité), permissions dédiées (`accounts/permissions.py`), validation dans les sérialiseurs, vues fines.
- **Modèles de données** (21 classes dont 2 énumérations) : `User`, `DeviceType`, `Brand`, `DeviceModel`, `Device`, `ReturnDeclaration`, `DossierSAV`, `StatusHistory`, `Fault`, `Part`, `Disinfection`, `Diagnosis`, `DetectedFault`, `Repair`, `ReplacedPart`, `QualityControl`, `StockMovement`, `Delivery`, `Photo`, et les énumérations `VisualCondition`, `BiohazardStatus`.
- **Frontend** (`frontend/src/`) : pages `/login`, `/` (tableau de bord), `/returns`, `/reception`, `/dossiers`, `/dossiers/[id]`, `/devices`, `/devices/[id]`, `/stock`, `/journal`, `/reports` ; composants `kit.tsx`, `step-forms.tsx`, `command-palette.tsx`.
- **Taille du code** (mesure du 28 octobre 2026, hors migrations et dépendances) : environ 2 200 lignes Python et 2 400 lignes TypeScript/TSX. À ne citer que comme ordre de grandeur, avec la méthode.

### 2.3 Règles métier effectivement codées [V]
- Un appareil physique = une fiche unique (numéro de série normalisé, code interne `APP-000001`) ; un appareil peut avoir plusieurs dossiers SAV ; **un seul dossier ouvert par appareil** (contrainte en base).
- Statuts : `RECU → DESINFECTE → DIAGNOSTIC_TERMINE → REPARE → QC_VALIDE → EN_STOCK → LIVRE`. Aucun saut possible ; chaque étape exige son enregistrement ; le recul est réservé au Responsable SAV avec commentaire ; un dossier livré ne se rouvre pas.
- Historique des statuts **immuable** (modification et suppression refusées).
- Contrôle qualité : checklist fixe de 7 points ; un contrôle non conforme exige un commentaire et bloque la mise en stock.
- Risque biologique déduit du questionnaire (statut « Inconnu » traité comme un risque).
- Rôles : `TECHNICIEN` et `RESPONSABLE_SAV` ; catalogues en écriture réservée au Responsable ; exports CSV des dossiers réservés au Responsable.

---

## 3. Matrice des fonctionnalités : preuves et niveau de vérification

Légende : **A** = implémenté et vérifié ; **B** = implémenté, non vérifié par test automatisé ; **C** = prévu ou partiel ; **D** = introuvable dans le dépôt.

### 3.1 Tests réellement disponibles
- **Backend : 49 tests automatisés, tous réussis** (exécution du 28 octobre 2026 sur SQLite). Les mêmes 49 tests avaient aussi réussi sur **PostgreSQL 16** plus tôt dans la session (33 tests lors de la première validation, puis 49 après l'ajout du questionnaire et du journal). Une nouvelle exécution sur PostgreSQL n'a pas pu aboutir le jour de l'audit : le moteur Docker renvoyait une erreur.
- Répartition : 12 tests dans `accounts/tests.py` (authentification, permissions, cookie, limitation de débit) et 37 dans `maintenance/tests.py` (workflow, étapes, photos, questionnaire, journal, tableau de bord, exports).
- **Frontend : aucun test automatisé.** Contrôles disponibles : vérification de types TypeScript, lint (0 erreur), compilation de production réussie, captures d'écran.

### 3.2 Tableau de synthèse
| Fonctionnalité | Niveau | Preuve |
|---|---|---|
| Authentification JWT, cookie HttpOnly, déconnexion, limitation de débit | A | tests `accounts` |
| Rôles et permissions (technicien / responsable, catalogues, exports) | A | tests `accounts` et `maintenance` |
| Administration des utilisateurs par API | A | tests `accounts` ; **pas d'écran dédié** dans le frontend (accès via l'API ou l'administration Django) |
| Référentiel appareils (types, marques, modèles) | A pour l'API ; C pour l'interface | API testée ; aucun écran de gestion des catalogues |
| Fiche de vie unique par appareil, réutilisée à chaque retour | A | tests `maintenance` |
| Dossier SAV, un seul dossier ouvert par appareil | A | contrainte en base + tests |
| Règles de transition et prérequis par étape | A | tests `maintenance` |
| Historique immuable | A | test dédié |
| Questionnaire de retour avant arrivée, rattachement à la réception | A | tests `maintenance` |
| Désinfection, diagnostic (catalogue de pannes par type), réparation (pièces, durée) | A | tests `maintenance` |
| Contrôle qualité (checklist, pureté, débit/pression, alarme) | A | tests `maintenance` |
| Stock livrable et mouvements ; livraison | A | tests `maintenance` |
| Photos (JPEG/PNG/WebP, 5 Mo, contenu vérifié) | A | tests `maintenance` |
| Journal de maintenance (12 colonnes du registre papier), export CSV | A pour les données ; B pour l'écran et l'impression | tests + captures |
| Tableau de bord (indicateurs) | A pour l'API ; B pour l'affichage | test + capture |
| Interface web (16 écrans capturés, mobile adapté) | B | build, lint, captures ; aucun test automatisé |
| Recherche rapide (Ctrl + K) | B | capture ; aucun test |
| Documentation API (Swagger) | B | page servie (code 200) |
| Exécution sur PostgreSQL 16 | A (avant l'incident Docker du jour) | tests réussis sur PostgreSQL pendant la session |
| Rapports **PDF** (prévus au cahier des charges et au premier README) | **C/D** | **non implémentés** : exports CSV uniquement |
| Types d'appareils BiPAP, respirateurs, aspirateurs médicaux (cahier des charges) | C | catalogue configurable ; la démonstration ne charge que 3 types |
| Maintenance préventive (onglet PM_LOG), correctives (CM_LOG), type de service RM/PM/CT, propriété IMMO/SAV, date du prochain service (Google Sheet « GMAO v1 ») | **D** | colonnes observées dans le Google Sheet, **absentes de l'application** |
| Application mobile Flutter | D | dossier `mobile/` absent |
| Dockerisation de l'application, CI/CD | D | non trouvés |
| Déploiement, utilisation en production, adoption par Air Liquide | D | **aucune preuve** |
| Mesure du temps de saisie inférieur à une minute (exigence du cahier des charges) | D | **jamais mesuré** |
| Évaluation par des utilisateurs réels | D | aucune trace |

---

## 4. Conventions de mise en forme réutilisables (modèle LaTeX trouvé)

Seules les conventions de présentation sont retenues ; aucun texte, nom, fait, résultat ni capture du modèle n'est repris.

| Élément | Convention observée |
|---|---|
| Classe et format | `report`, 12 pt, A4, recto seul |
| Marges et interligne | 2,5 cm de chaque côté ; interligne 1,5 ; petit espacement entre paragraphes |
| Langue et polices | français (`babel`), police Latin Modern |
| Couleur d'accent | bleu RGB (0, 114, 188) pour les titres de chapitres et de sections |
| Titres | chapitre en grand, gras, accent, « Chapitre N » ; section en gras de grande taille, accent ; sous-section en gras, noir |
| En-tête / pied de page | en-tête : titre du chapitre à gauche, mention du type de rapport à droite, filet fin ; pied de page : numéro centré |
| Pagination | chiffres romains pour les pages préliminaires, chiffres arabes à partir de l'introduction |
| Page de garde | mention officielle (République Tunisienne, ministère de l'Enseignement supérieur et de la Recherche scientifique), logo de l'établissement à gauche et de l'organisme d'accueil à droite, université et établissement, **titre encadré par deux filets accentués**, blocs « Réalisé par » (nom, niveau, spécialité) et « Encadrant professionnel » (nom, organisme), période du stage, année universitaire |
| Pages préliminaires | page de garde, remerciements, résumé, table des matières, liste des abréviations (tableau à deux colonnes) |
| Table des matières | profondeur 1 : chapitres et sections ; liens cliquables |
| Corps | introduction (contexte, missions et objectifs, organisation du rapport), **5 chapitres**, conclusion ; titres de sections courts |
| Figures et tableaux | tableaux : légende **au-dessus** ; figures : légende **en dessous** ; libellé de légende en gras, corps plus petit ; images placées à l'endroit exact ; tableaux pouvant se poursuivre sur la page suivante |
| Diagrammes | produits à part puis insérés en PDF ; code source des diagrammes conservé dans un dossier distinct |
| Bibliographie | liste manuelle numérotée, intitulée « Bibliographie et webographie », avec adresse web et date de consultation |
| Annexes | à la fin, après la bibliographie |
| Attention | le modèle porte la mention « Rapport de stage **technicien** » : à adapter au type exact de rapport demandé (voir section 7) |

Le livrable final étant un fichier Word, ces conventions seront reproduites avec les styles de Word (styles de titres, numérotation automatique, table des matières automatique, légendes automatiques).

---

## 5. Plan du rapport proposé (à ajuster selon les consignes de l'institut)

Les contenus de présentation d'Air Liquide Tunisie, du service d'accueil et des dates ne peuvent être rédigés qu'avec des informations confirmées (section 7).

| Partie | Objectif | Matière disponible |
|---|---|---|
| **Pages préliminaires** : page de garde, remerciements, résumé et mots-clés (français), abstract et keywords (anglais, si l'institut l'exige), table des matières, liste des figures, liste des tableaux, liste des abréviations | présenter et situer le rapport | informations administratives à fournir |
| **Introduction générale** | contexte du stage, problématique, missions, organisation du rapport | CDC, vision, objectifs |
| **Chapitre 1 : Présentation d'Air Liquide Tunisie et du cadre du stage** | situer l'organisme, le service Maintenance / SAV, le déroulement du stage | **à rédiger à partir de sources officielles citées et de vos informations** ; rien d'inventé |
| **Chapitre 2 : Contexte et analyse de l'existant** | décrire le circuit actuel (saisie papier, puis report dans Google Sheets), les outils observés (journal papier réf. 404, questionnaire en ligne, classeur « GMAO v1 »), les limites | photos du journal et des feuilles, CDC |
| **Chapitre 3 : Analyse des besoins et conception** | acteurs, besoins fonctionnels et non fonctionnels, cas d'utilisation, workflow, modèle de données, architecture, choix techniques, sécurité | docs 00 à 06, diagrammes (à compléter), pile technique vérifiée |
| **Chapitre 4 : Réalisation d'AirLiquide GMAO+** | environnement, backend (services, API, permissions), frontend (parcours, design, accessibilité), questionnaire de retour et journal, démarche de développement (Git, branches, commits) | code, docs 07 à 09, `DESIGN.md`, captures |
| **Chapitre 5 : Tests, résultats, limites et discussion** | 49 tests backend, contrôles frontend, démonstration sur données fictives, limites honnêtes, écarts avec le cahier des charges et avec le classeur existant | résultats de la section 3 |
| **Conclusion générale et perspectives** | bilan, apport personnel, suites possibles (rapports PDF, maintenance préventive, mobile, déploiement, tests utilisateurs) | section 3 (éléments C et D) |
| **Bibliographie et webographie** | sources citées (documentation officielle des technologies, normes si réellement utilisées) | à constituer ; ne citer que des sources effectivement consultées |
| **Annexes** | routes de l'API, modèle de données, captures complémentaires, extraits significatifs de tests, planification | docs 06 et 07, `docs/screenshots` |

Remarque sur la longueur : avec l'échéance du 30 octobre, un rapport d'environ 30 à 40 pages, structuré comme ci-dessus, est réaliste ; à confirmer avec le format exigé par l'institut.

---

## 6. Illustrations et preuves exploitables

| Illustration | Source | Utilisation proposée | Remarque |
|---|---|---|---|
| 16 captures de la plateforme (connexion, tableau de bord, retours annoncés, réception, dossiers, dossiers à plusieurs étapes, appareils, fiche de vie, stock, journal, rapports, recherche rapide, deux vues mobiles) | `docs/screenshots/` | chapitre 4 et annexes | **données fictives** ; légender comme telles |
| Résultat des 49 tests | exécution du 28 octobre 2026 | chapitre 5 | à refaire en sortie juste avant la remise ; produire une capture du terminal |
| Photo du journal papier et capture du questionnaire en ligne | images de la conversation | chapitre 2 | **à copier dans le dossier du rapport** ; vérifier l'autorisation d'Air Liquide et masquer les données sensibles |
| Captures du classeur Google « GMAO v1 » (3 images) | `AirLiquideGMAO\Documents\*.jpg` | chapitre 2 | contiennent des numéros de série qui paraissent réels : **à flouter ou remplacer** |
| Diagramme d'architecture | `docs/diagrams/architecture.puml` | chapitre 3 | à redessiner proprement |
| Diagramme entité-relation | `docs/diagrams/erd.md` (24 lignes) | chapitre 3 | **incomplet** par rapport aux 21 classes réelles : à régénérer |
| Diagrammes de cas d'utilisation, de workflow et de séquence | fichiers `.puml` **vides** | chapitre 3 | **à créer** |
| Cahier des charges | PDF « cahier des charges vf » | chapitre 3 et annexe | extraire les exigences et les comparer à la réalisation |

Incohérences documentaires à corriger ou à signaler :
- `docs/05_ARCHITECTURE.md` écrit « AirLiquide GMA+ » et décrit Docker et Flutter comme s'ils faisaient partie de l'architecture ; la section 3 précise ce qui est réellement réalisé.
- Le cahier des charges et le premier README annonçaient des « rapports PDF » : seul le CSV existe.
- `docs/06_BASE_DE_DONNEES.md` décrit initialement une entité « Machine » unique ; l'implémentation sépare **appareil** et **dossier SAV** (l'ajout correspondant est documenté en fin de fichier).

---

## 7. Informations manquantes, par ordre d'importance

1. **Consignes officielles de l'ISTMT** : type de rapport (stage de technicien, stage d'ingénieur, projet de fin d'études), nombre de pages, gabarit imposé, éléments obligatoires (liste des figures, abstract en anglais, etc.). Le modèle trouvé s'intitule « stage technicien ».
2. **Informations administratives** : dates exactes du stage et durée, nom et fonction de l'encadrant professionnel, nom de l'encadrant académique, intitulé exact du service d'accueil, année universitaire, titre définitif du rapport. Les documents « lettre d'affectation » et « Formulaire de stage de technicien » semblent les contenir : **autorisez-vous leur lecture, ou pouvez-vous les copier dans `docs/rapport-stage/ressources/` ?**
3. **Chronologie réelle du stage** : le classeur Google contient des lignes datées de mai 2026, le journal papier est daté du 14/07/2026, les documents du dépôt du 15 juillet 2026 et le développement du code d'octobre 2026. Il faut établir clairement quand le stage a eu lieu et quand chaque travail a été réalisé.
4. **Présentation d'Air Liquide Tunisie et du service Maintenance / SAV** : sources que vous souhaitez utiliser (site officiel, documents internes autorisés) et ce que vous avez réellement observé. Sans cela, ce chapitre ne sera pas inventé mais volontairement limité aux faits fournis.
5. **Rôle exact de l'étudiant** : tâches menées, ce qui a été fait seul ou avec d'autres, outils d'assistance utilisés (à mentionner honnêtement si l'institut l'exige).
6. **Signification des termes du classeur existant** : RM, PM, CT (types de service), IMMO / SAV (propriété), C.H, « Doc de sortie PR », PM_LOG, CM_LOG. Mes hypothèses actuelles (compteur horaire, document de sortie de pièces) sont à confirmer.
7. **Statut réel de l'application** : maquette de démonstration, prototype validé par un responsable, ou version essayée par des techniciens ? Aucune preuve d'essai ou d'adoption n'existe dans le dépôt.
8. **Autorisation de publication** des documents et captures d'Air Liquide (journal papier, classeur) et règles de confidentialité.
9. **Images supplémentaires utiles** : logo de l'établissement et logo de l'organisme (si autorisé), photo de la zone de travail ou d'un appareil si permise, éventuelle attestation de stage.
10. **Étendue des mesures à présenter** : temps de saisie, retours d'utilisateurs, retour d'un responsable. Aucune mesure n'existe aujourd'hui.

### Fichiers à fournir ou à confirmer
- `version finale du rapport.pdf` (rapport de l'Hôpital La Rabta), s'il doit servir de référence ; **introuvable** sur l'ordinateur.
- Copier le modèle `rapport_stage_vf.zip` dans `docs/rapport-stage/references/` si ce doit être l'emplacement de référence (il est actuellement dans `rapport-airl\mayssa\Nouveau dossier\`).
- Consignes de l'institut (PDF ou texte), lettre d'affectation et formulaire de stage.
- Photos du journal papier et du questionnaire en ligne (fichiers d'origine).
- Logos autorisés.

---

## 8. Avertissements : faits à ne pas inventer

- Ne **pas** affirmer que l'application est déployée, utilisée en production ou adoptée par Air Liquide.
- Ne **pas** inventer l'histoire de l'entreprise, des chiffres, des procédures internes, des statistiques d'activité, des modèles ou marques d'appareils, des noms d'encadrants, des dates de stage, ni des gains mesurés (temps gagné, erreurs évitées).
- Ne **pas** présenter les fonctions « prévues » (rapports PDF, maintenance préventive, mobile, Docker pour l'application, CI/CD) comme réalisées.
- Ne **pas** attribuer à Air Liquide des exigences ou des normes non confirmées ; ne pas affirmer de conformité à une norme ou à une certification sans vérification (le dépôt n'en apporte aucune preuve).
- Ne **pas** recopier de texte, de faits, de captures ou de résultats du modèle d'un autre étudiant (Smart Med / med.tn) ni d'autres rapports.
- Ne **pas** publier de numéros de série réels ni de données internes visibles sur les captures du classeur : les remplacer par des valeurs fictives ou les flouter.
- Les captures du dossier `docs/screenshots/` montrent des **données de démonstration** : les légender ainsi.
- Les chiffres de tests (49) doivent être **relancés avant remise** et cités avec la date et l'environnement.

---

## 10. Mise à jour du 28 octobre 2026 (après approbation de l'étudiant)

- **Informations fournies par l'étudiant [É]** : stage du **1er juillet au 1er août 2026** ; application **testée par des techniciens et validée**. Ces deux informations sont reprises dans le rapport mais **ne sont pas vérifiables** dans le dépôt.
- **Point de vigilance** : l'historique Git montre la documentation les 15 et 16 juillet 2026, puis le développement du code les 14, 27 et 28 octobre 2026, donc après la période de stage. L'étudiant doit préciser quelle version a été testée et à quelle date (section 4.3 du rapport laissée à compléter).
- **Modèle officiel trouvé** : `C:\Users\GIGABYTE\Documents\template stage\Template _Rapport_Stage_technicien.docx`. Il impose : page de garde, remerciements, résumé (10 à 15 lignes, 3 à 5 mots-clés, abstract conseillé), table des matières automatique, liste des figures et tableaux, introduction, **4 chapitres** (présentation de l'entreprise ; contexte et objectifs ; travaux réalisés ; résultats et bilan), conclusion, annexes, bibliographie. Ce plan **remplace** celui à 5 chapitres proposé en section 5.
- **Avertissement du modèle** : le rapport doit être un travail personnel fidèle à l'expérience vécue ; tout plagiat est sanctionné.
- **Source de conception** : la conversation avec un assistant conversationnel (architecture modulaire orientée domaine, base de données, ERD, diagrammes) documente l'origine de la conception ; elle est mentionnée dans le rapport comme outil d'assistance.
- **Livrable généré** : `docs/rapport-stage/Rapport_Stage_AirLiquide_GMAO+.docx` (voir `outils/` pour la reproduction).

---

## 9. Confirmation de langue

Ce document d'audit, le plan de rapport proposé et la liste des informations manquantes sont rédigés **en français**. Les identifiants techniques (noms de fichiers, routes, noms de classes, technologies) sont conservés dans leur forme d'origine. **Aucun chapitre du rapport n'a été rédigé** et aucun fichier DOCX n'a été généré.

**Prochaine étape (après votre approbation) :** trame détaillée, puis rédaction chapitre par chapitre en français, puis assemblage du document Word.
