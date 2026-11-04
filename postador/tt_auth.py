"""Conecta a conta do TikTok ao postador (uma vez só; refaz quando mudar de sandbox → produção).

  python3 tt_auth.py receber   # espera client_key/secret chegarem num POST local (vindo do navegador)
  python3 tt_auth.py login     # abre a autorização, recebe o código, salva os tokens no postador

Login Kit para Desktop: redirect http://localhost:8797/callback/ e PKCE
(no TikTok o code_challenge é o SHA-256 do verifier em HEX, não base64url).
"""
import hashlib, http.server, json, os, secrets, sys, time, urllib.parse, urllib.request
from pathlib import Path
import postador

HERE = Path(__file__).resolve().parent
CLIENTE = HERE / ".tt_client.json"
PORTA = 8797
REDIRECT = f"http://localhost:{PORTA}/callback/"
ESCOPOS = "user.info.basic,video.publish,video.upload"


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
    verifier = secrets.token_urlsafe(48)
    estado = secrets.token_hex(8)
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": c["client_key"], "scope": ESCOPOS, "response_type": "code",
        "redirect_uri": REDIRECT, "state": estado,
        "code_challenge": hashlib.sha256(verifier.encode()).hexdigest(), "code_challenge_method": "S256"})
    codigo = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in q and "error" not in q:
                self.send_response(404); self.end_headers(); return
            codigo.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h2>Pronto ✓ TikTok conectado ao postador. Pode fechar.</h2>".encode())
        def log_message(self, *a): pass

    srv = http.server.HTTPServer(("127.0.0.1", PORTA), H)
    print("URL:", url, flush=True)
    while not codigo:
        srv.handle_request()
    if "error" in codigo or codigo.get("state") != estado:
        sys.exit(f"recusado: {codigo.get('error_description') or codigo.get('error') or 'state diferente'}")
    corpo = urllib.parse.urlencode({
        "client_key": c["client_key"], "client_secret": c["client_secret"], "code": codigo["code"],
        "grant_type": "authorization_code", "redirect_uri": REDIRECT, "code_verifier": verifier}).encode()
    req = urllib.request.Request("https://open.tiktokapis.com/v2/oauth/token/", data=corpo,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, context=postador.SSL_CTX) as r:
        tok = json.loads(r.read())
    if "access_token" not in tok:
        sys.exit(f"sem token: {tok}")
    for k, v in (("tt_client_key", c["client_key"]), ("tt_client_secret", c["client_secret"]),
                 ("tt_refresh_token", tok["refresh_token"]), ("tt_access_token", tok["access_token"]),
                 ("tt_access_expira", str(int(time.time() * 1000) + int(tok.get("expires_in", 86400)) * 1000))):
        postador.chamar({"acao": "config", "chave": k, "valor": v})
    # confere a conta e o que ela permite postar
    req = urllib.request.Request("https://open.tiktokapis.com/v2/post/publish/creator_info/query/", data=b"{}",
                                 headers={"Authorization": f"Bearer {tok['access_token']}",
                                          "Content-Type": "application/json; charset=UTF-8"})
    with urllib.request.urlopen(req, context=postador.SSL_CTX) as r:
        info = json.loads(r.read()).get("data", {})
    print("✓ conectado:", info.get("creator_username"), "| privacidade permitida:", info.get("privacy_level_options"),
          "| escopos:", tok.get("scope"))


if __name__ == "__main__":
    {"receber": receber, "login": login}[sys.argv[1]]()
