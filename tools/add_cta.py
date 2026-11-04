"""Anexa o CTA PADRÃO (gravado 1x, guardado em assets/cta/) ao final de um vídeo single-source.

Uso: python add_cta.py <proj> '<main_kills_json>'
  - <proj>/src.mov  e  <proj>/edit/transcripts/src.json  já devem existir
    (vídeo principal normalizado com -r 30 e transcrito).
  - <main_kills_json> (opcional) = kills do vídeo PRINCIPAL, ex '[[12.0,12.6]]'.

Junta [src + cta_padrao] pelo pipeline multi (corte de silêncio + legenda + sync travado).
Legenda: FontSize 10 se vertical (2160x3840), 15 se horizontal. Saída em <proj>/edit/final_sync.mp4.
"""
import json, subprocess, sys, shutil
from pathlib import Path

ROOT = Path("/Users/mac-matteo/marketing machine")
TOOLS = ROOT / "tools"
proj = ROOT / sys.argv[1]
main_kills = sys.argv[2] if len(sys.argv) > 2 else "[]"
EDIT = proj / "edit"
CTA_MOV = ROOT / "assets/cta/cta_padrao.mov"
CTA_TR = ROOT / "assets/cta/cta_padrao.json"

assert (proj / "src.mov").exists(), "falta <proj>/src.mov"
assert (EDIT / "transcripts/src.json").exists(), "falta <proj>/edit/transcripts/src.json"

# 1) copia o CTA pro projeto (fonte + transcript)
shutil.copy(CTA_MOV, proj / "cta_padrao.mov")
(EDIT / "transcripts").mkdir(parents=True, exist_ok=True)
shutil.copy(CTA_TR, EDIT / "transcripts/cta_padrao.json")

# 2) detecta orientação pelo frame decodificado (respeita rotação do iPhone)
subprocess.run(["ffmpeg", "-y", "-ss", "1", "-i", str(proj / "src.mov"),
                "-frames:v", "1", "/tmp/_cta_dims.png"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
dims = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                       "-show_entries", "stream=width,height", "-of", "csv=p=0",
                       "/tmp/_cta_dims.png"], capture_output=True, text=True).stdout
w, h = [int(x) for x in dims.strip().split(",")[:2]]
vertical = h > w
font = 10 if vertical else 15
marginv = 45 if vertical else 60
STYLE = (f"FontName=Helvetica,FontSize={font},Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         f"OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV={marginv}")

# 3) build multi [principal + cta]
parts = json.dumps([{"name": "src", "kills": json.loads(main_kills)},
                    {"name": "cta_padrao", "kills": []}])
subprocess.run(["python3", str(TOOLS / "multi_build.py"), sys.argv[1], parts], check=True)

# 4) aplica o estilo certo e renderiza
edl = json.loads((EDIT / "edl.json").read_text())
edl["subtitle_style"] = STYLE
(EDIT / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
subprocess.run(["python3", str(TOOLS / "clean_srt_multi.py"), sys.argv[1]], check=True)
subprocess.run(["python3", str(TOOLS / "resync_multi.py"), sys.argv[1]], check=True)
print(f"OK: {'vertical' if vertical else 'horizontal'} font={font} -> {EDIT/'final_sync.mp4'}")
