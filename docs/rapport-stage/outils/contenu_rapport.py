"""Contenu du rapport, indépendant du format de sortie (Word ou LaTeX).
Le contenu est écrit une seule fois ; chaque backend (docx_lib, latex_lib) le met en forme."""
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def build(R, FIG):
    HEADER = "Rapport de stage technicien · AirLiquide GMAO+"
    # (page de garde : Word uniquement ; le LaTeX a sa propre page de garde)
    if R.kind == "docx":
        # =====================================================================================
        # PAGE DE GARDE
        # =====================================================================================
        R.first_section_clean()
        for t, size, bold in (
            ("République Tunisienne", 11, True),
            ("Ministère de l'Enseignement Supérieur et de la Recherche Scientifique", 11, True),
            ("Université de Tunis El Manar", 12, False),
            ("Institut Supérieur des Technologies Médicales de Tunis (ISTMT)", 12, False),
        ):
            para = R.p(f"**{t}**" if bold else t, align=WD_ALIGN_PARAGRAPH.CENTER, size=size, space_after=2)
        R.p("")
        R.p("")
        title = R.doc.add_paragraph("RAPPORT DE STAGE TECHNICIEN", style="Title")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        R.p("**AirLiquide GMAO+**", align=WD_ALIGN_PARAGRAPH.CENTER, size=22, space_after=4)
        R.p("Conception et réalisation d'une application web de gestion de la maintenance et du service après-vente "
            "des dispositifs médicaux respiratoires", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, space_after=30)
        for k, v in (
            ("Nom et prénom", "Zakaria Ali Fekih Ahmed"),
            ("Spécialité", "Technologies et Traitement de l'Information pour la Santé (TTIS), cycle ingénieur en génie biomédical"),
            ("Entreprise", "Air Liquide Tunisie, service Maintenance"),
            ("Encadrant professionnel", "M. Marouane Hassan, responsable génie biomédical"),
            ("Période du stage", "du 1er juillet au 1er août 2026"),
            ("Année universitaire", "2025/2026"),
        ):
            para = R.p(f"**{k} :** {v}", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
            para.paragraph_format.left_indent = Pt(60)


    # =====================================================================================
    # PAGES PRÉLIMINAIRES (chiffres romains)
    # =====================================================================================
    R.new_section("lowerRoman", 1, header_text=HEADER)
    R.h1("Remerciements", page_break=False)
    R.p("Au terme de ce stage effectué du 1er juillet au 1er août 2026 au sein d'Air Liquide Tunisie, je tiens à exprimer "
        "mes sincères remerciements à toutes les personnes qui ont contribué à son bon déroulement.")
    R.p("Je remercie tout particulièrement M. Marouane Hassan, responsable génie biomédical et mon encadrant au sein de "
        "l'entreprise, pour son accueil, sa disponibilité et la confiance qu'il m'a accordée. Mes remerciements vont aussi "
        "aux techniciens du service Maintenance, Fares et Maher, qui m'ont fait partager leur expérience de l'atelier, "
        "m'ont expliqué le circuit des appareils et ont testé l'application.")
    R.p("Je remercie également l'ensemble du corps enseignant de l'Institut Supérieur des Technologies Médicales de "
        "Tunis, et en particulier de la filière TTIS, pour la formation reçue.")
    R.p("Que toutes les personnes qui ont, de près ou de loin, contribué à ce travail trouvent ici l'expression de ma "
        "reconnaissance.")

    R.h1("Résumé")
    R.p("Ce rapport présente le stage de technicien effectué du 1er juillet au 1er août 2026 au sein du service "
        "Maintenance d'Air Liquide Tunisie, consacré aux équipements médicaux respiratoires (concentrateurs "
        "d'oxygène, appareils de ventilation non invasive et de pression positive continue). Les opérations de "
        "maintenance y étaient notées sur papier pendant la journée, puis reportées en fin de journée dans un classeur "
        "Google Sheets, ce qui entraînait une double saisie, une recherche lente et une traçabilité limitée.")
    R.p("L'objectif du stage était de concevoir et de réaliser AirLiquide GMAO+, une application web qui suit chaque "
        "appareil de son retour à sa livraison : réception, désinfection, diagnostic, réparation, contrôle qualité, "
        "stock et livraison. Le travail a comporté l'analyse de l'existant, la conception (workflow, modèle de données, "
        "architecture), puis la réalisation d'une API Django REST Framework, d'une base PostgreSQL et d'une interface "
        "Next.js. Chaque appareil dispose d'une fiche de vie unique, l'historique des statuts est immuable et les "
        "transitions sont contrôlées par des règles métier. Une suite de 49 tests automatisés valide ces règles, et "
        "l'application a été testée par des techniciens du service, qui l'ont validée.")
    R.p("**Mots-clés :** GMAO, maintenance, dispositifs médicaux, traçabilité, service après-vente, application web, "
        "Django, Next.js.")
    R.h2("Abstract")
    R.p("This report describes a technician internship carried out from 1 July to 1 August 2026 in the Maintenance / "
        "Maintenance department of Air Liquide Tunisia, which handles respiratory medical equipment. Maintenance work "
        "was recorded on paper and transferred to a shared spreadsheet at the end of each day, causing double entry "
        "and limited traceability. The internship aimed at designing and building AirLiquide GMAO+, a web application "
        "that follows each device from return to delivery (reception, disinfection, diagnosis, repair, quality "
        "control, stock and delivery). The solution relies on a Django REST Framework API, a PostgreSQL database and a "
        "Next.js interface. Each device has a single life record, the status history is immutable and workflow "
        "transitions are enforced by business rules, which 49 automated tests verify. The application was tested and "
        "validated by technicians of the department.")
    R.p("**Keywords:** CMMS, maintenance, medical devices, traceability, after-sales service, web application, Django, Next.js.")

    R.h1("Table des matières")
    R.toc('TOC \\o "1-3" \\h \\z \\u',
          "Clic droit sur cette ligne puis « Mettre à jour les champs » (ou Ctrl + A puis F9) pour afficher la table des matières.")
    R.h1("Liste des figures")
    R.toc('TOC \\h \\z \\c "Figure"', "Mettre à jour les champs (Ctrl + A puis F9) pour afficher la liste des figures.")
    R.h1("Liste des tableaux")
    R.toc('TOC \\h \\z \\c "Tableau"', "Mettre à jour les champs (Ctrl + A puis F9) pour afficher la liste des tableaux.")

    R.h1("Liste des abréviations")
    R.table(["Abréviation", "Signification"], [
        ["API", "Application Programming Interface (interface de programmation)"],
        ["CPAP", "Continuous Positive Airway Pressure (pression positive continue)"],
        ["CSV", "Comma-Separated Values (valeurs séparées par des virgules)"],
        ["GMAO", "Gestion de la maintenance assistée par ordinateur"],
        ["JWT", "JSON Web Token (jeton d'authentification)"],
        ["ORM", "Object-Relational Mapping (correspondance objet-relationnel)"],
        ["QC", "Quality Control (contrôle qualité)"],
        ["REST", "Representational State Transfer"],
        ["SAV", "Service après-vente"],
        ["VNI", "Ventilation non invasive"],
    ], "Liste des abréviations", widths=[3.5, 12.5])

    # =====================================================================================
    # CORPS (chiffres arabes)
    # =====================================================================================
    R.new_section("decimal", 1, header_text=HEADER)

    # ---------------------------------------------------------------- Introduction
    R.h1("Introduction générale", page_break=False)
    R.p("Les dispositifs médicaux respiratoires, tels que les concentrateurs d'oxygène, les appareils de ventilation non "
        "invasive (VNI) et les appareils à pression positive continue (CPAP), sont utilisés par des patients dont la "
        "santé dépend directement de leur bon fonctionnement. Leur maintenance doit donc être rigoureuse, mais aussi "
        "**traçable** : savoir à tout moment où se trouve un appareil, qui est intervenu, quelle panne a été constatée, "
        "quelles pièces ont été remplacées et si l'appareil a été contrôlé avant d'être remis à disposition.")
    R.p("Au sein du service Maintenance d'Air Liquide Tunisie, cette traçabilité reposait, au début du stage, sur "
        "des documents papier remplis pendant la journée, puis sur un classeur Google Sheets alimenté en fin de journée. "
        "Cette organisation, simple à mettre en place, présente des limites : double saisie, risque d'erreurs de "
        "retranscription, recherche lente d'un appareil et absence d'indicateurs d'activité.")
    R.p("Dans ce contexte, le stage a eu pour objectif de concevoir et de réaliser **AirLiquide GMAO+**, une application "
        "web de gestion de la maintenance qui remplace ces saisies par un suivi unique, rattaché à une fiche de vie "
        "durable pour chaque appareil. Ce rapport décrit la démarche suivie et les résultats obtenus.")
    R.p("Il est organisé en quatre chapitres. Le premier présente l'entreprise et le service d'accueil. Le deuxième "
        "décrit le contexte du stage, l'existant et les objectifs. Le troisième détaille les travaux réalisés : analyse, "
        "conception et réalisation de l'application. Le quatrième présente les résultats, les difficultés rencontrées, "
        "les limites et les perspectives. Une conclusion générale clôt le rapport.")

    # ---------------------------------------------------------------- Chapitre 1
    R.h1("Chapitre 1 : Présentation de l'entreprise")
    R.p("Ce chapitre situe Air Liquide Tunisie au sein du groupe Air Liquide, présente ses activités et décrit le service "
        "Maintenance dans lequel le stage s'est déroulé. Les informations générales proviennent des sites officiels du groupe ; "
        "la description du service repose sur les observations faites sur place.")
    R.h2("1.1 Le groupe Air Liquide")
    R.p("Air Liquide est un groupe industriel créé en 1902, à la suite des travaux de Georges Claude sur la liquéfaction de "
        "l'air et grâce à la mobilisation de Paul Delorme [1]. Il fournit des gaz, des technologies et des services pour "
        "l'industrie et la santé. Selon les données 2025 publiées en mars 2026, le groupe emploie environ 65 000 "
        "collaborateurs dans 59 pays [1].")
    R.h2("1.2 Air Liquide Tunisie")
    R.figure_side(FIG / "facade_air_liquide.jpg", "Façade d'un bâtiment d'Air Liquide Tunisie")
    R.p("Air Liquide est présent en Tunisie depuis 1917 [2]. Sa filiale tunisienne compte aujourd'hui 230 collaborateurs, "
        "6 sites de production et 35 points de vente, et sert plus de 16 000 clients, parmi lesquels la plupart des hôpitaux "
        "et cliniques du pays ; elle est cotée à la Bourse de Tunis et certifiée ISO 9001, ISO 14001 et FSSC 22000 [2].")
    R.p("Dans le domaine de la santé, Air Liquide Tunisie intervient à l'hôpital (gaz et équipements médicaux), tandis que "
        "la santé à domicile est assurée par la filiale VitalAire Tunisie, avec un accompagnement « de l'hôpital au domicile » "
        "[3]. Son offre comprend les gaz médicaux (oxygène médical, air médical reconstitué, dioxyde de carbone), les systèmes "
        "de distribution de gaz médicaux et des équipements complémentaires [3][4]. Le site d'exploitation visité se trouve "
        "à la zone industrielle de Charguia II, à Ariana [2].")
    R.table(["Domaine", "Contenu (d'après les sites officiels)"], [
        ["Gaz médicaux", "Oxygène médical, air médical reconstitué, dioxyde de carbone, systèmes de distribution de gaz médicaux"],
        ["Équipements", "Équipements cryogéniques et équipements pour installations hospitalières, en complément des gaz"],
        ["Santé à domicile", "Assurée par VitalAire Tunisie, de l'hôpital au domicile"],
    ], "Activités de santé d'Air Liquide Tunisie (synthèse des sources [2], [3] et [4])", widths=[3.6, 12.4])
    R.p("Les pages officielles consultées ne décrivent pas le service de maintenance des appareils respiratoires : la "
        "présentation qui suit repose donc sur les observations réalisées pendant le stage.")
    R.h2("1.3 Le service d'accueil : le service Maintenance")
    R.p("Le stage s'est déroulé au service Maintenance (maintenance biomédicale), placé sous la responsabilité de "
        "M. Marouane Hassan, responsable génie biomédical. Le service prend en charge les équipements médicaux respiratoires "
        "retournés par les patients ou les clients : concentrateurs d'oxygène, appareils de ventilation non invasive (VNI) et "
        "appareils de type CPAP. L'équipe de l'atelier comprend notamment deux techniciens, Fares et Maher.")
    R.p("Le plan de réaménagement des ateliers santé du site de Charguia (décembre 2025) et la signalétique des portes "
        "montrent l'organisation physique du circuit d'un appareil : une **salle de retour** (« Retour matériel infecté »), une "
        "**salle de désinfection**, l'**atelier de maintenance SAT** et une zone de **stockage des dispositifs médicaux "
        "livrables**. Ce circuit physique est celui que l'application reproduit.")
    R.figure(FIG / "plan_ateliers_sante.jpg", "Plan de réaménagement des ateliers santé, site de Charguia (Air Liquide Tunisie, décembre 2025)", width_cm=15.5, max_height_cm=11)
    R.figure(FIG / "signaletique_zones.jpg", "Signalétique des zones : (a) retour du matériel infecté, (b) atelier de maintenance, (c) stockage des dispositifs médicaux livrables", width_cm=15.5, max_height_cm=6.5)
    R.h2("1.4 Cadre du stage")
    R.table(["Élément", "Information"], [
        ["Période", "du 1er juillet au 1er août 2026"],
        ["Entreprise", "Air Liquide Tunisie"],
        ["Service", "Maintenance (maintenance biomédicale)"],
        ["Encadrant professionnel", "M. Marouane Hassan, responsable génie biomédical"],
        ["Équipe d'accueil", "Techniciens de l'atelier, dont Fares et Maher"],
        ["Sujet", "Conception et réalisation d'une application de gestion de la maintenance (AirLiquide GMAO+)"],
    ], "Cadre du stage", widths=[5, 11])

    # ---------------------------------------------------------------- Chapitre 2
    R.h1("Chapitre 2 : Contexte et objectifs du stage")
    R.h2("2.1 Contexte du stage")
    R.p("Le service reçoit chaque jour des appareils à contrôler, réparer ou remettre en état. Chaque appareil suit un "
        "parcours défini : retour et réception, désinfection, diagnostic, réparation, contrôle qualité, stock livrable puis "
        "livraison. L'enjeu est double : garantir la **sécurité** (un appareil ne doit pas repartir sans désinfection ni "
        "contrôle) et conserver l'**historique** de chaque appareil.")
    R.p("Les interventions portent sur des composants variés. Sur les concentrateurs d'oxygène, il s'agit notamment du "
        "compresseur, des électrovannes, des cartes électroniques et des colonnes à tamis moléculaire ; sur les appareils de "
        "ventilation, de l'écran tactile, des cartes électroniques, de la turbine et de la batterie. Ces composants "
        "alimentent le catalogue de pannes de l'application.")
    R.figure(FIG / "concentrateur_composants.jpg", "Composants d'un concentrateur d'oxygène : (a) vue interne, (b) compresseur, (c) carte électronique, (d) bobine d'électrovanne (étiquettes de série floutées)", width_cm=14, max_height_cm=12)
    R.figure(FIG / "ventilation_composants.jpg", "Appareil de ventilation et composants : (a) appareil à écran tactile, (b) dalle tactile démontée, (c) turbine, (d) multimètre utilisé pour les contrôles", width_cm=14, max_height_cm=12)
    R.h2("2.2 Analyse de l'existant")
    R.p("Trois supports étaient utilisés pour suivre l'activité. Par ailleurs, un progiciel de gestion (Microsoft Dynamics "
        "NAV) a été observé au poste de travail, utilisé pour les ordres de transfert ; le suivi technique des appareils "
        "restait en dehors de cet outil.")
    R.h3("2.2.1 Le journal de maintenance papier")
    R.p("Un registre imprimé, intitulé « Journal de maintenance des équipements O2, VNI, CPAP et respirateur » "
        "(référence 404, révision 1, propriétaire Air Liquide Tunisie), est rempli à la main pendant la journée sur un "
        "porte-bloc, une ligne par appareil. La figure suivante montre le registre le 14 juillet 2026.")
    R.table(["Colonne du registre", "Information notée"], [
        ["Année, Mois", "Date de l'intervention"],
        ["Équip. / type", "Type d'équipement"],
        ["N° série", "Numéro de série de l'appareil"],
        ["C.H", "Compteur horaire de l'appareil"],
        ["Pureté", "Pureté de l'oxygène produit (concentrateurs)"],
        ["Débit / pression", "Mesures de débit ou de pression"],
        ["Alarme sonore", "Fonctionnement de l'alarme"],
        ["Pannes", "Pannes constatées"],
        ["Doc de sortie PR", "Document de sortie des pièces utilisées"],
        ["Technicien", "Technicien intervenant"],
        ["Date sortie", "Date de sortie de l'appareil"],
    ], "Colonnes du journal de maintenance papier", widths=[5, 11])
    R.figure(FIG / "journal_papier.jpg", "Journal de maintenance papier du service (ligne manuscrite floutée)", width_cm=13.5, max_height_cm=10)
    R.h3("2.2.2 Le classeur Google Sheets « GMAO v1 »")
    R.p("En fin de journée, les informations du papier étaient reportées dans un classeur Google Sheets. Il comporte "
        "plusieurs onglets, dont **RETURNS** (retours d'appareils), **DISINFECTION** (opérateur, statut, notes), "
        "**MAINTENANCE_JOURNAL** (type de service, pièces, catégorie, propriété, heures de fonctionnement, pureté, dates de "
        "service), **LISTS**, **PM_LOG** et **CM_LOG**.")
    R.figure(FIG / "classeur_journal.jpg", "Onglet MAINTENANCE_JOURNAL du classeur (numéros de série floutés)", width_cm=15.5, max_height_cm=7)
    R.h3("2.2.3 Le questionnaire de retour")
    R.p("Avant l'arrivée d'un appareil, un questionnaire en ligne annonce le retour. Il recueille le numéro de série, l'état "
        "visuel (bon état, dégâts mineurs, réparation nécessaire, risque biologique), les accessoires manquants, des notes, "
        "un identifiant de retour et le statut biologique (normal, contamination importante, inconnu). Ses réponses "
        "alimentent l'onglet RETURNS du classeur.")
    R.figure(FIG / "classeur_retours.jpg", "Onglet RETURNS : réponses au questionnaire de retour (numéros de série floutés)", width_cm=15.5, max_height_cm=6.5)
    R.h2("2.3 Problématique")
    R.p("Ces supports présentent plusieurs limites, relevées dans le cahier des charges du projet : recherche lente des "
        "équipements, double saisie des informations, difficulté de suivre l'état des machines, absence de traçabilité "
        "complète et absence d'indicateurs de performance. La question centrale du stage est la suivante : **comment "
        "centraliser le suivi des appareils de leur retour à leur livraison, avec une traçabilité fiable et une saisie "
        "rapide pour les techniciens ?**")
    R.h2("2.4 Objectifs du stage")
    R.table(["Objectif", "Critère de vérification", "Statut"], [
        ["Enregistrer rapidement les retours", "Formulaire de réception, reprise du questionnaire de retour", "Réalisé"],
        ["Une fiche de vie unique par appareil", "Test : un appareil qui revient garde la même fiche", "Réalisé, testé"],
        ["Suivre chaque étape du cycle de maintenance", "Workflow à 7 statuts, historique horodaté", "Réalisé, testé"],
        ["Empêcher les transitions incohérentes", "Tests des règles de transition et des prérequis", "Réalisé, testé"],
        ["Enregistrer diagnostics, pannes, réparations, pièces", "Catalogues et formulaires d'étape", "Réalisé, testé"],
        ["Contrôle qualité avec checklist", "Checklist de 7 points, mesures", "Réalisé, testé"],
        ["Gérer le stock des appareils réparés", "Mouvements d'entrée et de sortie", "Réalisé, testé"],
        ["Fournir tableau de bord et statistiques", "Indicateurs et exports", "Réalisé (tableau de bord, exports CSV)"],
        ["Rapports PDF", "Mentionnés au cahier des charges", "Non réalisé (export CSV seulement)"],
        ["Temps de saisie inférieur à une minute", "Exigence du cahier des charges", "Non mesuré"],
    ], "Objectifs du stage et état de réalisation", widths=[5.5, 6.5, 4])
    R.h2("2.5 Intérêt du stage dans ce contexte")
    R.p("Le projet répond à un besoin réel du service. Il a permis de mettre en pratique la démarche complète d'un projet "
        "logiciel appliqué à la santé : recueil du besoin auprès des utilisateurs, conception, développement, tests et "
        "validation. Il se rattache directement à la formation TTIS, qui associe systèmes d'information et dispositifs "
        "médicaux.")

    # ---------------------------------------------------------------- Chapitre 3
    R.h1("Chapitre 3 : Travaux réalisés")
    R.h2("3.1 Démarche et organisation du travail")
    R.p("Le travail a suivi une démarche en trois temps : (1) documenter le besoin avant d'écrire du code, (2) concevoir "
        "l'architecture et le modèle de données, (3) développer fonctionnalité par fonctionnalité, en testant chaque "
        "règle métier.")
    R.bullets([
        "**Documentation préalable** : vision, cahier des charges, objectifs, workflow, cas d'utilisation, architecture "
        "et base de données (documents Markdown versionnés dans le dépôt).",
        "**Gestion de version Git** : branche `main` stable, branche `develop` d'intégration, branches de fonctionnalité "
        "et messages de commit normalisés (Conventional Commits). Le dépôt compte 31 commits.",
        "**Développement piloté par les règles métier** : chaque règle (transition, unicité, permission) est couverte par "
        "un test automatisé.",
    ])
    R.p("Le déroulement du projet est reconstitué à partir des observations du stage et de l'historique du dépôt Git.")
    R.table(["Période", "Activité"], [
        ["1er juillet – 1er août 2026 (stage)", "Immersion au service Maintenance : observation du circuit retour, désinfection, atelier et stockage ; échanges avec le responsable et les techniciens ; recueil du besoin à partir du journal papier (entrée du 14 juillet 2026), du classeur Google Sheets et du questionnaire de retour"],
        ["15 et 16 juillet 2026", "Rédaction de la documentation de conception (vision, cahier des charges, workflow, cas d'utilisation, architecture, base de données), structure du dépôt, projet Django"],
        ["Octobre 2026 (14, 27 et 28)", "Réalisation et consolidation de l'application : authentification, workflow complet, questionnaire de retour, journal, interface, tests et documentation"],
    ], "Déroulement du projet", widths=[4.5, 11.5])
    R.h3("Outils d'assistance utilisés")
    R.p("Conformément à une démarche transparente, il est précisé que des assistants d'intelligence artificielle ont été "
        "utilisés comme outils de travail : un assistant conversationnel pour structurer la conception initiale "
        "(architecture, base de données, workflow), puis un assistant de programmation pour accélérer le développement "
        "et la rédaction des tests. L'étudiant a défini le besoin, pris les décisions de conception, relu, exécuté et "
        "validé le résultat.")

    R.h2("3.2 Analyse des besoins")
    R.h3("3.2.1 Acteurs")
    R.table(["Acteur", "Rôle dans l'application", "Droits principaux"], [
        ["Technicien de maintenance", "Utilisateur principal de l'atelier", "Enregistrer les retours, réaliser et valider chaque étape, consulter les fiches de vie et le journal"],
        ["Responsable SAV", "Supervision et administration", "Tous les droits du technicien, plus : gestion des utilisateurs et des catalogues, rapports et exports, retour arrière d'un statut avec justification"],
    ], "Acteurs et droits", widths=[4, 4.5, 7.5])
    R.figure(FIG / "uml_cas_utilisation.png", "Diagramme de cas d'utilisation", width_cm=15.5, landscape=True)
    R.p("Le Responsable SAV hérite de tous les cas d'utilisation du technicien et dispose en plus de la gestion des utilisateurs et des catalogues et de l'export des rapports. Chaque étape du workflow inclut la vérification de ses prérequis.")
    R.h3("3.2.2 Besoins fonctionnels")
    R.bullets([
        "annoncer un retour avant l'arrivée de l'appareil, puis le réceptionner ;",
        "retrouver un appareil par son numéro de série et consulter sa fiche de vie ;",
        "enregistrer la désinfection, le diagnostic (pannes d'un catalogue), la réparation (pièces, durée), le contrôle "
        "qualité (checklist et mesures), l'entrée en stock et la livraison ;",
        "joindre des photos aux dossiers ;",
        "consulter un tableau de bord et un journal de maintenance équivalent au registre papier ;",
        "exporter les données (CSV).",
    ])
    R.h3("3.2.3 Besoins non fonctionnels")
    R.bullets([
        "**Traçabilité** : chaque changement de statut conserve la date, l'heure et l'utilisateur ; l'historique ne peut "
        "être ni modifié ni supprimé ;",
        "**Sécurité** : authentification, permissions par rôle, validation des entrées côté serveur, protection des "
        "fichiers téléversés ;",
        "**Ergonomie** : interface en français, utilisable sur ordinateur et tablette, parcours courts pour les techniciens ;",
        "**Maintenabilité** : code modulaire, logique métier séparée des vues, tests automatisés.",
    ])

    R.h2("3.3 Conception")
    R.p("Les diagrammes de cette section suivent la notation UML. Ils ont été dessinés pour ce rapport ; leurs sources textuelles équivalentes (PlantUML et Mermaid), versionnées avec le projet, se trouvent dans le dossier `docs/diagrams/`.")
    R.h3("3.3.1 Le workflow d'un appareil")
    R.p("Le cycle de vie d'un appareil est modélisé par sept statuts successifs. Un dossier ne peut avancer que d'une "
        "étape à la fois, et seulement si l'étape correspondante a été enregistrée.")
    R.figure(FIG / "uml_etats.png", "Diagramme d'états d'un dossier SAV", width_cm=15.5, landscape=True)
    R.table(["Statut", "Étape validée", "Prérequis pour y accéder"], [
        ["RECU", "Réception", "Appareil identifié par son numéro de série"],
        ["DESINFECTE", "Désinfection", "Désinfection enregistrée et validée"],
        ["DIAGNOSTIC_TERMINE", "Diagnostic", "Diagnostic enregistré (pannes du type d'appareil)"],
        ["REPARE", "Réparation", "Réparation enregistrée (début, fin, pièces)"],
        ["QC_VALIDE", "Contrôle qualité", "Dernier contrôle conforme sur les 7 points"],
        ["EN_STOCK", "Entrée en stock", "Emplacement renseigné"],
        ["LIVRE", "Livraison", "Destinataire renseigné"],
    ], "Statuts du dossier SAV et prérequis", widths=[4, 3.5, 8.5])
    R.h3("3.3.2 Règles métier")
    R.bullets([
        "un appareil physique possède **une seule fiche** (numéro de série normalisé) et peut avoir plusieurs retours ;",
        "un appareil ne peut avoir **qu'un seul dossier ouvert** à la fois (contrainte en base de données) ;",
        "aucun saut d'étape n'est possible ; le statut ne se modifie pas directement par l'API ;",
        "le **retour arrière** est réservé au Responsable SAV avec commentaire obligatoire, et un dossier livré ne se rouvre pas ;",
        "un contrôle qualité non conforme exige un commentaire, laisse le dossier à l'état « réparé » et bloque la mise en stock ;",
        "le **risque biologique** est déduit du questionnaire : un statut « inconnu » est traité comme un risque, par précaution ;",
        "les pannes d'un diagnostic doivent appartenir au type de l'appareil.",
    ])
    R.h3("3.3.3 Modèle de données")
    R.p("Une décision de conception importante a été de **séparer l'appareil physique de ses retours**. La première "
        "version de la conception reposait sur une entité unique « Machine » ; elle a évolué vers deux entités : "
        "l'**appareil** (fiche de vie durable, créée une seule fois) et le **dossier SAV** (un retour, avec ses étapes). "
        "Ainsi, un appareil qui revient plusieurs fois au service n'est jamais recréé.")
    R.p("Le modèle est présenté en deux diagrammes de classes : le premier montre le cœur (utilisateurs, appareils, retours et historique), le second les étapes rattachées à un dossier.")
    R.figure(FIG / "uml_classes_coeur.png", "Diagramme de classes : appareil, retour et historique", width_cm=15.5, landscape=True)
    R.figure(FIG / "uml_classes_etapes.png", "Diagramme de classes : étapes rattachées au dossier SAV", width_cm=15.5, landscape=True)
    R.p("Le modèle comprend 19 entités et 2 énumérations (annexe B), organisées autour de quatre groupes : "
        "utilisateurs, référentiel d'appareils (types, marques, modèles, appareils), dossier SAV et ses étapes, "
        "catalogues (pannes, pièces).")
    R.h3("3.3.4 Architecture")
    R.p("L'application suit une architecture client / serveur en couches, fondée sur une API REST. Le frontend ne "
        "contient aucune règle métier : il appelle l'API, qui applique les règles dans une couche de services.")
    R.figure(FIG / "uml_architecture.png", "Architecture d'AirLiquide GMAO+", width_cm=15.5, landscape=True)
    R.p("La conception initiale prévoyait une architecture modulaire orientée domaine, avec un module `maintenance` "
        "regroupant tout le cycle de vie, plus des modules `accounts`, `inventory`, `reports`, `dashboard` et `common`. "
        "Ce choix a été retenu. Le tableau suivant compare la cible initiale à ce qui a été réalisé.")
    R.table(["Élément de l'architecture cible", "État dans l'application réalisée"], [
        ["Modules `accounts`, `maintenance`, `inventory`, `dashboard`, `reports`", "Réalisés ; `common` créé mais non utilisé"],
        ["Services (règles métier hors des vues)", "Réalisés : `maintenance/services.py`"],
        ["Selectors et repositories", "Non réalisés : jugés inutiles à cette taille de projet"],
        ["Frontend web Next.js / TypeScript / Tailwind / shadcn/ui", "Réalisé"],
        ["Application mobile Flutter", "Non réalisée (prévue comme extension)"],
        ["Docker", "Partiel : seule la base PostgreSQL est conteneurisée"],
        ["Rapports PDF, notifications, QR code", "Non réalisés (perspectives)"],
    ], "Architecture cible et architecture réalisée", widths=[8, 8])
    R.h3("3.3.5 Sécurité")
    R.bullets([
        "**Authentification JWT** : le jeton d'accès reste en mémoire dans le navigateur ; le jeton de rafraîchissement est "
        "placé dans un cookie `HttpOnly`, inaccessible au code JavaScript (protection contre le vol de jeton) ;",
        "**limitation du nombre de tentatives** de connexion (10 par minute) ;",
        "**permissions par rôle** appliquées côté serveur, quelles que soient les actions de l'interface ;",
        "**validation côté serveur** de toutes les entrées ; contrôle des photos (formats JPEG, PNG, WebP, taille maximale 5 Mo, "
        "vérification du contenu) ;",
        "**exports CSV** protégés contre l'injection de formules dans les tableurs ;",
        "**secrets** (clé, mots de passe de base) hors du dépôt, dans un fichier d'environnement non versionné.",
    ])

    R.p("Le diagramme de séquence suivant détaille le cycle d'authentification : connexion, conservation du jeton d'accès en mémoire et renouvellement grâce au cookie.")
    R.figure(FIG / "uml_sequence_auth.png", "Diagramme de séquence : authentification et renouvellement du jeton", width_cm=15.5, landscape=True)
    R.h2("3.4 Réalisation")
    R.h3("3.4.1 Environnement technique")
    R.table(["Couche", "Technologies et versions"], [
        ["Backend", "Python 3.10, Django 5.2.16, Django REST Framework 3.17.1, SimpleJWT 5.5.1, drf-spectacular 0.30.0, django-cors-headers 4.9.0, Pillow 12.3.0"],
        ["Base de données", "PostgreSQL 16 (conteneur Docker) ; SQLite en repli pour le développement"],
        ["Frontend", "Next.js 16.4.3, React 19.3.0, TypeScript 5, Tailwind CSS 4, shadcn/ui, lucide-react, sonner"],
        ["Documentation API", "OpenAPI / Swagger généré automatiquement (`/api/docs/`)"],
        ["Outils", "Git et GitHub, Docker Compose, Chrome et outils de développement"],
    ], "Environnement technique (versions relevées dans les fichiers de dépendances)", widths=[3.5, 12.5])
    R.h3("3.4.2 Le backend")
    R.p("Le backend est organisé en applications Django. Les **vues** reçoivent la requête et délèguent ; les "
        "**sérialiseurs** valident les entrées ; les **services** (`maintenance/services.py`) exécutent les règles "
        "métier dans des transactions atomiques : réception, désinfection, diagnostic, réparation, contrôle qualité, "
        "entrée en stock, livraison et changement de statut. Chaque service verrouille le dossier, vérifie le statut "
        "attendu, enregistre l'étape, fait avancer le statut et écrit l'historique en une seule opération.")
    R.p("L'API expose des points d'accès REST documentés (annexe A). Les actions de workflow sont de simples `POST` sur "
        "le dossier (par exemple `/api/dossiers/{id}/quality-control/`), ce qui rend l'enregistrement d'une étape et le "
        "changement de statut indissociables.")
    R.figure(FIG / "uml_sequence_etape.png", "Diagramme de séquence : enregistrement d'une étape (contrôle qualité)", width_cm=15.5, landscape=True)
    R.h3("3.4.3 Le questionnaire de retour")
    R.p("Le questionnaire en ligne existant a été intégré à l'application sous la forme d'une **annonce de retour** : "
        "avant l'arrivée de l'appareil, un utilisateur saisit le numéro de série, l'état visuel, les accessoires manquants, "
        "l'identifiant de retour et le statut biologique. À l'arrivée, le technicien choisit le retour annoncé dans "
        "l'écran de réception : les réponses sont reprises, le numéro de série est verrouillé et l'annonce est rattachée "
        "au dossier. Une annonce ne peut être réceptionnée qu'une seule fois.")
    R.figure(FIG / "cap_retours.png", "Écran des retours annoncés (données de démonstration)", width_cm=15)
    R.figure(FIG / "cap_reception.png", "Écran de réception d'un appareil (données de démonstration)", width_cm=14)
    R.h3("3.4.4 Le journal de maintenance")
    R.p("Le registre papier a été reproduit sous forme numérique. Le journal n'est **pas une table à saisir** : il est "
        "calculé à partir des dossiers, une ligne par retour, avec les douze colonnes du registre (annexe D). Il ne peut "
        "donc pas diverger des dossiers. L'écran propose des filtres (année, mois, type, numéro de série), l'impression "
        "et l'export CSV. Pour alimenter les colonnes du registre, le compteur horaire est saisi à la réception ; la pureté, "
        "le débit ou la pression et l'alarme sonore au contrôle qualité ; le document de sortie des pièces à la réparation.")
    R.figure(FIG / "cap_journal.png", "Journal de maintenance numérique (données de démonstration)", width_cm=15)
    R.h3("3.4.5 Le frontend et l'expérience utilisateur")
    R.p("L'interface est en français et vise l'usage en atelier : cibles tactiles d'au moins 44 pixels, contrastes "
        "suffisants, statuts toujours accompagnés d'un libellé et d'une icône (jamais la couleur seule), navigation "
        "au clavier. Plusieurs choix répondent à des besoins observés :")
    R.bullets([
        "le **tableau de bord** montre la charge de l'atelier par poste (à désinfecter, à diagnostiquer, etc.) et la "
        "liste des dossiers à traiter en premier, du plus ancien au plus récent ;",
        "le **dossier** est présenté comme un parcours vertical : les étapes terminées se résument sur place et le "
        "formulaire de l'étape en cours s'ouvre à sa position ;",
        "la **recherche rapide** (Ctrl + K) retrouve un appareil par son numéro de série ;",
        "des **confirmations** (notifications) signalent chaque enregistrement ; les erreurs sont expliquées en clair.",
    ])
    R.figure(FIG / "cap_tableau_de_bord.png", "Tableau de bord (données de démonstration)", width_cm=15.5)
    R.figure(FIG / "cap_dossier_qc.png", "Dossier SAV : parcours et formulaire de contrôle qualité", width_cm=15)
    R.figure(FIG / "cap_dossier_livre.png", "Dossier livré : toutes les étapes sont résumées", width_cm=15)
    R.p("Les captures de ce rapport ont été réalisées avec des **données de démonstration fictives**, clairement "
        "identifiées, et non avec des données réelles d'Air Liquide.")

    # ---------------------------------------------------------------- Chapitre 4
    R.h1("Chapitre 4 : Résultats obtenus et bilan")
    R.h2("4.1 Tests réalisés")
    R.p("La suite de tests automatisés du backend comprend **49 tests, tous réussis** lors de l'exécution du 28 octobre "
        "2026 (environnement SQLite). Les mêmes tests avaient également réussi sur PostgreSQL 16 au cours du développement.")
    R.table(["Thème", "Nombre de tests", "Ce qui est vérifié"], [
        ["Authentification et permissions", "12", "Connexion, refus d'accès, droits par rôle, cookie HttpOnly, renouvellement, déconnexion, limitation du débit"],
        ["Réception et transitions", "10", "Création de l'appareil, doublons, saut d'étape interdit, retour arrière réservé, historique immuable"],
        ["Étapes du workflow", "11", "Cycle complet, fiche de vie unique, ordre des étapes, contrôle non conforme, livraison sans stock"],
        ["Photos", "3", "Image valide, fichier non image, type non autorisé"],
        ["Questionnaire de retour", "7", "Création, identifiant unique, rattachement à la réception, double réception, incohérence de série, risque biologique"],
        ["Journal et indicateurs", "6", "Colonnes du journal, filtres, export CSV, pureté hors limites, tableau de bord, accès aux rapports"],
    ], "Répartition des tests automatisés du backend (total : 49)", widths=[4.5, 2.5, 9])
    R.p("Côté frontend, aucun test automatisé n'a été écrit : les contrôles disponibles sont la vérification des types "
        "TypeScript, l'analyse statique (lint) sans erreur et la compilation de production, complétés par des captures "
        "d'écran et des essais manuels. C'est une limite assumée de ce travail (§ 4.5).")
    R.h2("4.2 Résultats fonctionnels")
    R.p("Le tableau suivant confronte les fonctionnalités à leur niveau de vérification.")
    R.table(["Fonctionnalité", "Niveau de vérification"], [
        ["Authentification, rôles, limitation de débit", "Implémentée, testée automatiquement"],
        ["Fiche de vie unique, dossier unique ouvert", "Implémentée, testée automatiquement"],
        ["Workflow à 7 statuts et prérequis", "Implémentée, testée automatiquement"],
        ["Historique immuable", "Implémentée, testée automatiquement"],
        ["Désinfection, diagnostic, réparation, contrôle qualité, stock, livraison", "Implémentée, testée automatiquement"],
        ["Questionnaire de retour, journal de maintenance, exports CSV", "Implémentée, testée automatiquement"],
        ["Interface web (16 écrans, version mobile adaptée)", "Implémentée, vérifiée par compilation, lint et captures"],
        ["Rapports PDF, maintenance préventive, application mobile", "Non réalisées"],
    ], "Niveau de vérification des fonctionnalités", widths=[9, 7])
    R.h2("4.3 Validation par les utilisateurs")
    R.p("L'application a été testée par les techniciens du service, Fares et Maher, qui l'ont validée.")
    R.h2("4.4 Difficultés rencontrées et solutions apportées")
    R.table(["Difficulté", "Solution apportée"], [
        ["Le modèle initial à entité unique « Machine » ne distinguait pas l'appareil de ses retours", "Séparation en appareil (fiche de vie) et dossier SAV, avec contrainte d'un seul dossier ouvert"],
        ["Éviter les transitions incohérentes (par exemple livrer sans contrôle)", "Services transactionnels : chaque étape vérifie le statut attendu et ses prérequis ; tests dédiés"],
        ["Stockage des jetons dans le navigateur exposé aux scripts malveillants", "Jeton de rafraîchissement en cookie HttpOnly, jeton d'accès en mémoire, limitation des tentatives"],
        ["Erreur « inconnue » affichée alors que la base n'était pas à jour (migration non appliquée)", "Messages d'erreur explicites côté interface (serveur injoignable, erreur interne, migrations)"],
        ["Polices téléchargées depuis un service externe, indisponibles sans réseau", "Polices installées localement avec le projet (paquets `@fontsource`)"],
        ["Contraintes d'une version récente de Next.js sur le rendu dynamique", "Réorganisation de la mise en page (suspension du rendu) et contenu toujours rendu"],
        ["Environnement Docker instable sur le poste de développement", "Démarrage de Docker Desktop, base SQLite de repli, validation sur les deux bases"],
    ], "Principales difficultés techniques et solutions", widths=[7.5, 8.5])
    R.h2("4.5 Limites du travail")
    R.bullets([
        "pas de **rapports PDF** (exports CSV uniquement), alors que le cahier des charges les mentionnait ;",
        "pas de **maintenance préventive** ni de suivi des interventions correctives, pourtant présents dans le classeur "
        "existant (onglets PM_LOG et CM_LOG), ni de type de service ou de propriété de l'appareil ;",
        "**aucun test automatisé du frontend** ;",
        "l'exigence de **saisie en moins d'une minute** n'a pas été mesurée ;",
        "pas d'écran d'administration des utilisateurs et des catalogues (disponibles par l'API et l'administration Django) ;",
        "pas d'**application mobile**, pas de déploiement documenté en production ;",
        "les captures du rapport utilisent des données de démonstration et ne reflètent pas des volumes réels.",
    ])
    R.h2("4.6 Perspectives")
    R.bullets([
        "génération de **rapports PDF** et de statistiques avancées ;",
        "intégration de la **maintenance préventive** (dates de prochain service) et des types de service du classeur ;",
        "**import des données existantes** du classeur Google Sheets ;",
        "**application mobile** Flutter connectée à la même API ;",
        "conteneurisation complète, intégration continue et déploiement sécurisé ;",
        "tests automatisés de bout en bout du frontend ;",
        "étiquettes **QR code** pour retrouver un appareil par lecture.",
    ])

    # ---------------------------------------------------------------- Conclusion
    R.h1("Conclusion générale")
    R.p("Ce stage au sein du service Maintenance d'Air Liquide Tunisie a permis de concevoir et de réaliser "
        "AirLiquide GMAO+, une application qui remplace les saisies papier et tableur par un suivi unique de chaque "
        "appareil, de son retour à sa livraison. Les principaux apports sont une **fiche de vie unique** par appareil, "
        "une **traçabilité** horodatée et immuable, des **règles de workflow** appliquées par le serveur et vérifiées "
        "par 49 tests, ainsi qu'un journal de maintenance qui reprend le registre existant.")
    R.p("Sur le plan des compétences, le stage a mobilisé l'analyse de besoin avec des utilisateurs de terrain, la "
        "modélisation, le développement d'une API et d'une interface web, la sécurité applicative et la rédaction de "
        "tests. Il a aussi montré l'importance de comprendre le métier avant de coder : plusieurs choix, comme la "
        "séparation entre l'appareil et ses retours, viennent directement de l'observation du circuit réel.")
    R.p("Le travail présente des limites, détaillées au chapitre 4 : absence de rapports PDF, de maintenance préventive et "
        "de version mobile, et tests du frontend à compléter. Ces points constituent les perspectives naturelles du projet.")
    R.p("Sur le plan personnel, ce stage m'a permis de confronter ma formation de futur ingénieur en génie biomédical, "
        "parcours TTIS, à une situation de terrain : comprendre le circuit réel d'un dispositif médical dans un atelier de "
        "maintenance, puis le traduire en une application utilisable par les techniciens. J'y ai gagné en autonomie, en "
        "rigueur de documentation et en aisance pour dialoguer avec des utilisateurs dont le métier n'est pas "
        "l'informatique. Cette expérience confirme l'intérêt, pour un ingénieur biomédical, de maîtriser à la fois la "
        "maintenance des dispositifs médicaux et les outils numériques qui en assurent la traçabilité ; elle constitue une "
        "base solide pour mon projet professionnel dans la maintenance biomédicale et les systèmes d'information de santé.")

    # ---------------------------------------------------------------- Annexes
    R.h1("Annexes")
    R.h2("Annexe A : Principaux points d'accès de l'API")
    R.table(["Méthode", "Route", "Rôle", "Description"], [
        ["POST", "`/api/auth/login/`", "public", "Connexion (jeton d'accès + cookie)"],
        ["POST", "`/api/auth/refresh/`, `/api/auth/logout/`", "cookie", "Renouvellement, déconnexion"],
        ["GET", "`/api/auth/me/`", "connecté", "Profil"],
        ["CRUD", "`/api/users/`", "Responsable", "Administration des utilisateurs"],
        ["CRUD", "`/api/device-types/`, `/brands/`, `/device-models/`, `/faults/`, `/parts/`", "lecture : tous ; écriture : Responsable", "Catalogues"],
        ["GET", "`/api/devices/?search=`, `/api/devices/{id}/life-sheet/`", "connecté", "Appareils et fiche de vie"],
        ["POST / GET", "`/api/returns/`", "connecté", "Questionnaire de retour"],
        ["POST", "`/api/dossiers/reception/`", "connecté", "Réception d'un appareil"],
        ["POST", "`/api/dossiers/{id}/disinfection/`, `/diagnosis/`, `/repair/`, `/quality-control/`, `/stock-entry/`, `/delivery/`", "connecté", "Étapes du workflow"],
        ["POST", "`/api/dossiers/{id}/transition/`, `/photos/`", "connecté ; recul : Responsable", "Transition contrôlée, photos"],
        ["GET", "`/api/dashboard/`, `/api/journal/`, `/api/stock-movements/`", "connecté", "Indicateurs, journal, mouvements"],
        ["GET", "`/api/reports/journal.csv`, `/api/reports/dossiers.csv`", "connecté / Responsable", "Exports CSV"],
    ], "Points d'accès de l'API", widths=[2.2, 6.6, 3.2, 4], size=8.5)

    R.h2("Annexe B : Entités du modèle de données")
    R.table(["Groupe", "Entités"], [
        ["Utilisateurs", "User (rôles : technicien, responsable SAV)"],
        ["Référentiel d'appareils", "DeviceType, Brand, DeviceModel, Device"],
        ["Retour et dossier", "ReturnDeclaration, DossierSAV, StatusHistory"],
        ["Étapes du dossier", "Disinfection, Diagnosis, DetectedFault, Repair, ReplacedPart, QualityControl, StockMovement, Delivery, Photo"],
        ["Catalogues", "Fault (pannes par type d'appareil), Part (pièces)"],
        ["Énumérations", "VisualCondition, BiohazardStatus"],
    ], "Entités du modèle de données", widths=[4, 12])

    R.h2("Annexe C : Organisation du dépôt")
    R.table(["Dossier", "Contenu"], [
        ["`backend/`", "Applications Django : accounts, inventory, maintenance, dashboard, reports, common ; configuration"],
        ["`frontend/`", "Application Next.js : pages, composants, bibliothèque d'appels à l'API"],
        ["`docs/`", "Vision, cahier des charges, workflow, cas d'utilisation, architecture, base de données, API, démarrage, captures"],
        ["`docs/diagrams/`", "Sources des diagrammes UML (PlantUML, Mermaid)"],
        ["`docker-compose.yml`", "Base de données PostgreSQL 16"],
    ], "Organisation du dépôt", widths=[4, 12])

    R.h2("Annexe D : Correspondance entre le journal papier et l'application")
    R.table(["Colonne du journal papier", "Origine dans AirLiquide GMAO+"], [
        ["Année, Mois", "Date de réception du dossier"],
        ["Équip. / type", "Type d'appareil et modèle"],
        ["N° série", "Appareil (numéro normalisé)"],
        ["C.H", "Compteur horaire saisi à la réception"],
        ["Pureté", "Contrôle qualité (pureté O₂, de 0 à 100 %)"],
        ["Débit / pression", "Contrôle qualité"],
        ["Alarme sonore", "Contrôle qualité (conforme, non conforme, non testée)"],
        ["Pannes", "Diagnostic (pannes du catalogue)"],
        ["Doc de sortie PR", "Réparation (référence du document de sortie des pièces)"],
        ["Technicien", "Technicien de la réparation, à défaut de la désinfection"],
        ["Date sortie", "Date de livraison"],
    ], "Correspondance journal papier / application", widths=[5.5, 10.5])
    R.p("Hypothèses à valider avec le service : « C.H » désigne le compteur horaire ; « Doc de sortie PR » désigne le "
        "document de sortie de pièces de rechange ; le dernier contrôle qualité fait foi pour les mesures.")

    R.h2("Annexe E : Captures complémentaires")
    R.figure(FIG / "cap_connexion.png", "Écran de connexion", width_cm=15)
    R.figure(FIG / "cap_dossiers.png", "Liste des dossiers SAV (données de démonstration)", width_cm=15)
    R.figure(FIG / "cap_fiche_vie.png", "Fiche de vie d'un appareil (données de démonstration)", width_cm=15)
    R.figure(FIG / "cap_palette.png", "Recherche rapide par numéro de série (Ctrl + K)", width_cm=15)
    R.figure(FIG / "cap_mobile.png", "Tableau de bord sur téléphone", width_cm=7.5, max_height_cm=17)

    R.h2("Annexe F : Exécution des tests automatisés")
    R.p("Commande (depuis le dossier `backend/`) :")
    R.p("`python manage.py test`")
    R.p("Résultat observé le 28 octobre 2026, environnement SQLite : `Ran 49 tests` suivi de `OK`.")

    # ---------------------------------------------------------------- Bibliographie
    R.h1("Bibliographie et webographie")
    R.p("Les sources ci-dessous sont celles réellement utilisées pour ce rapport. Les informations sur l'entreprise "
        "proviennent des pages officielles d'Air Liquide, consultées le 28 octobre 2026.")
    for ref in (
        "[1] Air Liquide, « Air Liquide in brief » (histoire et chiffres du groupe). https://www.airliquide.com/group/air-liquide-brief. Consulté le 28 octobre 2026.",
        "[2] Air Liquide, « Air Liquide in Tunisia ». https://www.airliquide.com/group/tunisia. Consulté le 28 octobre 2026.",
        "[3] Air Liquide Healthcare Tunisie, « Qui sommes-nous ». https://tn.healthcare.airliquide.com/propos-de-nous/qui-sommes-nous. Consulté le 28 octobre 2026.",
        "[4] Air Liquide Healthcare Tunisie, « Équipements ». https://tn.healthcare.airliquide.com/nos-solutions/equipements. Consulté le 28 octobre 2026.",
        "[5] Django Software Foundation, Documentation de Django. https://docs.djangoproject.com/",
        "[6] Encode OSS, Django REST Framework. https://www.django-rest-framework.org/",
        "[7] Vercel, Documentation de Next.js. https://nextjs.org/docs",
        "[8] PostgreSQL Global Development Group, Documentation de PostgreSQL 16. https://www.postgresql.org/docs/16/",
        "[9] Tailwind Labs, Documentation de Tailwind CSS. https://tailwindcss.com/docs",
        "[10] shadcn, Documentation de shadcn/ui. https://ui.shadcn.com/",
        "[11] Jones M., Bradley J., Sakimura N., « JSON Web Token (JWT) », RFC 7519, IETF, 2015. https://datatracker.ietf.org/doc/html/rfc7519",
    ):
        p = R.p(ref, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=4)

