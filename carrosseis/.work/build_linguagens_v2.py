#!/usr/bin/env python3
# "Como eu saí de 35 pra 40 em Linguagens" v2. Copy baseada no relato do Matteo de 04/11/2026
# (aulas do Felipe Pereira + listas por competência). CTA: comenta BANCO.
import math
import os
from render_livro2 import W, WORK, F, S, GREEN, INK, paper, text, Canvas
from build_revisao_v2 import X, MAXW, BODY, LH, GAP
from build_mais_cai_areas import PANEL

RED = (196, 44, 44)
OUT = os.path.join(WORK, "..", "output", "linguagens-semana-final-v2")


def strike(c, x0, y0, x1, y1, w=6):
    c.d.line([x0 * 3, y0 * 3, x1 * 3, y1 * 3], fill=RED + (255,), width=w * 3)


def node(c, x, y, rx, ry, lines, fill=None, size=28):
    c.ellipse(x, y, rx, ry, fill=fill)
    n = len(lines)
    for i, ln in enumerate(lines):
        c.label(x, y + (i - (n - 1) / 2) * (size + 8), ln, size=size)


def s1():
    img = paper(401)
    img, y = text(img, ["Como eu saí de 35 pra 40"], F(78, "it"), 50, 290, W - 100, 100, 0, align="center")
    img, y = text(img, ["**em Linguagens no ENEM:**"], F(78), 50, y, W - 100, 100, 0, align="center")
    img, y = text(img, ["(Com aula grátis no YouTube, na reta final)"], F(46), 70, y + 24, W - 140, 58, 0, align="center")
    c = Canvas()
    yy = y + 270
    c.label(285, yy - 180, "SIMULADOS", size=30)
    c.circle(285, yy, 135)
    c.label(285, yy, "30-35", size=58)
    c.arrow(450, yy, 630, yy, head=30, width=5)
    c.label(795, yy - 180, "DIA OFICIAL", size=30)
    c.circle(795, yy, 135, fill=GREEN)
    c.label(795, yy, "40", size=74)
    return c.compose(img)


def s2():
    img = paper(402)
    img, y = text(img, ["Eu era ruim em Linguagens. Nos simulados, fazia 30, 35 acertos.",
                        "No dia oficial, **fiz 40.**",
                        "E o método não tinha nada de complexo. Eram só duas coisas:"],
                  BODY, X, 190, MAXW, LH, GAP)
    c = Canvas()
    yy = y + 190
    node(c, 255, yy, 170, 100, ["AULAS DO", "FELIPE PEREIRA"], size=27)
    c.label(W / 2, yy, "+", size=70)
    node(c, 825, yy, 170, 100, ["QUESTÕES POR", "COMPETÊNCIA"], size=27)
    return c.compose(img)


def s3():
    img = paper(403)
    img, y = text(img, ["Não era sobre estudar gramática. E também não era “só interpretação”.",
                        "O Felipe Pereira ensina outra visão: estudar pelas **competências e habilidades** com que a prova é feita."],
                  BODY, X, 130, MAXW, LH, GAP)
    c = Canvas()
    y1 = y + 120
    for x, lab in [(285, "GRAMÁTICA"), (795, "SÓ INTERPRETAÇÃO")]:
        node(c, x, y1, 190, 64, [lab], size=27)
        strike(c, x - 190, y1 + 44, x + 190, y1 - 44)
    y2 = y1 + 260
    c.arrow(285, y1 + 76, 445, y2 - 74)
    c.arrow(795, y1 + 76, 635, y2 - 74)
    node(c, W / 2, y2, 290, 72, ["COMPETÊNCIAS", "E HABILIDADES"], fill=GREEN, size=29)
    return c.compose(img)


def s4():
    img = paper(404)
    img, y = text(img, ["Toda prova sai da mesma matriz de referência.",
                        "Cada questão cobra **uma habilidade.** E várias habilidades formam **uma competência.**"],
                  BODY, X, 95, MAXW, LH, GAP)
    c = Canvas()
    ym = y + 90
    node(c, W / 2, ym, 270, 54, ["MATRIZ DE REFERÊNCIA"], size=28)
    yc = ym + 150
    c.arrow(W / 2, ym + 60, W / 2, yc - 62)
    node(c, W / 2, yc, 215, 54, ["COMPETÊNCIA 8"], fill=GREEN, size=28)
    yh = yc + 165
    yq = yh + 150
    xs = [230, 540, 850]
    for x, h in zip(xs, ["H25", "H26", "H27"]):
        c.arrow(W / 2 + (x - W / 2) * 0.42, yc + 54, x, yh - 62)
        c.circle(x, yh, 54)
        c.label(x, yh, h, size=31)
        c.arrow(x, yh + 60, x, yq - 44)
        c.rect(x - 95, yq - 36, x + 95, yq + 36)
        c.label(x, yq, "QUESTÃO", size=26)
    img = c.compose(img)
    img, _ = text(img, ["São só 30 habilidades em 9 competências. Por isso, a prova repete padrões. E padrão dá pra treinar."], BODY, X, yq + 66, MAXW, LH, GAP)
    return img


def s5():
    img = paper(405)
    img, y = text(img, ["As competências e habilidades têm palavras-chave. E elas aparecem nas alternativas.",
                        "Identificou o que a questão cobra? Fica bem mais fácil **anular as alternativas erradas.**"],
                  BODY, X, 120, MAXW, LH, GAP)
    c = Canvas()
    yy = y + 105
    node(c, 270, yy, 195, 62, ["HABILIDADE"], size=28)
    c.arrow(475, yy, 590, yy)
    node(c, 800, yy, 195, 62, ["PALAVRA-CHAVE"], size=28)
    ya = yy + 185
    c.arrow(800, yy + 70, 800, ya - 66)
    xs = [W * (2 * i + 1) / 10 for i in range(5)]
    for i, (x, l) in enumerate(zip(xs, "ABCDE")):
        right = i == 3
        c.circle(x, ya, 56, fill=GREEN if right else None)
        c.label(x, ya, l, size=36)
        if not right:
            strike(c, x - 48, ya + 48, x + 48, ya - 48, w=5)
    img = c.compose(img)
    img, _ = text(img, ["Em algumas questões, dá pra marcar **sem nem ler o texto.**"], BODY, X, ya + 100, MAXW, LH, GAP)
    return img


def s6():
    img = paper(406)
    img, y = text(img, ["Um exemplo: a **habilidade 25** da matriz diz isso:"], BODY, X, 300, MAXW, LH, 0)
    y += 55
    y0 = y
    img, y = text(img, ["“Identificar, em textos de diferentes gêneros, as **marcas linguísticas** que singularizam as variedades linguísticas sociais, regionais e de registro.”"],
                  F(48, "it"), X + 40, y0 + 40, MAXW - 80, 62, 0)
    c = Canvas()
    c.rect(X, y0, W - X, y + 30)
    img = c.compose(img)
    img, _ = text(img, ["Agora olha uma questão do ENEM que cobra essa habilidade:"], BODY, X, y + 90, MAXW, LH, GAP)
    return img


def s6b():
    img = paper(410)
    img, y = text(img, ["ENEM 2018, 1º dia, sobre uma campanha do Ministério da Saúde:"], F(40, "it"), X, 95, MAXW, 50, 0)
    img, y = text(img, ["“A utilização de determinadas variedades linguísticas em campanhas educativas [...] No caso desse texto, identifica-se essa estratégia pelo(a)”"],
                  F(44), X, y + 30, MAXW, 56, 0)
    alts = [("A", "discurso formal da língua portuguesa."), ("B", "registro padrão próprio da língua escrita."),
            ("C", "seleção lexical restrita à esfera da medicina."), ("D", "fidelidade ao jargão da linguagem publicitária."),
            ("E", "uso de **marcas linguísticas** típicas da oralidade.")]
    y += 45
    c = Canvas()
    for i, (l, _) in enumerate(alts):
        yy = y + i * 105
        c.circle(X + 34, yy + 26, 34, fill=GREEN if l == "E" else None)
        c.label(X + 34, yy + 26, l, size=28)
    img = c.compose(img)
    for i, (_, t) in enumerate(alts):
        img, _y = text(img, [t], F(40), X + 92, y + i * 105 + (0 if len(t) > 41 else 2), MAXW - 92, 48, 0)
    y += len(alts) * 105 + 30
    img, _ = text(img, ["A habilidade fala em marcas linguísticas. **A resposta certa também.**",
                        "E só 34% acertaram."], BODY, X, y, MAXW, LH, 22)
    return img


def s7():
    img = paper(407)
    img, y = text(img, ["**O método, passo 1:** muita videoaula do Felipe Pereira.",
                        "É tudo de graça no YouTube. Ele resolve questões do ENEM e mostra como identificar a habilidade que cada uma cobra.",
                        "Foi assim que eu passei a enxergar os padrões da prova."],
                  BODY, X, 120, MAXW, LH, GAP)
    c = Canvas()
    yy = y + 170
    c.rect(95, yy - 105, 395, yy + 105, fill=PANEL)
    c.d.polygon([(205 * 3, (yy - 45) * 3), (205 * 3, (yy + 45) * 3), (285 * 3, yy * 3)], fill=INK + (255,))
    c.arrow(420, yy, 560, yy)
    node(c, 790, yy, 215, 90, ["QUAL HABILIDADE", "ELA COBRA?"], fill=GREEN, size=27)
    return c.compose(img)


def s8():
    img = paper(408)
    img, y = text(img, ["**O método, passo 2:** muitas, mas muitas questões.",
                        "Eu faria listas de questões do ENEM divididas por competência e habilidade.",
                        "Assim, você vê como cada uma é cobrada e o que as questões da mesma habilidade têm em comum."],
                  BODY, X, 120, MAXW, LH, GAP)
    c = Canvas()
    y0 = y + 90
    xs = [190, 430, 670, 910]
    for k, x in enumerate(xs):
        c.label(x, y0, f"COMP. {k + 1}", size=28)
        for j in range(4):
            c.rect(x - 80, y0 + 45 + j * 58, x + 80, y0 + 45 + j * 58 + 44, fill=GREEN if k == 0 else None)
    return c.compose(img)


def curva(c, p0, p1, p2, p3, w=6, head=36):
    """Seta redonda: curva de Bézier com pontas arredondadas."""
    pts = []
    for i in range(121):
        t = i / 120
        u = 1 - t
        pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    for x, y in pts:
        c.d.ellipse([(x - w / 2) * 3, (y - w / 2) * 3, (x + w / 2) * 3, (y + w / 2) * 3], fill=INK + (255,))
    a = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
    for da in (2.5, -2.5):
        for k in range(41):
            r = head * k / 40
            x, y = p3[0] + r * math.cos(a + da), p3[1] + r * math.sin(a + da)
            c.d.ellipse([(x - w / 2) * 3, (y - w / 2) * 3, (x + w / 2) * 3, (y + w / 2) * 3], fill=INK + (255,))


def s9():
    img = paper(409)
    img, y = text(img, ["Comenta **“BANCO”**"], F(76), X, 110, MAXW, 92, 0)
    img, y = text(img, ["e eu te mando a minha plataforma: um banco de questões que você filtra por competência e habilidade do ENEM."],
                  BODY, X, y + 25, MAXW, LH, GAP)
    c = Canvas()
    curva(c, (190, y + 35), (195, y + 215), (360, y + 290), (570, y + 245))
    x0, y0, x1 = 600, y + 50, 980
    y1 = y0 + 410
    c.rect(x0, y0, x1, y1, width=4, fill=PANEL)
    c.label((x0 + x1) / 2, y0 + 52, "BANCO DE QUESTÕES", size=27)
    c.line(x0 + 28, y0 + 92, x1 - 28, y0 + 92)
    for i, lab in enumerate(["COMPETÊNCIA 8", "HABILIDADE 25"]):
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


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate([s1, s2, s3, s4, s5, s6, s6b, s7, s8, s9], 1):
        fn().save(os.path.join(OUT, f"slide-{i:02d}.jpg"), quality=94)
    print("ok", os.path.abspath(OUT))
