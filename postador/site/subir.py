"""Sobe um arquivo no bucket público "site": python3 site/subir.py <arquivo> <caminho/no/bucket>"""
import json, mimetypes, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import postador
arq, destino = Path(sys.argv[1]), sys.argv[2]
req = urllib.request.Request(postador.ENV["SUPABASE_URL"] + "/functions/v1/site-upload", method="POST",
    data=json.dumps({"caminho": destino}).encode(),
    headers={"Content-Type": "application/json", "x-postador-token": postador.ENV["POSTADOR_TOKEN"]})
url = json.loads(urllib.request.urlopen(req, context=postador.SSL_CTX).read())["url"]
tipo = mimetypes.guess_type(arq.name)[0] or "text/plain"
put = urllib.request.Request(url, data=arq.read_bytes(), method="PUT", headers={"Content-Type": tipo, "x-upsert": "true"})
urllib.request.urlopen(put, context=postador.SSL_CTX).read()
print(postador.ENV["SUPABASE_URL"] + "/storage/v1/object/public/site/" + destino)
