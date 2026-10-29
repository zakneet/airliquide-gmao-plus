"""Génère le rapport Word (DOCX) à partir du modèle de l'institut.

Usage : python generer_rapport.py <modele.docx> <figures_dir> <sortie.docx>
Le contenu est dans contenu_rapport.py (partagé avec la version LaTeX).
Les passages à compléter par l'étudiant sont surlignés en jaune : [À COMPLÉTER : ...].
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from contenu_rapport import build  # noqa: E402
from docx_lib import Rapport  # noqa: E402

TEMPLATE, FIG, OUT = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
R = Rapport(TEMPLATE)
build(R, FIG)
cp = R.doc.core_properties
cp.author = cp.last_modified_by = "Zakaria Ali Fekih Ahmed"
cp.title = "AirLiquide GMAO+ : rapport de stage technicien"
cp.comments = cp.keywords = cp.subject = ""
R.save(OUT)
print("rapport Word ok :", OUT, "| figures :", R.fig, "| tableaux :", R.tab)
