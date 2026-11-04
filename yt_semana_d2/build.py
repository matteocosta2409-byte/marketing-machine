"""Semana do ENEM dia 2 (YouTube, estilo Ali+Dan). Passo 1: A-cut (retakes fora + silêncio >0.45s apertado) -> acut.mp4
Passo 2: props do Remotion (gráficos/zooms/sfx em tempo de fonte -> tempo do A-cut).
Uso: python3 build.py acut | props"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
PUB = P.parent / "motion/remotion/public/semana2"

# trechos bons da fonte (src.mov = bruto único; retakes e "corta" fora)
RANGES = [
    (4.98, 23.85), (24.32, 39.75), (40.30, 56.85), (58.78, 87.00), (89.16, 96.85), (97.88, 114.80), (116.94, 122.72),
    (124.50, 133.95), (135.74, 188.15), (189.96, 216.25), (216.62, 222.98), (223.90, 236.60), (284.92, 297.42),
    (299.38, 301.95), (305.28, 308.76), (310.18, 313.80), (316.20, 331.62), (334.50, 348.00), (348.60, 405.30),
    (408.00, 413.80), (416.45, 423.55), (444.22, 448.00), (451.00, 466.08), (467.62, 485.40), (488.00, 490.50),
    (491.90, 508.85), (511.36, 518.05), (519.10, 531.40), (531.78, 537.70), (538.80, 542.90), (544.20, 572.75),
    (579.60, 598.10),
]
GAP, PAD = 0.45, 0.12


def tighten(ranges):
    sil = [tuple(map(float, l.split())) for l in (P / "edit/silences.txt").read_text().split("\n") if l.strip()]
    out = []
    for s, e in ranges:
        cur = s
        for a, b in sil:
            if b - a >= GAP and a > cur and b < e:
                out.append((cur, a + PAD))
                cur = b - PAD
        out.append((cur, e))
    return [(round(a, 3), round(b, 3)) for a, b in out if b - a > 0.08]


R = tighten(RANGES)


def out_t(t):
    acc = 0.0
    for s, e in R:
        if s <= t <= e:
            return round(acc + t - s, 3)
        acc += e - s
    # caiu num corte: proximo trecho
    acc = 0.0
    for s, e in R:
        if t < s:
            return round(acc, 3)
        acc += e - s
    return round(acc, 3)


TOTAL = round(sum(e - s for s, e in R), 3)


def acut():
    parts, labels = [], ""
    for i, (s, e) in enumerate(R):
        parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={e - s - 0.012:.3f}:d=0.012[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(R)}:v=1:a=1[v][a0]")
    parts.append("[a0]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    (P / "edit/acut_fc.txt").write_text(";\n".join(parts))
    PUB.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "src.mov"), "-filter_complex_script", str(P / "edit/acut_fc.txt"),
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "30",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", str(PUB / "acut.mp4")], check=True)
    print(f"{len(R)} trechos, {TOTAL}s -> {PUB / 'acut.mp4'}")


if __name__ == "__main__":
    if sys.argv[1] == "acut":
        acut()
    elif sys.argv[1] == "words":
        w = [x for x in json.load(open(P / "edit/transcripts/src.json"))["words"] if x.get("type") == "word"]
        for x in w:
            if any(s <= x["start"] <= e for s, e in R):
                print(f"{out_t(x['start']):.2f} {x['start']:.2f} {x['text']}")
    elif sys.argv[1] == "props":
        import importlib.util
        spec = importlib.util.spec_from_file_location("plan", P / "plan.py")
        plan = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plan)
        props = plan.make(out_t, TOTAL)
        out = Path(sys.argv[2]) if len(sys.argv) > 2 else P / "edit/props.json"
        out.write_text(json.dumps(props, ensure_ascii=False, indent=1))
        print("props ->", out, "| total", TOTAL)
