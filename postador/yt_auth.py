"""Conecta o canal do YouTube ao postador (uma vez só).

  python3 yt_auth.py receber   # espera o client_id/secret chegarem num POST local (vindo do navegador)
  python3 yt_auth.py login     # abre o consentimento, recebe o código, salva o refresh token no postador

Escopos: youtube.upload (postar) + youtube.readonly (ler views dos Shorts).
O app do Google está "Em produção" (sem verificação): o Google mostra o aviso
"app não verificado" → Avançado → Acessar. O refresh token não expira em 7 dias.
"""
import json, os, sys, urllib.parse, urllib.request, http.server, webbrowser
from pathlib import Path
import postador

HERE = Path(__file__).resolve().parent
CLIENTE = HERE / ".yt_client.json"
PORTA = 8798
ESCOPOS = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def receber():
    class H(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            dados = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            fd = os.open(CLIENTE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            os.write(fd, json.dumps(dados).encode()); os.close(fd)
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
            raise SystemExit
        def log_message(self, *a): pass
    try:
        http.server.HTTPServer(("127.0.0.1", 8799), H).serve_forever()
    except SystemExit:
        print("cliente salvo")


def login():
    c = json.loads(CLIENTE.read_text())
    redirect = f"http://127.0.0.1:{PORTA}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": redirect, "response_type": "code",
        "scope": ESCOPOS, "access_type": "offline", "prompt": "consent"})
    codigo = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in q and "error" not in q:
                self.send_response(404); self.end_headers(); return
            codigo.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h2>Pronto ✓ YouTube conectado ao postador. Pode fechar.</h2>".encode())
        def log_message(self, *a): pass

    srv = http.server.HTTPServer(("127.0.0.1", PORTA), H)
    print("URL:", url, flush=True)
    while not codigo:
        srv.handle_request()
    if "error" in codigo:
        sys.exit(f"recusado: {codigo['error']}")
    corpo = urllib.parse.urlencode({"code": codigo["code"], "client_id": c["client_id"],
                                    "client_secret": c["client_secret"], "redirect_uri": redirect,
                                    "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=corpo, context=postador.SSL_CTX) as r:
        tok = json.loads(r.read())
    if "refresh_token" not in tok:
        sys.exit("o Google não devolveu refresh_token (rodar de novo)")
    for k, v in (("yt_client_id", c["client_id"]), ("yt_client_secret", c["client_secret"]),
                 ("yt_refresh_token", tok["refresh_token"])):
        postador.chamar({"acao": "config", "chave": k, "valor": v})
    # confere: qual canal ficou conectado
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true",
                                 headers={"Authorization": f"Bearer {tok['access_token']}"})
    with urllib.request.urlopen(req, context=postador.SSL_CTX) as r:
        ch = json.loads(r.read()).get("items", [{}])[0]
    print("✓ conectado:", ch.get("snippet", {}).get("title"), "|", ch.get("statistics", {}).get("subscriberCount"), "inscritos")


if __name__ == "__main__":
    {"receber": receber, "login": login}[sys.argv[1]]()
