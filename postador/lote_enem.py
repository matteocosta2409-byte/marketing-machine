"""Cortes do ENEM (semana + estratégia de prova, 1º e 2º dia) no Reel de teste, em pares vertical × horizontal.

12 por dia, a cada 20 min (ver lote_qa2.py). A "semana" sai antes da "estratégia", que é mais perto da prova.
Sobe tudo de uma vez (cabe em 1 GB) e pula o que já está agendado, então dá pra rodar de novo se cair no meio.

  python3 lote_enem.py            # mostra o plano
  python3 lote_enem.py --valendo  # agenda
"""
import json, re, sys
from datetime import datetime, timedelta
from pathlib import Path
import postador

SEMANA = postador.DRIVE / "Reels/New/Edited Reels/Semana 9 - 02-11-2026"
CORTES = Path("/Users/mac-matteo/marketing machine/cortes")
ESPACO, POR_DIA = 20, 12
CTA = ('Comenta "{palavra}" pra receber o link do vídeo completo no YT!\n\n'
       '🔥 Dia 16/11 tem Black Friday de mentorias: chironvest.com.br\n\n'
       'Me segue pra mais @matteo.rocha_ 💻⚕️🐧')
# (início) → projetos na ordem em que saem
BLOCOS = [
    (datetime(2026, 11, 3, 13, 40, tzinfo=postador.SP), [("Cortes Semana ENEM d1", "semana-d1", "semana1"),
                                                         ("Cortes ENEM d1", "enem-d1", "prova1")]),
    (datetime(2026, 11, 9, 12, 0, tzinfo=postador.SP), [("Cortes Semana ENEM d2", "semana-d2", "semana2"),
                                                        ("Cortes ENEM d2", "enem-d2", "prova2")]),
]


def por_numero(pasta):
    return {int(re.match(r"\d+", f.name)[0]): f for f in pasta.glob("*.mp4") if re.match(r"\d+", f.name)}


def plano():
    out = []
    for inicio, projetos in BLOCOS:
        vagas = 0
        for pasta, proj, palavra in projetos:
            clips = {c["id"]: c for c in json.loads((CORTES / proj / "clips.json").read_text())}
            vert, hor = por_numero(SEMANA / pasta / "v1 - vertical"), por_numero(SEMANA / pasta / "v2 - horizontal")
            for n in sorted(clips):
                legenda = clips[n]["caption"].rstrip() + "\n\n" + CTA.format(palavra=palavra)
                for f, sufixo in ((vert[n], ""), (hor[n], " - v2 horizontal")):
                    titulo = re.sub(r"\s*-\s*v\d+$", "", re.sub(r"^\d+\s*-\s*", "", f.stem), flags=re.I) + sufixo
                    # o 1º dia pode começar depois do meio-dia; os seguintes sempre às 12:00
                    q = inicio + timedelta(minutes=ESPACO * vagas) if vagas < POR_DIA else \
                        inicio.replace(hour=12, minute=0) + timedelta(days=vagas // POR_DIA, minutes=ESPACO * (vagas % POR_DIA))
                    out.append((f, titulo, legenda, q))
                    vagas += 1
    return out


itens = plano()
ja = set()
if "--valendo" in sys.argv:
    d = postador.chamar({"acao": "historico", "de": "2026-11-03T00:00:00+00:00", "ate": "2026-11-20T00:00:00+00:00"})
    ja = {p.get("origem") for p in d["posts"]}
for f, titulo, legenda, q in itens:
    print(f"{q:%d/%m %H:%M}  {titulo}")
    if "--valendo" in sys.argv and str(f.relative_to(postador.DRIVE)) not in ja:
        postador.agendar(f, "corte-yt", q, legenda, None, ["ig_teste"], titulo)
print(len(itens), "posts")
if "--ver" in sys.argv:
    print(itens[0][2])
