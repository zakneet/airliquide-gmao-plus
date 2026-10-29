"""Prépare les photos du stage pour le rapport : sélection, recadrage, floutage des données sensibles,
montages légendés, ré-encodage JPEG sans aucune métadonnée (EXIF, GPS, etc.).

Usage : python preparer_images.py <index.json> <dossier_feuilles_google> <dossier_sortie>
  index.json : correspondance numéro -> chemin des photos d'origine (WhatsApp) ; les originaux ne sont jamais modifiés.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

IDX = {int(k): v for k, v in json.load(open(sys.argv[1], encoding="utf-8")).items()}
SHEETS = Path(sys.argv[2])
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)


def load(n):
    return ImageOps.exif_transpose(Image.open(IDX[n])).convert("RGB")


def blur(im, box, radius=18):
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(radius))
    im.paste(reg, box)
    return im


def save(im, name, maxw=1600):
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    clean = Image.new("RGB", im.size)
    clean.paste(im)  # ré-encodage : aucune métadonnée d'origine n'est conservée
    clean.save(OUT / name, "JPEG", quality=86, optimize=True)


def montage(items, name, rows_h=520, cols=None, gap=14):
    """items : liste de (image, étiquette) ; étiquette (a), (b)… en bas à gauche de chaque vignette."""
    cols = cols or len(items)
    thumbs = []
    for im, lab in items:
        t = im.copy()
        t = t.resize((int(t.width * rows_h / t.height), rows_h), Image.LANCZOS)
        d = ImageDraw.Draw(t)
        d.rectangle([0, rows_h - 52, 64, rows_h], fill=(255, 255, 255))
        d.text((10, rows_h - 46), lab, fill=(20, 40, 100), font=FONT)
        thumbs.append(t)
    rows = [thumbs[i:i + cols] for i in range(0, len(thumbs), cols)]
    W = max(sum(t.width for t in r) + gap * (len(r) - 1) for r in rows)
    H = rows_h * len(rows) + gap * (len(rows) - 1)
    sheet = Image.new("RGB", (W, H), "white")
    y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y))
            x += t.width + gap
        y += rows_h + gap
    save(sheet, name, 1800)


# --- plan des ateliers santé (siège de Charguia)
im = load(84)
save(ImageOps.autocontrast(im, cutoff=1), "plan_ateliers_sante.jpg")

# --- signalétique des zones : retour, atelier, stockage
a = load(45).crop((560, 70, 1060, 718))
b = load(43).crop((520, 90, 1000, 310))
c = load(44).crop((500, 60, 960, 330))
montage([(a, "(a)"), (b, "(b)"), (c, "(c)")], "signaletique_zones.jpg", rows_h=420)

# --- journal papier : la ligne manuscrite (série, mesures, pannes) est floutée
j = load(67)
j = blur(j, (415, 252, 935, 288), 20)
save(j.crop((140, 0, 1250, 718)), "journal_papier.jpg")

# --- classeur Google Sheets : colonne des numéros de série floutée
r = Image.open(SHEETS / "1.jpg").convert("RGB")
r = blur(r, (385, 340, 640, 600), 22)
# fond clair (inversion du thème sombre de Google Sheets) pour limiter l'encre à l'impression
save(ImageOps.invert(r.crop((385, 250, 2230, 950))), "classeur_retours.jpg", 1800)  # colonne des horodatages exclue
m = Image.open(SHEETS / "2.jpg").convert("RGB")
m = blur(m, (680, 330, 885, 510), 22)
save(ImageOps.invert(m.crop((360, 250, 2230, 950))), "classeur_journal.jpg", 1800)

# --- montages d'équipements
comp = blur(blur(load(10), (670, 420, 930, 550), 16), (1330, 250, 1480, 460), 16)  # étiquettes de série des pièces
conc = [(load(2).crop((0, 150, 718, 1300)), "(a)"), (comp.crop((200, 0, 1500, 718)), "(b)"),
        (load(15).crop((0, 300, 718, 1250)), "(c)"), (load(16).crop((0, 300, 718, 1250)), "(d)")]
montage(conc, "concentrateur_composants.jpg", rows_h=460, cols=2)
vent = [(load(49).crop((0, 250, 718, 1250)), "(a)"), (load(46).crop((0, 250, 718, 1250)), "(b)"),
        (load(54).crop((200, 0, 1500, 718)), "(c)"), (load(12).crop((0, 200, 718, 1250)), "(d)")]
montage(vent, "ventilation_composants.jpg", rows_h=460, cols=2)
print("images ok :", sorted(p.name for p in OUT.glob("*.jpg")))
