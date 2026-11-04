"""Cortes Q&A 12–25 (vertical × horizontal) no Reel de teste, em pares, 20 min entre eles.
No máximo 12 Reels de teste por dia: em 28–29/10 saíram 36 em ~24h e o IG passou a recusar
(mesmo a 20 min). 31/10 começa 12:40 porque 12:00 e 12:20 são as sobras do lote 1–11.
Sobe um dia por vez pra não passar de 1 GB no bucket.

  python3 lote_qa2.py                       # mostra o plano
  python3 lote_qa2.py --valendo --dia 30    # agenda só o dia 30 (ou 31)
"""
import sys

ESPACO = 20  # min
from datetime import datetime, timedelta
import lote, postador

# (início, quantos)
DIAS = [(datetime(2026, 10, 31, 12, 40, tzinfo=postador.SP), 10),
        (datetime(2026, 11, 1, 12, 0, tzinfo=postador.SP), 12),
        (datetime(2026, 11, 2, 13, 20, tzinfo=postador.SP), 6)]
VAGAS = [ini + timedelta(minutes=ESPACO * k) for ini, qtd in DIAS for k in range(qtd)]

itens = [i for i in lote.plano() if "Cortes Q&A" in str(i[0]) and int(i[0].name[:2]) >= 12]
for n, (f, titulo, legenda) in enumerate(itens):
    quando = VAGAS[n]
    if "--dia" in sys.argv and quando.day != int(sys.argv[sys.argv.index("--dia") + 1]):
        continue
    print(f"{quando:%d/%m %H:%M}  {titulo}")
    if "--valendo" in sys.argv:
        postador.agendar(f, "corte-yt", quando, legenda, None, ["ig_teste"], titulo)
print(len(itens), "posts")
