"""Backend LaTeX du rapport : mêmes appels que docx_lib.Rapport, sortie en fichiers .tex
(main.tex, config/preambule.tex, pages_preliminaires/, chapitres/, bibliographie.tex).
"""
import re
from pathlib import Path

TEXT_W_CM = 15.5  # largeur utile (A4, marges 3 cm et 2,5 cm)

PLACEHOLDER = re.compile(r"(\*\*.+?\*\*|`.+?`|\{\{.+?\}\})")

REPLACE = {
    "₂": r"\textsubscript{2}",
    "\u00a0": "~",
    "\u202f": r"\,",
}
ALLOWED_NON_ASCII = set("àâäçéèêëîïôöùûüÿœÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒ«»·×°§–—…’‘“”€²")

SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def esc(s):
    out = []
    for ch in s:
        out.append(SPECIAL.get(ch, ch))
        if ch == "_":
            out.append(r"\allowbreak{}")
    return "".join(out)


def esc_code(s):
    """Texte machine : échappement + points de coupure après / _ . pour éviter les débordements."""
    out = []
    for ch in s:
        out.append(SPECIAL.get(ch, ch))
        if ch in "/_.-(,":
            out.append(r"\allowbreak{}")
    return "".join(out)


def typo(s):
    for k, v in REPLACE.items():
        s = s.replace(k, v)
    s = re.sub(r"\b1er\b", r"1\\textsuperscript{er}", s)
    s = re.sub(r"«\s*", r"\\og{}", s)
    s = re.sub(r"\s*»", r"\\fg{}", s)
    return s


class LatexRapport:
    kind = "latex"

    def __init__(self):
        self.files = {}
        self.cur = None
        self.mode = None
        self.fig = 0
        self.tab = 0
        self.placeholders = 0
        self.bib = []
        self.bib_note = ""
        self.unknown_chars = set()

    # ---------- utilitaires ----------
    def _w(self, s):
        if self.cur is not None:
            self.files[self.cur].append(s)

    def _open(self, path):
        self.cur = path
        self.files.setdefault(path, [])

    def inline(self, text):
        parts = []
        for part in PLACEHOLDER.split(text):
            if not part:
                continue
            if part.startswith("**"):
                parts.append(r"\textbf{" + self.inline(part[2:-2]) + "}")
            elif part.startswith("`"):
                parts.append(r"\texttt{" + typo(esc_code(part[1:-1])) + "}")
            elif part.startswith("{{"):
                self.placeholders += 1
                parts.append(r"\textcolor{red}{\textbf{[" + typo(esc(part[2:-2])) + "]}}")
            else:
                t = typo(esc(part))
                t = re.sub(r"\s*\[(\d{1,2})\]", lambda m: "~\\cite{ref" + m.group(1) + "}", t)
                parts.append(t)
        out = "".join(parts)
        for ch in set(re.findall(r"[^\x00-\x7f]", out)):
            if ch not in ALLOWED_NON_ASCII:
                self.unknown_chars.add(ch)
        return out

    # ---------- structure ----------
    def first_section_clean(self):
        pass

    def new_section(self, *a, **k):
        pass

    def page_break(self):
        self._w("\\newpage\n")

    def h1(self, text, page_break=True):
        t = text.strip()
        if t == "Remerciements":
            self.mode = "prelim"
            self._open("pages_preliminaires/remerciements.tex")
            self._w("\\chapter*{Remerciements}\n\\markboth{Remerciements}{Remerciements}\n\n")
        elif t == "Résumé":
            self.mode = "prelim"
            self._open("pages_preliminaires/resume.tex")
            self._w("\\chapter*{Résumé}\n\\markboth{Résumé}{Résumé}\n\n")
        elif t in ("Table des matières", "Liste des figures", "Liste des tableaux"):
            self.mode = "skip"
            self.cur = None
        elif t == "Liste des abréviations":
            self.mode = "abbr"
            self._open("pages_preliminaires/abreviations.tex")
            self._w("\\chapter*{Liste des abréviations}\n\\markboth{Liste des abréviations}{Liste des abréviations}\n\n")
        elif t in ("Introduction générale", "Conclusion générale"):
            self.mode = "body"
            fn = "introduction" if t.startswith("Intro") else "conclusion"
            self._open(f"chapitres/{fn}.tex")
            self._w(f"\\chapter*{{{t}}}\n\\addcontentsline{{toc}}{{chapter}}{{{t}}}\n\\markboth{{{t}}}{{{t}}}\n\n")
        elif t.startswith("Chapitre"):
            m = re.match(r"Chapitre (\d+) : (.+)", t)
            n, title = m.group(1), m.group(2)
            names = {"1": "ch1_entreprise", "2": "ch2_contexte", "3": "ch3_travaux", "4": "ch4_resultats"}
            self.mode = "body"
            self._open(f"chapitres/{names[n]}.tex")
            self._w(f"\\chapter{{{self.inline(title)}}}\n\n")
        elif t == "Annexes":
            self.mode = "annex"
            self._open("chapitres/annexes.tex")
            self._w("\\appendix\n\\setlength{\\emergencystretch}{2em}\n\n")
        elif t.startswith("Bibliographie"):
            self.mode = "bib"
            self._open("bibliographie.tex")
        else:
            raise ValueError("titre de niveau 1 inattendu : " + t)

    def h2(self, text):
        t = text.strip()
        if self.mode == "annex":
            m = re.match(r"Annexe [A-Z] : (.+)", t)
            self._w(f"\\clearpage\n\\chapter{{{self.inline(m.group(1))}}}\n\n")
        elif self.mode == "prelim":
            self._w(f"\\section*{{{self.inline(t)}}}\n\n")
        else:
            t = re.sub(r"^\d+(\.\d+)*\s+", "", t)
            self._w(f"\\section{{{self.inline(t)}}}\n\n")

    def h3(self, text):
        t = re.sub(r"^\d+(\.\d+)*\s+", "", text.strip())
        self._w(f"\\subsection{{{self.inline(t)}}}\n\n")

    # ---------- texte ----------
    def p(self, text, style=None, align=None, size=None, space_after=None, keep_next=False):
        if self.mode in ("skip", None) or not text.strip():
            return
        if self.mode == "bib":
            m = re.match(r"\[(\d+)\]\s+(.*)", text)
            if m:
                self.bib.append((m.group(1), m.group(2)))
            else:
                self.bib_note = text
            return
        self._w(self.inline(text) + "\n\n")

    def bullets(self, items):
        self._w("\\begin{itemize}\n" + "".join(f"  \\item {self.inline(t)}\n" for t in items) + "\\end{itemize}\n\n")

    def numbered(self, items):
        self._w("\\begin{enumerate}\n" + "".join(f"  \\item {self.inline(t)}\n" for t in items) + "\\end{enumerate}\n\n")

    def toc(self, instr, hint):
        pass  # \tableofcontents, \listoffigures, \listoftables sont dans main.tex

    # ---------- figures et tableaux ----------
    def figure(self, path, caption, width_cm=15.5, max_height_cm=17.5, landscape=False):
        """landscape=True : schéma UML seul sur une page A4 portrait, centré verticalement et horizontalement."""
        self.fig += 1
        name = Path(path).name
        cap = self.inline(caption)
        if landscape:
            lines = [
                "\\clearpage",
                "\\vspace*{\\fill}",
                "\\begin{center}",
                f"\\includegraphics[width={TEXT_W_CM:.1f}cm,height=19.5cm,keepaspectratio]{{{name}}}\\par\\medskip",
                f"\\captionof{{figure}}{{{cap}}}",
                "\\end{center}",
                "\\vspace*{\\fill}",
                "\\clearpage",
            ]
        else:
            w, h = min(width_cm, TEXT_W_CM), max_height_cm
            lines = [
                "\\begin{figure}[!htb]",
                "\\centering",
                f"\\includegraphics[width={w:.1f}cm,height={h:.1f}cm,keepaspectratio]{{{name}}}",
                f"\\caption{{{cap}}}",
                "\\end{figure}",
            ]
        self._w("\n".join(lines) + "\n\n")

    def figure_side(self, path, caption, width_cm=6.5):
        """Photo à droite du texte (habillage), utilisée pour la présentation de l'entreprise."""
        self.fig += 1
        name = Path(path).name
        self._w("\\begin{wrapfigure}[13]{r}{0.34\\textwidth}\n\\vspace{-6pt}\n\\centering\n"
                f"\\includegraphics[width=\\linewidth]{{{name}}}\n"
                f"\\caption{{{self.inline(caption)}}}\n\\end{{wrapfigure}}\n\n")

    def figure_placeholder(self, instruction, caption):
        self.fig += 1
        self._w("\\begin{figure}[H]\n\\centering\n"
                f"\\fbox{{\\parbox[c][4cm][c]{{0.8\\textwidth}}{{\\centering\\textcolor{{red}}{{{self.inline(instruction)}}}}}}}\n"
                f"\\caption{{{self.inline(caption)}}}\n\\end{{figure}}\n\n")

    def table(self, header, rows, caption, widths=None, size=9.5):
        n = len(header)
        if widths is None:
            widths = [1] * n
        # largeur utile moins le remplissage des cellules (2 × 5 pt) et les filets verticaux
        total = TEXT_W_CM - 0.37 * n - 0.15
        ws = [w / sum(widths) * total for w in widths]
        spec = "|" + "|".join(">{\\raggedright\\arraybackslash}p{%.2fcm}" % w for w in ws) + "|"
        head = " & ".join("\\sffamily\\bfseries\\color{white} " + self.inline(h) for h in header)
        grid = "\\renewcommand{\\arraystretch}{1.3}\\arrayrulecolor{ALtexte}"
        if self.mode == "abbr":
            body = "".join(f"\\textbf{{{self.inline(r[0])}}} & {self.inline(r[1])} \\\\ \\hline\n" for r in rows)
            self._w("{" + grid + "\\small\n\\begin{tabular}{|p{3cm}|p{%.2fcm}|}\n\\hline\n" % (TEXT_W_CM - 3 - 0.9)
                    + body + "\\end{tabular}\n}\n\n")
            return
        self.tab += 1
        fs = "\\footnotesize" if size < 9 else "\\small"
        cap = self.inline(caption)
        lines = [
            "\\Needspace{%d\\baselineskip}" % min(2 * len(rows) + 4, 22),
            "{" + fs + "\\setstretch{1.05}" + grid,
            "\\begin{longtable}{" + spec + "}",
            f"\\caption{{{cap}}}\\\\",
            "\\hline",
            "\\rowcolor{ALbleu} " + head + " \\\\ \\hline",
            "\\endfirsthead",
            f"\\caption[]{{{cap} (suite)}}\\\\",
            "\\hline",
            "\\rowcolor{ALbleu} " + head + " \\\\ \\hline",
            "\\endhead",
        ]
        for i, r in enumerate(rows):
            cells = " & ".join(self.inline(str(c)) for c in r)
            shade = "\\rowcolor{ALgris} " if i % 2 else ""
            lines.append(shade + cells + " \\\\ \\hline")
        lines += ["\\end{longtable}", "}", ""]
        self._w("\n".join(lines) + "\n")

    # ---------- sortie ----------
    def _bib_entry(self, text):
        parts, last = [], 0
        for m in re.finditer(r"https?://[^\s]+", text):
            url = m.group(0).rstrip(".,;)")
            parts.append(self.inline(text[last:m.start()]))
            parts.append("\\url{" + url + "}")
            last = m.start() + len(url)
        parts.append(self.inline(text[last:]))
        return "".join(parts)

    def _finish(self):
        if not self.bib:
            return
        items = "\n".join(f"\\bibitem{{ref{n}}}\n{self._bib_entry(t)}\n" for n, t in self.bib)
        tex = ("% BIBLIOGRAPHIE ET WEBOGRAPHIE\n{\\small\\setstretch{1.1}\n\\begin{thebibliography}{99}\n"
               "\\addcontentsline{toc}{chapter}{Bibliographie et webographie}\n\n" + items +
               "\\end{thebibliography}\n}\n")
        if self.bib_note:
            tex += "\n\\vspace{0.6em}\n\\noindent\\textit{" + self.inline(self.bib_note) + "}\n"
        self.files["bibliographie.tex"] = [tex]

    def save(self, outdir):
        self._finish()
        out = Path(outdir)
        for rel, chunks in self.files.items():
            p = out / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("".join(chunks), encoding="utf-8")
        return sorted(self.files)
