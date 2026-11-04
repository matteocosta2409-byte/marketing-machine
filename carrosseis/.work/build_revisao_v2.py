#!/usr/bin/env python3
# "O que mais cai no 1º dia do ENEM" v2, estilo das refs @matthgray de 04/11/2026.
# Dados: ENEM_1o_dia_o_que_mais_cai.pdf (GPS Chiron, 16 provas, 2018 a 2025, regular e PPL).
import os
from render_livro2 import (W, H, WORK, F, S, GREEN, BLUE, ROSE, YELLOW, INK, paper, text, Canvas)

OUT = os.path.join(WORK, "..", "output", "revisao-1-dia-v2")
X, MAXW = 84, W - 168
BODY, LH, GAP = F(54), 67, 36
SMALL = F(38)


def label_wrap(c, x, y, s, size=30, lh=37):
    for i, ln in enumerate(s.split("|")):
        c.label(x, y + i * lh, ln, size=size)


def nodes(c, y, items, r=80, fill=None, xs=None):
    """Fileira de círculos com % dentro e rótulo embaixo."""
    xs = xs or [W * (2 * i + 1) / (2 * len(items)) for i in range(len(items))]
    for x, (pct, lab) in zip(xs, items):
        c.circle(x, y, r, fill=fill)
        c.label(x, y, pct, size=39)
        label_wrap(c, x, y + r + 38, lab)
    return xs


def s1():
    img = paper(101)
    img, y = text(img, ["O que mais cai no"], F(84, "it"), 60, 150, W - 120, 104, 0, align="center")
    img, y = text(img, ["**1º dia do ENEM:**"], F(84), 60, y, W - 120, 104, 0, align="center")
    img, y = text(img, ["(3 matérias são 70% das questões)"], F(46), 60, y + 26, W - 120, 58, 0, align="center")
    c = Canvas()
    cols, r, step = 10, 29, 80
    x0 = (W - (cols - 1) * step) / 2
    y0 = 590
    seq = [GREEN] * 33 + [BLUE] * 15 + [ROSE] * 14 + [None] * 28
    for i, col in enumerate(seq):
        c.circle(x0 + (i % cols) * step, y0 + (i // cols) * step, r, fill=col, width=3)
    img = c.compose(img)
    fl = F(38)
    yl = y0 + 9 * step - 8
    for k, (lab, col) in enumerate([("**Português e Literatura**", GREEN), ("**Geografia**", BLUE), ("**História**", ROSE)]):
        xl = {0: 84, 1: 575, 2: 810}[k]
        img, _ = text(img, [(lab, col)], fl, xl, yl, 460, 46, 0)
    return img


def s2():
    img = paper(102)
    img, y = text(img, ["Na semana da prova, não dá pra revisar tudo. Eu revisaria **só o que mais cai.**",
                        "Os números são do GPS Chiron: 16 provas do ENEM, de 2018 a 2025."],
                  BODY, X, 120, MAXW, LH, GAP)
    data = [("Português e Literatura", 33.4, GREEN), ("Geografia", 15.3, BLUE), ("História", 14, ROSE),
            ("Sociologia", 8.6, None), ("Filosofia", 7.1, None), ("Artes", 6.6, None), ("Inglês ou espanhol", 5, None)]
    c = Canvas()
    y += 74
    c.label(X, y, "MÉDIA DE QUESTÕES POR PROVA", size=29, anchor="lm")
    y += 62
    for name, v, col in data:
        c.label(X, y + 22, name, size=30, anchor="lm")
        c.rect(X + 385, y, X + 385 + v * 13, y + 46, fill=col)
        c.label(X + 385 + v * 13 + 16, y + 22, f"{v:g}".replace(".", ","), size=30, anchor="lm")
        y += 80
    return c.compose(img)


def s3():
    img = paper(103)
    img, y = text(img, [("**Português e Literatura:** 33 questões por prova.", GREEN),
                        "80% delas são de linguística e semântica textual. Classes de palavras? Só 2%."],
                  BODY, X, 120, MAXW, LH, GAP)
    c = Canvas()
    top = y + 115
    c.ellipse(W / 2, top, 250, 76)
    c.label(W / 2, top - 20, "LÍNGUA E TEXTO", size=30)
    c.label(W / 2, top + 22, "80%", size=30)
    xs = [W * (2 * i + 1) / 6 for i in range(3)]
    yn = top + 235
    c.arrow(W / 2 - 140, top + 76, xs[0] + 40, yn - 90)
    c.arrow(W / 2, top + 84, W / 2, yn - 90)
    c.arrow(W / 2 + 140, top + 76, xs[2] - 40, yn - 90)
    nodes(c, yn, [("16%", "Textos|jornalísticos"), ("14%", "Variação|linguística"), ("13%", "Tipologia|textual")], xs=xs)
    img = c.compose(img)
    img, _ = text(img, ["Em literatura: **Modernismo e contemporânea (18%).**"], BODY, X, yn + 205, MAXW, LH, GAP)
    return img


def s4():
    img = paper(104)
    img, y = text(img, [("**Geografia:** 15 questões por prova.", BLUE),
                        "Dois temas dominam: questões ambientais (22%) e agropecuária (21%)."],
                  BODY, X, 170, MAXW, LH, GAP)
    c = Canvas()
    y1 = y + 115
    xa, xb = 280, 780
    c.ellipse(xa, y1, 205, 74)
    c.label(xa, y1 - 19, "AMBIENTAIS", size=29)
    c.label(xa, y1 + 22, "22%", size=29)
    c.ellipse(xb, y1, 205, 74)
    c.label(xb, y1 - 19, "AGROPECUÁRIA", size=29)
    c.label(xb, y1 + 22, "21%", size=29)
    yn = y1 + 230
    x1, x2, x3 = 280, 640, 925
    c.arrow(xa, y1 + 82, x1, yn - 90)
    c.arrow(xb - 60, y1 + 78, x2 + 24, yn - 90)
    c.arrow(xb + 60, y1 + 78, x3 - 24, yn - 90)
    nodes(c, yn, [("12%", "Problemas|ambientais|do Brasil"), ("13%", "Agropecuária|brasileira"), ("8%", "Sistemas|agrários")], xs=[x1, x2, x3])
    img = c.compose(img)
    img, _ = text(img, ["Depois, **problemas urbanos (8%).**"], BODY, X, yn + 250, MAXW, LH, GAP)
    return img


def s5():
    img = paper(105)
    img, y = text(img, [("**História:** 14 questões por prova.", ROSE),
                        "O que mais cai é Brasil. Eu seguiria a linha do tempo:"],
                  BODY, X, 170, MAXW, LH, GAP)
    c = Canvas()
    yl = y + 190
    xs = [205, 540, 875]
    c.arrow(70, yl, W - 60, yl)
    for x, (name, pct, sub) in zip(xs, [("COLÔNIA", "19%", "Economia colonial|e invasões|holandesas (6%)"),
                                        ("IMPÉRIO", "16%", "Segundo|Reinado (12%)"),
                                        ("REPÚBLICA", "27%", "República|Oligárquica (11%)|Era Vargas (5%)")]):
        c.circle(x, yl, 80, fill=(232, 233, 228))
        c.label(x, yl, pct, size=39)
        c.label(x, yl - 112, name, size=30)
        c.arrow(x, yl + 90, x, yl + 160)
        label_wrap(c, x, yl + 196, sub, size=29, lh=36)
    img = c.compose(img)
    img, _ = text(img, ["Se só der tempo pra dois: **Segundo Reinado e República Oligárquica.**"],
                  BODY, X, yl + 345, MAXW, LH, GAP, color=GREEN)
    return img


def s6():
    img = paper(106)
    img, y = text(img, ["**Sociologia:** 9 questões por prova."], BODY, X, 215, MAXW, LH, GAP)
    c = Canvas()
    yn = y + 125
    nodes(c, yn, [("27%", "Cultura|e etnia"), ("15%", "Estado, democracia|e cidadania"), ("13%", "Movimentos|sociais")])
    img = c.compose(img)
    img, y = text(img, ["**Filosofia:** 7 questões por prova."], BODY, X, yn + 250, MAXW, LH, GAP)
    c = Canvas()
    yn = y + 125
    nodes(c, yn, [("18%", "Filosofia política:|justiça e cidadania"), ("15%", "Ética|e moral"), ("9%", "Aristóteles")])
    return c.compose(img)


def s7():
    img = paper(107)
    img, y = text(img, ["**Artes:** 7 questões por prova."], BODY, X, 215, MAXW, LH, GAP)
    c = Canvas()
    yn = y + 125
    nodes(c, yn, [("28%", "Arte|contemporânea"), ("16%", "Cultura|de massa"), ("14%", "Panorama|da MPB")])
    img = c.compose(img)
    img, y = text(img, ["**Inglês ou espanhol:** 5 questões, quase só leitura de texto.",
                        "Gramática isolada praticamente não cai. Eu não gastaria essa semana decorando regra."],
                  BODY, X, yn + 250, MAXW, LH, GAP)
    return img


def s8():
    img = paper(108)
    img, y = text(img, ["Se fosse hoje, eu revisaria **nessa ordem:**"], BODY, X, 92, MAXW, LH, 0)
    rows = [("Modernismo e literatura contemporânea", 6), ("Textos jornalísticos", 5), ("Variação linguística", 5),
            ("Tipologia textual", 4), ("Textos técnicos e científicos", 3), ("Tipos de argumento", 3),
            ("Coerência e concisão", 3), ("Cultura e etnia", 2), ("Agropecuária brasileira", 2),
            ("Arte contemporânea", 2), ("Problemas ambientais do Brasil", 2), ("Segundo Reinado", 2)]
    c = Canvas()
    y += 42
    y0 = y
    step = 86
    for i, (name, n) in enumerate(rows):
        yy = y0 + i * step
        c.rect(X, yy + 2, X + 42, yy + 44, width=3)
        c.label(X + 66, yy + 22, name, size=38, font=lambda s: F(s), anchor="lm")
        c.label(W - X, yy + 22, f"≈ {n}", size=30, anchor="rm")
    img = c.compose(img)
    yf = y0 + len(rows) * step + 8
    img, _ = text(img, ["≈ questões por prova, estimadas pela média da matéria. Uma questão pode cobrar mais de um assunto."],
                  F(32, "it"), X, yf, MAXW, 42, 0)
    return img


def s9():
    img = paper(109)
    img, y = text(img, ["Comenta **“LISTA”**"], F(76), X, 210, MAXW, 92, 0)
    img, y = text(img, ["e eu te mando o PDF completo com o que mais cai em cada matéria do 1º dia."],
                  BODY, X, y + 30, MAXW, LH, GAP)
    from PIL import Image, ImageDraw
    c = Canvas()
    # seta à mão até a folha
    pts = [(250, y + 60), (330, y + 150), (450, y + 215), (585, y + 250)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], width=6)
    c.arrow(pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1], head=34, width=6)
    # folha
    x0, y0, x1, y1 = 610, y + 110, 950, y + 560
    c.rect(x0, y0, x1, y1, width=4, fill=(232, 233, 228))
    c.label((x0 + x1) / 2, y0 + 52, "O QUE MAIS CAI", size=27)
    c.line(x0 + 30, y0 + 92, x1 - 30, y0 + 92)
    for i, (w, col) in enumerate([(240, GREEN), (130, BLUE), (120, ROSE), (75, None), (62, None), (58, None), (45, None)]):
        yy = y0 + 124 + i * 44
        c.rect(x0 + 34, yy, x0 + 34 + w, yy + 24, width=2, fill=col)
    return c.compose(img)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate([s1, s2, s3, s4, s5, s6, s7, s8, s9], 1):
        fn().save(os.path.join(OUT, f"slide-{i:02d}.jpg"), quality=94)
    print("ok", os.path.abspath(OUT))
