"""Posta um vídeo (inclusive longo) no TikTok direto do Mac, em pedaços (FILE_UPLOAD chunked).

  python3 tt_postar.py info                                  # conta conectada e limites (não posta)
  python3 tt_postar.py "<video.mp4>" --legenda "..." [--privacidade SELF_ONLY]
  python3 tt_postar.py "<video.mp4>" --rascunho     # manda pra caixa de entrada do app (você publica lá)

Vídeo grande não cabe no bucket de 50 MB, então não passa pela fila: sobe na hora.
App no sandbox / sem auditoria → só SELF_ONLY (privado).
Regras do TikTok: pedaços de 5–64 MB; total = piso(tamanho/pedaço); o último leva o resto.
"""
import argparse, json, sys, time, urllib.request
from pathlib import Path
import postador

API = "https://open.tiktokapis.com/v2"
PEDACO = 20_000_000


def token():
    req = urllib.request.Request(postador.ENV["SUPABASE_URL"] + "/functions/v1/tt-token", data=b"{}", method="POST",
                                 headers={"Content-Type": "application/json", "x-postador-token": postador.ENV["POSTADOR_TOKEN"]})
    with urllib.request.urlopen(req, context=postador.SSL_CTX) as r:
        return json.loads(r.read())["access_token"]


def tiktok(caminho, tok, corpo):
    req = urllib.request.Request(f"{API}/{caminho}", data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"})
    try:
        with urllib.request.urlopen(req, context=postador.SSL_CTX, timeout=60) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        d = json.loads(e.read() or b"{}")
    if d.get("error", {}).get("code") not in (None, "ok"):
        raise SystemExit(f"TikTok: {d['error'].get('code')} — {d['error'].get('message')}")
    return d.get("data", {})


def info(tok):
    i = tiktok("post/publish/creator_info/query/", tok, {})
    print(f"conta: {i.get('creator_username')} ({i.get('creator_nickname')})")
    print(f"duração máxima por post: {i.get('max_video_post_duration_sec')} s")
    print(f"privacidade permitida: {i.get('privacy_level_options')}")
    return i


def postar(video: Path, legenda: str, privacidade: str, rascunho: bool = False):
    tok = token()
    i = info(tok)
    dur, _ = postador.sondar(video)
    if dur > (i.get("max_video_post_duration_sec") or 0):
        raise SystemExit(f"vídeo tem {dur:.0f}s, acima do limite da conta ({i.get('max_video_post_duration_sec')}s)")
    tamanho = video.stat().st_size
    total = max(1, tamanho // PEDACO) if tamanho > 64_000_000 else 1
    pedaco = PEDACO if total > 1 else tamanho
    fonte = {"source": "FILE_UPLOAD", "video_size": tamanho, "chunk_size": pedaco, "total_chunk_count": total}
    if rascunho:
        # Upload (video.upload): vai pra caixa de entrada; a legenda e a privacidade são escolhidas no app.
        ini = tiktok("post/publish/inbox/video/init/", tok, {"source_info": fonte})
    else:
        if privacidade not in (i.get("privacy_level_options") or []):
            raise SystemExit(f"privacidade {privacidade} não permitida: {i.get('privacy_level_options')}")
        ini = tiktok("post/publish/video/init/", tok, {
            "post_info": {"title": legenda[:2200], "privacy_level": privacidade,
                          "disable_comment": False, "disable_duet": False, "disable_stitch": False},
            "source_info": fonte,
        })
    print(f"enviando {tamanho / 1e6:.0f} MB em {total} pedaço(s)…")
    with open(video, "rb") as f:
        for n in range(total):
            ini_b = n * pedaco
            fim_b = tamanho - 1 if n == total - 1 else ini_b + pedaco - 1
            f.seek(ini_b)
            dados = f.read(fim_b - ini_b + 1)
            req = urllib.request.Request(ini["upload_url"], data=dados, method="PUT", headers={
                "Content-Type": "video/mp4", "Content-Length": str(len(dados)),
                "Content-Range": f"bytes {ini_b}-{fim_b}/{tamanho}"})
            with urllib.request.urlopen(req, context=postador.SSL_CTX, timeout=300) as r:
                r.read()
            print(f"  {n + 1}/{total}", flush=True)
    for _ in range(60):  # até ~10 min processando
        time.sleep(10)
        st = tiktok("post/publish/status/fetch/", tok, {"publish_id": ini["publish_id"]})
        print("  status:", st.get("status"), flush=True)
        if st.get("status") == "SEND_TO_USER_INBOX":
            print("✓ rascunho entregue: abra a notificação no app do TikTok e publique")
            return
        if st.get("status") == "PUBLISH_COMPLETE":
            print("✓ publicado no TikTok", st.get("publicaly_available_post_id") or "(privado: sem link público)")
            return
        if st.get("status") == "FAILED":
            raise SystemExit(f"falhou: {st.get('fail_reason')}")
    print("ainda processando — conferir no app do TikTok")


if __name__ == "__main__":
    if sys.argv[1:] == ["info"]:
        info(token())
        sys.exit()
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--legenda", default="")
    ap.add_argument("--privacidade", default="SELF_ONLY")
    ap.add_argument("--rascunho", action="store_true")
    a = ap.parse_args()
    postar(Path(a.video).expanduser(), a.legenda, a.privacidade, a.rascunho)
