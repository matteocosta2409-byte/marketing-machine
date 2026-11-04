# /// script
# requires-python = ">=3.11"
# dependencies = ["opencv-python-headless>=4.10,<5", "numpy", "pillow"]
# ///
"""Clipper estilo OpusClip: video longo -> varios cortes 9:16 prontos pra Reels/Shorts/TikTok.

Fluxo:
  1) uv run tools/clipper.py prep "<video>" <nome>
       -> cortes/<nome>/ com transcricao (Scribe) + transcript.md (frases com timestamp)
  2) Claude le o transcript.md e escreve cortes/<nome>/clips.json (momentos virais)
  3) uv run tools/clipper.py render <nome> [--only 1,3]
       -> cortes/<nome>/out/NN_slug.mp4 (1080x1920, rosto enquadrado, legenda italica padrao) + posts.md
     uv run tools/clipper.py render <nome> --layout tarjas --out out_v2
       -> mesma coisa com o 16:9 inteiro no meio e titulo na tarja de cima (teste A/B)

clips.json = lista de:
  {"id": 1, "start": 12.3, "end": 58.9, "title": "gancho no peito|2a linha (| quebra)",
   "subtitle": "(fiz isso e passei em 1º lugar em Medicina 2x)",
   "score": 90, "why": "...", "caption": "legenda do post",
   "kills": [[20.1, 24.0]],          # trechos (tempo fonte) a remover: retakes/"corta"
   "layout": "crop" | "tarjas"}      # crop = segue o rosto em tela cheia (padrao)
                                     # tarjas = video 16:9 inteiro no meio, legenda embaixo
"""
import argparse, glob, json, re, subprocess, sys, tempfile, unicodedata
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from sdr import sdr_chain, OUT_TAGS, RGBA_709
from pathlib import Path

ROOT = Path("/Users/mac-matteo/marketing machine")
VIDEO_USE = ROOT / "video-use"
FONTS = ROOT / "assets/fonts/clipper"
SF = "/System/Library/Fonts/SFNS.ttf"  # SF Pro (fonte do sistema), titulo no peito
TITLE_BOTTOM = 1500  # base do bloco do titulo no vertical (peito); bloco alto cresce pra cima
MAX_TW = 1000  # largura maxima de cada linha; encolhe a fonte se passar
TITLE_SECS = 4.0  # titulo so nos primeiros segundos
W, H = 1080, 1920
GAP, PAD, KEEP = 0.30, 0.04, 0.06
FIXES = {"matheus": "Matteo", "mateus": "Matteo", "mateu": "Matteo", "akironvest": "ChironVest"}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe_dims(src):
    """Dimensoes de exibicao (ja considerando rotacao do iPhone)."""
    out = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams",
                          "-of", "json", str(src)]).stdout)["streams"][0]
    w, h = out["width"], out["height"]
    rot = 0
    for sd in out.get("side_data_list", []):
        rot = int(sd.get("rotation", rot) or rot)
    rot = rot or int(out.get("tags", {}).get("rotate", 0))
    return (h, w) if abs(rot) % 180 == 90 else (w, h)


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


def load_words(proj):
    data = json.loads(Path(glob.glob(str(proj / "edit/transcripts/*.json"))[0]).read_text())
    return [w for w in data["words"] if w.get("type") == "word" and w.get("start") is not None]


# ---------------------------------------------------------------- prep
def prep(video, name):
    video = Path(video).expanduser().resolve()
    proj = ROOT / "cortes" / name
    (proj / "edit").mkdir(parents=True, exist_ok=True)
    meta = {"src": str(video)}
    (proj / "project.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    if not glob.glob(str(proj / "edit/transcripts/*.json")):
        r = subprocess.run(["uv", "run", "python", "helpers/transcribe.py", str(video),
                            "--edit-dir", str(proj / "edit"), "--language", "pt"], cwd=VIDEO_USE)
        if r.returncode:
            sys.exit("falhou a transcricao")
    words = load_words(proj)
    # frases: quebra em pontuacao final ou pausa longa
    lines, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1]["start"] if i + 1 < len(words) else None
        if re.search(r"[.!?]$", w["text"]) or nxt is None or nxt - w["end"] > 0.8:
            lines.append(f"[{fmt(cur[0]['start'])}–{fmt(cur[-1]['end'])}] "
                         f"({cur[0]['start']:.2f}-{cur[-1]['end']:.2f}) "
                         + " ".join(x["text"] for x in cur))
            cur = []
    dw, dh = probe_dims(video)
    head = (f"# {name}\nfonte: {video}\n{dw}x{dh} | {words[-1]['end'] / 60:.1f} min\n\n"
            "Formato: [mm:ss] (segundos) texto\n\n")
    (proj / "transcript.md").write_text(head + "\n".join(lines) + "\n")
    print(f"OK -> {proj / 'transcript.md'} ({len(lines)} frases)")


# ---------------------------------------------------------------- render helpers
def silences(src, t0, dur):
    err = run(["ffmpeg", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(src), "-vn",
               "-af", "silencedetect=noise=-32dB:d=0.18", "-f", "null", "-"]).stderr
    out, cur = [], None
    for m in re.finditer(r"silence_(start|end):\s*(-?[0-9.]+)", err):
        if m.group(1) == "start":
            cur = float(m.group(2))
        elif cur is not None:
            out.append((t0 + cur, t0 + float(m.group(2)))); cur = None
    return out


def cut_ranges(words, sils, kills):
    """Mesmo metodo do solo_build: buraco entre palavras + silencedetect (ver corte-silencio-metodo)."""
    killed = lambda t: any(a <= t < b for a, b in kills)
    kept = []
    for w in words:
        if killed(w["start"]):
            continue
        end = w["end"]
        for a, b in kills:
            if w["start"] < a < end:
                end = a
        kept.append({"start": w["start"], "end": end})
    segs, s, prev = [], kept[0]["start"] - PAD, kept[0]["end"]
    for w in kept[1:]:
        if w["start"] - prev >= GAP or any(a < w["start"] and b > prev for a, b in kills):
            segs.append([s, prev + PAD]); s = w["start"] - PAD
        prev = max(prev, w["end"])
    segs.append([s, prev + PAD])
    ranges = []
    for a0, b0 in segs:
        for a, b in sils:
            if a - 0.01 <= a0 < b:
                a0 = max(a0, b - KEEP)
            if a < b0 <= b + 0.01:
                b0 = min(b0, a + KEEP)
        c = a0
        for a, b in sorted(sils):
            if a0 < a and b < b0 and (b - a) >= GAP:
                if a + KEEP - c >= 0.12:
                    ranges.append([c, a + KEEP])
                c = b - KEEP
        if b0 - c >= 0.12:
            ranges.append([max(0.0, c), b0])
    return ranges


def face_track(src, t0, dur, dims):
    """Centro X normalizado do maior rosto, amostrado a 3fps -> [(t, x)]."""
    import cv2
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    sw = 480
    sh = int(round(dims[1] * sw / dims[0] / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}",
                          "-i", str(src), "-vf", f"fps=3,scale={sw}:{sh}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True).stdout
    import numpy as np
    n = len(raw) // (sw * sh)
    frames = np.frombuffer(raw[:n * sw * sh], np.uint8).reshape(n, sh, sw)
    pts = []
    for i, f in enumerate(frames):
        faces = cascade.detectMultiScale(f, 1.15, 5, minSize=(sw // 14, sw // 14))
        if len(faces):
            x, y, fw, fh = max(faces, key=lambda r: r[2] * r[3])
            pts.append((t0 + i / 3, (x + fw / 2) / sw))
    return pts


def crop_x_for(ranges, pts, dims):
    """Um enquadramento fixo por range (a camera 'pula' nos cortes, igual OpusClip).
    Zona morta: so reenquadra se o rosto andar > 6% da largura."""
    cw = int(dims[1] * 9 / 16) // 2 * 2
    if cw >= dims[0]:
        return cw, [0] * len(ranges)
    xs, last = [], 0.5
    for a, b in ranges:
        inside = sorted(x for t, x in pts if a - 0.3 <= t <= b + 0.3)
        c = inside[len(inside) // 2] if inside else last
        if abs(c - last) < 0.06 and xs:
            c = last
        last = c
        xs.append(int(min(max(c * dims[0] - cw / 2, 0), dims[0] - cw)) // 2 * 2)
    return cw, xs


def to_out_time(t, ranges):
    acc = 0.0
    for a, b in ranges:
        if a <= t <= b:
            return acc + t - a
        acc += b - a
    return None


def fix_word(txt):
    k = unicodedata.normalize("NFKD", txt.lower()).encode("ascii", "ignore").decode()
    k = re.sub(r"[^a-z]", "", k)
    return re.sub(r"\w+", FIXES[k], txt, count=1) if k in FIXES else txt


def ass_escape(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def build_ass(words, ranges, layout, path):
    # cada palavra vai pro range de maior sobreposicao (sem duplicar em borda de corte)
    out = []
    for w in words:
        best, bo = None, 0.0
        for a, b in ranges:
            o = min(b, w["end"]) - max(a, w["start"])
            if o > bo:
                best, bo = (a, b), o
        if best and bo >= 0.15 * max(w["end"] - w["start"], 0.01):
            s = to_out_time(max(w["start"], best[0]), ranges)
            e = to_out_time(min(w["end"], best[1]), ranges)
            out.append({"t": fix_word(w["text"]), "s": s, "e": e})
    # blocos de 2 palavras, quebrando em pontuacao (igual master.srt dos reels)
    chunks, cur = [], []
    for w in out:
        if cur and (len(cur) == 2 or w["s"] - cur[-1]["e"] > 0.5):
            chunks.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.,!?:;]$", w["t"]):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)

    cap_mv = 540 if layout == "tarjas" else 300  # tarjas: logo abaixo do video
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Helvetica,67,&H00FFFFFF,&H00FFFFFF,&HC8000000,&HC8000000,0,1,0,0,100,100,0,0,1,6.7,6.7,2,60,60,{cap_mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ts = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    ev = []
    for ci, ch in enumerate(chunks):
        end_chunk = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.4
        end_chunk = min(end_chunk, ch[-1]["e"] + 0.6)
        s = ch[0]["s"]
        if end_chunk > s:
            ev.append(f"Dialogue: 0,{ts(s)},{ts(end_chunk)},Cap,,0,0,0,,"
                      + ass_escape(" ".join(x["t"] for x in ch)))
    path.write_text(hdr + "\n".join(ev) + "\n")


def title_png(title, subtitle, path, bottom=None):
    """Titulo + subtitulo em SF Pro branco com sombra suave escura (legivel na camisa branca)."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    def font(size, weight):
        f = ImageFont.truetype(SF, size)
        f.set_variation_by_name(weight)
        return f
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    def fit(t, size, weight):
        f = font(size, weight)
        while d.textlength(t, font=f) > MAX_TW and size > 24:
            size -= 2
            f = font(size, weight)
        return f
    lines = [(t, fit(t, 60, "Semibold"), 255) for t in title.split("|") if t.strip()]
    if subtitle:
        sf = fit(subtitle, 40, "Regular")
        if sf.size < 34:  # longo demais: quebra em 2 linhas no espaco mais perto do meio
            sp = [i for i, ch in enumerate(subtitle) if ch == " "]
            cut = min(sp, key=lambda i: abs(i - len(subtitle) / 2))
            for part in (subtitle[:cut], subtitle[cut + 1:]):
                lines.append((part, fit(part, 38, "Regular"), 240))
        else:
            lines.append((subtitle, sf, 240))
    # bloco ancorado pela base: vertical no peito, tarjas logo acima do video
    y = (bottom or TITLE_BOTTOM) - sum(int(f.size * 1.22) for _, f, _ in lines) - (10 if subtitle else 0)
    n_title = len([t for t in title.split("|") if t.strip()])
    for i, (t, f, a) in enumerate(lines):
        w = d.textlength(t, font=f)
        if i == n_title and subtitle:
            y += 10
        d.text(((W - w) / 2, y), t, font=f, fill=(255, 255, 255, a))
        y += int(f.size * 1.22)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").point(lambda v: min(255, v * 1.1)))
    sh = Image.merge("RGBA", (*[Image.new("L", (W, H), 0)] * 3, sh.getchannel("A")))
    glow = sh.filter(ImageFilter.GaussianBlur(14))
    glow.putalpha(glow.getchannel("A").point(lambda v: min(255, v * 2.2)))
    tight = sh.filter(ImageFilter.GaussianBlur(4)).transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -3))
    out = Image.alpha_composite(Image.alpha_composite(glow, tight), txt)
    out.save(path)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "corte"


def render_clip(proj, src, dims, words_all, clip, outdir="out", clean=None):
    t0, t1 = float(clip["start"]), float(clip["end"])
    kills = clip.get("kills", [])
    layout = clip.get("layout", "crop")
    words = [w for w in words_all if w["start"] >= t0 - 0.05 and w["end"] <= t1 + 0.3]
    sils = silences(clean or src, t0, t1 - t0 + 0.5)  # clean: audio sem musica/SFX, mantem v1 e v2 com os mesmos cortes
    ranges = cut_ranges(words, sils, kills)
    ss = max(0.0, ranges[0][0] - 1.0)  # seek rapido; tempos do grafo ficam relativos a ss
    dur = ranges[-1][1] - ss + 0.5

    vertical = dims[0] < dims[1]
    if vertical:
        vf = lambda i: f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    elif layout == "tarjas":
        vf = lambda i: f"scale={W}:-2,pad={W}:{H}:0:(oh-ih)/2:black"
    else:
        pts = face_track(src, ss, dur, dims)
        cw, xs = crop_x_for(ranges, pts, dims)
        vf = lambda i: f"crop={cw}:{dims[1]}:{xs[i]}:0,scale={W}:{H}"

    tag = f"{int(clip['id']):02d}_{slug(clip.get('title', '').replace('|', ' ') or clip.get('caption', ''))}"
    work = proj / "edit" / (tag + ("" if outdir == "out" else "_" + outdir))
    work.mkdir(parents=True, exist_ok=True)
    ass = work / "caps.ass"
    build_ass(words, ranges, layout, ass)
    title = clip.get("title", "")
    if title:
        vid_top = (H - round(dims[1] * W / dims[0])) // 2
        title_png(title, clip.get("subtitle", ""), work / "title.png",
                  bottom=vid_top - 30 if layout == "tarjas" and dims[0] > dims[1] else None)

    fc = []
    for i, (a, b) in enumerate(ranges):
        fc.append(f"[0:v]trim=start={a - ss:.3f}:end={b - ss:.3f},setpts=PTS-STARTPTS,{vf(i)},setsar=1[v{i}]")
        fc.append(f"[0:a]atrim=start={a - ss:.3f}:end={b - ss:.3f},asetpts=PTS-STARTPTS[a{i}]")
    n = len(ranges)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv0][ca]")
    fc.append(f"[cv0]{sdr_chain(src)}[cv]")  # HDR do iPhone -> SDR (senao foto fica vermelha)
    # loudnorm no ffmpeg 8 solta ~117 frames de 1 amostra no inicio -> aac estala/engasga no comeco;
    # reagrupa em blocos de 1024 antes do encoder
    fc.append("[ca]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000,asetnsamples=n=1024:p=0,asetpts=N/SR/TB[aout]")
    esc = lambda p: str(p).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    if title:
        fc.append(f"movie='{esc(work / 'title.png')}',{RGBA_709}[tt]")
        # vertical: titulo so nos primeiros segundos; tarjas: o video inteiro (tarja de cima)
        gate = "" if layout == "tarjas" else f":enable='lt(t,{TITLE_SECS})'"
        fc.append(f"[cv][tt]overlay=0:0{gate}[cvt]")
        cv = "cvt"
    else:
        cv = "cv"
    fc.append(f"[{cv}]ass='{esc(ass)}':fontsdir='{esc(FONTS)}'[outv]")
    (work / "fc.txt").write_text(";\n".join(fc))

    out = proj / outdir / f"{tag}.mp4"
    out.parent.mkdir(exist_ok=True)
    r = run(["ffmpeg", "-y", "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
             "-filter_complex_script", str(work / "fc.txt"), "-map", "[outv]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", *OUT_TAGS, "-r", "30",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)])
    if r.returncode:
        print(r.stderr[-2500:]); raise SystemExit(f"falhou corte {clip['id']}")
    total = sum(b - a for a, b in ranges)
    print(f"  #{clip['id']} {total:.1f}s ({len(ranges)} ranges, cortou {t1 - t0 - total:.1f}s) -> {out.name}")
    return out, total


def render(name, only, layout=None, outdir="out", use_final=False):
    proj = ROOT / "cortes" / name
    meta = json.loads((proj / "project.json").read_text())
    src, clean = meta["src"], None
    if use_final:  # video ja editado (com graficos) na mesma timeline do src
        src, clean = meta["final"], meta["src"]
    clips = json.loads((proj / "clips.json").read_text())
    if only:
        clips = [c for c in clips if int(c["id"]) in only]
    if layout:
        clips = [{**c, "layout": layout} for c in clips]
    dims = probe_dims(src)
    words = load_words(proj)
    posts = []
    for c in clips:
        out, total = render_clip(proj, src, dims, words, c, outdir, clean)
        posts.append(f"## {out.name}  ·  score {c.get('score', '-')}  ·  {total:.0f}s\n"
                     f"**Título:** {c.get('title', '')}\n\n**Por que:** {c.get('why', '')}\n\n"
                     f"**Legenda do post:**\n{c.get('caption', '')}\n")
    if not only:
        (proj / outdir / "posts.md").write_text(f"# Cortes — {name}\n\n" + "\n".join(posts))
    print("OK ->", proj / outdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep"); p.add_argument("video"); p.add_argument("name")
    r = sub.add_parser("render"); r.add_argument("name"); r.add_argument("--only", default="")
    r.add_argument("--layout", choices=["crop", "tarjas"]); r.add_argument("--out", default="out")
    r.add_argument("--final", action="store_true", help="usa o video editado do project.json como imagem")
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(a.video, a.name)
    else:
        render(a.name, {int(x) for x in a.only.split(",") if x}, a.layout, a.out, a.final)
