"""Builder de VLOG (YouTube 16:9): normaliza cada trecho (blur-fill 1920x1080, 30fps,
audio 48k) -> junta (concat sync) -> legenda queimada. SEM corte de silencio.
Plano de segmentos definido inline (clip, start, end, kind).
  kind: "talk"  -> legenda da transcricao
        "broll" -> sem legenda (mantem audio ambiente)
Uso: python vlog_build.py
"""
import json, subprocess, glob, os, sys
from pathlib import Path

PROJ = Path("/Users/mac-matteo/marketing machine/vlog_yt1")
RAW = Path("/Users/mac-matteo/Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/"
           "Meu Drive/2026/Personal Branding/YouTube/Raw/Vlog 1")
EDIT = PROJ / "edit"
SEG = PROJ / "seg"
SEG.mkdir(parents=True, exist_ok=True)
TR = EDIT / "transcripts"

STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")

# (stem, start, end|None=full, kind)
PLAN = [
    ("IMG_9961", 0.0, None, "talk"),    # cafe da manha / intro
    ("IMG_9962", 0.0, None, "talk"),    # dia nublado, indo
    ("IMG_9963", 0.0, None, "broll"),   # b-roll UnB
    ("IMG_9965", 0.0, None, "talk"),    # chegou, ver fotos
    ("IMG_9967", 0.0, None, "talk"),    # dica organizacao / agenda
    ("IMG_9968", 0.0, None, "talk"),    # casa do socio, soco
    ("IMG_9969", 0.0, None, "talk"),    # vamo treinar
    ("IMG_9970", 0.0, 14.40, "talk"),   # academia: plano (CORTA competicao depois de 14.4)
    ("IMG_9972", 0.0, None, "talk"),    # roupa emprestada
    ("IMG_9976", 5.0, 30.70, "broll"),  # execucao desenvolvimento (CORTA fala de competicao 0-5)
    ("IMG_9979", 0.0, None, "talk"),    # treino finalizado, almoco
    ("IMG_9981", 0.0, None, "talk"),    # dica fitness do Luca
    ("IMG_9985", 0.0, None, "talk"),    # casa do Isaac, timelapse
    ("IMG_9986", 0.0, None, "talk"),    # cachorro Platz (vertical)
    ("IMG_9988", 0.0, None, "talk"),    # cadeiras do Isaac
    ("IMG_9990", 0.0, 10.0, "broll"),   # timelapse reuniao (mudo) - encurtado
    ("IMG_9993", 0.0, 10.0, "broll"),   # timelapse reuniao (mudo) - encurtado
    ("IMG_9999", 0.0, None, "talk"),    # "depois de horas... to gravando"
    ("IMG_0001", 0.0, None, "talk"),    # descanso / refeicao merecida
    ("IMG_0002", 0.0, None, "talk"),    # comida "babar" (vertical)
    ("IMG_0004", 0.0, None, "talk"),    # fusca do socio / volta (outro)
]


def probe_dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=noprint_wrappers=1:nokey=1", str(f)],
                                capture_output=True, text=True).stdout.strip())


def has_audio(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout
    return bool(out.strip())


# blur-fill 1920x1080: fg = cabe dentro; bg = preenche + blur; overlay centralizado
VF = ("[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,fps=30,split=2[a][b];"
      "[a]scale=1920:1080:force_original_aspect_ratio=decrease[fg];"
      "[b]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=18:4[bg];"
      "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]")


def normalize(stem, s, e, out):
    src = RAW / f"{stem}.MOV"
    dur = probe_dur(src)
    if e is None or e > dur:
        e = dur
    aud = has_audio(src)
    fc = VF.format(s=f"{s:.3f}", e=f"{e:.3f}")
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if aud:
        cmd += ["-filter_complex", fc,
                "-map", "[v]", "-map", f"0:a:0", "-af", f"atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS"]
    else:
        cmd += ["-f", "lavfi", "-t", f"{e-s:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", fc, "-map", "[v]", "-map", "1:a"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO normalize", stem, "\n", r.stderr[-1500:]); sys.exit(1)
    return e - s


def load_words(stem):
    p = TR / f"{stem}.json"
    if not p.exists():
        return []
    return [w for w in json.loads(p.read_text())["words"]
            if w.get("type") == "word" and w.get("start") is not None]


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')


def main():
    manifest = []   # (segfile, dur)
    cues = []       # (abs_start, abs_end, text)
    offset = 0.0
    for i, (stem, s, e, kind) in enumerate(PLAN):
        out = SEG / f"{i:02d}_{stem}.mp4"
        segdur = normalize(stem, s, e, out)
        se = s + segdur
        print(f"[{i:02d}] {stem} {s:.1f}-{se:.1f} ({segdur:.1f}s) {kind} -> {out.name}")
        manifest.append(out)
        if kind == "talk":
            words = [w for w in load_words(stem) if w["start"] < se and w["end"] > s]
            # agrupa em cues curtas (quebra em pontuacao ou a cada 2 palavras)
            group = []
            def flush():
                if not group:
                    return
                a = offset + max(0.0, group[0]["start"] - s)
                b = offset + max(0.0, min(group[-1]["end"], se) - s) + 0.30
                txt = " ".join(x["text"] for x in group).strip()
                cues.append([a, b, txt])
                group.clear()
            for w in words:
                group.append(w)
                if w["text"].rstrip().endswith(('.', '!', '?', ',', ':', ';')) or len(group) >= 2:
                    flush()
            flush()
        offset += segdur

    # evita sobreposicao de cues
    for j in range(len(cues)):
        if j + 1 < len(cues):
            cues[j][1] = min(cues[j][1], cues[j + 1][0] - 0.001)
        if cues[j][1] <= cues[j][0]:
            cues[j][1] = cues[j][0] + 0.05
    srt = "\n".join(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n" for k, (a, b, txt) in enumerate(cues, 1))
    (EDIT / "master.srt").write_text(srt)
    print(f"total {offset:.1f}s | {len(cues)} cues")

    # concat demuxer (stream copy) -> joined
    lst = EDIT / "concat.txt"
    lst.write_text("\n".join(f"file '{p.resolve()}'" for p in manifest))
    joined = EDIT / "joined.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", "-movflags", "+faststart", str(joined)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO concat\n", r.stderr[-1500:]); sys.exit(1)

    # queima legenda
    srt_esc = str((EDIT / "master.srt").resolve()).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    final = EDIT / "final_sync.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-i", str(joined),
                        "-vf", f"subtitles='{srt_esc}':force_style='{STYLE}'",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", str(final)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO burn\n", r.stderr[-1500:]); sys.exit(1)
    print("OK ->", final, f"({probe_dur(final):.1f}s)")


if __name__ == "__main__":
    main()
