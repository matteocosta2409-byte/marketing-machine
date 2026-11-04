"""Rascunho da TRI sem gravacao: blocos 4, 8 e 9 do roteiro. Gera props com voz e props mudo.
Tempos vem das palavras da voz de teste (edit/transcripts/voz.json). Quando a gravacao chegar, troca tempos e video."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent
W, POP, TICK = "sfx/whoosh.wav", "sfx/pop.wav", "sfx/tick.wav"
T8, T9, TOTAL = 45.3, 142.2, 187.3

FRASES = [
    (0.0, "Cada questão do Enem tem uma curva em forma de S."), (2.9, "Na horizontal, o nível do aluno."), (5.1, "Na vertical, a chance de ele acertar."),
    (7.7, "Olha essa aqui: questão 91 de natureza de 2025, caderno amarelo."), (13.4, "Física, transferência de calor."),
    (15.6, "Pra quem está abaixo de 500, a curva prevê 41% de acerto."), (20.6, "Os candidatos reais dessa faixa acertaram 44%."),
    (24.9, "De 600 a 649, a curva diz 83%, os reais, 86%."), (32.4, "De 700 a 749, 99 e 99."),
    (37.4, "A teoria e os candidatos reais quase se sobrepõem."), (40.6, "Nem sempre encaixa tão bem assim, e daqui a pouco eu te mostro quando não encaixa."),
    (45.5, "Essa é a parte que quase ninguém explica."), (48.0, "A conta é uma multiplicação, não uma soma."),
    (50.9, "Vou usar três questões reais de natureza de 2024, caderno amarelo: a 93, fácil, a 92, média, e a 127, difícil."), (62.3, "O aluno acertou as duas primeiras e errou a difícil."),
    (65.4, "A conta pergunta, pra cada nota possível: qual a chance de alguém desse nível responder exatamente assim?"),
    (72.0, "Alguém de nota 400 tem 18% de chance de acertar a fácil, 26% de acertar a média e 72% de errar a difícil."), (82.1, "Multiplica tudo: cerca de 3%."),
    (85.1, "Alguém de nota 700: 92%, 74% e 53%."), (92.1, "Multiplica: 36%."),
    (94.8, "Só com as respostas, o nível mais provável é 700."), (98.8, "Depois entra uma informação inicial, que é como os concluintes de 2009 se distribuíam."),
    (104.7, "Com três questões, ela puxa pra perto de 600."), (108.3, "Com a prova inteira, as respostas contam muito mais."),
    (111.8, "E a nota final é a média de todos esses níveis, levando em conta o quanto cada um é plausível."),
    (117.6, "Agora inverte, com as mesmas três."), (120.1, "Errou as duas mais fáceis e acertou a difícil."), (123.1, "Os níveis mais plausíveis caem pra 400 e 500."),
    (127.0, "O acerto na difícil não sustentou uma nota alta, porque errar as fáceis é muito improvável pra um aluno forte."),
    (133.9, "Esse exemplo é cálculo nosso, com os parâmetros oficiais e só seis notas, pra caber na tela."), (139.8, "A conta real percorre a escala toda."),
    (142.4, "Agora com a prova inteira."), (144.1, "Isso aqui é uma simulação: um aluno inventado, de nível 700, respondendo às questões reais de natureza de 2024."),
    (152.7, "Depois da primeira resposta, certa, a estimativa é 582, com margem de 110."), (159.6, "Quase não diz nada."), (161.1, "Na terceira ele erra, e cai pra 556."),
    (165.0, "Na oitava, já está em 681, com margem de 49."), (169.9, "No fim, nas 44 questões válidas, 722, com margem de 26."),
    (176.4, "A cada resposta, a montanha fica mais estreita."), (179.7, "E repara: o aluno era 700 e saiu com 722."), (184.4, "A nota é uma medida, e toda medida tem erro."),
]
LEG = [{"from": a, "to": (FRASES[i + 1][0] if i + 1 < len(FRASES) else TOTAL), "t": t} for i, (a, t) in enumerate(FRASES)]

r8 = lambda t: round(t - T8, 2)
r9 = lambda t: round(t - T9, 2)
FAIXAS = [
    {"rot": "abaixo de 500", "n": 450, "a": 300, "z": 500, "curva": 41, "real": 44, "tb": 16.3, "tc": 18.9, "tr": 23.7},
    {"rot": "600 a 649", "n": 625, "a": 600, "z": 650, "curva": 83, "real": 86, "tb": 24.9, "tc": 28.2, "tr": 30.6},
    {"rot": "700 a 749", "n": 725, "a": 700, "z": 750, "curva": 99, "real": 99, "tb": 32.4, "tc": 35.3, "tr": 36.2},
]
B4 = {"curva": 0.8, "h": 2.9, "v": 5.1, "tag": 8.6, "assunto": 13.4, "final": 37.4, "ressalva": 40.6}
B8 = {
    "titulo": r8(48.0), "q0": r8(56.3), "qd": 1.9, "acertou": r8(62.7), "errou": r8(64.2), "pergunta": r8(65.4),
    "l400": [r8(72.0), r8(74.0), r8(77.0), r8(79.4), r8(83.4)], "l700": [r8(85.1), r8(87.2), r8(88.8), r8(90.3), r8(93.1)],
    "barras": r8(94.8), "info": r8(98.8), "puxa": r8(104.7), "media": r8(111.8), "invMarca": r8(120.1), "invCai": r8(123.1), "sustentou": r8(127.0), "selo": r8(133.9),
}
B9 = {"selo": r9(144.6), "real": r9(147.6), "reparo": r9(179.7), "medida": r9(184.4)}
PASSOS = [(1, "q121", True, 582, 110, 154.7), (2, "q100", True, 609, 99, 159.6), (3, "q95", False, 556, 94, 162.1), (4, "q135", True, 595, 81, 163.8), (5, "q92", True, 621, 79, 164.2),
          (6, "q128", True, 655, 62, 164.6), (7, "q124", True, 670, 53, 165.0), (8, "q96", True, 681, 49, 165.4), (15, "q98", True, 698, 41, 170.1), (30, "q120", True, 721, 30, 171.0), (44, "q106", True, 722, 26, 172.9)]
PASSOS_P = [{"n": n, "q": q, "ok": ok, "m": m, "sd": s, "at": r9(a)} for n, q, ok, m, s, a in PASSOS]

segs = [
    {"from": 0.0, "to": T8, "g": "Curva", "props": {"b": B4, "faixas": FAIXAS, "extras": [[525, 50], [575, 68], [675, 95], [825, 100]]}},
    {"from": T8, "to": T9, "g": "Multiplica", "props": {"b": B8}},
    {"from": T9, "to": TOTAL, "g": "Montanha", "props": {"b": B9, "passos": PASSOS_P}},
]
sfx = [{"t": s["from"], "f": W, "v": 0.3} for s in segs]
for f in FAIXAS:
    sfx += [{"t": f["tc"], "f": POP, "v": 0.2}, {"t": f["tr"], "f": POP, "v": 0.2}]
for row in (B8["l400"], B8["l700"]):
    sfx += [{"t": T8 + a, "f": POP, "v": 0.2} for a in row[1:]]
sfx += [{"t": a, "f": TICK, "v": 0.22} for *_, a in PASSOS]

base = {"video": "", "duration": TOTAL, "segs": segs, "lowers": [], "zooms": [], "sfx": sfx, "music": {"f": "enem/music.mp3", "v": 0.045}}
(P / "edit/props_voz.json").write_text(json.dumps({**base, "voz": "tri/voz.mp3"}, ensure_ascii=False))
(P / "edit/props_mudo.json").write_text(json.dumps({**base, "legendas": LEG}, ensure_ascii=False))
