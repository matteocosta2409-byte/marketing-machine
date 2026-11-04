"""v2 do arco: (1) congela o video no ultimo quadro de frente onde a cabeca vira pro roteiro
(audio intacto), (2) gancho visual estilo ref (2 fotos aura lado a lado no peito no 1o take).
Uso: video-use/.venv/bin/python build_v2.py <med.jpg> <ent.jpg>"""
import json, subprocess, sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

EDIT = Path(__file__).resolve().parent
PROJ = EDIT.parent
W, H, FPS = 1080, 1920, 30
SRCS = {"main": PROJ / "main.mov", "cta": PROJ / "cta.mov"}

# fim do VIDEO (tempo fonte) em takes onde a cabeca comeca a virar antes do corte
VEND = {1: 28.75, 2: 45.00, 9: 121.86, 19: 274.75, 21: 308.98}

# gancho: 2 fotos 380x380 no peito, legenda sobe pro pescoco durante o gancho
BOX, GAP, Y0 = 380, 24, 1240
STAGGER = 0.15

edl = json.loads((EDIT / "edl.json").read_text())
ranges = edl["ranges"]
HOOK = ranges[0]["end"] - ranges[0]["start"]


def card(path):
    im = Image.open(path).convert("RGB")
    s = max(BOX / im.width, BOX / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - BOX) // 2, (im.height - BOX) // 2
    im = im.crop((l, t, l + BOX, t + BOX)).convert("RGBA")
    mask = Image.new("L", (BOX, BOX), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, BOX - 1, BOX - 1), 22, fill=255)
    im.putalpha(mask)
    return im


def ease_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def build_hook(med, ent):
    cards = [card(med), card(ent)]
    x0 = (W - (2 * BOX + GAP)) // 2
    pos = [(x0, Y0), (x0 + BOX + GAP, Y0)]
    fdir = EDIT / "hook_frames"
    fdir.mkdir(exist_ok=True)
    n = int(round(HOOK * FPS))
    for f in range(n):
        t = f / FPS
        frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        placed = []
        for i, (c, (x, y)) in enumerate(zip(cards, pos)):
            p = (t - i * STAGGER) / 0.28
            if p <= 0:
                continue
            k = ease_back(min(p, 1.0))
            size = max(2, int(BOX * k))
            ci = c.resize((size, size), Image.LANCZOS)
            cx, cy = x + BOX // 2 - size // 2, y + BOX // 2 - size // 2
            sd.rounded_rectangle((cx, cy + 8, cx + size, cy + size + 8), 22, fill=(0, 0, 0, 120))
            placed.append((ci, cx, cy))
        frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
        for ci, cx, cy in placed:
            frame.alpha_composite(ci, (cx, cy))
        frame.save(fdir / f"{f:04d}.png")
    out = EDIT / "hook.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(fdir / "%04d.png"),
                    "-c:v", "qtrle", "-pix_fmt", "argb", str(out)], check=True)
    return out


def hook_srt():
    """Separa o master.srt: cues do gancho vao pra um ASS proprio (acima das fotos, SRT ignora \\pos);
    o resto segue no SRT com o estilo original."""
    blocks = (EDIT / "master.srt").read_text().strip().split("\n\n")
    rest, hook = [], []
    for b in blocks:
        ls = b.split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ls[1])
        st = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
        en = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
        (hook if st < HOOK else rest).append((st, en, " ".join(ls[2:]), b))
    p = EDIT / "master_v2.srt"
    p.write_text("\n\n".join(b for *_, b in rest) + "\n")
    ts = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    # mesmo visual do force_style original, convertido de PlayResY 288 -> 1920 (x6.67)
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Helvetica,87,&H00FFFFFF,&H00FFFFFF,&HB0000000,&H00000000,0,0,0,0,100,100,0,0,1,6.7,0,2,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(f"Dialogue: 0,{ts(s)},{ts(e)},Hook,,0,0,0,,{{\\pos({W // 2},{Y0 - 30})}}{t}"
                for s, e, t, _ in hook) + "\n"
    (EDIT / "hook_caps.ass").write_text(ass)
    return p


def render(hook_mov, srt):
    names = list(SRCS)
    inputs = []
    for n in names:
        inputs += ["-i", str(SRCS[n])]
    inputs += ["-i", str(hook_mov)]
    hk = len(names)
    parts, labels = [], []
    for i, r in enumerate(ranges):
        s, e = float(r["start"]), float(r["end"])
        k = names.index(r["source"])
        ve = VEND.get(i, e) if r["source"] == "main" else e
        hold = f",tpad=stop_mode=clone:stop_duration={e - ve:.3f}" if ve < e else ""
        parts.append(f"[{k}:v]trim=start={s:.3f}:end={ve:.3f},setpts=PTS-STARTPTS{hold}[v{i}]")
        parts.append(f"[{k}:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    parts.append("".join(labels) + f"concat=n={len(ranges)}:v=1:a=1[cv][cca]")
    parts.append("[cca]loudnorm=I=-14:TP=-1:LRA=11[aout]")
    parts.append(f"[cv][{hk}:v]overlay=0:0:eof_action=pass[ov]")
    esc = str(srt).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    hass = str(EDIT / "hook_caps.ass").replace(":", r"\:").replace("'", r"\'")
    parts.append(f"[ov]subtitles='{esc}':force_style='{edl['subtitle_style']}',ass='{hass}'[outv]")
    (EDIT / "_fc_v2.txt").write_text(";\n".join(parts))
    out = EDIT / "final_v2.mp4"
    r = subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex_script", str(EDIT / "_fc_v2.txt"),
                        "-map", "[outv]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-movflags", "+faststart", str(out)], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2500:]); raise SystemExit(1)
    print("OK ->", out)


if __name__ == "__main__":
    render(build_hook(sys.argv[1], sys.argv[2]), hook_srt())
