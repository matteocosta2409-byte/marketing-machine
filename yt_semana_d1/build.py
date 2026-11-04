"""Semana do ENEM dia 1 (YouTube, estilo Ali+Dan). Passo 1: A-cut (retakes fora + silêncio >0.45s apertado) -> acut.mp4
Passo 2: props do Remotion (gráficos/zooms/sfx em tempo de fonte -> tempo do A-cut).
Uso: python3 build.py acut | props"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
PUB = P.parent / "motion/remotion/public/semana1"

# trechos bons da fonte (src.mov = raw_b [0-463.9] conteúdo + raw_a [463.9-] resumo/fechamento)
RANGES = [
    (0.48, 31.0), (35.98, 39.75), (50.62, 53.80), (54.18, 56.45), (58.90, 68.90), (73.24, 79.55), (80.45, 82.50),
    (84.38, 97.62), (102.35, 105.20), (112.02, 132.92), (133.94, 139.00), (140.06, 146.60), (152.58, 155.46), (156.06, 172.30),
    (176.40, 183.80), (186.72, 200.14), (202.64, 206.24), (209.96, 218.54), (228.26, 242.95), (246.20, 250.30),
    (252.42, 255.50), (259.32, 262.80), (270.64, 286.50), (294.86, 300.40), (301.74, 316.72), (323.70, 336.06),
    (340.64, 353.06), (358.88, 372.42), (387.46, 405.60), (411.92, 418.14), (425.42, 439.20), (447.18, 455.22),
    # resumo + fechamento (raw_a)
    (483.72, 510.90), (513.52, 521.10), (522.88, 529.92), (530.80, 550.60), (556.14, 573.15),
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
