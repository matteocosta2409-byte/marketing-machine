"""Plano de edição sincronizado à fala (tempos em segundos na timeline do A-cut, tirados de edit/words_out.txt).
Seg: gráfico na esquerda + rosto no card. b = batidas relativas ao início do gráfico."""

W, P = "sfx/whoosh.wav", "sfx/pop.wav"


def seg(a, z, g, **props):
    return {"from": a, "to": z, "g": g, "props": props}


def ov(t0, t1, k, **props):
    return {"from": t0, "to": t1, "k": k, **props}


def make(out_t, total):
    segs = [
        seg(10.9, 20.9, "Abertura", b=[0.3, 4.6]),
        seg(42.4, 62.0, "Aquecimento", b=[0.0, 5.8]),
        seg(62.2, 75.9, "DiaTimeline", b=[0.3, 2.55, 3.2, 3.9, 4.5]),
        seg(79.5, 97.2, "Folhear", b=[0.2, 5.4, 6.3, 7.4, 8.2]),
        seg(105.27, 141.4, "TRI", b=[0.0, 8.6, 12.2, 21.2, 25.7, 6.8]),
        seg(141.9, 159.6, "Alunos", b=[3.7, 6.4, 13.5]),
        seg(159.72, 166.0, "Regra", t="Não deixe escapar *nenhuma fácil*", sub="nem média: elas são a base da sua nota", b=[2.0]),
        seg(169.36, 207.1, "Hora1", b=[7.5, 9.3, 11.2, 17.3, 15.7, 27.1, 3.4, 5.3]),
        seg(222.2, 240.9, "Hora2", b=[1.0, 5.3, 6.5, 7.5, 16.1]),
        seg(240.96, 250.9, "Hora34", b=[99]),
        seg(268.48, 282.6, "Hora34", b=[7.9]),
        seg(282.9, 303.5, "Garimpo", b=[7.6, 1.8, 3.2, 14.3, 17.9, 11.1]),
        seg(303.63, 327.9, "Gabarito", b=[0.2, 16.0]),
        seg(328.9, 350.3, "Resumo", b=[0.6, 5.7, 7.8, 11.6, 16.25, 18.8]),
        seg(360.7, 365.8, "Final", b=[0.3, 2.1]),
    ]
    zooms = [
        {"from": 9.1, "to": 10.9, "s": 1.15},
        {"from": 29.0, "to": 31.2, "s": 1.12},
        {"from": 97.3, "to": 99.5, "s": 1.15},
        {"from": 166.0, "to": 169.3, "s": 1.12},
        {"from": 216.2, "to": 221.1, "s": 1.12},
        {"from": 262.2, "to": 268.4, "s": 1.12},
        {"from": 356.5, "to": 360.2, "s": 1.12},
    ]
    # v2 (estilo Dan): fotos de arquivo, texto kinetic, reframe riscado, pilulas. Tempos em s do A-cut.
    ovs = [
        ov(0.0, 2.40, "Big", lines=[{"t": "5 HORAS", "at": 0.35}, {"t": "90 QUESTÕES", "at": 1.45, "size": 150, "c": "g"}]),
        ov(2.40, 4.45, "Quote", t="quase todo mundo erra no *mesmo lugar*", step=0.13),
        ov(4.45, 9.10, "Race", end=3.9),
        ov(9.10, 10.90, "Strike", a="uma por uma", b="hora por hora", tb=0.9),
        ov(22.15, 23.42, "Photo", src="enem/fotos/pintado.jpg", title="Medicina · UnB", sub="o dia da aprovação"),
        ov(23.42, 26.15, "Photo", src="enem/fotos/farinha.jpg", title="1º lugar em Medicina", sub="universidade federal"),
        ov(31.2, 42.4, "Pills", items=[{"t": "primeiros *15–20 min*", "at": 1.5, "x": True}, {"t": "lê a questão *2, 3 vezes*", "at": 5.6, "x": True}]),
        ov(77.0, 79.45, "Quote", t="a primeira coisa *não* era resolver nada", step=0.2),
        ov(97.3, 99.5, "Quote", t="a prova para de ser um *mistério*", step=0.15),
        ov(103.5, 105.27, "Big", lines=[{"t": "NOTA NÃO É", "at": 0.07, "size": 150}, {"t": "Nº DE ACERTOS", "at": 0.8, "size": 150, "c": "g"}]),
        ov(210.9, 213.0, "Photo", src="enem/fotos/matematica.jpg", title="Matemática", sub="era minha facilidade"),
        ov(213.0, 222.1, "Pills", items=[{"t": "a que mais *consome tempo*", "at": 0.9, "x": True}, {"t": "fácil ≠ *rápida*", "at": 7.6, "x": True}]),
        ov(250.9, 262.1, "Pills", items=[{"t": "3+ min por questão: *ok*", "at": 0.4}, {"t": "volta na *física*", "at": 5.1}, {"t": "depois de *60 questões*", "at": 9.4}]),
        ov(263.9, 268.4, "Quote", t="você enxerga o que *não tinha visto*", step=0.14),
        ov(353.6, 356.4, "Quote", t="a *lógica* vale pra qualquer pessoa", step=0.14),
    ]
    sfx = [{"t": s["from"], "f": W, "v": 0.32} for s in segs]
    sfx += [{"t": o["from"], "f": W, "v": 0.22} for o in ovs if o["k"] in ("Big", "Race", "Photo")]
    sfx += [{"t": o["from"] + it["at"], "f": P, "v": 0.22} for o in ovs if o["k"] == "Pills" for it in o["items"]]
    sfx += [{"t": 141.9 + 13.5, "f": P, "v": 0.35}, {"t": 159.72 + 0.2, "f": P, "v": 0.35},
            {"t": 169.36 + 27.1, "f": P, "v": 0.3}, {"t": 222.2 + 16.1, "f": P, "v": 0.3}]
    sfx += [{"t": 282.9 + 14.3 + i * 0.42, "f": P, "v": 0.3} for i in (1, 3, 4, 6)]  # acertos do garimpo
    sfx += [{"t": 303.63 + 16.0 + i * 0.55, "f": "sfx/tick.wav", "v": 0.25} for i in range(8)]
    return {
        "video": "enem/acut.mp4",
        "duration": total,
        "segs": segs,
        "lowers": [{"from": 26.2, "to": 29.6, "name": "Matteo", "role": "@matteo.rocha_"},
                   {"from": 366.0, "to": 371.0, "name": "Matteo", "role": "Medicina + educação"}],
        "zooms": zooms,
        "sfx": sfx,
        "music": {"f": "enem/music.mp3", "v": 0.045},
        "ovs": ovs,
    }
