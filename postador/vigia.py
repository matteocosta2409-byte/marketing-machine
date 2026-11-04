"""Vigia uma pasta e agenda cada vídeo novo como Reel de teste assim que ele termina de chegar.

  python3 vigia.py "<pasta>" --clips "<clips.json>" --tipo corte-yt --sufixo " - v2 horizontal" [--horas 8]

- "Terminou de chegar" = mesmo tamanho por 60 s (o Drive sincroniza aos poucos).
- Legenda e título vêm do clips.json pelo número no começo do arquivo ("03 - ..." → id 3).
- Horário: --intervalo min (padrão 2) depois do último agendado por este vigia (ou do último da fila hoje), nunca antes de agora + 5 min.
- Pula o que já está no postador (mesma origem no Drive) e para quando todos os ids do clips.json estiverem agendados.
"""
import argparse, json, re, sys, time
from datetime import datetime, timedelta
from pathlib import Path
import postador


def ja_agendados():
    agora = datetime.now(postador.SP)
    d = postador.chamar({"acao": "historico", "de": (agora - timedelta(days=3)).isoformat(),
                         "ate": (agora + timedelta(days=30)).isoformat()})
    posts = d["posts"] or []
    origens = {p["origem"] for p in posts if p.get("origem")}
    fim_fila = max((datetime.fromisoformat(p["publicar_em"]) for p in posts
                    if p.get("publicar_em") and p["tipo"] != "antigo"), default=agora)
    return origens, fim_fila


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("--clips", required=True)
    ap.add_argument("--tipo", default="corte-yt"); ap.add_argument("--sufixo", default="")
    ap.add_argument("--horas", type=float, default=8)
    ap.add_argument("--intervalo", type=int, default=2, help="minutos entre posts")
    a = ap.parse_args()
    pasta = Path(a.pasta)
    clips = {c["id"]: c for c in json.loads(Path(a.clips).read_text())}
    tamanhos, estavel_desde = {}, {}
    limite = time.time() + a.horas * 3600
    proximo = None
    print(f"vigiando {pasta.name} ({len(clips)} ids esperados)", flush=True)
    while time.time() < limite:
        origens, fim_fila = ja_agendados()
        feitos = set()
        for f in sorted(pasta.glob("*.mp4")):
            m = re.match(r"(\d+)", f.name)
            if not m or int(m.group(1)) not in clips:
                continue
            rel = str(f.relative_to(postador.DRIVE)) if str(f).startswith(str(postador.DRIVE)) else str(f)
            if rel in origens:
                feitos.add(int(m.group(1)))
                continue
            t = f.stat().st_size
            if tamanhos.get(f) != t:
                tamanhos[f], estavel_desde[f] = t, time.time()
                continue
            if time.time() - estavel_desde[f] < 60:
                continue
            c = clips[int(m.group(1))]
            base = max(fim_fila, proximo or fim_fila)
            quando = max(base + timedelta(minutes=a.intervalo), datetime.now(postador.SP) + timedelta(minutes=5))
            quando = quando.astimezone(postador.SP).replace(second=0, microsecond=0)
            titulo = c["title"].replace("|", " ") + a.sufixo
            try:
                postador.agendar(f, a.tipo, quando, c["caption"], None, ["ig_teste"], titulo)
                proximo = quando
                feitos.add(c["id"])
                print(f"{datetime.now(postador.SP):%H:%M} agendado {f.name} → {quando:%H:%M}", flush=True)
            except Exception as e:  # tenta de novo na próxima volta
                print(f"erro em {f.name}: {e}", flush=True)
        if feitos >= set(clips):
            print("todos agendados — vigia encerrado", flush=True)
            return
        time.sleep(30)
    print(f"tempo esgotado; faltaram: {sorted(set(clips) - feitos)}", flush=True)


if __name__ == "__main__":
    main()
