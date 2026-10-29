"""Diagrammes UML du rapport, dessinés dans le style du modèle de rapport (bleu 0,114,188, police à empattements).

Usage : python generer_uml.py <dossier_sortie>
Les diagrammes sont dessinés en code (Pillow) pour rester reproductibles et versionnables ;
leurs sources textuelles équivalentes (PlantUML / Mermaid) sont dans docs/diagrams/.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
F = Path("C:/Windows/Fonts")
S = 3  # facteur de suréchantillonnage (rendu net à l'impression)

BLUE = (0, 114, 188)
LIGHT = (229, 241, 250)
BLACK = (20, 20, 20)
GREY = (110, 110, 110)


def font(size, bold=False, italic=False):
    name = {(False, False): "times.ttf", (True, False): "timesbd.ttf", (False, True): "timesi.ttf", (True, True): "timesbi.ttf"}[(bold, italic)]
    return ImageFont.truetype(str(F / name), int(size * S))


class Canvas:
    def __init__(self, w, h):
        self.im = Image.new("RGB", (w * S, h * S), "white")
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def line(self, pts, color=BLACK, width=1.4, dash=False):
        pts = self.P(pts)
        if not dash:
            self.d.line(pts, fill=color, width=int(width * S), joint="curve")
            return
        for a, b in zip(pts, pts[1:]):
            length = math.dist(a, b)
            n = int(length / (7 * S))
            for i in range(0, n, 2):
                p0 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                p1 = (a[0] + (b[0] - a[0]) * min(i + 1, n) / n, a[1] + (b[1] - a[1]) * min(i + 1, n) / n)
                self.d.line([p0, p1], fill=color, width=int(width * S))

    def head(self, tip, frm, kind="open", color=BLACK, size=10):
        """Pointe de flèche : open (>), filled, triangle (généralisation), diamond (agrégation)."""
        a = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        t = (tip[0] * S, tip[1] * S)
        s = size * S
        def pt(dx, dy):
            return (t[0] - dx * math.cos(a) + dy * math.sin(a), t[1] - dx * math.sin(a) - dy * math.cos(a))
        if kind == "filled":
            self.d.polygon([t, pt(s, s * 0.38), pt(s, -s * 0.38)], fill=color)
        elif kind == "triangle":
            self.d.polygon([t, pt(s, s * 0.5), pt(s, -s * 0.5)], fill="white", outline=color)
        else:
            self.d.line([pt(s, s * 0.45), t, pt(s, -s * 0.45)], fill=color, width=int(1.4 * S))

    def arrow(self, pts, kind="open", color=BLACK, width=1.4, dash=False, both=False, size=10):
        self.line(pts, color, width, dash)
        self.head(pts[-1], pts[-2], kind, color, size)
        if both:
            self.head(pts[0], pts[1], kind, color, size)

    def text(self, xy, s, size=14, bold=False, italic=False, color=BLACK, anchor="l", bg=None):
        f = font(size, bold, italic)
        w = self.d.textlength(s, font=f)
        x, y = xy[0] * S, xy[1] * S
        if anchor == "c":
            x -= w / 2
        elif anchor == "r":
            x -= w
        h = f.size
        if bg:
            self.d.rectangle([x - 2 * S, y - 1 * S, x + w + 2 * S, y + h * 1.05], fill=bg)
        self.d.text((x, y), s, font=f, fill=color)
        return w / S

    def multiline(self, cx, cy, s, size=14, bold=False, color=BLACK, lead=1.18):
        lines = s.split("\n")
        f = font(size, bold)
        total = len(lines) * f.size * lead
        y = cy * S - total / 2
        for ln in lines:
            w = self.d.textlength(ln, font=f)
            self.d.text((cx * S - w / 2, y), ln, font=f, fill=color)
            y += f.size * lead

    def box(self, x, y, w, h, fill=None, outline=BLUE, width=1.6, r=6):
        self.d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=r * S, fill=fill, outline=outline, width=int(width * S))

    def ellipse(self, cx, cy, w, h, fill="white", outline=BLUE):
        self.d.ellipse([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S], fill=fill, outline=outline, width=int(1.6 * S))

    def actor(self, x, y, label, size=15):
        d = self.d
        def p(a, b): return (a * S, b * S)
        r = 9
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=BLACK, width=int(1.6 * S), fill="white")
        for a, b in (((x, y + r), (x, y + 38)), ((x - 15, y + 22), (x + 15, y + 22)), ((x, y + 38), (x - 12, y + 62)), ((x, y + 38), (x + 12, y + 62))):
            d.line([p(*a), p(*b)], fill=BLACK, width=int(1.6 * S))
        self.text((x, y + 66), label, size, anchor="c")

    def save(self, name):
        """Rogne les marges blanches : le schéma occupe toute la largeur disponible dans le rapport."""
        from PIL import ImageChops
        bbox = ImageChops.difference(self.im, Image.new("RGB", self.im.size, "white")).getbbox()
        im = self.im
        if bbox:
            pad = 12 * S
            im = im.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0), min(bbox[2] + pad, im.width), min(bbox[3] + pad, im.height)))
        im.save(OUT / name, dpi=(300, 300))




RED = (160, 60, 40)


def stereotype(c, x, y, s, color=BLUE):
    c.text((x, y), s, 13, italic=True, color=color, anchor="c", bg="white")


# Tous les schémas sont dessinés sur une toile d'environ 860 px de large : placés sur 15,5 cm (largeur
# utile d'une page A4 portrait), les textes restent lisibles (environ 7 pt).

# =====================================================================================
# 1. Cas d'utilisation
# =====================================================================================
def cas_utilisation():
    c = Canvas(860, 975)
    c.box(115, 15, 630, 885, outline=BLUE, width=1.6)
    c.text((130, 24), "AirLiquide GMAO+", 18, bold=True, color=BLUE)
    left = [
        ("S'authentifier", 95), ("Annoncer un retour", 173), ("Réceptionner un appareil", 251),
        ("Désinfecter l'appareil", 329), ("Réaliser le diagnostic", 407), ("Enregistrer la réparation", 485),
        ("Effectuer le contrôle qualité", 563), ("Mettre en stock et livrer", 641),
        ("Consulter la fiche de vie", 719), ("Consulter le journal et\nle tableau de bord", 807),
    ]
    xl, lw = 270, 250
    pos = {}
    for label, y in left:
        c.ellipse(xl, y, lw, 56)
        c.multiline(xl, y, label, 14.5)
        pos[label] = (xl, y)
    xr, rw = 620, 200
    right = {
        "Gérer utilisateurs\net catalogues": 173,
        "Reprendre le questionnaire\nde retour": 251,
        "Exporter les rapports\nen CSV": 329,
        "Joindre des photos": 485,
        "Vérifier les prérequis\nde l'étape": 641,
    }
    for label, y in right.items():
        c.ellipse(xr, y, rw, 56)
        c.multiline(xr, y, label, 14)
    # acteurs
    c.actor(55, 440, "Technicien", 15)
    c.actor(800, 190, "Responsable SAV", 15)
    for label, (x, y) in pos.items():
        c.line([(68, 462), (x - lw / 2, y)], width=1.1)
    for key in ("Gérer utilisateurs\net catalogues", "Exporter les rapports\nen CSV"):
        c.line([(790, 212), (xr + rw / 2, right[key])], width=1.1)
    # généralisation Responsable -> Technicien
    c.arrow([(800, 285), (800, 935), (55, 935), (55, 535)], kind="triangle", width=1.1, size=12)
    c.text((430, 938), "hérite de tous les cas d'utilisation du technicien", 13, italic=True, color=GREY, anchor="c", bg="white")
    # extend
    c.arrow([(xr - rw / 2, 251), (xl + lw / 2, 251)], dash=True, color=BLUE, width=1.2)
    stereotype(c, 458, 232, "«extend»")
    c.arrow([(xr - rw / 2, 485), (xl + lw / 2, 485)], dash=True, color=BLUE, width=1.2)
    stereotype(c, 475, 466, "«extend»")
    # include : chaque étape inclut la vérification des prérequis (bus vertical)
    for label in ("Désinfecter l'appareil", "Réaliser le diagnostic", "Effectuer le contrôle qualité"):
        y = pos[label][1]
        c.line([(xl + lw / 2, y), (430, y)], color=BLUE, width=1.0, dash=True)
    c.line([(430, 329), (430, 641)], color=BLUE, width=1.0, dash=True)
    c.arrow([(xl + lw / 2, 641), (xr - rw / 2, 641)], dash=True, color=BLUE, width=1.2)
    stereotype(c, 458, 622, "«include»")
    c.save("uml_cas_utilisation.png")


# =====================================================================================
# 2. Diagramme d'états du dossier (colonne verticale)
# =====================================================================================
def etats():
    c = Canvas(860, 900)
    cx, w, h = 410, 190, 58
    names = ["Reçu", "Désinfecté", "Diagnostic\nterminé", "Réparé", "Contrôle\nqualité validé", "En stock\nlivrable", "Livré"]
    labels = ["désinfection validée", "diagnostic enregistré", "réparation enregistrée", "contrôle conforme", "entrée en stock", "livraison enregistrée"]
    ys = [70 + i * 108 for i in range(7)]
    c.d.ellipse([(cx - 8) * S, 18 * S, (cx + 8) * S, 34 * S], fill=BLACK)
    c.arrow([(cx, 34), (cx, ys[0])], kind="filled", size=10)
    for i, n in enumerate(names):
        c.box(cx - w / 2, ys[i], w, h, fill=LIGHT, r=14)
        c.multiline(cx, ys[i] + h / 2, n, 16, bold=True)
    for i, lab in enumerate(labels):
        a, b = ys[i] + h, ys[i + 1]
        c.arrow([(cx, a), (cx, b)], kind="filled", size=10)
        c.text((cx + 14, (a + b) / 2 - 9), lab, 14, color=BLUE)
    # état final
    fy = ys[6] + h + 62
    c.arrow([(cx, ys[6] + h), (cx, fy - 12)], kind="filled", size=10)
    c.d.ellipse([(cx - 12) * S, (fy - 12) * S, (cx + 12) * S, (fy + 12) * S], outline=BLACK, width=int(1.6 * S))
    c.d.ellipse([(cx - 7) * S, (fy - 7) * S, (cx + 7) * S, (fy + 7) * S], fill=BLACK)
    c.text((cx + 14, ys[6] + h + 20), "un dossier livré ne se rouvre pas", 13, italic=True, color=GREY)
    # boucle : contrôle non conforme (sur Réparé)
    y3 = ys[3]
    c.line([(cx + w / 2, y3 + 16), (cx + w / 2 + 62, y3 + 16), (cx + w / 2 + 62, y3 + 42), (cx + w / 2, y3 + 42)], width=1.4)
    c.head((cx + w / 2, y3 + 42), (cx + w / 2 + 62, y3 + 42), "filled", size=10)
    c.text((cx + w / 2 + 74, y3 + 12), "contrôle non conforme :", 13.5, color=RED)
    c.text((cx + w / 2 + 74, y3 + 30), "le statut reste « Réparé »", 13.5, color=RED)
    # retour arrière (Responsable SAV) : de Réparé vers Désinfecté
    xa = cx - w / 2 - 72
    c.arrow([(cx - w / 2, y3 + h / 2), (xa, y3 + h / 2), (xa, ys[1] + h / 2), (cx - w / 2, ys[1] + h / 2)], kind="filled", color=RED, dash=True, size=10)
    for k, t in enumerate(["retour arrière d'une étape :", "Responsable SAV uniquement,", "commentaire obligatoire"]):
        c.text((xa - 10, ys[2] + 4 + k * 18), t, 13.5, color=RED, anchor="r")
    c.save("uml_etats.png")


# =====================================================================================
# 3. Diagrammes de classes
# =====================================================================================
def cls(c, x, y, w, name, attrs, fill=LIGHT):
    lh = 19
    h = 30 + lh * len(attrs) + 8
    c.box(x, y, w, h, fill="white", r=3)
    c.d.rectangle([x * S, y * S, (x + w) * S, (y + 30) * S], fill=fill, outline=BLUE, width=int(1.6 * S))
    c.text((x + w / 2, y + 5), name, 16, bold=True, anchor="c")
    for i, a in enumerate(attrs):
        c.text((x + 8, y + 36 + i * lh), a, 13.5)
    return (x, y, w, h)


def mult(c, x, y, s, anchor="l"):
    c.text((x, y), s, 13.5, color=BLUE, bold=True, anchor=anchor, bg="white")


def classes_coeur():
    c = Canvas(860, 830)
    br = cls(c, 30, 12, 200, "Brand", ["name"])
    dt = cls(c, 630, 12, 200, "DeviceType", ["name"])
    dm = cls(c, 330, 150, 200, "DeviceModel", ["name"])
    dv = cls(c, 300, 290, 260, "Device", ["serial_number (unique)", "internal_code (unique)", "created_at"])
    ds = cls(c, 330, 460, 290, "DossierSAV", ["reference (unique)", "status", "biohazard", "biohazard_status", "visual_condition", "hour_counter", "received_at"])
    rd = cls(c, 20, 490, 250, "ReturnDeclaration", ["return_id (unique)", "serial_number", "visual_condition", "biohazard_status", "missing_accessories", "declared_at"])
    sh = cls(c, 330, 700, 240, "StatusHistory", ["from_status", "to_status", "comment", "at (immuable)"])
    us = cls(c, 650, 560, 190, "User", ["email (unique)", "first_name", "last_name", "role", "is_active"])
    B = lambda b: b[1] + b[3]
    # Brand 1 — * DeviceModel
    c.line([(130, B(br)), (130, 178), (330, 178)]); mult(c, 136, B(br) + 3, "1"); mult(c, 304, 159, "*")
    # DeviceType 1 — * DeviceModel
    c.line([(700, B(dt)), (700, 178), (530, 178)]); mult(c, 706, B(dt) + 3, "1"); mult(c, 534, 159, "*")
    # DeviceType 1 — * Device
    c.line([(790, B(dt)), (790, 337), (560, 337)]); mult(c, 796, B(dt) + 3, "1"); mult(c, 564, 318, "*")
    # DeviceModel 0..1 — * Device
    c.line([(430, B(dm)), (430, 290)]); mult(c, 436, B(dm) + 3, "0..1"); mult(c, 436, 270, "*")
    # Device 1 — * DossierSAV
    c.line([(430, B(dv)), (430, 460)]); mult(c, 436, B(dv) + 3, "1"); mult(c, 436, 440, "*")
    # ReturnDeclaration 0..1 — 1 DossierSAV
    c.line([(270, 540), (330, 540)]); mult(c, 272, 520, "0..1"); mult(c, 312, 560, "1")
    # DossierSAV 1 — * StatusHistory
    c.line([(450, B(ds)), (450, 700)]); mult(c, 456, B(ds) + 3, "1"); mult(c, 456, 680, "*")
    # User 1 — * DossierSAV (received_by)
    c.line([(620, 520), (745, 520), (745, 560)]); mult(c, 624, 500, "*"); mult(c, 751, 536, "1")
    c.text((660, 500), "received_by", 13, italic=True, color=GREY)
    # User 1 — * StatusHistory (user)
    c.line([(570, 757), (745, 757), (745, B(us))]); mult(c, 576, 737, "*"); mult(c, 751, B(us) + 4, "1")
    c.text((640, 737), "user", 13, italic=True, color=GREY)
    c.save("uml_classes_coeur.png")


def classes_etapes():
    c = Canvas(860, 815)
    w = 195
    xs = [10, 225, 440, 655]
    # colonne 2 : Fault, DetectedFault, Diagnosis (empilés vers le haut)
    fa = cls(c, xs[1], 10, w, "Fault", ["name", "active"])
    df = cls(c, xs[1], 140, w, "DetectedFault", ["severity", "comment"])
    dg = cls(c, xs[1], 270, w, "Diagnosis", ["comment", "at"])
    # colonne 3 : Part, ReplacedPart, Repair
    pa = cls(c, xs[2], 10, w, "Part", ["reference (unique)", "name", "manufacturer", "active"])
    rp = cls(c, xs[2], 170, w, "ReplacedPart", ["quantity"])
    rep = cls(c, xs[2], 270, w, "Repair", ["started_at", "ended_at", "tests", "parts_exit_document", "comment"])
    di = cls(c, xs[0], 270, w, "Disinfection", ["product", "validated", "comment", "at"])
    qc = cls(c, xs[3], 270, w, "QualityControl", ["checklist", "result", "purity", "flow_pressure", "audible_alarm_ok", "comment"])
    c.text((xs[1] - 8, 38), "catalogue par type d'appareil", 12.5, italic=True, color=GREY, anchor="r")
    d2, d3 = xs[1] + w / 2, xs[2] + w / 2
    # Diagnosis 1 — * DetectedFault — * ... 1 Fault
    c.line([(d2, 270), (d2, 216)]); mult(c, d2 + 5, 250, "1"); mult(c, d2 + 5, 218, "*")
    c.line([(d2, 140), (d2, 86)]); mult(c, d2 + 5, 120, "*"); mult(c, d2 + 5, 88, "1")
    # Repair 1 — * ReplacedPart — * ... 1 Part
    c.line([(d3, 270), (d3, 227)]); mult(c, d3 + 5, 250, "1"); mult(c, d3 + 5, 229, "*")
    c.line([(d3, 170), (d3, 124)]); mult(c, d3 + 5, 150, "*"); mult(c, d3 + 5, 126, "1")
    # bus haut
    bus = 470
    tops = [(di, "0..1"), (dg, "0..1"), (rep, "0..1"), (qc, "*")]
    c.line([(xs[0] + w / 2, bus), (xs[3] + w / 2, bus)])
    for (b, m), x in zip(tops, xs):
        cxm = x + w / 2
        c.line([(cxm, b[1] + b[3]), (cxm, bus)])
        mult(c, cxm + 5, b[1] + b[3] + 3, m)
    ds = cls(c, 332, 520, 200, "DossierSAV", ["reference, status, …"])
    c.line([(432, bus), (432, 520)]); mult(c, 438, 495, "1")
    # bus bas
    bus2 = 635
    c.line([(432, 520 + ds[3]), (432, bus2)]); mult(c, 438, 520 + ds[3] + 3, "1")
    bottom = [("StockMovement", ["kind", "location", "at"], "*", 137), ("Delivery", ["recipient", "delivery_note", "comment", "at"], "0..1", 432), ("Photo", ["kind", "image", "at"], "*", 722)]
    c.line([(137, bus2), (722, bus2)])
    for name, attrs, m, cxm in bottom:
        cls(c, cxm - w / 2, 685, w, name, attrs)
        c.line([(cxm, bus2), (cxm, 685)]); mult(c, cxm + 5, 662, m)
    c.save("uml_classes_etapes.png")


# =====================================================================================
# 4. Diagrammes de séquence
# =====================================================================================
def sequence(name, w, parts, msgs, frames):
    """msgs : (type, de, vers, libellé[, pas]) ; frames : (libellé, idx_début, idx_fin, couleur)."""
    top = 90
    ys, y = [], top
    for m in msgs:
        ys.append(y)
        y += m[4] if len(m) > 4 else 42
    h = int(y + 20)
    c = Canvas(w, h)
    xs = {}
    for label, x in parts:
        xs[label] = x
        c.box(x - 66, 10, 132, 48, fill=LIGHT, r=4)
        c.multiline(x, 34, label, 14.5, bold=True)
        c.line([(x, 58), (x, h - 12)], color=GREY, width=1.0, dash=True)
    for label, i0, i1, color in frames:
        y0, y1 = ys[i0] - 22, ys[i1] + 22
        c.box(10, y0, w - 20, y1 - y0, outline=color, width=1.3, r=2)
        c.text((18, y0 + 2), label, 13, bold=True, color=color, bg="white")
    for m, y in zip(msgs, ys):
        kind, a, b, label = m[0], m[1], m[2], m[3]
        if kind == "sep":
            c.line([(10, y), (w - 10, y)], color=RED, width=1.0, dash=True)
            c.text((18, y + 3), label, 13, bold=True, color=RED)
            continue
        xa = xs[a]
        if kind == "self":
            c.line([(xa, y - 6), (xa + 44, y - 6), (xa + 44, y + 14), (xa, y + 14)], width=1.2)
            c.head((xa, y + 14), (xa + 44, y + 14), "filled", size=9)
            c.text((xa + 52, y - 4), label, 13)
            continue
        xb = xs[b]
        ret = kind == "ret"
        c.arrow([(xa, y), (xb, y)], kind="open" if ret else "filled", dash=ret, width=1.2, size=9)
        c.text(((xa + xb) / 2, y - 19), label, 13, anchor="c", bg="white")
    c.save(name)


def sequences():
    T, N, A, Sv, P = "Technicien", "Navigateur\n(Next.js)", "API Django\nREST", "Service métier\n(services.py)", "PostgreSQL"
    sequence("uml_sequence_etape.png", 860,
             [(T, 70), (N, 235), (A, 405), (Sv, 575), (P, 765)],
             [
                 ("msg", T, N, "remplit le formulaire"),
                 ("msg", N, A, "POST …/quality-control/"),
                 ("self", A, None, "authentification, rôle, validation des champs", 46),
                 ("msg", A, Sv, "record_quality_control(…)"),
                 ("msg", Sv, P, "SELECT … FOR UPDATE"),
                 ("ret", P, Sv, "dossier verrouillé"),
                 ("self", Sv, None, "statut et checklist vérifiés", 46),
                 ("msg", Sv, P, "INSERT ContrôleQualité"),
                 ("msg", Sv, P, "[conforme] UPDATE statut"),
                 ("msg", Sv, P, "INSERT HistoriqueStatut"),
                 ("sep", None, None, "[non conforme : commentaire obligatoire, statut inchangé, trace dans HistoriqueStatut]", 38),
                 ("ret", Sv, A, "dossier mis à jour"),
                 ("ret", A, N, "200 + dossier (JSON)"),
                 ("ret", N, T, "étape suivante affichée"),
             ],
             [("transaction atomique", 3, 11, BLUE)])
    U, N2, A2, P2 = "Utilisateur", "Navigateur\n(Next.js)", "API Django\nREST", "PostgreSQL"
    sequence("uml_sequence_auth.png", 860,
             [(U, 80), (N2, 290), (A2, 520), (P2, 760)],
             [
                 ("msg", U, N2, "saisit e-mail et mot de passe"),
                 ("msg", N2, A2, "POST /api/auth/login/"),
                 ("self", A2, None, "limite de 10 essais par minute", 46),
                 ("msg", A2, P2, "vérifie le mot de passe"),
                 ("ret", A2, N2, "jeton d'accès + cookie HttpOnly"),
                 ("self", N2, None, "jeton d'accès gardé en mémoire", 46),
                 ("msg", N2, A2, "requête + Authorization: Bearer"),
                 ("ret", A2, N2, "401 (jeton expiré)"),
                 ("msg", N2, A2, "POST /api/auth/refresh/ (cookie)"),
                 ("ret", A2, N2, "nouveau jeton d'accès"),
             ],
             [("connexion", 0, 5, BLUE), ("renouvellement", 6, 9, RED)])


# =====================================================================================
# 5. Architecture
# =====================================================================================
def architecture():
    c = Canvas(860, 680)
    def block(x, y, w, h, text, fill="white", size=14.5):
        c.box(x, y, w, h, fill=fill, r=8)
        c.multiline(x + w / 2, y + h / 2, text, size)
    block(215, 20, 430, 110, "Navigateur (poste ou tablette)\nNext.js · React · TypeScript\nTailwind CSS · shadcn/ui\npages, formulaires, parcours du dossier", fill=LIGHT)
    block(215, 215, 430, 100, "Serveur Django : API REST (Django REST Framework)\nJWT · permissions par rôle · sérialiseurs")
    block(215, 395, 430, 90, "Services métier (services.py)\nworkflow, prérequis, transactions atomiques")
    block(130, 575, 280, 90, "PostgreSQL 16 (conteneur Docker)\ndonnées et historique immuable")
    block(450, 575, 280, 90, "Fichiers médias\nphotos des dossiers")
    block(690, 215, 160, 100, "Documentation\nde l'API\nOpenAPI / Swagger", size=13.5)
    c.arrow([(430, 130), (430, 215)], both=True, color=BLUE, width=1.6, kind="filled", size=10)
    c.text((446, 160), "HTTPS · JSON · /api/…", 13.5, anchor="l")
    c.arrow([(430, 315), (430, 395)], both=True, color=BLUE, width=1.6, kind="filled", size=10)
    c.arrow([(270, 485), (270, 575)], both=True, color=BLUE, width=1.6, kind="filled", size=10)
    c.text((284, 520), "SQL (ORM)", 13.5, anchor="l")
    c.arrow([(590, 485), (590, 575)], color=BLUE, width=1.6, kind="filled", size=10)
    c.text((604, 520), "écriture des fichiers", 13.5, anchor="l")
    c.arrow([(645, 265), (690, 265)], dash=True, color=BLUE, width=1.4, kind="filled", size=9)
    c.save("uml_architecture.png")


if __name__ == "__main__":
    cas_utilisation(); etats(); classes_coeur(); classes_etapes(); sequences(); architecture()
    print("uml ok")
