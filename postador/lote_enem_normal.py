"""Reels normais dos cortes ENEM d1 escolhidos em 03/11 (versão horizontal), sempre depois do teste do mesmo vídeo.
São 13 de 3/11 a 7/11: 3, 3, 3, 2, 2. Até 15/11 só entra post de ENEM.
Rodar de novo reagenda os que já foram validados.

  python3 lote_enem_normal.py            # mostra o plano
  python3 lote_enem_normal.py --valendo  # agenda
"""
import sys
from datetime import datetime
import postador

SP = postador.SP
SEM, EST = "Cortes Semana ENEM d1", "Cortes ENEM d1"
PLANO = [
    (SEM, "03", (3, 17, 40)), (SEM, "04", (3, 18, 40)), (SEM, "05", (3, 19, 40)),
    (SEM, "06", (4, 10, 0)), (SEM, "07", (4, 16, 0)), (SEM, "08", (4, 19, 0)),
    (SEM, "09", (5, 10, 0)), (EST, "01", (5, 15, 0)), (EST, "02", (5, 19, 0)),
    (EST, "04", (6, 10, 0)), (EST, "05", (6, 19, 0)),
    (EST, "07", (7, 10, 0)), (EST, "08", (7, 19, 0)),
]

d = postador.chamar({"acao": "historico", "de": "2026-11-03T00:00:00+00:00", "ate": "2026-11-20T00:00:00+00:00"})
posts = [p for p in d["posts"] if "Semana 9 - 02-11-2026" in (p.get("origem") or "") and "v2 - horizontal" in p["origem"]]
itens = []
for pasta, num, (dia, h, m) in PLANO:
    achados = [p for p in posts if f"/{pasta}/" in p["origem"] and p["origem"].split("/")[-1].startswith(num + " - ")]
    assert len(achados) == 1, (pasta, num, len(achados))
    teste = next(x for x in achados[0]["publicacoes"] if x["destino"] == "ig_teste")
    quando = datetime(2026, 11, dia, h, m, tzinfo=SP)
    assert datetime.fromisoformat(teste["publicar_em"]) < quando, ("normal antes do teste", pasta, num)
    assert quando > datetime.now(SP), ("horário já passou", pasta, num)
    assert "Black Friday" in achados[0]["legenda"]
    itens.append((achados[0], quando))
for p, quando in itens:
    print(f"{quando:%d/%m %H:%M}  {p['titulo']}")
    if "--valendo" in sys.argv:
        normal = next((x for x in p["publicacoes"] if x["destino"] == "ig_normal"), None)
        r = postador.chamar({"acao": "reagendar", "publicacao_id": normal["id"], "publicar_em": quando.isoformat()}) if normal \
            else postador.validar({"acao": "validar", "post_id": p["id"], "publicar_em": quando.isoformat()})
        print("  ", r)
print(len(itens), "posts")
