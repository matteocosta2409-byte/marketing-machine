"""Plano de edição "Semana do ENEM dia 2" (tempos em s na timeline do A-cut, de edit/words_out.txt).
Seg: gráfico na esquerda + rosto no card. b = batidas relativas ao início do gráfico. ovs = camada estilo Dan."""

W, P = "sfx/whoosh.wav", "sfx/pop.wav"
D = ["prova à tarde", "ordem de prova", "correção à noite", "questões de manhã", "revisão + flashcards", "sábado e domingo"]


def seg(t0, t1, g, **props):
    return {"from": t0, "to": t1, "g": g, "props": props}


def ov(t0, t1, k, **props):
    return {"from": t0, "to": t1, "k": k, **props}


def make(out_t, total):
    cells = [[d, 1, "prova antiga · 5h", 1.0 + d * 0.15] for d in range(5)]
    cells += [[d, 0, "questões + revisão", 7.0 + d * 0.15] for d in range(5)]
    cells += [[d, 2, "correção", 13.8 + d * 0.15] for d in range(5)]
    cells += [[d, 0, "flashcards", 19.7 + d * 0.1, False, True] for d in range(5)]  # a mais: 1/4 de baixo da manha
    cells += [[5, r, "descanso", 24.4] for r in range(3)] + [[6, 1, "ENEM", 27.0, True]]
    segs = [
        seg(12.7, 18.6, "AberturaS", t="A semana do *dia 2*", items=["*Natureza*", "*Matemática*", "treino de *tempo*"], b=[1.2, 2.2, 3.2]),
        seg(25.2, 33.5, "Notas", t="*82 acertos* no dia 2", itens=[[40, "/45", "Natureza", 5.4], [42, "/45", "Matemática", 6.6]]),
        seg(50.1, 65.5, "Maratona", dicas=D, t="Um *Enem por dia*", nota="5 horas cronometradas, como no domingo", b=[2.5, 12.9, 7.9]),
        seg(65.6, 102.0, "Provas", dicas=D, b=[1.1, 23.3],
            chips=[["o próprio Enem, feito pelo *Inep*", "ok", 8.2], ["vale até as mais antigas e o *PPL*", "ok", 15.0]]),
        seg(102.1, 117.3, "Dica", on=0, dicas=D, t="Um *ensaio* do dia oficial",
            chips=[["sem celular", "ok", 9.1], ["sem calculadora", "ok", 9.9], ["cartão-resposta impresso", "ok", 11.5]],
            card={"big": "13:30", "label": "o horário de verdade", "at": 5.8}),
        seg(117.4, 136.8, "Aquecimento", b=[0.0, 3.0]),
        seg(136.9, 146.8, "Dica", on=1, dicas=D, t="Treine sua *ordem de prova*",
            chips=[["o vídeo completo tá no *card aqui em cima*", "ok", 5.2]]),
        seg(146.9, 155.6, "Alunos", b=[1.0, 3.2, 5.6]),
        seg(155.7, 159.1, "Regra", t="Garantir *fáceis e médias* primeiro", b=[9]),
        seg(159.2, 191.3, "Lista", title="Minha *ordem de prova*", items=[
            ["1ª hora", "natureza teórica", 0.2], ["Depois", "matemática rápida e fácil", 7.9], ["~3h30", "as que ficaram, pulando", 16.5],
            ["Última hora", "garimpar acertos", 22.4], ["15 min finais", "gabarito com calma", 28.5]]),
        seg(206.3, 255.9, "Dica", on=2, dicas=D, t="Corrigir à *noite*", sub="por que você errou?",
            chips=[["não sabia: *lista de revisão*", "go", 14.9], ["falta de atenção: *anota*", "go", 19.3], ["faltou tempo: *ordem e ritmo*", "go", 27.6]],
            card={"big": "TEMPO", "label": "quantas questões em 1h e em 3h30?", "at": 39.6}),
        seg(256.0, 281.0, "Dica", on=3, dicas=D, t="De manhã: *questões*", sub="natureza + matemática misturadas",
            chips=[["*altíssimo* volume", "ok", 2.3], ["todos os modelos de questão", "ok", 8.4], ["revisão direcionada nos erros", "ok", 15.2]]),
        seg(281.1, 295.8, "Dica", on=3, dicas=D, t="Por que *misturadas*?",
            chips=[["a prova não avisa o assunto", "ok", 2.1], ["genética ao lado de eletrodinâmica", "go", 4.3], ["treina *reconhecer* o que ela pede", "ok", 11.0]]),
        seg(295.9, 318.9, "Cai", on=3, dicas=D, cols=[
            ["MATEMÁTICA", [["porcentagem", 2.5], ["razão e proporção", 3.3], ["estatística", 4.2], ["leitura de gráfico", 5.1], ["geometria", 6.3]]],
            ["NATUREZA", [["ecologia", 8.1], ["fisiologia humana", 8.8], ["genética", 9.9], ["química ambiental", 10.9], ["eletricidade", 12.2]]]]),
        seg(324.9, 343.5, "Dica", on=4, dicas=D, t="Revisão *passiva*", sub="pra não ficar exausto",
            chips=[["videoaula do assunto", "ok", 3.9], ["relida no material", "ok", 5.5], ["matéria nova", "x", 7.8], ["energia pra prova da tarde", "ok", 13.0]]),
        seg(358.9, 378.8, "Provas", on=4, dicas=D, title="Não é pra *qualquer pessoa*", b=[1.9, 13.9],
            a={"tag": "INICIANTE", "t": "SÓ AS PROVAS DE MATEMÁTICA", "s": "sobe a média com menos esforço"},
            c={"tag": "ESTUDOU O ANO TODO", "t": "ESTRATÉGIA COMPLETA", "s": "e tá indo bem nos simulados"}),
        seg(378.9, 404.0, "Dica", on=5, dicas=D, t="Sábado: *descanso*", sub="nada de prova, deixa tudo pronto",
            chips=[["documento com foto", "ok", 6.1], ["caneta + cartão de confirmação", "ok", 7.2], ["água e algo pra comer", "ok", 10.5], ["confere o caminho", "ok", 13.8], ["*dorme cedo*", "ok", 19.4]]),
        seg(404.1, 416.6, "Dica", on=5, dicas=D, t="Domingo: *só repetir*",
            chips=[["5 fáceis de matemática de manhã", "ok", 2.2], ["chegar por volta do meio-dia", "ok", 5.5], ["a ordem que já fez *5 vezes*", "ok", 8.1]]),
        seg(416.7, 444.3, "Semana", cells=cells),
    ]
    ovs = [
        ov(0.0, 3.2, "Big", lines=[{"t": "FALTA 1 SEMANA", "at": 0.1, "size": 170}, {"t": "PRO DIA 2", "at": 1.5, "size": 150, "c": "g"}]),
        ov(3.2, 5.8, "Quote", t="a prova mais *temida* do Brasil", step=0.14),
        ov(5.8, 12.6, "Pills", items=[{"t": "base do vídeo do *dia 1*", "at": 1.5}, {"t": "com alguns *ajustes*", "at": 5.2}]),
        ov(20.2, 21.3, "Photo", src="enem1/fotos/ucb.jpg", title="1º lugar em Medicina"),
        ov(21.3, 23.0, "Photo", src="enem1/fotos/pintado.jpg", title="1º lugar em Medicina", sub="duas vezes"),
        ov(33.6, 41.6, "Pills", items=[{"t": "treinar *redação*", "at": 2.4, "x": True}, {"t": "*caderninho* de repertórios", "at": 3.7, "x": True}, {"t": "reler *redações*", "at": 6.0, "x": True}]),
        ov(41.6, 44.7, "Quote", t="outra dificuldade, *muito maior*", step=0.18),
        ov(44.7, 45.8, "Big", lines=[{"t": "O TEMPO", "at": 0.1, "size": 240, "c": "g"}]),
        ov(45.8, 50.1, "Quote", t="consomem tempo até nas *questões fáceis*", step=0.14),
        ov(191.3, 194.4, "Pills", items=[{"t": "vídeo da *estratégia* aqui em cima", "at": 0.1}]),
        ov(196.5, 200.7, "Quote", t="no domingo, *nada pela primeira vez*", step=0.16),
        ov(319.0, 324.8, "Pills", items=[{"t": "banco com *todas as provas*", "at": 2.5}, {"t": "link na *descrição*", "at": 0.3}]),
        ov(343.6, 350.6, "Pills", items=[{"t": "flashcards *todo dia*", "at": 0.4}, {"t": "matéria *fresca*", "at": 3.0}]),
        ov(354.9, 358.8, "Quote", t="“a pessoa não vai ficar *cansada*?”", step=0.15),
        ov(444.4, 450.4, "Pills", items=[{"t": "lista do que *mais cai*", "at": 0.5}, {"t": "banco de *questões*", "at": 3.0}]),
        ov(452.7, 456.2, "Quote", t="boa prova dia *15*", step=0.2),
        ov(456.2, 457.7, "Quote", t="vai correr atrás dos seus *sonhos*", step=0.08),
        ov(457.7, total, "Photo", src="enem1/fotos/selfie-estudo.jpg", title="o que minha mãe me dizia", sub="todo dia, no ano do vestibular"),
    ]
    zooms = [
        {"from": 200.8, "to": 206.2, "s": 1.12},
        {"from": 350.7, "to": 354.8, "s": 1.12},
        {"from": 450.5, "to": 452.6, "s": 1.15},
    ]
    sfx = [{"t": s["from"], "f": W, "v": 0.32} for s in segs]
    sfx += [{"t": o["from"], "f": W, "v": 0.22} for o in ovs if o["k"] in ("Big", "Photo")]
    sfx += [{"t": o["from"] + it["at"], "f": P, "v": 0.22} for o in ovs if o["k"] == "Pills" for it in o["items"]]
    return {
        "video": "semana2/acut.mp4",
        "duration": total,
        "segs": segs,
        "lowers": [{"from": 22.9, "to": 25.15, "name": "Matteo", "role": "@matteo.rocha_"}],
        "zooms": zooms,
        "sfx": sfx,
        "music": {"f": "enem/music.mp3", "v": 0.045},
        "ovs": ovs,
    }
