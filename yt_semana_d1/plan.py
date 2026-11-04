"""Plano de edição "Semana do ENEM dia 1" (tempos em s na timeline do A-cut, de edit/words_out.txt).
Seg: gráfico na esquerda + rosto no card. b = batidas relativas ao início do gráfico. ovs = camada estilo Dan."""

W, P = "sfx/whoosh.wav", "sfx/pop.wav"


def seg(a, z, g, **props):
    return {"from": a, "to": z, "g": g, "props": props}


def ov(t0, t1, k, **props):
    return {"from": t0, "to": t1, "k": k, **props}


def make(out_t, total):
    T, N, M = "prova antiga + redação", "correção", "repertórios + flashcards"
    cells = [[d, 1, T, 2.0 + d * 0.15] for d in range(5)] + [[d, 2, N, 9.2 + d * 0.15] for d in range(5)]
    cells += [[d, 0, M, 14.0 + d * 0.15, False, True] for d in range(5)]  # 1/4 de baixo da manha, antes da prova
    cells += [[d, 0, "humanas + revisão", 17.0 + i * 0.3] for i, d in enumerate([0, 2, 4])]
    cells += [[d, 0, "Felipe + linguagens", 25.6 + i * 0.3] for i, d in enumerate([1, 3])]
    cells += [[5, r, "descanso", 32.2] for r in range(3)] + [[6, 1, "ENEM", 33.6, True]]
    segs = [
        seg(12.8, 23.2, "AberturaS", b=[5.0, 6.3, 8.9]),
        seg(33.7, 57.5, "Maratona", b=[3.2, 5.5, 7.0]),
        seg(57.6, 73.0, "Provas", b=[1.3, 8.7]),
        seg(73.1, 106.0, "Fiscal", b=[6.8, 10.2, 11.7, 13.2, 16.7, 24.0]),
        seg(106.1, 124.9, "Dica", on=1, t="Corrigir *erro por erro*", sub="à noite, no mesmo dia",
            chips=[["não entendi o conteúdo?", "go", 7.1], ["li errado?", "go", 8.3], ["faltou tempo?", "go", 9.8]],
            card={"big": "AMANHÃ", "label": "vira a revisão do dia seguinte", "at": 11.1}),
        seg(125.0, 145.7, "Caderno", b=[0.0, 0.5, 99, 99], eixos=["Educação", "Meio ambiente", "Saúde", "Defesa das minorias", "Tecnologia", "Cultura"],
            marcas=[["Educação", 14.8], ["Meio ambiente", 15.5], ["Saúde", 16.3], ["Defesa das minorias", 16.9]]),
        seg(158.0, 198.2, "Dica", on=3, t="Releia as *redações boas*", sub="o modelo de texto já tem que estar pronto",
            chips=[["quanto tempo demora", "ok", 13.6], ["ideias no D1 e no D2", "ok", 15.5], ["proposta com *5 elementos*", "ok", 19.2],
                   ["1 redação por dia na maratona", "ok", 25.0], ["só pra quem está *avançado*", "x", 29.6]],
            card={"big": "REDAÇÕES", "label": "as que deram certo no ano", "at": 3.9}),
        seg(203.7, 230.5, "Matriz", b=[4.2, 6.2, 8.5, 16.5, 18.4, 20.3]),
        seg(230.6, 242.9, "Antes", b=[2.5, 11.2]),
        seg(256.0, 279.8, "Dica", on=5, t="Questões *misturadas*", sub="do dia 1, em alto volume",
            chips=[["linguagens, geografia, sociologia, história", "ok", 3.0], ["padrões de cobrança *gravados*", "ok", 7.6],
                   ["questão igual no domingo", "ok", 11.0], ["marca *mais rápido*", "ok", 16.1]]),
        seg(279.9, 301.6, "Dica", on=6, t="Revisão *direcionada*", sub="o que vai aumentar a sua nota",
            chips=[["estudar a mais difícil", "x", 4.1], ["reestudar o que não entendeu", "x", 5.8], ["o que *mais cai* + o que você *erra*", "ok", 11.4]],
            card={"big": "LISTA", "label": "na descrição", "at": 13.8}),
        seg(301.7, 336.4, "Semana", cells=cells),
        seg(336.5, 362.9, "Lista", title="*Resumo*", items=[
            ["1 prova antiga/dia", "no tempo, com redação", 0.7], ["Corrigir à noite", "erro por erro", 3.0],
            ["Repertórios + flashcards", "antes da prova", 4.0], ["Reler redações boas", "o modelo pronto", 7.2],
            ["Felipe Pereira", "linguagens por competência", 10.0], ["Questões do dia 1", "alto volume", 12.7],
            ["Revisão direcionada", "o que cai + o que erra", 14.3], ["Na descrição", "lista + plataforma", 17.9]]),
    ]
    ovs = [
        ov(0.0, 3.0, "Big", lines=[{"t": "FALTA 1 SEMANA", "at": 0.1, "size": 170}, {"t": "PRO DIA 1", "at": 1.4, "size": 150, "c": "g"}]),
        ov(3.0, 12.7, "Pills", items=[{"t": "alguns *acertos a mais*", "at": 2.2}, {"t": "ou *mais cansado*", "at": 5.6, "x": True}]),
        ov(24.5, 25.8, "Photo", src="enem1/fotos/ucb.jpg", title="1º lugar em Medicina"),
        ov(25.8, 27.2, "Photo", src="enem1/fotos/pintado.jpg", title="1º lugar em Medicina", sub="duas vezes"),
        ov(27.2, 29.9, "Quote", t="na prova com a *maior concorrência* do Brasil", step=0.12),
        ov(145.8, 149.3, "Quote", t="já tem? relê *todos os dias*", step=0.15),
        ov(149.4, 158.0, "Pills", items=[{"t": "flashcards do *dia 1*", "at": 2.5}, {"t": "só pra *não acumular*", "at": 6.8}]),
        ov(243.0, 256.0, "Pills", items=[{"t": "listas *por competência*", "at": 0.4}, {"t": "link na *descrição*", "at": 6.3}]),
        ov(371.3, 375.0, "Quote", t="vai correr atrás dos seus *sonhos*", step=0.14),
        ov(375.0, 379.3, "Photo", src="enem1/fotos/selfie-estudo.jpg", title="o que minha mãe me dizia", sub="todo dia, no ano do vestibular"),
    ]
    zooms = [
        {"from": 9.0, "to": 12.7, "s": 1.12},
        {"from": 198.3, "to": 199.3, "s": 1.15},
        {"from": 363.0, "to": 366.0, "s": 1.12},
    ]
    sfx = [{"t": s["from"], "f": W, "v": 0.32} for s in segs]
    sfx += [{"t": o["from"], "f": W, "v": 0.22} for o in ovs if o["k"] in ("Big", "Photo")]
    sfx += [{"t": o["from"] + it["at"], "f": P, "v": 0.22} for o in ovs if o["k"] == "Pills" for it in o["items"]]
    sfx += [{"t": 73.1 + x, "f": "sfx/tick.wav", "v": 0.3} for x in (10.2, 11.7, 13.2)]
    lowers = [{"from": 30.0, "to": 33.6, "name": "Matteo", "role": "@matteo.rocha_"},
                   {"from": 199.3, "to": 203.6, "name": "Felipe Pereira", "role": "professor de linguagens · grátis no YouTube"},
                   {"from": 366.0, "to": 370.5, "name": "Matteo", "role": "Medicina + educação"}]
    # v2: tirei o "com aquele," (src 139.0-140.06); tudo depois do corte adianta
    corte, delta = 104.0, 379.302 - 378.585
    d = lambda x: round(x - delta, 3) if x >= corte else x
    for it in segs + ovs + lowers + zooms:
        it["from"], it["to"] = d(it["from"]), d(it["to"])
    for it in sfx:
        it["t"] = d(it["t"])
    return {
        "video": "semana1/acut.mp4",
        "duration": total,
        "segs": segs,
        "lowers": lowers,
        "zooms": zooms,
        "sfx": sfx,
        "music": {"f": "enem/music.mp3", "v": 0.045},
        "ovs": ovs,
    }
