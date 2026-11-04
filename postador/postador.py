"""Postador do Matteo — agenda vídeos na fila do Supabase e abre o painel.

A fila e a publicação moram no Supabase (projeto matteo-postador, função "postador"):
os posts saem mesmo com o Mac desligado. Este script só sobe vídeo, mexe na fila e
serve o painel local.

Uso:
  python3 postador.py agendar "<video.mp4>" --tipo broll [--quando "2026-10-29 08:00"]
                      [--legenda "..."] [--yt-titulo "..."] [--tiktok] [--youtube]
        tipo: yap-horizontal | yap-vertical | broll | caixinha | corte-yt | outro
        sem --quando: próximo horário livre da grade daquele tipo
  python3 postador.py lista                  # próximos 7 dias + testes esperando decisão
  python3 postador.py validar <post_id> [--quando "..."]   # teste → Reel normal
  python3 postador.py descartar <post_id>
  python3 postador.py cancelar <publicacao_id>
  python3 postador.py reagendar <publicacao_id> --quando "..."
  python3 postador.py rodar                  # força uma rodada agora (não espera o cron)
  python3 postador.py metricas               # força a coleta de métricas
  python3 postador.py config <chave> <valor> # tokens: ig_token, yt_*, tt_*, grade_*, destinos_padrao
  python3 postador.py ig-token               # copia o IG_ACCESS_TOKEN do social-catalog/.env
  python3 postador.py importar               # posts antigos (social-catalog/posted_ig.json) p/ base
  python3 postador.py sincronizar            # traz os Reels que você postou direto no app (últimos 7 dias)
  python3 postador.py painel                 # http://127.0.0.1:8766

Horários sempre de São Paulo.
"""
import argparse, json, os, ssl, subprocess, sys, tempfile, threading, urllib.request, urllib.parse, uuid, webbrowser
import http.server
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:  # Python do python.org não traz CA certs
    SSL_CTX = ssl.create_default_context()

HERE = Path(__file__).resolve().parent
SP = timezone(timedelta(hours=-3))  # sem horário de verão desde 2019
DRIVE = Path.home() / "Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/Meu Drive/2026/Personal Branding"
PASTAS_VIDEO = [DRIVE / "Reels/New/Edited Reels", DRIVE / "YouTube/Cortes"]
TIPOS = ["yap-horizontal", "yap-vertical", "broll", "caixinha", "corte-yt", "outro"]
LIMITE_MB = 45  # bucket do plano grátis aceita 50 MB por arquivo


def load_env():
    env = {}
    p = HERE / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
FUNCAO = ENV.get("SUPABASE_URL", "").rstrip("/") + "/functions/v1/postador"


def chamar(corpo: dict, timeout=170):
    req = urllib.request.Request(FUNCAO, data=json.dumps(corpo).encode(), method="POST", headers={
        "Content-Type": "application/json", "x-postador-token": ENV.get("POSTADOR_TOKEN", "")})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()
        try:
            msg = json.loads(corpo).get("error", corpo)
        except Exception:
            msg = corpo
        raise RuntimeError(f"postador: {msg}")


# ------------------------------------------------------------------ vídeo ----
def sondar(path: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,codec_type",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    video = next((s["codec_name"] for s in d.get("streams", []) if s.get("codec_type") == "video"), "")
    return float(d.get("format", {}).get("duration", 0) or 0), video


def preparar_video(path: Path) -> Path:
    """Recodifica SEMPRE para mp4 H.264/AAC limpo, abaixo de 45 MB (limite do bucket). Mantém o fps.

    Sempre, mesmo quando o arquivo já é pequeno e H.264: em 28/10 os cortes montados com concat
    subiram crus e o Instagram picotou o áudio dos primeiros ~3 s (o 1º trecho da montagem);
    o mesmo vídeo recodificado aqui sai perfeito.
    """
    tamanho_mb = path.stat().st_size / 1e6
    duracao, codec = sondar(path)
    alvo_kbps = int((LIMITE_MB - 3) * 8000 / max(duracao, 1)) - 128
    alvo_kbps = max(1500, min(alvo_kbps, 5000))  # o IG recomprime pra ~3,5 Mbps; mais que isso só ocupa o bucket
    alvo_kbps = min(alvo_kbps, max(1500, int(tamanho_mb * 8000 / max(duracao, 1))))  # não inflar arquivo já leve
    saida = Path(tempfile.gettempdir()) / f"postador-{uuid.uuid4().hex[:8]}.mp4"
    print(f"  comprimindo {tamanho_mb:.0f} MB ({codec}, {duracao:.0f}s) → ~{alvo_kbps} kbps…")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
                    # lado menor até 1080 (4K do iPhone não cabe em 45 MB com qualidade)
                    "-vf", "scale='if(gt(iw,ih),-2,min(1080,iw))':'if(gt(iw,ih),min(1080,ih),-2)'",
                    "-c:v", "libx264", "-preset", "medium", "-b:v", f"{alvo_kbps}k",
                    "-maxrate", f"{int(alvo_kbps * 1.3)}k", "-bufsize", f"{alvo_kbps * 2}k",
                    "-pix_fmt", "yuv420p", "-g", "60",  # keyframe a cada 2 s
                    "-af", "aresample=async=1:first_pts=0", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    str(saida)], check=True)
    print(f"  → {saida.stat().st_size / 1e6:.0f} MB")
    return saida


def subir(path: Path, tipo: str) -> str:
    destino = f"{datetime.now(SP):%Y-%m}/{tipo}-{uuid.uuid4().hex[:8]}.mp4"
    url = chamar({"acao": "upload", "caminho": destino})["url"]
    req = urllib.request.Request(url, data=path.read_bytes(), method="PUT",
                                 headers={"Content-Type": "video/mp4", "x-upsert": "true"})
    with urllib.request.urlopen(req, timeout=600, context=SSL_CTX) as r:
        r.read()
    return destino


def validar(corpo: dict) -> dict:
    """Teste → normal. O vídeo sai do bucket quando o teste publica; aqui sobe de novo do Drive se preciso."""
    try:
        return chamar(corpo)
    except RuntimeError as e:
        if "sem_arquivo" not in str(e):
            raise
    post = chamar({"acao": "post", "post_id": corpo["post_id"]})
    if not post.get("origem"):
        raise RuntimeError("o vídeo saiu do bucket e esse post não tem arquivo no Drive — posta pelo app")
    video = DRIVE / post["origem"]
    if not video.exists():
        raise RuntimeError(f"não achei no Drive: {post['origem']}")
    chamar({"acao": "anexar", "post_id": post["id"], "arquivo": subir(preparar_video(video), post["tipo"])})
    return chamar(corpo)


# ---------------------------------------------------------------- horários ---
def parse_quando(s: str) -> datetime:
    s = s.strip().replace("T", " ")
    # "DD/MM HH:MM" sem ano → ano corrente (o strptime sem ano é ambíguo a partir do 3.15)
    if len(s.split(" ")[0].split("/")) == 2:
        dia, hora = s.split(" ", 1)
        s = f"{dia}/{datetime.now(SP).year} {hora}"
    for fmt in ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=SP)
        except ValueError:
            pass
    raise SystemExit(f"data inválida: {s} (use 'AAAA-MM-DD HH:MM' ou 'DD/MM HH:MM')")


def proximo_livre(tipo: str) -> datetime:
    """Próximo dia em que o horário da grade desse tipo ainda está vago."""
    agora = datetime.now(SP)
    dados = chamar({"acao": "listar", "de": agora.isoformat(), "ate": (agora + timedelta(days=60)).isoformat()})
    hhmm = dados["grade_teste"].get(tipo, "15:00")
    ocupados = {datetime.fromisoformat(p["publicar_em"]).astimezone(SP).date()
                for p in dados["posts"] or [] if p["tipo"] == tipo and p.get("publicar_em")}
    h, m = map(int, hhmm.split(":"))
    dia = agora.date()
    while True:
        quando = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=SP)
        if quando > agora + timedelta(minutes=20) and dia not in ocupados:
            return quando
        dia += timedelta(days=1)


# ------------------------------------------------------------------ ações ----
def agendar(video: Path, tipo: str, quando: datetime | None, legenda: str, yt_titulo: str | None,
            destinos: list[str], titulo: str | None = None):
    if tipo not in TIPOS:
        raise SystemExit(f"tipo inválido: {tipo} ({', '.join(TIPOS)})")
    if not video.exists():
        raise SystemExit(f"não achei o vídeo: {video}")
    quando = quando or proximo_livre(tipo)
    if "youtube" in destinos:
        w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                        "stream=width,height", "-of", "csv=p=0", str(video)],
                                       capture_output=True, text=True).stdout.strip().split(",")[:2])
        if w > h:
            print("  ⚠ vídeo horizontal: no YouTube ele entra como vídeo comum, não como Short")
    pronto = preparar_video(video)
    print(f"  subindo {pronto.name}…")
    arquivo = subir(pronto, tipo)
    if pronto != video:
        pronto.unlink(missing_ok=True)
    origem = str(video.relative_to(DRIVE)) if str(video).startswith(str(DRIVE)) else str(video)
    r = chamar({"acao": "agendar", "destinos": destinos, "post": {
        "tipo": tipo, "titulo": titulo or video.stem, "legenda": legenda, "youtube_titulo": yt_titulo,
        "arquivo": arquivo, "origem": origem, "publicar_em": quando.isoformat()}})
    print(f"✓ agendado {quando:%a %d/%m %H:%M} → {', '.join(r['destinos'])}  (post {r['post_id']})")
    return r


def fmt(iso):
    return datetime.fromisoformat(iso).astimezone(SP).strftime("%a %d/%m %H:%M") if iso else "—"


def lista():
    agora = datetime.now(SP)
    dados = chamar({"acao": "listar", "de": (agora - timedelta(days=1)).isoformat(),
                    "ate": (agora + timedelta(days=7)).isoformat()})
    posts = sorted(dados["posts"] or [], key=lambda p: p.get("publicar_em") or "")
    espera = [p for p in posts if not p["decisao"] and any(
        x["destino"] == "ig_teste" and x["status"] == "publicado" for x in p["publicacoes"])]
    if espera:
        print("ESPERANDO VALIDAÇÃO (teste → normal):")
        for p in espera:
            t = next(x for x in p["publicacoes"] if x["destino"] == "ig_teste")
            v = (t.get("metricas") or {}).get("views", "?")
            print(f"  {p['id']}  {p['tipo']:<15} {p['titulo'][:40]:<40} {v} views  {t.get('permalink') or ''}")
        print()
    print("FILA:")
    for p in posts:
        pubs = " ".join(f"{x['destino']}:{x['status']}" for x in sorted(p["publicacoes"], key=lambda x: x["destino"]))
        print(f"  {fmt(p['publicar_em'])}  {p['tipo']:<15} {p['titulo'][:38]:<38} {pubs}")
        for x in p["publicacoes"]:
            if x.get("erro"):
                print(f"      ⚠ {x['destino']} ({x['id']}): {x['erro']}")


def importar():
    arq = HERE.parent / "social-catalog/posted_ig.json"
    posts = json.loads(arq.read_text())["posts"]
    itens = [{
        "media_id": p["id"], "titulo": (p.get("caption") or "").split("\n")[0][:80] or "(sem legenda)",
        "legenda": p.get("caption") or "", "publicado_em": p["timestamp"].replace("+0000", "+00:00"),
        "permalink": p.get("permalink"),
        "metricas": {"likes": p.get("like_count", 0), "comments": p.get("comments_count", 0)},
    } for p in posts if p.get("media_product_type") == "REELS"]
    total = 0
    for i in range(0, len(itens), 40):
        total += chamar({"acao": "importar", "itens": itens[i:i + 40]})["importados"]
    print(f"✓ {total} Reels antigos importados (base de comparação)")


METRICAS_IG = "views,reach,saved,shares,likes,comments,total_interactions,ig_reels_avg_watch_time"


def seguidores_por_dia(dias=30):
    """Seguidores novos por dia (insight da conta "follower_count"). A Meta não dá isso por Reel.

    O dia da Meta fecha às 07:00 UTC (meia-noite no Pacífico); o valor com end_time do dia D+1
    é o ganho do dia D. Volta {"AAAA-MM-DD": n}.
    """
    env = {}
    for line in (HERE.parent / "social-catalog/.env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    fim = int(datetime.now(timezone.utc).timestamp())
    out = {}
    while dias > 0:  # a API aceita no máximo 30 dias por chamada
        lote = min(dias, 29)
        q = urllib.parse.urlencode({"metric": "follower_count", "period": "day", "since": fim - lote * 86400,
                                    "until": fim, "access_token": env["IG_ACCESS_TOKEN"]})
        with urllib.request.urlopen(f"https://graph.instagram.com/v23.0/{env['IG_USER_ID']}/insights?{q}",
                                    context=SSL_CTX, timeout=60) as r:
            for v in json.loads(r.read())["data"][0]["values"]:
                dia = (datetime.fromisoformat(v["end_time"].replace("+0000", "+00:00")) - timedelta(days=1)).date()
                out[dia.isoformat()] = v["value"]
        fim -= lote * 86400; dias -= lote
    # Dias que a Meta ainda não fechou (vem 0 nos últimos 1–2 dias): diferença entre as fotos
    # de hora em hora do total (tabela seguidores). Hoje = ganho até agora.
    try:
        fotos = [(datetime.fromisoformat(f["em"]).astimezone(SP), f["total"]) for f in chamar({"acao": "seguidores"})]
    except Exception:
        fotos = []
    for dia in sorted({d.date() for d, _ in fotos}):
        if out.get(dia.isoformat()):
            continue
        antes = [t for d, t in fotos if d.date() < dia]
        no_dia = [t for d, t in fotos if d.date() == dia]
        base = antes[-1] if antes else no_dia[0]
        if no_dia[-1] - base:
            out[dia.isoformat()] = no_dia[-1] - base
    return out


def sincronizar(dias=7):
    """Traz pro postador os Reels que ele postou direto no app (tipo "manual"), pra acompanhar métricas.

    Reel que não foi pro feed (is_shared_to_feed = false) = Reel de teste. Os já conhecidos
    (pelo media_id) são ignorados pela função; as métricas depois o cron atualiza sozinho.
    """
    env = {}
    for line in (HERE.parent / "social-catalog/.env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    tok, base = env["IG_ACCESS_TOKEN"], "https://graph.instagram.com/v23.0"
    url = f"{base}/{env['IG_USER_ID']}/media?" + urllib.parse.urlencode({
        "fields": "id,caption,media_product_type,timestamp,permalink,is_shared_to_feed", "limit": 50, "access_token": tok})
    with urllib.request.urlopen(url, context=SSL_CTX, timeout=60) as r:
        midias = json.loads(r.read()).get("data", [])
    corte = datetime.now(timezone.utc) - timedelta(days=dias)
    itens = []
    for m in midias:
        quando = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
        if m.get("media_product_type") != "REELS" or quando < corte:
            continue
        try:
            q = urllib.parse.urlencode({"metric": METRICAS_IG, "access_token": tok})
            with urllib.request.urlopen(f"{base}/{m['id']}/insights?{q}", context=SSL_CTX, timeout=60) as r:
                met = {x["name"]: x["values"][0]["value"] for x in json.loads(r.read())["data"]}
        except Exception:
            met = None
        legenda = m.get("caption") or ""
        itens.append({"media_id": m["id"], "tipo": "manual",
                      "titulo": legenda.split("\n")[0][:80] or "(sem legenda)", "legenda": legenda,
                      "publicado_em": quando.isoformat(), "permalink": m.get("permalink"),
                      "destino": "ig_normal" if m.get("is_shared_to_feed") else "ig_teste", "metricas": met})
    n = chamar({"acao": "importar", "itens": itens})["importados"] if itens else 0
    return n


# ------------------------------------------------------------------ painel ---
def videos_drive(ja_agendados: set[str]):
    out = []
    for pasta in PASTAS_VIDEO:
        if not pasta.exists():
            continue
        for f in pasta.rglob("*"):
            if f.suffix.lower() in (".mp4", ".mov") and not f.name.startswith("."):
                rel = str(f.relative_to(DRIVE))
                out.append({"caminho": rel, "nome": f.stem, "pasta": f.parent.name,
                            "mb": round(f.stat().st_size / 1e6), "agendado": rel in ja_agendados,
                            "mtime": f.stat().st_mtime})
    return sorted(out, key=lambda x: -x["mtime"])


class Painel(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responder(self, corpo, status=200, tipo="application/json"):
        dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.responder((HERE / "painel.html").read_bytes(), tipo="text/html; charset=utf-8")
        self.responder({"error": "não achei"}, 404)

    def do_POST(self):
        tam = int(self.headers.get("Content-Length") or 0)
        b = json.loads(self.rfile.read(tam) or b"{}")
        try:
            if self.path == "/api/seguidores":
                return self.responder(seguidores_por_dia())
            if self.path == "/api/sincronizar":
                return self.responder({"novos": sincronizar()})
            if self.path == "/api/drive":
                return self.responder({"videos": videos_drive(set(b.get("agendados", [])))})
            if self.path == "/api/agendar-drive":
                quando = parse_quando(b["quando"]) if b.get("quando") else None
                r = agendar(DRIVE / b["caminho"], b["tipo"], quando, b.get("legenda", ""),
                            b.get("yt_titulo") or None, b.get("destinos") or ["ig_teste"], b.get("titulo"))
                return self.responder(r)
            if self.path == "/api":
                return self.responder(validar(b) if b.get("acao") == "validar" else chamar(b))
            self.responder({"error": "não achei"}, 404)
        except Exception as e:
            self.responder({"error": str(e)}, 500)


def painel(porta=8766):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", porta), Painel)
    url = f"http://127.0.0.1:{porta}"
    print(f"painel em {url}  (Ctrl+C pra fechar)")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# --------------------------------------------------------------------- cli ---
def main():
    ap = argparse.ArgumentParser(description="Postador do Matteo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agendar")
    a.add_argument("video")
    a.add_argument("--tipo", required=True, choices=TIPOS)
    a.add_argument("--quando")
    a.add_argument("--legenda", default="")
    a.add_argument("--legenda-arquivo")
    a.add_argument("--titulo")
    a.add_argument("--yt-titulo")
    a.add_argument("--tiktok", action="store_true")
    a.add_argument("--youtube", action="store_true")
    sub.add_parser("lista")
    v = sub.add_parser("validar"); v.add_argument("post_id"); v.add_argument("--quando")
    d = sub.add_parser("descartar"); d.add_argument("post_id")
    c = sub.add_parser("cancelar"); c.add_argument("publicacao_id")
    r = sub.add_parser("reagendar"); r.add_argument("publicacao_id"); r.add_argument("--quando", required=True)
    sub.add_parser("rodar"); sub.add_parser("metricas"); sub.add_parser("ig-token"); sub.add_parser("importar")
    sub.add_parser("sincronizar")
    sub.add_parser("testar-ig"); sub.add_parser("ver-config")
    cf = sub.add_parser("config"); cf.add_argument("chave"); cf.add_argument("valor")
    sub.add_parser("painel")
    args = ap.parse_args()

    if args.cmd == "agendar":
        legenda = Path(args.legenda_arquivo).read_text() if args.legenda_arquivo else args.legenda
        destinos = ["ig_teste"] + (["tiktok"] if args.tiktok else []) + (["youtube"] if args.youtube else [])
        agendar(Path(args.video).expanduser(), args.tipo, parse_quando(args.quando) if args.quando else None,
                legenda, args.yt_titulo, destinos, args.titulo)
    elif args.cmd == "lista":
        lista()
    elif args.cmd == "validar":
        corpo = {"acao": "validar", "post_id": args.post_id}
        if args.quando:
            corpo["publicar_em"] = parse_quando(args.quando).isoformat()
        print(f"✓ Reel normal agendado para {fmt(validar(corpo)['publicar_em'])}")
    elif args.cmd == "descartar":
        chamar({"acao": "descartar", "post_id": args.post_id}); print("✓ descartado")
    elif args.cmd == "cancelar":
        print(chamar({"acao": "cancelar", "publicacao_id": args.publicacao_id}))
    elif args.cmd == "reagendar":
        print(chamar({"acao": "reagendar", "publicacao_id": args.publicacao_id,
                      "publicar_em": parse_quando(args.quando).isoformat()}))
    elif args.cmd == "rodar":
        print(json.dumps(chamar({}), ensure_ascii=False, indent=2))
    elif args.cmd == "metricas":
        print(json.dumps(chamar({"acao": "metricas"}), ensure_ascii=False, indent=2))
    elif args.cmd == "testar-ig":
        print(chamar({"acao": "testar_ig"}))
    elif args.cmd == "ver-config":
        print(json.dumps(chamar({"acao": "config_ver"}), ensure_ascii=False, indent=2))
    elif args.cmd == "config":
        print(chamar({"acao": "config", "chave": args.chave, "valor": args.valor}))
    elif args.cmd == "ig-token":
        env = {}
        for line in (HERE.parent / "social-catalog/.env").read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, val = line.split("=", 1)
                env[k.strip()] = val.strip().strip('"').strip("'")
        chamar({"acao": "config", "chave": "ig_token", "valor": env["IG_ACCESS_TOKEN"]})
        print("✓ token do IG copiado pro postador")
    elif args.cmd == "importar":
        importar()
    elif args.cmd == "sincronizar":
        print(f"✓ {sincronizar()} post(s) feitos no app trazidos pro postador")
    elif args.cmd == "painel":
        painel()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
