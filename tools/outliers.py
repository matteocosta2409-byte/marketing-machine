#!/usr/bin/env python3
"""Buscador de outliers: acha os videos que estouraram em relacao a mediana da PROPRIA conta.

Uso:
  python3 tools/outliers.py scan [--grupo vestibular] [--plat yt,yts,tt,ig] [--dias 180] [--min 3] [--fresco]
  python3 tools/outliers.py descobrir "como passar em medicina" ["outro termo"] [--add vestibular]
  python3 tools/outliers.py add yt UCxxxx|@handle --grupo vestibular [--nome "Fulano"]
  python3 tools/outliers.py add tt handle --grupo vestibular
  python3 tools/outliers.py contas

Saida: outliers/relatorio.html (abre sozinho com --abrir) e outliers/outliers.json (eu leio pra propor titulos).

Fontes:
  yt / yts  videos longos e Shorts de qualquer canal, via yt-dlp, sem login. Baselines separados.
  tt        qualquer perfil publico do TikTok, via yt-dlp. O yt-dlp falha em alguns perfis.
  ig        SO o @matteo.rocha_, das metricas oficiais que o postador ja guarda no Supabase.
            A API oficial do IG nao le contas de terceiros com o login que usamos.

Score = views / mediana de views da conta na janela. Mediana, nao media: um viral nao infla a regua.
Video com menos de --idade-min dias sai da regua e da lista (ainda nao acumulou views).
"""
import argparse, json, re, ssl, statistics, subprocess, sys, threading, time, urllib.request, webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "outliers"
CACHE = DIR / "cache"
CONTAS = DIR / "contas.json"
YTDLP = str(Path.home() / ".local/bin/yt-dlp")
SSL_CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
AGORA = datetime.now(timezone.utc)
MIN_VIDEOS = 8  # com menos que isso a mediana nao diz nada
MIN_VIDEOS_EU = 4  # canal dele ainda e pequeno: regua fraca, mas e a que existe
TRAVA = threading.Lock()


def ler_contas():
    return json.loads(CONTAS.read_text()) if CONTAS.exists() else []


def salvar_contas(c):
    DIR.mkdir(exist_ok=True)
    CONTAS.write_text(json.dumps(c, ensure_ascii=False, indent=1))


def _ytdlp(args, timeout=240):
    p = subprocess.run([YTDLP, "--no-warnings", "--ignore-errors", *args],
                       capture_output=True, text=True, timeout=timeout)
    itens = []
    for linha in p.stdout.splitlines():
        try:
            itens.append(json.loads(linha))
        except ValueError:
            pass
    return itens, p.stderr.strip()


def _url_yt(conta, aba):
    h = conta["id"]
    base = f"https://www.youtube.com/channel/{h}" if h.startswith("UC") else f"https://www.youtube.com/{h}"
    return f"{base}/{aba}"


def buscar_yt(conta, aba, limite):
    # Views e datas SEMPRE do pedido em ingles: em pt o yt-dlp le "54 mil visualizacoes" como 54.
    # O YouTube traduz titulos conforme o idioma, entao os titulos originais vem de um 2o pedido em pt.
    base = ["--flat-playlist", "-j", "--playlist-end", str(limite)]
    itens, erro = _ytdlp([*base, "--extractor-args", "youtubetab:approximate_date", _url_yt(conta, aba)])
    em_pt, _ = _ytdlp([*base, "--extractor-args", "youtube:lang=pt", _url_yt(conta, aba)])
    titulo_pt = {v["id"]: v.get("title") for v in em_pt}
    out = []
    for v in itens:
        if v.get("view_count") is None:  # estreia agendada / live
            continue
        d = v.get("upload_date")
        out.append({"id": v["id"], "titulo": titulo_pt.get(v["id"]) or v.get("title") or "", "views": v["view_count"],
                    "data": f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else None,
                    "duracao": v.get("duration"),
                    "url": f"https://youtu.be/{v['id']}" if aba == "videos" else f"https://www.youtube.com/shorts/{v['id']}",
                    "thumb": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"})
    return out, ("" if out else erro[:200])


def buscar_tt(conta, limite):
    url = f"https://www.tiktok.com/@{conta['id']}"
    itens, erro = _ytdlp(["--skip-download", "-j", "--playlist-end", str(limite), url])
    if not itens:  # o yt-dlp falha de forma intermitente em perfis do TikTok
        time.sleep(8)
        itens, erro = _ytdlp(["--skip-download", "-j", "--playlist-end", str(limite), url])
    out = []
    for v in itens:
        if v.get("view_count") is None:
            continue
        ts = v.get("timestamp")
        out.append({"id": str(v["id"]), "titulo": (v.get("title") or v.get("description") or "")[:200],
                    "views": v["view_count"], "curtidas": v.get("like_count"),
                    "data": datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else None,
                    "duracao": v.get("duration"), "url": v.get("webpage_url"), "thumb": v.get("thumbnail")})
    return out, ("" if out else erro[:200])


def buscar_ig_proprio():
    """Metricas oficiais do @matteo.rocha_ guardadas pelo postador. So le."""
    env = {}
    for linha in (ROOT / "postador/.env").read_text().splitlines():
        if "=" in linha and not linha.startswith("#"):
            k, v = linha.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    req = urllib.request.Request(env["SUPABASE_URL"].rstrip("/") + "/functions/v1/postador",
                                 data=json.dumps({"acao": "historico", "de": "2000-01-01T00:00:00Z",
                                                  "ate": AGORA.isoformat()}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-postador-token": env["POSTADOR_TOKEN"]})
    with urllib.request.urlopen(req, timeout=120, context=SSL_CTX) as r:
        dados = json.loads(r.read())
    out = []
    for post in dados.get("posts") or []:
        for p in post.get("publicacoes") or []:
            views = (p.get("metricas") or {}).get("views")
            if p.get("destino") != "ig_normal" or views is None:
                continue
            out.append({"id": p.get("permalink") or str(p.get("id")), "titulo": (post.get("titulo") or "")[:200],
                        "views": views, "curtidas": p["metricas"].get("likes"), "tipo": post.get("tipo"),
                        "data": (p.get("publicado_em") or p.get("publicar_em") or "")[:10] or None,
                        "url": p.get("permalink"), "thumb": None})
    return out, ("" if out else "historico sem Reels normais com metricas")


def buscar(conta, plat, limite, fresco):
    chave = re.sub(r"\W+", "_", f"{plat}_{conta['id']}")
    arq = CACHE / f"{chave}.json"
    if not fresco and arq.exists() and time.time() - arq.stat().st_mtime < 20 * 3600:
        return json.loads(arq.read_text()), ""
    if plat == "yt":
        v, e = buscar_yt(conta, "videos", limite)
    elif plat == "yts":
        v, e = buscar_yt(conta, "shorts", limite)
    elif plat == "tt":
        v, e = buscar_tt(conta, limite)
    else:
        v, e = buscar_ig_proprio()
    if v:
        CACHE.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(v, ensure_ascii=False))
    return v, e


def data_real_short(vid):
    """A aba de Shorts nao traz data. Busca so nos candidatos a outlier, com cache."""
    arq = CACHE / "datas_shorts.json"
    with TRAVA:
        datas = json.loads(arq.read_text()) if arq.exists() else {}
    if vid in datas:
        return datas[vid]
    p = subprocess.run([YTDLP, "--no-warnings", "--skip-download", "--print", "%(upload_date)s",
                        f"https://www.youtube.com/shorts/{vid}"], capture_output=True, text=True, timeout=90)
    d = p.stdout.strip()
    d = f"{d[:4]}-{d[4:6]}-{d[6:]}" if re.fullmatch(r"\d{8}", d) else None
    if d:
        with TRAVA:
            datas = json.loads(arq.read_text()) if arq.exists() else {}
            datas[vid] = d
            CACHE.mkdir(parents=True, exist_ok=True)
            arq.write_text(json.dumps(datas))
    return d


def pontuar(videos, dias, idade_min, min_videos=MIN_VIDEOS):
    """Devolve (mediana, videos pontuados). Sem data (Shorts) o video fica na regua e entra na lista."""
    corte, novo = (AGORA - timedelta(days=dias)).strftime("%Y-%m-%d"), (AGORA - timedelta(days=idade_min)).strftime("%Y-%m-%d")
    janela = [v for v in videos if not v.get("data") or corte <= v["data"] <= novo]
    if len(janela) < min_videos:
        return None, []
    med = statistics.median(v["views"] for v in janela)
    if med <= 0:
        return None, []
    return med, [{**v, "score": round(v["views"] / med, 1)} for v in janela]


def cmd_scan(a):
    plats = a.plat.split(",")
    contas = [c for c in ler_contas() if not a.grupo or c["grupo"] == a.grupo]
    tarefas = [(c, p) for c in contas for p in c["plats"] if p in plats]
    if not tarefas:
        sys.exit("Nenhuma conta nesse filtro. Veja: python3 tools/outliers.py contas")

    def rodar(t):
        c, p = t
        try:
            return c, p, *buscar(c, p, a.limite, a.fresco)
        except Exception as e:
            return c, p, [], str(e)[:200]

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(rodar, tarefas))

    achados, resumo = [], []
    for c, p, videos, erro in res:
        eu = c["grupo"] == "eu"  # canal dele tem poucos videos: a regua usa todo o historico
        med, pont = pontuar(videos, 36500 if eu else a.dias, a.idade_min, MIN_VIDEOS_EU if eu else MIN_VIDEOS)
        nome = c.get("nome") or c["id"]
        if med is None:
            motivo = erro or f"so {len(videos)} videos no total, poucos na janela"
            resumo.append({"conta": nome, "plat": p, "grupo": c["grupo"], "status": "sem regua", "motivo": motivo})
            continue
        # conta dele entra sem piso: um estouro pequeno dele ainda ensina
        piso = 0 if c["grupo"] == "eu" else a.min_views
        top = [v for v in pont if v["score"] >= a.min and v["views"] >= piso]
        resumo.append({"conta": nome, "plat": p, "grupo": c["grupo"], "status": "ok", "videos": len(pont),
                       "mediana": int(med), "outliers": len(top)})
        for v in top:
            achados.append({**v, "conta": nome, "plat": p, "grupo": c["grupo"], "mediana": int(med)})
    # Shorts vem sem data: confere a data real dos candidatos e tira os fora da janela
    sem_data = [v for v in achados if v["plat"] == "yts" and not v.get("data")]
    with ThreadPoolExecutor(4) as ex:
        for v, d in zip(sem_data, ex.map(lambda v: data_real_short(v["id"]), sem_data)):
            v["data"] = d
    corte = (AGORA - timedelta(days=a.dias)).strftime("%Y-%m-%d")
    fora = [v for v in sem_data if v["data"] and v["data"] < corte]
    achados = [v for v in achados if v not in fora]
    for r in resumo:
        if r["status"] == "ok":
            r["outliers"] -= sum(v["conta"] == r["conta"] and v["plat"] == r["plat"] for v in fora)
    if a.busca:
        achados = [v for v in achados if re.search(a.busca, v["titulo"], re.I)]
    achados.sort(key=lambda v: -v["score"])

    DIR.mkdir(exist_ok=True)
    (DIR / "outliers.json").write_text(json.dumps(
        {"gerado_em": AGORA.isoformat(), "params": {"dias": a.dias, "min": a.min, "min_views": a.min_views},
         "contas": resumo, "outliers": achados}, ensure_ascii=False, indent=1))
    (DIR / "relatorio.html").write_text(html(achados, resumo, a))

    ok = sum(r["status"] == "ok" for r in resumo)
    print(f"{ok}/{len(resumo)} fontes lidas, {len(achados)} outliers (>= {a.min}x, ultimos {a.dias} dias)\n")
    for r in resumo:
        if r["status"] != "ok":
            print(f"  ! {r['plat']:3} {r['conta']}: {r['motivo']}")
    print()
    for rotulo, lista in (("REFERENCIAS", [v for v in achados if v["grupo"] != "eu"]),
                          ("SEUS", [v for v in achados if v["grupo"] == "eu"])):
        print(rotulo)
        for v in lista[:a.top]:
            print(f"{v['score']:>7}x {v['views']:>10,}  {v['plat']:3} {v['conta'][:22]:22} {v['titulo'][:70]}")
        print()
    print(f"\nRelatorio: {DIR / 'relatorio.html'}")
    if a.abrir:
        webbrowser.open((DIR / "relatorio.html").as_uri())


def n_curto(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.1f}k" if n >= 1e3 else str(int(n))


def html(achados, resumo, a):
    rotulo = {"yt": "YouTube", "yts": "Shorts", "tt": "TikTok", "ig": "Instagram"}
    grupos = sorted({v["grupo"] for v in achados})
    plats = sorted({v["plat"] for v in achados})
    cards = []
    for v in achados:
        img = f'<img src="{escape(v["thumb"], quote=True)}" loading="lazy" alt="" referrerpolicy="no-referrer">' if v.get("thumb") else '<div class="sem">sem capa</div>'
        cards.append(
            f'<a class="c" data-g="{escape(v["grupo"], quote=True)}" data-p="{v["plat"]}" href="{escape(v.get("url") or "#", quote=True)}" target="_blank" rel="noreferrer">'
            f'<div class="t {v["plat"]}">{img}<b>{v["score"]:g}x</b></div>'
            f'<h3>{escape(v["titulo"] or "(sem titulo)")}</h3>'
            f'<p>{escape(v["conta"])} · {rotulo[v["plat"]]}</p>'
            f'<p>{n_curto(v["views"])} views · mediana {n_curto(v["mediana"])}{" · " + v["data"] if v.get("data") else ""}</p></a>')
    botoes = "".join(f'<button data-f="g:{escape(g, quote=True)}">{escape(g)}</button>' for g in grupos) + \
        "".join(f'<button data-f="p:{p}">{rotulo[p]}</button>' for p in plats)
    falhas = [r for r in resumo if r["status"] != "ok"]
    aviso = "" if not falhas else "<details><summary>" + f"{len(falhas)} fontes sem leitura</summary><ul>" + \
        "".join(f"<li>{escape(r['conta'])} ({rotulo[r['plat']]}): {escape(r['motivo'])}</li>" for r in falhas) + "</ul></details>"
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outliers</title><style>
:root{{--bg:#fff;--tx:#111;--mut:#666;--ln:#e4e4e4;--ac:#0a7a3d}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111;--tx:#eee;--mut:#999;--ln:#2a2a2a;--ac:#2be86b}}}}
*{{box-sizing:border-box}}body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--tx);font:15px/1.4 -apple-system,system-ui,sans-serif}}
h1{{margin:0 0 4px;font-size:24px}}.m{{color:var(--mut);margin:0 0 16px}}
.f{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px}}button{{font:inherit;padding:5px 12px;border:1px solid var(--ln);border-radius:99px;background:none;color:var(--tx);cursor:pointer}}button.on{{background:var(--tx);color:var(--bg)}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:20px 14px}}
.c{{color:inherit;text-decoration:none;min-width:0}}.t{{position:relative;aspect-ratio:16/9;background:var(--ln);border-radius:8px;overflow:hidden}}
.t img{{width:100%;height:100%;object-fit:cover;display:block}}.t b{{position:absolute;top:6px;left:6px;background:var(--ac);color:#000;padding:1px 7px;border-radius:5px;font-size:14px}}
.sem{{height:100%;display:grid;place-items:center;color:var(--mut)}}
h3{{font-size:14px;margin:8px 0 2px;line-height:1.3}}.c p{{margin:0;font-size:12.5px;color:var(--mut)}}details{{margin-bottom:18px;color:var(--mut)}}.vz{{display:none}}
</style><h1>Outliers</h1><p class="m">{len(achados)} vídeos com {a.min:g}x ou mais a mediana da própria conta · últimos {a.dias} dias · {AGORA.strftime('%d/%m/%Y')}</p>
{aviso}<div class="f"><button class="on" data-f="">Referências</button>{botoes}</div><div class="g">{''.join(cards)}</div>
<script>const bs=[...document.querySelectorAll('button')],cs=[...document.querySelectorAll('.c')];
bs.forEach(b=>b.onclick=()=>{{bs.forEach(x=>x.classList.toggle('on',x===b));const f=b.dataset.f;
cs.forEach(c=>{{const ok=!f?c.dataset.g!=='eu':(f[0]==='g'?c.dataset.g===f.slice(2):c.dataset.p===f.slice(2));c.classList.toggle('vz',!ok)}})}});bs[0].click()</script></html>"""


def cmd_descobrir(a):
    conhecidos = {c["id"] for c in ler_contas()}
    cont, nomes = {}, {}
    for termo in a.termos:
        itens, _ = _ytdlp(["--flat-playlist", "-j", f"ytsearch40:{termo}"])
        for v in itens:
            cid = v.get("channel_id")
            if cid:
                cont[cid] = cont.get(cid, 0) + 1
                nomes[cid] = v.get("channel") or cid
    rank = sorted(cont, key=lambda c: -cont[c])
    for cid in rank[:a.top]:
        print(f"{cont[cid]:>3}  {nomes[cid][:40]:40} {cid}{'  (ja na lista)' if cid in conhecidos else ''}")
    if a.add:
        contas = ler_contas()
        novos = [c for c in rank[:a.top] if c not in conhecidos]
        contas += [{"id": c, "nome": nomes[c], "grupo": a.add, "plats": ["yt", "yts"]} for c in novos]
        salvar_contas(contas)
        print(f"\n{len(novos)} canais adicionados em '{a.add}'")


def cmd_add(a):
    contas = ler_contas()
    cid = a.id.lstrip("@") if a.plat == "tt" else a.id
    plats = ["tt"] if a.plat == "tt" else ["yt", "yts"]
    for c in contas:
        if c["id"] == cid:
            c["plats"] = sorted(set(c["plats"]) | set(plats))
            break
    else:
        contas.append({"id": cid, "nome": a.nome or cid, "grupo": a.grupo, "plats": plats})
    salvar_contas(contas)
    print(f"ok: {cid} em '{a.grupo}'")


def cmd_contas(_):
    for c in sorted(ler_contas(), key=lambda c: c["grupo"]):
        print(f"{c['grupo']:12} {','.join(c['plats']):10} {c.get('nome') or c['id']}")


def main():
    ap = argparse.ArgumentParser(description="Buscador de outliers")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--grupo")
    s.add_argument("--plat", default="yt,yts,tt,ig")
    s.add_argument("--dias", type=int, default=180)
    s.add_argument("--min", type=float, default=3, help="score minimo (x a mediana)")
    s.add_argument("--min-views", type=int, default=2000, help="piso de views pra contas de terceiros")
    s.add_argument("--idade-min", type=int, default=3)
    s.add_argument("--limite", type=int, default=60, help="videos mais recentes lidos por conta")
    s.add_argument("--top", type=int, default=40)
    s.add_argument("--fresco", action="store_true", help="ignora o cache de 20h")
    s.add_argument("--busca", help="regex no titulo, ex: 'enem|medicina'")
    s.add_argument("--abrir", action="store_true")
    s.set_defaults(fn=cmd_scan)
    d = sub.add_parser("descobrir")
    d.add_argument("termos", nargs="+")
    d.add_argument("--top", type=int, default=25)
    d.add_argument("--add", metavar="GRUPO")
    d.set_defaults(fn=cmd_descobrir)
    n = sub.add_parser("add")
    n.add_argument("plat", choices=["yt", "tt"])
    n.add_argument("id")
    n.add_argument("--grupo", required=True)
    n.add_argument("--nome")
    n.set_defaults(fn=cmd_add)
    sub.add_parser("contas").set_defaults(fn=cmd_contas)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
