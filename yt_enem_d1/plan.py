"""Plano de edição do ENEM DIA 1 (tempos em s na timeline do A-cut, de edit/words_out.txt).
Seg: gráfico na esquerda + rosto no card. b = batidas relativas ao início do gráfico. ovs = camada estilo Dan."""

W, P = "sfx/whoosh.wav", "sfx/pop.wav"


def seg(a, z, g, **props):
    return {"from": a, "to": z, "g": g, "props": props}


def ov(t0, t1, k, **props):
    return {"from": t0, "to": t1, "k": k, **props}


def make(out_t, total):
    segs = [
        seg(6.2, 18.0, "Abertura1", b=[0.2, 7.3, 8.7, 10.45]),
        seg(34.6, 48.6, "Caderno", b=[0.0, 0.4, 8.2, 11.8]),
        seg(69.4, 82.0, "Linha", title="O *domingo* da prova",
            nodes=[["12:00", "portões abrem", 1.85], ["13:00", "portões fecham", 3.0, True], ["13:30", "prova começa", 3.6], ["19:00", "fim", 4.1]]),
        seg(82.2, 95.5, "Tema", b=[0.2, 5.6, 12.2]),
        seg(95.6, 128.8, "Esqueleto", b=[0.2, 5.9, 10.9, 15.4, 21.4, 26.7]),
        seg(131.8, 147.9, "Bloco", on=1, t="Língua *estrangeira*", sub="5 questões de inglês",
            chips=[["não era meu forte", "x", 7.0], ["com a *cabeça fresca*", "ok", 10.3]],
            card={"big": "15 min", "label": "e já acabava", "at": 14.5}),
        seg(148.1, 176.8, "Bloco", on=2, t="*Humanas*: interpretação", sub="a que eu tinha mais facilidade",
            chips=[["textos base + o básico", "ok", 8.3], ["não sabe? *pula*", "go", 18.9], ["volume no começo", "ok", 20.4]],
            card={"n": 40, "label": "questões em 1h15", "at": 27.3}),
        seg(176.9, 192.9, "Insight", b=[0.2, 3.2, 11.2, 13.0]),
        seg(193.0, 213.3, "Rascunho", b=[0.2, 8.8, 9.9, 10.6, 13.6]),
        seg(221.1, 237.5, "Bloco", on=4, t="*Linguagens*", sub="de pouco em pouco",
            chips=[["45 − 5 de inglês = *40*", "ok", 4.2], ["pula as que *travava*", "go", 9.0]],
            card={"n": 35, "label": "questões em 1h15", "at": 15.0}),
        seg(237.6, 250.8, "Bloco", on=5, t="Passar a *limpo*", sub="com ~4h de prova",
            chips=[["proposta direto no definitivo", "ok", 5.7], ["escrever *superdevagar*", "ok", 9.9]],
            card={"big": "30 min", "label": "só pra copiar", "at": 7.5}),
        seg(250.9, 268.9, "Bloco", on=6, t="*Garimpar* acertos", sub="as que ficaram pra trás",
            chips=[["5 de humanas", "go", 4.5], ["5 de linguagens", "go", 5.4], ["exigem *raciocínio*", "ok", 9.6], ["ir e voltar, reler", "ok", 13.8]],
            card={"big": "30 min", "label": "1ª metade da última hora", "at": 0.6}),
        seg(269.1, 290.8, "Gabarito1", b=[0.2, 14.6, 4.6]),
        seg(290.9, 331.8, "Revisao", b=[0.0, 8.7, 22.8, 26.8, 29.9, 36.9, 40.0]),
        seg(331.9, 353.5, "Lista", title="*Resumo*", items=[
            ["Antes", "reler os repertórios", 1.6], ["Tema + esqueleto", "15 min", 4.6], ["Inglês", "15 min", 7.0],
            ["Humanas", "1h15", 7.7], ["Rascunho", "1h", 8.5], ["Linguagens", "1h15", 9.8], ["Definitivo", "30 min", 10.8],
            ["Garimpo", "30 min", 12.6], ["Gabarito + revisão", "15 + 15 min", 16.5]]),
        seg(356.3, 363.7, "Final1", t="Tire a *ansiedade* no começo", sub="e deixe humanas te dar repertório", date="08/11 · BOA PROVA",
            b=[0.5, 4.8, 6.0]),
    ]
    ovs = [
        ov(0.0, 3.9, "Big", lines=[{"t": "O DIA 1 TEM", "at": 0.15, "size": 130}, {"t": "A REDAÇÃO", "at": 2.95, "size": 210, "c": "g"}]),
        ov(3.9, 6.2, "Quote", t="e é ela que deixa todo mundo *nervoso*", step=0.13),
        ov(19.9, 21.0, "Photo", src="enem1/fotos/ucb.jpg", title="1º lugar em Medicina"),
        ov(21.0, 22.4, "Photo", src="enem1/fotos/pintado.jpg", title="1º lugar em Medicina", sub="duas vezes"),
        # "oitava melhor faculdade do pais": print do RUF 2025 com UnB e 8º grifados
        ov(22.4, 25.45, "Shot", src="enem1/ruf.png", w=1555, h=985, zoom=[300, 815],
           hl=[[22, 798, 72, 36, 0.6], [538, 806, 46, 36, 1.0]], cap="Ranking Universitário Folha (RUF) 2025"),
        ov(48.7, 62.7, "Pills", items=[{"t": "usados nas minhas *redações*", "at": 3.1}, {"t": "já *treinados*", "at": 7.8}, {"t": "funcionavam nos *temas*", "at": 12.0}]),
        ov(63.0, 69.3, "Quote", t="1 hora antes: *relia todos*", step=0.2),
        ov(213.4, 217.8, "Quote", t="é aqui que a redação é *feita de fato*", step=0.14),
        ov(372.5, 376.0, "Quote", t="vai correr atrás dos seus *sonhos*", step=0.14),
        ov(376.0, 379.9, "Photo", src="enem1/fotos/selfie-estudo.jpg", title="o que minha mãe me dizia", sub="todo dia, no ano do vestibular"),
    ]
    zooms = [
        {"from": 128.9, "to": 131.7, "s": 1.15},
        {"from": 217.9, "to": 221.0, "s": 1.12},
        {"from": 353.6, "to": 356.2, "s": 1.15},
        {"from": 363.8, "to": 366.9, "s": 1.12},
    ]
    sfx = [{"t": s["from"], "f": W, "v": 0.32} for s in segs]
    sfx += [{"t": o["from"], "f": W, "v": 0.22} for o in ovs if o["k"] in ("Big", "Photo")]
    sfx += [{"t": o["from"] + it["at"], "f": P, "v": 0.22} for o in ovs if o["k"] == "Pills" for it in o["items"]]
    sfx += [{"t": 269.1 + 14.6 + (i * 1.4 if i < 2 else 2.8 + (i - 2) * 0.45), "f": "sfx/tick.wav", "v": 0.25} for i in range(8)]
    return {
        "video": "enem1/acut.mp4",
        "duration": total,
        "segs": segs,
        "lowers": [{"from": 25.5, "to": 29.3, "name": "Matteo", "role": "@matteo.rocha_"},
                   {"from": 367.0, "to": 371.0, "name": "Matteo", "role": "Medicina + educação"}],
        "zooms": zooms,
        "sfx": sfx,
        "music": {"f": "enem/music.mp3", "v": 0.045},
        "ovs": ovs,
    }
