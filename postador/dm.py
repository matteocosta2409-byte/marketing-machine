"""DM automática — "comenta a palavra que eu te mando o link na DM".

Mora no Supabase (função "dm-chat" + cron de minuto em minuto): funciona com o Mac desligado.
Só responde comentários feitos DEPOIS de a automação ser criada (e até 7 dias, regra da Meta).

Uso:
  python3 dm.py criar --palavra QA --link "https://youtu.be/..." \
      --mensagem "Aqui está o vídeo completo do Q&A 👇" [--botao "Assistir"] [--post <media_id>] \
      [--publica "..." (repete)] [--sem-publica]
  python3 dm.py lista                    # regras + quantas DMs cada uma já mandou
  python3 dm.py log [-n 30]              # últimos comentários vistos (enviado / ignorado / erro)
  python3 dm.py pausar <id> | ligar <id>
  python3 dm.py editar <id> [--link ...] [--mensagem ...] [--palavra ...] [--botao ...]
                    [--publica "..." (repete) | --sem-publica]
  python3 dm.py varrer                   # força uma rodada agora (não espera o cron)

--palavra pode repetir (qualquer uma vale). Casa sem acento/maiúscula e como palavra inteira:
"qa", "QA!", "Q.A"... sim; "qualquer" não.
"""
import argparse, json, sys

from postador import ENV, SSL_CTX
import urllib.request, urllib.error

FUNCAO = ENV.get("SUPABASE_URL", "").rstrip("/") + "/functions/v1/dm-chat"
PUBLICAS_PADRAO = ["Te mandei na DM! me avisa se já chegou!"]


def chamar(corpo: dict):
    req = urllib.request.Request(FUNCAO, data=json.dumps(corpo).encode(), method="POST", headers={
        "Content-Type": "application/json", "x-postador-token": ENV.get("POSTADOR_TOKEN", "")})
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"dm-chat: {e.read().decode()}")


def mostrar_lista():
    for a in chamar({"acao": "lista"}):
        estado = "LIGADA " if a["ativo"] else "pausada"
        posts = ", ".join(a["post_ids"]) or "qualquer post"
        print(f"[{estado}] {a['nome']}  ({a['id']})")
        print(f"   palavras: {', '.join(a['palavras'])}  ·  {posts}")
        print(f"   link: {a['link']}  ·  botão: {a['botao_texto']}")
        print(f"   DMs enviadas: {a['enviados']}  ·  erros: {a['erros']}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    cr = sub.add_parser("criar")
    cr.add_argument("--palavra", action="append", required=True)
    cr.add_argument("--link", required=True)
    cr.add_argument("--mensagem", required=True)
    cr.add_argument("--botao", default="Assistir")
    cr.add_argument("--nome")
    cr.add_argument("--post", action="append", default=[])
    cr.add_argument("--publica", action="append")
    cr.add_argument("--sem-publica", action="store_true")

    ed = sub.add_parser("editar")
    ed.add_argument("id")
    ed.add_argument("--palavra", action="append")
    ed.add_argument("--link")
    ed.add_argument("--mensagem")
    ed.add_argument("--botao")
    ed.add_argument("--post", action="append")
    ed.add_argument("--publica", action="append")
    ed.add_argument("--sem-publica", action="store_true")

    for nome in ("pausar", "ligar"):
        sub.add_parser(nome).add_argument("id")
    sub.add_parser("lista")
    sub.add_parser("varrer")
    lg = sub.add_parser("log")
    lg.add_argument("-n", type=int, default=30)

    a = ap.parse_args()
    if a.cmd == "criar":
        if len(a.mensagem) > 640 or len(a.botao) > 20:
            sys.exit("mensagem tem limite de 640 caracteres e o botão, de 20 (regra da Meta)")
        r = chamar({"acao": "criar", "nome": a.nome or " / ".join(a.palavra), "palavras": a.palavra,
                    "link": a.link, "mensagem": a.mensagem, "botao_texto": a.botao, "post_ids": a.post,
                    "respostas_publicas": [] if a.sem_publica else (a.publica or PUBLICAS_PADRAO)})
        print(f"criada: {r['id']} — já está valendo (o cron confere os comentários a cada minuto)")
    elif a.cmd == "editar":
        campos = {"palavras": a.palavra, "link": a.link,
                  "mensagem": a.mensagem, "botao_texto": a.botao, "post_ids": a.post,
                  "respostas_publicas": [] if a.sem_publica else a.publica}
        r = chamar({"acao": "editar", "id": a.id, **{k: v for k, v in campos.items() if v is not None}})
        print(f"editada: {r['nome']}")
    elif a.cmd in ("pausar", "ligar"):
        r = chamar({"acao": "editar", "id": a.id, "ativo": a.cmd == "ligar"})
        print(f"{r['nome']}: {'ligada' if r['ativo'] else 'pausada'}")
    elif a.cmd == "lista":
        mostrar_lista()
    elif a.cmd == "varrer":
        print(json.dumps(chamar({"acao": "varrer"}), ensure_ascii=False))
    elif a.cmd == "log":
        for c in chamar({"acao": "log", "limite": a.n}):
            extra = f" — {c['erro']}" if c.get("erro") else ""
            print(f"{(c['comentado_em'] or '')[:16]}  {c['status']:8}  @{c['username']}: {c['texto']}{extra}")


if __name__ == "__main__":
    main()
