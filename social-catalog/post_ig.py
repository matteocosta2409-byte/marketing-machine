"""Posta um Reel (ou Reel de teste) no Instagram via Graph API (Content Publishing).

Uso:
  python post_ig.py "<video.mp4>" --caption "legenda aqui"
  python post_ig.py "<video.mp4>" --caption "..." --trial                 # Reel de teste (graduação MANUAL)
  python post_ig.py "<video.mp4>" --caption "..." --trial --strategy SS_PERFORMANCE
  python post_ig.py "<video.mp4>" --caption "..." --dry-run               # só hospeda e mostra a URL, não publica

Requer social-catalog/.env com:
  IG_ACCESS_TOKEN=<token de longa duração>   (usuário; o script acha a Página + conta IG)
  IG_USER_ID=<opcional; se vazio, descobre>
  IG_PAGE_TOKEN=<opcional; se vazio, deriva da Página>

Hospeda o vídeo local via cloudflared quick tunnel (sem conta), a Meta baixa de lá,
publica, e derruba o túnel. Fluxo: /media (container) -> poll status -> /media_publish.
"""
import argparse, json, os, re, ssl, subprocess, sys, time, threading, urllib.request, urllib.parse
import http.server, socketserver
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl.create_default_context()

HERE = Path(__file__).resolve().parent
# Instagram API com Login do Instagram -> base graph.instagram.com, token IG direto (sem Página).
API_VERSION = os.environ.get("IG_API_VERSION", "v21.0")
GRAPH = os.environ.get("IG_GRAPH_BASE", f"https://graph.instagram.com/{API_VERSION}")
CLOUDFLARED = HERE / "bin" / "cloudflared"


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


def api_get(path, params):
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60, context=SSL_CTX) as r:
        return json.loads(r.read())


def api_post(path, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120, context=SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API erro {e.code}: {e.read().decode()[:600]}")


def resolve_account(env):
    # Login do Instagram: o próprio IG_ACCESS_TOKEN publica, com o IG_USER_ID.
    token = env.get("IG_ACCESS_TOKEN") or os.environ.get("IG_ACCESS_TOKEN", "")
    if not token:
        sys.exit("Falta IG_ACCESS_TOKEN no social-catalog/.env (veja README_TOKEN.md)")
    uid = env.get("IG_USER_ID", "") or os.environ.get("IG_USER_ID", "")
    if not uid:
        uid = str(api_get("me", {"fields": "user_id", "access_token": token}).get("user_id", ""))
    if not uid:
        sys.exit("Falta IG_USER_ID (não consegui descobrir pelo token).")
    return uid, token


def serve_file(video: Path):
    """Sobe um HTTP server servindo a pasta do vídeo; retorna (porta, httpd, thread)."""
    directory = str(video.parent)

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=directory, **k)
        def log_message(self, *a):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    httpd.daemon_threads = True
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return port, httpd


def start_tunnel(port):
    """Inicia cloudflared quick tunnel e retorna (url_publica, processo)."""
    proc = subprocess.Popen([str(CLOUDFLARED), "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    url = None
    t0 = time.time()
    while time.time() - t0 < 75:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        # exige pelo menos um hífen (o túnel é tipo "a-b-c-d.trycloudflare.com"); ignora "api.trycloudflare.com"
        m = re.search(r"https://[a-z0-9]+(?:-[a-z0-9]+)+\.trycloudflare\.com", line)
        if m and "api.trycloudflare.com" not in m.group(0):
            url = m.group(0)
            break
    if not url:
        proc.terminate()
        sys.exit("cloudflared não forneceu URL pública (sem internet?).")
    return url, proc


def wait_until_live(public_url, timeout=40):
    """Espera o túnel ficar acessível de fora (a Meta precisa conseguir baixar)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(public_url, method="GET", headers={"Range": "bytes=0-1023"})
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
                if r.status in (200, 206):
                    return True
        except Exception:
            time.sleep(2)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--caption", default="")
    ap.add_argument("--trial", action="store_true", help="publica como Reel de TESTE")
    ap.add_argument("--strategy", default="MANUAL", choices=["MANUAL", "SS_PERFORMANCE"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"vídeo não encontrado: {video}")

    env = load_env()
    uid, page_token = (None, None) if args.dry_run else resolve_account(env)

    port, httpd = serve_file(video)
    url, tunnel = start_tunnel(port)
    public_url = f"{url}/" + urllib.parse.quote(video.name)
    print(f"hospedado: {public_url}")

    try:
        print("aguardando o túnel ficar acessível...")
        if wait_until_live(public_url):
            print("  túnel OK (acessível de fora)")
        else:
            print("  (meu check não acessou — pode ser o sandbox local; vou tentar mesmo assim, a Meta baixa de outro servidor)")
            time.sleep(8)
        if args.dry_run:
            print("dry-run: fim.")
            return

        # 1) container
        params = {"media_type": "REELS", "video_url": public_url,
                  "caption": args.caption, "access_token": page_token}
        if args.trial:
            params["trial_params"] = json.dumps({"graduation_strategy": args.strategy})
        print(f"criando container{' (TESTE)' if args.trial else ''}...")
        cid = api_post(f"{uid}/media", params)["id"]
        print("  container:", cid)

        # 2) poll status (até ~5 min)
        for i in range(30):
            st = api_get(cid, {"fields": "status_code", "access_token": page_token}).get("status_code")
            print(f"  status: {st}")
            if st == "FINISHED":
                break
            if st in ("ERROR", "EXPIRED"):
                sys.exit(f"falha no processamento: {st}")
            time.sleep(10)
        else:
            sys.exit("timeout esperando o vídeo processar")

        # 3) publish
        print("publicando...")
        mid = api_post(f"{uid}/media_publish", {"creation_id": cid, "access_token": page_token})["id"]
        link = api_get(mid, {"fields": "permalink", "access_token": page_token}).get("permalink", "")
        print(f"PUBLICADO: media_id={mid}")
        if link:
            print(f"link: {link}")
        if args.trial:
            print("(Reel de TESTE — graduação:", args.strategy + ")")
    finally:
        tunnel.terminate()
        httpd.shutdown()


if __name__ == "__main__":
    main()
