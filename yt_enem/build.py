"""Enem 2º dia (YouTube, estilo Ali Abdaal). Passo 1: A-cut (retakes fora + silêncio >0.45s apertado) -> acut.mp4
Passo 2: props do Remotion (gráficos/zooms/sfx em tempo de fonte -> tempo do A-cut).
Uso: python3 build.py acut | props"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
PUB = P.parent / "motion/remotion/public/enem"

# trechos bons da fonte (src.mov = raw_a [0-84.4] + raw_b [84.4-556.8]); raw_a é o resumo/fechamento -> vai pro fim
RANGES = [
    (84.95, 111.70), (114.00, 116.80), (118.15, 160.72), (164.62, 180.42), (182.12, 192.98),
    (194.92, 225.80), (228.86, 235.55), (240.58, 266.40), (283.55, 288.24), (289.42, 333.40),
    (344.42, 353.45), (359.40, 368.75), (392.78, 458.52), (464.30, 485.35), (486.96, 492.05),
    (493.03, 498.80), (507.36, 516.05),
    # resumo + fechamento (raw_a)
    (34.20, 41.25), (42.98, 73.80), (73.96, 74.50), (78.36, 84.00),
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
