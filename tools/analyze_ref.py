"""Analise de video de REFERENCIA (link IG/TikTok/YT ou arquivo) -> numeros + quadros pra eu ler.
Junta o prompt 1 do Matheus Gobbi (ritmo, layout, visual, movimento, audio) com a "lupa do gancho"
do claude-watch (0-10s quadro a quadro x o que e falado).
Uso: python analyze_ref.py <url|arquivo> [--scene 0.10] [--no-transcribe] [--out DIR]
- O video NAO fica salvo no PC do Matteo: baixa em pasta temporaria (ou --out na scratchpad).
- Transcricao: ElevenLabs Scribe (helper do video-use) -> palavras/min e falas do gancho.
Saida em DIR: report.md, hook_0-3s.jpg (4fps), hook_3-10s.jpg (2fps), shots.jpg (1 quadro por corte)."""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path("/Users/mac-matteo/marketing machine")
YTDLP = str(Path.home() / ".local/bin/yt-dlp")
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
src = sys.argv[1]
thr = float(arg("--scene", "0.10"))
out = Path(arg("--out") or tempfile.mkdtemp(prefix="ref_"))
out.mkdir(parents=True, exist_ok=True)


def ff(*a):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *a], capture_output=True, text=True).stderr


if re.match(r"https?://", src):
    subprocess.run([YTDLP, "-q", "-f", "mp4/bestvideo*+bestaudio/best", "--merge-output-format", "mp4",
                    "-o", str(out / "ref.%(ext)s"), src], check=True)
    video = next(out.glob("ref.*"))
else:
    video = Path(src)

meta = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "stream=width,height,r_frame_rate:format=duration", "-select_streams", "v:0",
                                  "-of", "json", str(video)], capture_output=True, text=True).stdout)
w, h = meta["streams"][0]["width"], meta["streams"][0]["height"]
dur = float(meta["format"]["duration"])

# ritmo: cortes por mudanca de cena (jump cut de talking head da score baixo -> threshold baixo)
e = ff("-i", str(video), "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-")
cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", e)]
shots = [b - a for a, b in zip([0.0] + cuts, cuts + [dur])]

e = ff("-i", str(video), "-af", "ebur128", "-f", "null", "-")
lufs = re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)

stamp = f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=10:y=10:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.6"
ff("-y", "-t", "3", "-i", str(video), "-vf", f"fps=4,{stamp},scale=300:-2,tile=6x2", "-frames:v", "1", str(out / "hook_0-3s.jpg"))
ff("-y", "-ss", "3", "-t", "7", "-i", str(video), "-vf", f"fps=2,setpts=PTS+3/TB,{stamp},scale=300:-2,tile=7x2",
   "-frames:v", "1", str(out / "hook_3-10s.jpg"))
ff("-y", "-i", str(video), "-vf", f"select='eq(n,0)+gt(scene,{thr})',{stamp},scale=240:-2,tile=8x5",
   "-vsync", "vfr", "-frames:v", "1", str(out / "shots.jpg"))

words, wpm, hook_words = [], None, ""
if "--no-transcribe" not in sys.argv:
    py = str(ROOT / "video-use/.venv/bin/python")
    subprocess.run([py, str(ROOT / "video-use/helpers/transcribe.py"), str(video), "--edit-dir", str(out)],
                   capture_output=True, text=True)
    tj = next((out / "transcripts").glob("*.json"), None)
    if tj:
        words = [x for x in json.loads(tj.read_text())["words"] if x.get("type") == "word"]
        wpm = round(len(words) / (dur / 60))
        hook_words = " ".join(f"{x['text']}@{x['start']:.1f}" for x in words if x["start"] < 10)

md = [f"# Referencia: {src}", "",
      f"- Formato: {w}x{h} | {dur:.1f}s",
      f"- Cortes detectados (scene>{thr}): {len(cuts)} -> {len(cuts) / (dur / 60):.1f} cortes/min | plano medio {sum(shots) / len(shots):.2f}s",
      f"- Tempos dos cortes: {[round(c, 2) for c in cuts][:60]}",
      f"- Loudness: {lufs[-1] if lufs else '?'} LUFS integrado",
      f"- Palavras/min: {wpm if wpm else '(sem transcricao)'}",
      f"- Fala 0-10s (palavra@seg): {hook_words or '-'}", "",
      "## Imagens", "- hook_0-3s.jpg (4fps) e hook_3-10s.jpg (2fps): lupa do gancho",
      "- shots.jpg: 1 quadro por corte (layout, tipografia, graficos)", "",
      "## Pra eu preencher olhando as imagens (prompt Gobbi + lupa claude-watch)",
      "1. Ritmo: cortes/min, palavras/min, pausas removidas?",
      "2. Layout: camera, graficos, legenda; quando vai pra tela cheia",
      "3. Visual: tipografia, cores, estilo dos graficos",
      "4. Movimento: entradas/saidas, transicoes",
      "5. Audio: LUFS, musica, SFX",
      "6. Gancho quadro a quadro: o que muda na tela x o que e falado; tipo (pergunta, contrario, in-medias-res, demo primeiro, lista, promessa)",
      "7. O que eu reproduzo com o nosso pipeline x o que depende do Matteo (gravar, asset)"]
(out / "report.md").write_text("\n".join(md))
print(out); print("\n".join(md[:9]))
