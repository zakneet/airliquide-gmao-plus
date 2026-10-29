"""Génère les schémas du rapport (PNG) et prépare les captures : recadrage, floutage des données sensibles.

Usage : python generer_figures.py <dossier_sortie>
Dépendance : Pillow. Les schémas sont dessinés ici pour rester modifiables et reproductibles.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[3]
SHOTS = REPO / "docs" / "screenshots"
FONTS = Path("C:/Windows/Fonts")

INK = (11, 37, 82)
BLUE = (31, 78, 160)
SOFT = (230, 238, 250)
GREY = (90, 100, 115)
LINE = (150, 165, 190)
OK = (214, 238, 222)
WARN = (252, 240, 205)


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("arialbd.ttf" if bold else "arial.ttf")), size)


def center_text(d, box, text, f, fill=INK, spacing=6):
    x0, y0, x1, y1 = box
    lines = text.split("\n")
    hs = [d.textbbox((0, 0), t, font=f)[3] for t in lines]
    total = sum(hs) + spacing * (len(lines) - 1)
    y = y0 + (y1 - y0 - total) / 2
    for t, h in zip(lines, hs):
        w = d.textlength(t, font=f)
        d.text((x0 + (x1 - x0 - w) / 2, y), t, font=f, fill=fill)
        y += h + spacing


def rbox(d, box, text, fill=SOFT, outline=BLUE, f=None, fg=INK, width=3):
    d.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=width)
    center_text(d, box, text, f or font(30, True), fill=fg)


def arrow(d, p0, p1, color=BLUE, width=4, head=14):
    d.line([p0, p1], fill=color, width=width)
    import math
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = [p1, (p1[0] - head * math.cos(a - 0.45), p1[1] - head * math.sin(a - 0.45)),
           (p1[0] - head * math.cos(a + 0.45), p1[1] - head * math.sin(a + 0.45))]
    d.polygon(pts, fill=color)


def new(w, h):
    im = Image.new("RGB", (w, h), "white")
    return im, ImageDraw.Draw(im)


# 1. Cycle de vie d'un appareil -------------------------------------------------------------
def workflow():
    im, d = new(1700, 640)
    steps = [("Réception", "RECU"), ("Désinfection", "DESINFECTE"), ("Diagnostic", "DIAGNOSTIC_TERMINE"),
             ("Réparation", "REPARE"), ("Contrôle\nqualité", "QC_VALIDE"), ("Stock\nlivrable", "EN_STOCK"),
             ("Livraison", "LIVRE")]
    bw, bh, gap, x0, y = 180, 150, 45, 45, 120
    for i, (t, code) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rbox(d, (x, y, x + bw, y + bh), t, fill=OK if i in (4, 5) else SOFT, f=font(26, True))
        center_text(d, (x - 20, y + bh + 14, x + bw + 20, y + bh + 70), code, font(19), fill=GREY)
        if i < len(steps) - 1:
            arrow(d, (x + bw + 6, y + bh / 2), (x + bw + gap - 6, y + bh / 2))
    d.text((50, 30), "Statut du dossier SAV après chaque étape validée", font=font(30, True), fill=INK)
    # retour arrière
    d.line([(x0 + 3 * (bw + gap) + bw / 2, y + bh + 90), (x0 + 3 * (bw + gap) + bw / 2, y + bh + 150),
            (x0 + 1 * (bw + gap) + bw / 2, y + bh + 150), (x0 + 1 * (bw + gap) + bw / 2, y + bh + 90)],
           fill=(170, 80, 70), width=3)
    arrow(d, (x0 + 1 * (bw + gap) + bw / 2, y + bh + 110), (x0 + 1 * (bw + gap) + bw / 2, y + bh + 88), color=(170, 80, 70))
    center_text(d, (x0 + (bw + gap), y + bh + 155, x0 + 3 * (bw + gap) + bw, y + bh + 205),
                "Retour arrière : Responsable SAV uniquement, commentaire obligatoire", font(22), fill=(150, 60, 50))
    center_text(d, (x0, y + bh + 230, 1650, y + bh + 280),
                "Contrôle non conforme : le dossier reste à « Réparé » et la mise en stock est bloquée", font(22), fill=GREY)
    im.save(OUT / "fig_workflow.png")


# 2. Architecture en couches -----------------------------------------------------------------
def architecture():
    im, d = new(1700, 900)
    cx = 850
    layers = [
        ("Navigateur : Next.js 16 · React 19 · TypeScript · Tailwind CSS · shadcn/ui", "Présentation", 40, SOFT),
        ("API REST : Django REST Framework (vues fines, sérialiseurs, permissions) · JWT", "API", 220, SOFT),
        ("Services métier : transitions, prérequis, atomicité (transactions)", "Métier", 400, OK),
        ("Modèles Django · migrations · contraintes d'unicité", "Données (ORM)", 580, SOFT),
    ]
    for text, tag, y, fill in layers:
        rbox(d, (150, y + 28, 1550, y + 130), text, fill=fill, f=font(28, True))
        d.text((152, y), tag, font=font(22, True), fill=GREY)
    for y in (170, 350, 530):
        arrow(d, (cx, y), (cx, y + 50))
    rbox(d, (150, 760, 800, 870), "PostgreSQL 16 (Docker)", f=font(28, True), fill=WARN, outline=(190, 150, 40))
    rbox(d, (900, 760, 1550, 870), "Médias : photos (disque)", f=font(28, True), fill=WARN, outline=(190, 150, 40))
    arrow(d, (475, 710), (475, 758))
    arrow(d, (1225, 710), (1225, 758))
    im.save(OUT / "fig_architecture.png")


# 3. Modèle de données simplifié -------------------------------------------------------------
def donnees():
    im, d = new(1700, 1060)
    f = font(25, True)
    d.text((30, 20), "Un appareil, plusieurs retours ; chaque retour porte ses étapes", font=font(28, True), fill=INK)
    cx0, cy0, cx1, cy1 = 640, 440, 1020, 580
    rbox(d, (cx0, cy0, cx1, cy1), "DossierSAV\n(un retour SAV)", fill=OK, f=font(30, True), outline=(60, 130, 90))
    rbox(d, (40, 120, 400, 230), "Questionnaire\nde retour", f=f)
    rbox(d, (40, 455, 400, 565), "Appareil\n(fiche de vie unique)", f=f)
    rbox(d, (40, 800, 400, 910), "Type · Marque · Modèle\n(catalogues)", f=f, fill=WARN, outline=(190, 150, 40))
    arrow(d, (400, 510), (cx0, 510))
    center_text(d, (400, 470, cx0, 500), "1 : n", font(22), fill=GREY)
    d.line([(400, 175), (830, 175), (830, 418)], fill=BLUE, width=4)
    d.polygon([(830, 438), (818, 414), (842, 414)], fill=BLUE)
    d.text((450, 135), "0..1 : 1 (retour annoncé avant l'arrivée)", font=font(22), fill=GREY)
    d.line([(220, 567), (220, 798)], fill=LINE, width=4)
    items = [("Désinfection", SOFT), ("Diagnostic  (+ PanneDétectée)", SOFT), ("Réparation  (+ PièceRemplacée)", SOFT),
             ("ContrôleQualité", SOFT), ("MouvementStock", SOFT), ("Livraison", SOFT), ("Photo", SOFT),
             ("HistoriqueStatut (immuable)", WARN)]
    x0, x1, h, gap, y = 1180, 1670, 80, 22, 60
    ys = []
    for text, fill in items:
        rbox(d, (x0, y, x1, y + h), text, fill=fill, f=font(24, True), outline=BLUE if fill == SOFT else (190, 150, 40))
        ys.append(y + h // 2)
        y += h + gap
    bus = 1100
    d.line([(cx1, 510), (bus, 510)], fill=BLUE, width=4)
    d.line([(bus, ys[0]), (bus, ys[-1])], fill=BLUE, width=4)
    for yy in ys:
        d.line([(bus, yy), (x0, yy)], fill=BLUE, width=3)
    im.save(OUT / "fig_donnees.png")


# 4. Captures : recadrage et floutage ----------------------------------------------------------
def crop_shot(name, out, max_ratio=1.1, top=None):
    im = Image.open(SHOTS / name).convert("RGB")
    w, h = im.size
    if top:
        im = im.crop((0, 0, w, min(h, top)))
    elif h / w > max_ratio:
        im = im.crop((0, 0, w, int(w * max_ratio)))
    im.save(OUT / out)


def blur_region(src, out, boxes, radius=14):
    im = Image.open(src).convert("RGB")
    for b in boxes:
        reg = im.crop(b).filter(ImageFilter.GaussianBlur(radius))
        im.paste(reg, b)
    im.save(OUT / out)


if __name__ == "__main__":
    workflow(); architecture(); donnees()
    crop_shot("01-connexion.png", "cap_connexion.png")
    crop_shot("02-tableau-de-bord.png", "cap_tableau_de_bord.png")
    crop_shot("03-retours-annonces.png", "cap_retours.png", top=1400)
    crop_shot("04-reception.png", "cap_reception.png", top=1750)
    crop_shot("06-dossier-controle-qualite.png", "cap_dossier_qc.png", top=1650)
    crop_shot("08-dossier-livre.png", "cap_dossier_livre.png", top=1100)
    crop_shot("12-journal-de-maintenance.png", "cap_journal.png", top=1000)
    crop_shot("14-palette-de-commandes.png", "cap_palette.png", top=1200)
    crop_shot("15-mobile-tableau-de-bord.png", "cap_mobile.png", top=1500)
    crop_shot("05-dossiers.png", "cap_dossiers.png", top=1000)
    crop_shot("10-fiche-de-vie.png", "cap_fiche_vie.png", top=1100)
    print("figures ok")
