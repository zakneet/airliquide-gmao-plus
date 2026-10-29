"""Génère le projet LaTeX du rapport (compilable sur Overleaf, pdfLaTeX).

Usage : python generer_latex.py <figures_dir> <logos_dir> <dossier_sortie>
<figures_dir> contient les schémas UML (uml_*.png), les captures (cap_*.png) et les photos préparées (*.jpg).
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from contenu_rapport import build  # noqa: E402
from latex_lib import LatexRapport  # noqa: E402

FIG, LOGOS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])

MAIN = r"""% =====================================================================
%  Rapport de stage technicien : AirLiquide GMAO+ (Air Liquide Tunisie, juillet 2026)
%  Fichier principal à compiler : main.tex (compilateur pdfLaTeX, deux passes).
% =====================================================================
\documentclass[11pt,a4paper,oneside]{report}

\input{config/preambule}

% ---------------------------------------------------------------------
%  Informations de la page de garde
% ---------------------------------------------------------------------
\newcommand{\Auteur}{Zakaria Ali FEKIH AHMED}
\newcommand{\Formation}{Cycle ingénieur en Génie Biomédical, parcours TTIS}
\newcommand{\Organisme}{Air Liquide Tunisie, service Maintenance}
\newcommand{\EncadrantPro}{M. Marouane HASSAN, responsable génie biomédical}
\newcommand{\PeriodeStage}{du 1\textsuperscript{er} juillet au 1\textsuperscript{er} août 2026}
\newcommand{\AnneeUniv}{2025/2026}
\newcommand{\SousTitre}{Conception et réalisation d'une application web de gestion de la maintenance et du service après-vente des dispositifs médicaux respiratoires}

\begin{document}

% ---------- Pages préliminaires (non numérotées : la numérotation commence à l'introduction) ----------
\pagenumbering{roman}
\input{pages_preliminaires/page_de_garde}
\input{pages_preliminaires/remerciements}
\input{pages_preliminaires/resume}

\tableofcontents
\clearpage
\listoffigures
\clearpage
\listoftables
\clearpage
\input{pages_preliminaires/abreviations}

% ---------- Corps du rapport : chiffres arabes, numérotation à partir de l'introduction ----------
\clearpage
\corpstrue
\pagenumbering{arabic}
\input{chapitres/introduction}
\input{chapitres/ch1_entreprise}
\input{chapitres/ch2_contexte}
\input{chapitres/ch3_travaux}
\input{chapitres/ch4_resultats}
\input{chapitres/conclusion}

\input{bibliographie}
\input{chapitres/annexes}

\end{document}
"""

PREAMBULE = r"""% =====================================================================
%  Préambule : polices, couleurs, titres, en-têtes, tableaux, figures
% =====================================================================

% --- Langue, encodage, polices (Pagella pour le texte, Heros pour les titres, Cursor pour le code) ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage[french]{babel}
\frenchsetup{StandardLists=true}
\usepackage{tgpagella}
\usepackage[scale=0.92]{tgheros}
\usepackage[scale=0.88]{tgcursor}
\usepackage{microtype}

% --- Page ---
\usepackage[a4paper,top=2.8cm,bottom=2.6cm,left=3cm,right=2.5cm,headheight=22pt]{geometry}
\usepackage{setspace}
\setstretch{1.18}
\setlength{\parskip}{0.35em}
\setlength{\parindent}{0pt}

% --- Couleurs (charte du logo Air Liquide) ---
\usepackage[table]{xcolor}
\definecolor{ALbleu}{RGB}{35,72,152}
\definecolor{ALrouge}{RGB}{214,28,52}
\definecolor{ALgris}{RGB}{239,242,247}
\definecolor{ALtexte}{RGB}{105,113,128}

% --- Figures, tableaux, listes ---
\usepackage{graphicx}
\graphicspath{{images/}}
\usepackage{float}
\usepackage{wrapfig}
\usepackage{needspace}
\usepackage{booktabs}
\usepackage{longtable}
\setlength{\LTpre}{0.6em}
\setlength{\LTpost}{0.6em}
\usepackage{caption}
\captionsetup{font={small,sf},labelfont={bf,color=ALbleu},labelsep=endash,skip=6pt}
\captionsetup[table]{position=top,skip=5pt}
\captionsetup[figure]{position=bottom}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
\usepackage{enumitem}
\setlist{itemsep=0.2em,topsep=0.3em,parsep=0pt,leftmargin=1.4em}
\setlist[itemize,1]{label=\textendash}
\setlist[itemize,2]{label=\textendash}
\usepackage{xurl}

% --- Titres ---
\usepackage{titlesec}
\titleformat{\chapter}[hang]
  {\sffamily\bfseries\color{ALbleu}\fontsize{25}{29}\selectfont}
  {\color{ALrouge}\thechapter}{0.7em}{}[\vspace{5pt}{\color{ALrouge}\titlerule[1.4pt]}]
\titleformat{name=\chapter,numberless}[hang]
  {\sffamily\bfseries\color{ALbleu}\fontsize{25}{29}\selectfont}
  {}{0pt}{}[\vspace{5pt}{\color{ALrouge}\titlerule[1.4pt]}]
\titlespacing*{\chapter}{0pt}{-12pt}{28pt}
\titleformat{\section}{\sffamily\bfseries\Large\color{ALbleu}}{\color{ALrouge}\thesection}{0.6em}{}
\titleformat{\subsection}{\sffamily\bfseries\large}{\thesubsection}{0.6em}{}
\titlespacing*{\section}{0pt}{18pt}{8pt}
\titlespacing*{\subsection}{0pt}{12pt}{5pt}

% --- En-têtes et pieds de page ---
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\sffamily\small\color{ALtexte}AirLiquide GMAO+}
\fancyhead[R]{\sffamily\small\color{ALtexte}\nouppercase{\leftmark}}
% Numéro de page centré ; il n'apparaît qu'à partir de l'introduction (\corpstrue dans main.tex)
\newif\ifcorps\corpsfalse
\newcommand{\numpage}{\ifcorps{\sffamily\small\color{ALtexte}\thepage}\fi}
\fancyfoot[C]{\numpage}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{ALrouge}\leaders\hrule height \headrulewidth\hfill}}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\numpage}\renewcommand{\headrulewidth}{0pt}}

% --- Intitulés en français ---
\addto\captionsfrench{\renewcommand{\bibname}{Bibliographie et webographie}}
\addto\captionsfrench{\renewcommand{\listfigurename}{Liste des figures}}
\addto\captionsfrench{\renewcommand{\listtablename}{Liste des tableaux}}
\setlength{\emergencystretch}{2em}

% --- Liens ---
\usepackage[colorlinks=true,linkcolor=ALbleu,urlcolor=ALbleu,citecolor=ALrouge]{hyperref}
\hypersetup{pdftitle={AirLiquide GMAO+ : rapport de stage technicien},pdfauthor={Zakaria Ali Fekih Ahmed}}
\setcounter{tocdepth}{1}
"""

COVER = r"""% =====================================================================
%  Page de garde
% =====================================================================
\begin{titlepage}
\thispagestyle{empty}
\setstretch{1.1}

\noindent
\begin{minipage}[c]{0.27\textwidth}
  \IfFileExists{images/logo_etablissement.png}{\includegraphics[height=2.4cm]{logo_etablissement.png}}{}
\end{minipage}\hfill
\begin{minipage}[c]{0.44\textwidth}
  \centering\sffamily\footnotesize
  République Tunisienne\\
  Ministère de l'Enseignement Supérieur\\et de la Recherche Scientifique\\[2pt]
  Université de Tunis El Manar\\
  \textbf{Institut Supérieur des Technologies Médicales de Tunis}
\end{minipage}\hfill
\begin{minipage}[c]{0.27\textwidth}
  \raggedleft
  \IfFileExists{images/logo_air_liquide.png}{\includegraphics[width=4.2cm]{logo_air_liquide.png}}{}
\end{minipage}

\vspace{3.2cm}

\noindent{\color{ALrouge}\rule{1.4cm}{3.5pt}}\par\vspace{0.5cm}
{\sffamily\bfseries\large\color{ALtexte}RAPPORT DE STAGE TECHNICIEN\par}
\vspace{0.4cm}
{\sffamily\bfseries\fontsize{38}{42}\selectfont\color{ALbleu}AirLiquide GMAO+\par}
\vspace{0.6cm}
{\large\itshape\SousTitre\par}

\vfill

\noindent
{\renewcommand{\arraystretch}{2.0}
\begin{tabular}{@{}>{\sffamily\bfseries\small\color{ALbleu}}l@{\hspace{1em}}!{\color{ALrouge}\vrule width 1.2pt}@{\hspace{1em}}l@{}}
Réalisé par & \Auteur \\
Formation & \Formation \\
Organisme d'accueil & \Organisme \\
Encadrant professionnel & \EncadrantPro \\
Période du stage & \PeriodeStage \\
Année universitaire & \AnneeUniv \\
\end{tabular}}

\vspace{1.2cm}
\end{titlepage}
"""


def main():
    R = LatexRapport()
    build(R, FIG)
    files = R.save(OUT)
    for rel, txt in (("main.tex", MAIN), ("config/preambule.tex", PREAMBULE), ("pages_preliminaires/page_de_garde.tex", COVER)):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
    img = OUT / "images"
    img.mkdir(exist_ok=True)
    for old in img.glob("*"):
        old.unlink()
    for pat in ("uml_*.png", "cap_*.png", "*.jpg"):
        for f in FIG.glob(pat):
            shutil.copy2(f, img / f.name)
    for src, dst in (("logo_etablissement.png", "logo_etablissement.png"), ("air_liquide_logo.png", "logo_air_liquide.png")):
        if (LOGOS / src).exists():
            shutil.copy2(LOGOS / src, img / dst)
    print("LaTeX ok :", len(files) + 3, "fichiers |", R.fig, "figures |", R.tab, "tableaux | champs à compléter :", R.placeholders)
    if R.unknown_chars:
        print("ATTENTION caractères non gérés :", "".join(sorted(R.unknown_chars)))


main()
