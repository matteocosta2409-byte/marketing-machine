"""v9 do arco = v8 enxuta: mesmo visual (fotos, legenda italica, SDR), sem as frases dispensaveis.
CUTS sao frases da timeline do v8 (texto da 1a e da ultima legenda cortada); o script remapeia
trechos, legendas e imagens. Imagem cuja palavra-gatilho cai num corte some (a anterior segura).
Uso: video-use/.venv/bin/python build_v9.py"""
import subprocess
import build_v3 as b3

# (tempo aprox. no v8, 1a legenda cortada, 1a legenda que FICA)
CUTS = [
    (8.6, "E aí", "sua nota"),                      # "acontece uma coisa que nunca tinha acontecido antes"
    (12.3, "Cê não", "cê fica"),                     # "cê nao fica viciado na materia,"
    (24.1, "A disciplina", "Dois ou"),               # "a disciplina... parte de quem voce e"
    (30.1, "A coisa", "E aí"),                       # "a coisa mais dificil... voce conseguiu"
    (38.6, "E não", "O motor"),                      # "nao e decepcao com o curso. e outra coisa"
    (47.1, "Porque a", "aí que"),                    # "medicina vai te tomar seis anos... construir algo"
    (99.1, "As duas", "E se"),                       # CTA: "as duas coisas, nao uma ao inves da outra"
]
PAD = 0.05  # corta um pouco antes do inicio da palavra (Scribe marca o inicio levemente atrasado)


def locate(cues, approx, text):
    for st, en, t in cues:
        if st >= approx - 0.3 and t.strip().startswith(text):
            return st
    raise SystemExit(f"nao achei '{text}' perto de {approx}")


def main():
    cues = b3.srt_cues()
    cuts = []
    for approx, first, keep in CUTS:
        a = locate(cues, approx, first)
        b = locate(cues, a + 0.01, keep)
        cuts.append((a - PAD, b - PAD))

    def removed_before(t):
        return sum(min(t, b) - a for a, b in cuts if t > a)

    def inside(t):
        return any(a <= t < b for a, b in cuts)

    def remap(t):
        return t - removed_before(t)

    # trechos do v8 (timeline de saida) -> sub-trechos sem os cortes
    ranges, out = [], 0.0
    for i, r in enumerate(b3.ranges):
        s, e = float(r["start"]), float(r["end"])
        o0, o1 = out, out + (e - s)
        out = o1
        pieces = [(o0, o1)]
        for a, b in cuts:
            nxt = []
            for p0, p1 in pieces:
                if b <= p0 or a >= p1:
                    nxt.append((p0, p1)); continue
                if a > p0: nxt.append((p0, a))
                if b < p1: nxt.append((b, p1))
            pieces = nxt
        for p0, p1 in pieces:
            if p1 - p0 < 0.08:
                continue
            ss, ee = s + (p0 - o0), s + (p1 - o0)
            ve = b3.VEND.get(i, e) if r["source"] == "main" else e
            ranges.append({"source": r["source"], "start": ss, "end": ee,
                           "vend": min(ve, ee) if abs(ee - e) < 1e-6 else ee})

    new_cues = [(remap(st), remap(en), t) for st, en, t in cues if not inside(st)]
    starts = [b3.find(cues, w, tmin) for w, tmin, _ in b3.BEATS]
    starts[0] = 0.0
    for j, (w, _, _) in enumerate(b3.BEATS):  # gatilho cortado: usa a mesma palavra logo depois (<3s)
        if inside(starts[j]):
            nxt = [st for st, _, t in cues if starts[j] < st < starts[j] + 3 and not inside(st)
                   and b3.re.search(rf"(?<!\w){w.lower()}(?!\w)", t.lower())]
            if nxt:
                starts[j] = nxt[0]
    end_all = remap(b3.find(cues, b3.END_IMAGES, starts[-1]))
    beats = [(w, remap(st), imgs) for (w, _, imgs), st in zip(b3.BEATS, starts) if not inside(st)]

    names = list(b3.SRCS)
    inputs = []
    for n in names:
        inputs += ["-i", str(b3.SRCS[n])]
    parts, labels = [], []
    for i, r in enumerate(ranges):
        k = names.index(r["source"])
        s, e, ve = r["start"], r["end"], r["vend"]
        hold = f",tpad=stop_mode=clone:stop_duration={e - ve:.3f}" if ve < e - 0.001 else ""
        parts.append(f"[{k}:v]trim=start={s:.3f}:end={ve:.3f},setpts=PTS-STARTPTS{hold}[v{i}]")
        parts.append(f"[{k}:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.01,afade=t=out:st={e - s - 0.01:.3f}:d=0.01[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    parts.append("".join(labels) + f"concat=n={len(ranges)}:v=1:a=1[hdr][cca]")
    parts.append(f"[hdr]{b3.SDR}[cv]")
    parts.append("[cca]loudnorm=I=-14:TP=-1:LRA=11[aout]")
    cur = "cv"
    for bi, (w, a, imgs) in enumerate(beats):
        b = beats[bi + 1][1] if bi + 1 < len(beats) else end_all
        mov, _ = b3.beat_clip(100 + bi, imgs)
        k = inputs.count("-i")
        inputs += ["-loop", "1", "-framerate", str(b3.FPS), "-t", f"{b - a:.3f}", "-i", str(mov)]
        parts.append(f"[{k}:v]format=rgba,scale=out_color_matrix=bt709:out_range=tv,format=yuva420p,"
                     f"setpts=PTS+{a:.3f}/TB[b{bi}]")
        parts.append(f"[{cur}][b{bi}]overlay=0:{b3.RY}:eof_action=pass[o{bi}]")
        cur = f"o{bi}"
        print(f"  {a:6.2f}-{b:6.2f}  {w:<11} {'+'.join(imgs)}")
    ass_p = b3.captions_ass(new_cues)
    ass9 = ass_p.with_name("caps_v9.ass")
    ass_p.rename(ass9)
    ass = str(ass9).replace(":", r"\:").replace("'", r"\'")
    parts.append(f"[{cur}]ass='{ass}'[outv]")
    fc = b3.EDIT / "_fc_v9.txt"
    fc.write_text(";\n".join(parts))
    outp = b3.EDIT / "final_v9.mp4"
    r = subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex_script", str(fc),
                        "-map", "[outv]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-color_range", "tv", "-r", str(b3.FPS), "-c:a", "aac",
                        "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(outp)],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2500:]); raise SystemExit(1)
    print(f"OK -> {outp}  ({sum(r['end'] - r['start'] for r in ranges):.1f}s, cortou "
          f"{sum(b - a for a, b in cuts):.1f}s)")


if __name__ == "__main__":
    main()
