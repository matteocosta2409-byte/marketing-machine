"""Agenda um lote de cortes (vertical × horizontal) como Reels de teste, intercalados em pares.

  python3 lote.py              # mostra o plano (não agenda nada)
  python3 lote.py --valendo    # cancela os cortes desses projetos ainda na fila e agenda tudo de novo

Para cada projeto: pasta do Drive com "v1 - vertical" e "v2 - horizontal" + clips.json (legendas).
Ordem: corte 1 vertical, corte 1 horizontal, corte 2 vertical… (o par sai lado a lado → comparação justa).
Intervalo de 2 min. O arquivo é lido do Drive na hora (pega sempre a versão mais nova).
"""
import argparse, json, re
from datetime import datetime, timedelta
from pathlib import Path
import postador

SEMANA = postador.DRIVE / "Reels/New/Edited Reels/Semana 8 - 26-10-2026"
CORTES = Path("/Users/mac-matteo/marketing machine/cortes")
PROJETOS = [
    (SEMANA / "Cortes sono - Por que nós dormimos", CORTES / "sono-yt/clips.json"),
    (SEMANA / "Cortes Q&A", CORTES / "qa/clips.json"),
]
INTERVALO = 2
CTA = 'Comenta "vídeo" pra receber o link do vídeo completo no YT!\n\nMe segue pra mais @matteo.rocha_ 💻⚕️🐧'


def plano():
    itens = []
    for pasta, clips_json in PROJETOS:
        clips = {c["id"]: c for c in json.loads(clips_json.read_text())}
        def por_numero(sub):
            out = {}
            for f in (pasta / sub).glob("*.mp4"):
                m = re.match(r"(\d+)", f.name)
                if m: out[int(m.group(1))] = f
            return out
        vert, hor = por_numero("v1 - vertical"), por_numero("v2 - horizontal")
        def titulo_do_arquivo(f):  # "03 - Sabia que ... - v2.mp4" → "Sabia que ..." (o nome é a versão mais nova)
            t = re.sub(r"^\d+\s*-\s*", "", f.stem)
            return re.sub(r"\s*-\s*v\d+$", "", t, flags=re.I)
        for n in sorted(clips):
            legenda = clips[n]["caption"].rstrip()
            if "me segue" not in legenda.lower():
                legenda += "\n\n" + CTA
            if n in vert: itens.append((vert[n], titulo_do_arquivo(vert[n]), legenda))
            if n in hor: itens.append((hor[n], titulo_do_arquivo(hor[n]) + " - v2 horizontal", legenda))
            if n not in vert or n not in hor:
                print(f"⚠ {pasta.name} corte {n}: falta {'vertical' if n not in vert else 'horizontal'}")
    return itens


def cancelar_fila(origens):
    """Tira da fila (e da validação) os posts desses projetos que ainda não saíram."""
    agora = datetime.now(postador.SP)
    d = postador.chamar({"acao": "historico", "de": (agora - timedelta(days=1)).isoformat(),
                         "ate": (agora + timedelta(days=7)).isoformat()})
    n = 0
    for p in d["posts"] or []:
        if p["tipo"] != "corte-yt":
            continue
        for x in p["publicacoes"]:
            if x["status"] in ("pendente", "erro"):
                postador.chamar({"acao": "cancelar", "publicacao_id": x["id"]}) if x["status"] == "pendente" else None
                n += 1
        if not p["decisao"] and not any(x["status"] == "publicado" for x in p["publicacoes"]):
            postador.chamar({"acao": "descartar", "post_id": p["id"]})
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--valendo", action="store_true")
    ap.add_argument("--inicio-em", type=int, default=10, help="minutos até o 1º post")
    a = ap.parse_args()
    itens = plano()
    inicio = (datetime.now(postador.SP) + timedelta(minutes=a.inicio_em)).replace(second=0, microsecond=0)
    for i, (f, titulo, _) in enumerate(itens):
        print(f"{inicio + timedelta(minutes=INTERVALO * i):%H:%M}  {titulo}")
    print(f"{len(itens)} posts, de {inicio:%H:%M} a {inicio + timedelta(minutes=INTERVALO * (len(itens) - 1)):%H:%M}")
    if not a.valendo:
        return
    print(f"cancelados da fila antiga: {cancelar_fila(None)}")
    for i, (f, titulo, legenda) in enumerate(itens):
        quando = inicio + timedelta(minutes=INTERVALO * i)
        if quando < datetime.now(postador.SP) + timedelta(minutes=2):  # o upload atrasou: empurra
            inicio += datetime.now(postador.SP) + timedelta(minutes=3) - quando
            quando = inicio + timedelta(minutes=INTERVALO * i)
        postador.agendar(f, "corte-yt", quando, legenda, None, ["ig_teste"], titulo)


if __name__ == "__main__":
    main()
