#!/usr/bin/env python3
# "O que mais cai" por área, matéria por matéria: só verde como cor de destaque, sem comparar o peso das matérias.
# Dados: ENEM_1o_dia_o_que_mais_cai.pdf (GPS Chiron, 16 provas, 2018 a 2025, regular e PPL).
import glob
import os
from render_livro2 import W, WORK, F, GREEN, paper, text, Canvas
from build_revisao_v2 import X, MAXW, BODY, LH, GAP, label_wrap, nodes

PANEL = (232, 233, 228)
FEST = "≈ questões por prova, estimadas pela média da matéria. Uma questão pode cobrar mais de um assunto."


def cover(area, materias, seed):
    img = paper(seed)
    img, y = text(img, ["O que mais cai em"], F(84, "it"), 60, 215, W - 120, 104, 0, align="center")
    img, y = text(img, [f"**{area} no ENEM:**"], F(84), 60, y, W - 120, 104, 0, align="center")
    img, y = text(img, ["(Os tópicos de cada matéria, em 16 provas)"], F(46), 70, y + 24, W - 140, 58, 0, align="center")
    c = Canvas()
    yt = y + 150
    c.ellipse(W / 2, yt, 210, 66, fill=GREEN)
    c.label(W / 2, yt, area.upper(), size=32)
    xs = [W * (2 * i + 1) / (2 * len(materias)) for i in range(len(materias))]
    yn = yt + 255
    r = 100 if len(materias) == 4 else 115
    for x, m in zip(xs, materias):
        c.arrow(W / 2 + (x - W / 2) * 0.42, yt + 68, x, yn - r - 8)
        c.circle(x, yn, r, fill=PANEL)
        label_wrap(c, x, yn - (m.count("|") * 15), m, size=24, lh=30)
    return c.compose(img)


def intro(seed, cred):
    img = paper(seed)
    img, _ = text(img, [f"Já fiz **{cred}**",
                        "Na semana da prova, não dá pra revisar tudo. Eu revisaria só o que mais cai em cada matéria.",
                        "Os números são do **GPS Chiron,** uma ferramenta da minha plataforma que mede o quanto cai de cada matéria e tópico nas provas de todo o Brasil.",
                        "Aqui, são 16 provas do ENEM, de 2018 a 2025. Cada % mostra quanto o tópico pesa dentro da matéria."],
                  BODY, X, 210, MAXW, LH, GAP)
    return img


def materia(seed, head, topicos, fim=None):
    """Título da matéria, 6 tópicos em 2 fileiras e uma frase final opcional."""
    img = paper(seed)
    img, y = text(img, [head], BODY, X, 150, MAXW, LH, GAP)
    c = Canvas()
    yn = y + 135
    nodes(c, yn, topicos[:3])
    nodes(c, yn + 340, topicos[3:])
    img = c.compose(img)
    if fim:
        img, _ = text(img, [fim], BODY, X, yn + 570, MAXW, LH, GAP)
    return img


def timeline(c, yl, items, xs):
    c.arrow(60, yl, W - 50, yl)
    for x, (name, pct, sub) in zip(xs, items):
        c.circle(x, yl, 80, fill=PANEL)
        c.label(x, yl, pct, size=39)
        c.label(x, yl - 112, name, size=30)
        c.arrow(x, yl + 90, x, yl + 160)
        label_wrap(c, x, yl + 196, sub, size=29, lh=36)


def checklist(seed, rows):
    img = paper(seed)
    img, y = text(img, ["Se fosse hoje, eu revisaria **nessa ordem:**"], BODY, X, 92, MAXW, LH, 0)
    c = Canvas()
    y0 = y + 42
    step = 86
    for i, (name, n) in enumerate(rows):
        yy = y0 + i * step
        c.rect(X, yy + 2, X + 42, yy + 44)
        c.label(X + 66, yy + 22, name, size=38, font=lambda s: F(s), anchor="lm")
        c.label(W - X, yy + 22, f"≈ {n}", size=30, anchor="rm")
    img = c.compose(img)
    img, _ = text(img, [FEST], F(32, "it"), X, y0 + len(rows) * step + 8, MAXW, 42, 0)
    return img


def cta(seed, filtros):
    from build_linguagens_v2 import curva  # importado aqui porque esse módulo importa PANEL daqui
    img = paper(seed)
    img, y = text(img, ["Comenta **“BANCO”**"], F(76), X, 110, MAXW, 92, 0)
    img, y = text(img, ["e eu te mando a minha plataforma, com o banco de questões do ENEM."],
                  BODY, X, y + 25, MAXW, LH, GAP)
    c = Canvas()
    curva(c, (190, y + 35), (195, y + 215), (360, y + 290), (570, y + 245))
    x0, y0, x1 = 600, y + 50, 980
    y1 = y0 + 410
    c.rect(x0, y0, x1, y1, width=4, fill=PANEL)
    c.label((x0 + x1) / 2, y0 + 52, "BANCO DE QUESTÕES", size=27)
    c.line(x0 + 28, y0 + 92, x1 - 28, y0 + 92)
    for i, lab in enumerate(filtros):
        yy = y0 + 118 + i * 72
        c.rect(x0 + 34, yy, x1 - 34, yy + 54, width=2, fill=GREEN)
        c.label((x0 + x1) / 2, yy + 27, lab, size=25)
    for i in range(2):
        yy = y0 + 276 + i * 54
        c.rect(x0 + 34, yy, x1 - 34, yy + 38, width=2)
    img = c.compose(img)
    img, _ = text(img, ["Fica ligado no meu perfil que teremos a **maior Black Friday de mentorias do Brasil.**"],
                  BODY, X, y1 + 65, MAXW, LH, GAP)
    return img


# ------------------------------------------------------------------ HUMANAS
def h_hist():
    img = paper(204)
    img, y = text(img, ["**História:** 14 questões por prova.", "Eu seguiria a linha do tempo do Brasil:"],
                  BODY, X, 150, MAXW, LH, GAP)
    c = Canvas()
    yl = y + 190
    timeline(c, yl, [("COLÔNIA", "19%", "Economia colonial|e invasões|holandesas (6%)"),
                     ("IMPÉRIO", "16%", "Segundo|Reinado (12%)"),
                     ("REPÚBLICA", "27%", "República|Oligárquica (11%)|Era Vargas (5%)")], [205, 540, 875])
    img = c.compose(img)
    img, _ = text(img, ["Se só der tempo pra dois: **Segundo Reinado e República Oligárquica.**"],
                  BODY, X, yl + 345, MAXW, LH, GAP)
    return img


def h_filo():
    img = paper(206)
    img, y = text(img, ["**Filosofia:** 7 questões por prova.",
                        "O que mais cai: filosofia política (18%) e ética e moral (15%).",
                        "Por período, com os autores que mais aparecem:"], BODY, X, 120, MAXW, LH, GAP)
    c = Canvas()
    timeline(c, y + 190, [("ANTIGA", "22%", "Aristóteles|(9%)"),
                          ("MODERNA", "20%", "Bacon, Locke|e Hume (7%)"),
                          ("CONTEMPORÂNEA", "32%", "Foucault (8%)|Deleuze e|Derrida (6%)")], [205, 530, 860])
    return c.compose(img)


def humanas():
    return [
        cover("Humanas", ["GEOGRAFIA", "HISTÓRIA", "SOCIOLOGIA", "FILOSOFIA"], 201),
        intro(210, "42 acertos em humanas."),
        materia(202, "**Geografia:** 15 questões por prova.",
                [("13%", "Agropecuária|brasileira"), ("12%", "Problemas ambientais|do Brasil"), ("8%", "Problemas|urbanos"),
                 ("8%", "Sistemas|agrários"), ("7%", "Urbanização|brasileira"), ("6%", "Norte|e Amazônia")],
                "Os grandes temas: questões ambientais (22%) e agropecuária (21%)."),
        h_hist(),
        materia(205, "**Sociologia:** 9 questões por prova.",
                [("27%", "Cultura|e etnia"), ("15%", "Estado, democracia|e cidadania"), ("13%", "Movimentos|sociais"),
                 ("12%", "Globalização"), ("12%", "Questão|de gênero"), ("8%", "Estratificação|social")],
                "Eu começaria por cultura e etnia."),
        h_filo(),
        checklist(207, [("Cultura e etnia", 2), ("Agropecuária brasileira", 2), ("Problemas ambientais do Brasil", 2),
                        ("Segundo Reinado", 2), ("República Oligárquica", 2), ("Estado, democracia e cidadania", 1),
                        ("Filosofia política", 1), ("Problemas urbanos", 1), ("Sistemas agrários", 1),
                        ("Movimentos sociais", 1), ("Urbanização brasileira", 1), ("Ética e moral", 1)]),
        cta(208, ["HUMANAS", "HISTÓRIA"]),
    ]


# ---------------------------------------------------------------- LINGUAGENS
def l_lit():
    img = paper(304)
    img, y = text(img, ["**Literatura:** Modernismo e contemporânea caem 3x mais do que tudo do Realismo pra trás."],
                  BODY, X, 220, MAXW, LH, GAP)
    c = Canvas()
    timeline(c, y + 200, [("ATÉ O REALISMO", "6%", "≈ 2 questões|por prova"),
                          ("MODERNISMO E CONTEMPORÂNEA", "18%", "≈ 6 questões|por prova")], [260, 760])
    img = c.compose(img)
    img, _ = text(img, ["Na semana final, eu começaria pelo Modernismo."], BODY, X, y + 520, MAXW, LH, GAP)
    return img


def l_lingua():
    img = paper(306)
    img, y = text(img, ["**Inglês ou espanhol:** 5 questões por prova.",
                        "Inglês é quase só leitura de texto (100%). Em espanhol, a leitura é 79%, e vocabulário no texto, 27%."],
                  BODY, X, 170, MAXW, LH, GAP)
    c = Canvas()
    y0 = y + 95
    for x, (lab, pct) in zip([290, 790], [("INGLÊS", "100%"), ("ESPANHOL", "79%")]):
        c.label(x, y0 - 8, lab, size=30)
        c.circle(x, y0 + 110, 92, fill=PANEL)
        c.label(x, y0 + 110, pct, size=44)
        c.label(x, y0 + 240, "LEITURA", size=28)
    img = c.compose(img)
    img, _ = text(img, ["Gramática isolada praticamente não cai. Eu **não gastaria essa semana decorando regra.**"],
                  BODY, X, y0 + 305, MAXW, LH, GAP)
    return img


def linguagens():
    return [
        cover("Linguagens", ["PORTUGUÊS|E LITERATURA", "ARTES", "INGLÊS OU|ESPANHOL"], 301),
        intro(310, "40 acertos em linguagens."),
        materia(303, "**Português e Literatura:** 33 questões por prova.",
                [("16%", "Textos|jornalísticos"), ("14%", "Variação|linguística"), ("13%", "Tipologia|textual"),
                 ("9%", "Textos técnicos|e científicos"), ("9%", "Tipos de|argumento"), ("9%", "Coerência|e concisão")],
                "Classes de palavras? **Só 2%.**"),
        l_lit(),
        materia(305, "**Artes:** 7 questões por prova.",
                [("28%", "Arte|contemporânea"), ("16%", "Cultura|de massa"), ("14%", "Panorama|da MPB"),
                 ("11%", "Música tradicional|e folclore"), ("8%", "Vanguardas|europeias"), ("8%", "Música popular|nordestina")],
                "Mais da metade é artes visuais (55%), seguida de música (40%)."),
        l_lingua(),
        checklist(307, [("Modernismo e literatura contemporânea", 6), ("Textos jornalísticos", 5),
                        ("Variação linguística", 5), ("Leitura em inglês ou espanhol", "4 a 5"),
                        ("Tipologia textual", 4), ("Textos técnicos e científicos", 3),
                        ("Tipos de argumento", 3), ("Coerência e concisão", 3),
                        ("Literatura até o Realismo", 2), ("Arte contemporânea", 2),
                        ("Cultura de massa", 1), ("Panorama da MPB", 1)]),
        cta(308, ["LINGUAGENS", "PORTUGUÊS"]),
    ]


if __name__ == "__main__":
    for name, fn in [("o-que-mais-cai-humanas", humanas), ("o-que-mais-cai-linguagens", linguagens)]:
        out = os.path.join(WORK, "..", "output", name)
        os.makedirs(out, exist_ok=True)
        for old in glob.glob(os.path.join(out, "slide-*.jpg")):
            os.remove(old)
        for i, s in enumerate(fn(), 1):
            s.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=94)
        print("ok", name)
