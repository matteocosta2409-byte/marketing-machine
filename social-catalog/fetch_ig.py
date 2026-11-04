"""Puxa TODOS os Reels/posts publicados da conta profissional do Instagram via Graph API
e salva em posted_ig.json (id, legenda, tipo, data, link, thumbnail).

Uso:
  1) preencha social-catalog/.env com IG_ACCESS_TOKEN (e IG_USER_ID se já souber)
  2) python social-catalog/fetch_ig.py

Token: ver README_TOKEN.md (passo a passo). Token de longa duração dura ~60 dias.
"""
import json, os, ssl, sys, urllib.parse, urllib.request
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl.create_default_context()
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Instagram API com Login do Instagram -> graph.instagram.com, token IG direto.
API = os.environ.get("IG_GRAPH_BASE", "https://graph.instagram.com/" + os.environ.get("IG_API_VERSION", "v21.0"))


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


def get(url, params):
    full = f"{url}?{urllib.parse.urlencode(params)}" if params else url
    with urllib.request.urlopen(full, timeout=60, context=SSL_CTX) as r:
        return json.loads(r.read())


def discover_user_id(token):
    # Login do Instagram: o próprio token é da conta IG.
    return str(get(f"{API}/me", {"fields": "user_id", "access_token": token}).get("user_id", ""))


def main():
    env = load_env()
    token = env.get("IG_ACCESS_TOKEN") or os.environ.get("IG_ACCESS_TOKEN", "")
    if not token:
        sys.exit("Falta IG_ACCESS_TOKEN no social-catalog/.env — veja README_TOKEN.md")
    uid = env.get("IG_USER_ID") or os.environ.get("IG_USER_ID", "")
    if not uid:
        print("IG_USER_ID não informado; tentando descobrir pelo token...")
        uid = discover_user_id(token)
        print("  -> IG_USER_ID =", uid)

    fields = "id,caption,media_type,media_product_type,permalink,thumbnail_url,timestamp,like_count,comments_count"
    items, url, params = [], f"{API}/{uid}/media", {"fields": fields, "limit": 100, "access_token": token}
    while True:
        data = get(url, params)
        items += data.get("data", [])
        nxt = data.get("paging", {}).get("next")
        if not nxt:
            break
        url, params = nxt, {}  # 'next' já traz tudo na query
    out = HERE / "posted_ig.json"
    out.write_text(json.dumps({"ig_user_id": uid, "count": len(items), "posts": items},
                              ensure_ascii=False, indent=2))
    print(f"OK: {len(items)} posts -> {out}")


if __name__ == "__main__":
    main()
