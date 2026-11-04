"""Builder VLOG v4: intro nova (VLOG verde trocando de FONTE devagar, semi-transparente,
sem contorno, takes atras + musica 'Sunset Ballin' Uppbeat) + vlog completo TUDO HORIZONTAL
tela cheia, clipes girados, legendas + labels de treino.
Mudancas v4: (1) corta tempo morto depois do TAPA em cada clipe de fala; (2) intro nova;
(3) remove take do perdao (IMG_9999); (4) adiciona cafe da manha (IMG_9959) antes do 9961.
"""
import json, subprocess, os, sys, re, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJ = Path("/Users/mac-matteo/marketing machine/vlog_yt1")
RAW = Path("/Users/mac-matteo/Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/"
           "Meu Drive/2026/Personal Branding/YouTube/Raw/Vlog 1 ")
EDIT = PROJ / "edit"; SEG = PROJ / "seg"; SEG.mkdir(parents=True, exist_ok=True)
TR = EDIT / "transcripts"
MUSIC = PROJ / "sunset_ballin.mp3"
SCR = Path("/private/tmp/claude-501/-Users-mac-matteo-marketing-machine/0a2f6991-e245-4c81-865f-0c4025b08c92/scratchpad")
GF = str(SCR / "gfonts") + "/"
SUP = "/System/Library/Fonts/Supplemental/"
W, H, FPS = 1920, 1080, 30
GREEN = (61, 163, 93)

STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")
GREEN_TAG = r"{\an8\b1\i0\fs22\c&H005DA33D&\3c&H00000000&\bord3}"

# clipes landscape com flag de rotacao errada -> -noautorotate (+180 p/ alguns)
ROT = {
    "IMG_9955": ("noauto", ",vflip,hflip"),
    "IMG_9958": ("noauto", ",vflip,hflip"),
    "IMG_9986": ("noauto", ""),
    "IMG_0002": ("noauto", ""),
    "IMG_9959": ("noauto", ""),   # cafe da manha
}

# fontes da intro (mescla Google Fonts baixadas + fontes do Mac)
FONTS = [GF+"Anton.ttf", GF+"BebasNeue.ttf", SUP+"Futura.ttc", GF+"Oswald.ttf",
         GF+"ArchivoBlack.ttf", SUP+"Impact.ttf", SUP+"Times New Roman.ttf", GF+"Pacifico.ttf",
         SUP+"Chalkduster.ttf", GF+"Lobster.ttf", SUP+"Courier New.ttf", GF+"PressStart2P.ttf",
         SUP+"Georgia.ttf", SUP+"Arial Rounded Bold.ttf", SUP+"Copperplate.ttc", SUP+"Didot.ttc"]
FONTS = [f for f in FONTS if os.path.exists(f)]


def vf_cover(s, e, stem):
    flip = ROT.get(stem, ("", ""))[1]
    return (f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS,fps=30{flip},"
            f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[v]")

def probe_dur(f):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nk=1:nw=1",str(f)],capture_output=True,text=True).stdout.strip() or 0)

def has_audio(f):
    return bool(subprocess.run(["ffprobe","-v","error","-select_streams","a","-show_entries",
        "stream=index","-of","csv=p=0",str(f)],capture_output=True,text=True).stdout.strip())

def normalize(stem, s, e, out, mute=False):
    src = RAW / f"{stem}.MOV"
    dur = probe_dur(src)
    if e is None or e > dur: e = dur
    pre = ["-noautorotate"] if ROT.get(stem,("",""))[0]=="noauto" else []
    cmd = ["ffmpeg","-y",*pre,"-i",str(src)]
    if mute or not has_audio(src):
        cmd += ["-f","lavfi","-t",f"{e-s:.3f}","-i","anullsrc=r=48000:cl=stereo",
                "-filter_complex",vf_cover(s,e,stem),"-map","[v]","-map","1:a"]
    else:
        cmd += ["-filter_complex",vf_cover(s,e,stem),"-map","[v]","-map","0:a:0",
                "-af",f"atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS"]
    cmd += ["-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",
            "-c:a","aac","-b:a","192k","-ar","48000",str(out)]
    r = subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print("ERRO normalize",stem,"\n",r.stderr[-1200:]); sys.exit(1)
    return e - s

# ---------- corte do tempo morto apos o TAPA (cauda de silencio) ----------
def _last_word_end(stem, s, e):
    """Fim da ultima palavra transcrita dentro de [s,e] (0 se nao houver transcript)."""
    p = TR / f"{stem}.json"
    if not p.exists(): return None
    ws = [w for w in json.loads(p.read_text())["words"]
          if w.get("type")=="word" and w.get("end") is not None and s <= w["end"] <= e]
    return max((w["end"] for w in ws), default=0.0)

def trim_after_slap(stem, s, e):
    """Corta o tempo morto DEPOIS do TAPA. Acha o tapa = pico de som alto apos a fala
    terminar, corta ~0.25s depois dele. Trava: nunca corta antes da ultima palavra
    transcrita (protege fala baixa, ex: 0002 no restaurante). Se nao achar tapa claro,
    mantem o clipe inteiro."""
    import numpy as np, wave, tempfile
    src = RAW / f"{stem}.MOV"
    dur = probe_dur(src)
    if e is None or e > dur: e = dur
    last_end = _last_word_end(stem, s, e)
    if last_end is None: return e
    ws = max(s, s + last_end - 0.10)          # janela de busca: do fim da fala ate o fim
    wl = e - ws
    if wl < 0.6: return e                     # quase nada depois da fala -> nada a cortar
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf: wav = tf.name
    subprocess.run(["ffmpeg","-y","-ss",f"{ws:.3f}","-i",str(src),"-t",f"{wl:.3f}",
                    "-ac","1","-ar","22050","-vn",wav], capture_output=True)
    try:
        w = wave.open(wav,"rb"); sr = w.getframerate()
        y = np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
        w.close()
    except Exception:
        os.unlink(wav); return e
    os.unlink(wav)
    if len(y) < sr*0.3: return e
    fr = int(sr*0.03)                          # envelope em janelas de 30ms
    env = np.array([np.abs(y[i:i+fr]).mean() for i in range(0,len(y)-fr,fr)])
    if len(env) < 3: return e
    pk = int(np.argmax(env)); peak = env[pk]
    med = np.median(env) + 1e-6
    if peak < med*3.0: return e                # sem transiente claro (sem tapa) -> inteiro
    slap_t = ws + pk*fr/sr                      # tempo absoluto do tapa
    new_e = slap_t + 0.25                       # deixa o tapa soar
    new_e = max(new_e, s + last_end + 0.20)     # nunca antes da fala
    new_e = min(new_e, e)
    return new_e if new_e < e - 0.30 else e

# ---------- INTRO v4 (VLOG trocando de fonte devagar, sem contorno) ----------
random.seed(7)
CLIP_I = 0.70
TEASER = [("IMG_9968",3.9),("IMG_9974",27.5),("IMG_9966",11.0),("IMG_0002",7.0),
          ("IMG_9986",4.0),("IMG_0007",9.0),("IMG_0004",5.0),("IMG_9981",8.0)]
INTRO_DUR = CLIP_I * len(TEASER)

def render_layer(fontpath):
    target = random.randint(820,1080); size = 360
    try: fnt = ImageFont.truetype(fontpath, size)
    except Exception: fnt = ImageFont.truetype(FONTS[0], size)
    d = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    bb = d.textbbox((0,0),"VLOG",font=fnt,stroke_width=5); w = bb[2]-bb[0]
    size = max(120, int(size*target/max(1,w)))
    try: fnt = ImageFont.truetype(fontpath, size)
    except Exception: fnt = ImageFont.truetype(FONTS[0], size)
    bb = d.textbbox((0,0),"VLOG",font=fnt); tw,th = bb[2]-bb[0], bb[3]-bb[1]
    lay = Image.new("RGBA",(tw+60,th+60),(0,0,0,0))
    ImageDraw.Draw(lay).text((30-bb[0],30-bb[1]),"VLOG",font=fnt,fill=GREEN+(185,))  # sem contorno
    return lay

def build_intro(out):
    layers = [render_layer(f) for f in FONTS]
    FR = SCR/"introv4frames_b"; FR.mkdir(exist_ok=True)
    for f in FR.glob("*.png"): f.unlink()
    NF = int(round(INTRO_DUR*FPS)); CHANGE = 6; jit = (0,0)
    for i in range(NF):
        fi = (i//CHANGE) % len(layers)
        if i % CHANGE == 0: jit = (random.randint(-60,60), random.randint(-40,40))
        lay = layers[fi]
        cv = Image.new("RGBA",(W,H),(0,0,0,0))
        cv.alpha_composite(lay, (int((W-lay.width)/2)+jit[0], int((H-lay.height)/2)+jit[1]))
        cv.save(f"{FR}/f_{i:04d}.png")
    IS = SCR/"introv4segs_b"; IS.mkdir(exist_ok=True); segs=[]
    for i,(stem,s) in enumerate(TEASER):
        o=IS/f"s{i}.mp4"; normalize(stem,s,s+CLIP_I,o,mute=True); segs.append(o)
    (IS/"list.txt").write_text("\n".join(f"file '{p}'" for p in segs))
    traw=SCR/"teaser_v4b.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(IS/"list.txt"),"-c","copy",str(traw)],check=True,capture_output=True)
    cmd=["ffmpeg","-y","-i",str(traw),"-framerate","30","-i",f"{FR}/f_%04d.png","-ss","74","-i",str(MUSIC),
         "-filter_complex",
         f"[0:v][1:v]overlay=0:0:format=auto[v];"
         f"[2:a]atrim=0:{INTRO_DUR:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.15,"
         f"afade=t=out:st={INTRO_DUR-0.9:.3f}:d=0.9,volume=0.9[a]",
         "-map","[v]","-map","[a]","-t",f"{INTRO_DUR:.3f}",
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",
         "-c:a","aac","-b:a","192k","-ar","48000",str(out)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print("ERRO intro\n",r.stderr[-1200:]); sys.exit(1)
    return INTRO_DUR

# ---------- MAIN (v4: + cafe 9959 antes do 9961, - perdao 9999) ----------
MAIN = [
    ("IMG_9955",0.0,None,"talk"),("IMG_9956",0.0,None,"talk"),("IMG_9958",0.0,None,"talk"),
    ("IMG_9959",0.0,None,"talk"),  # cafe da manha (novo)
    ("IMG_9961",0.0,None,"talk"),("IMG_9962",0.0,None,"talk"),("IMG_9963",0.0,None,"broll"),
    ("IMG_9965",0.0,None,"talk"),("IMG_9966",0.0,None,"talk"),("IMG_9967",0.0,None,"talk"),
    ("IMG_9968",0.0,None,"talk"),("IMG_9969",0.0,None,"talk"),("IMG_9970",0.0,14.40,"talk"),
    ("IMG_9972",0.0,None,"talk"),
    ("IMG_9974",26.0,33.0,"exec:Supino"),("IMG_9976",6.0,13.0,"exec:Desenvolvimento"),
    ("IMG_9977",15.0,22.0,"exec:Elevação lateral"),("IMG_9978",6.0,13.0,"exec:Bíceps"),
    ("IMG_9979",0.0,None,"talk"),("IMG_9981",0.0,None,"talk"),("IMG_9985",0.0,None,"talk"),
    ("IMG_9986",0.0,None,"talk"),("IMG_9988",0.0,None,"talk"),
    ("IMG_9990",0.0,10.0,"broll"),("IMG_9993",0.0,10.0,"broll"),
    # IMG_9999 (perdao/irma do socio) REMOVIDO
    ("IMG_0001",0.0,None,"talk"),("IMG_0002",0.0,None,"talk"),
    ("IMG_0004",0.0,None,"talk"),("IMG_0005",0.0,None,"talk"),("IMG_0006",0.0,None,"talk"),
    ("IMG_0007",0.0,None,"talk"),("IMG_0021",0.0,None,"talk"),
]

def load_words(stem):
    p=TR/f"{stem}.json"
    if not p.exists(): return []
    return [w for w in json.loads(p.read_text())["words"] if w.get("type")=="word" and w.get("start") is not None]
def fix(t): return t.replace("Matheus","Matteo").replace("matheus","Matteo")
def ts(t):
    h=int(t//3600);m=int((t%3600)//60);s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.',',')

def main():
    manifest=[]; cues=[]
    intro=SEG/"00_intro.mp4"
    offset=build_intro(intro); manifest.append(intro)
    print(f"[intro] {offset:.1f}s")
    for i,(stem,s,e,kind) in enumerate(MAIN):
        if kind=="talk":
            e = trim_after_slap(stem, s, e)   # corta tempo morto depois do tapa
        out=SEG/f"m{i:02d}_{stem}.mp4"
        d=normalize(stem,s,e,out); se=s+d; manifest.append(out)
        print(f"[m{i:02d}] {stem} {s:.1f}-{se:.1f} ({d:.1f}s) {kind}")
        if kind=="talk":
            words=[w for w in load_words(stem) if w["start"]<se and w["end"]>s]
            group=[]
            def flush():
                if not group: return
                a=offset+max(0.0,group[0]["start"]-s)
                b=offset+max(0.0,min(group[-1]["end"],se)-s)+0.30
                cues.append([a,b,fix(" ".join(x["text"] for x in group).strip())]); group.clear()
            for w in words:
                group.append(w)
                if w["text"].rstrip().endswith(('.','!','?',',',':',';')) or len(group)>=2: flush()
            flush()
        elif kind.startswith("exec:"):
            cues.append([offset+0.15,offset+d-0.15,GREEN_TAG+kind.split(":",1)[1]])
        offset+=d
    cues.sort()
    for j in range(len(cues)):
        if j+1<len(cues): cues[j][1]=min(cues[j][1],cues[j+1][0]-0.001)
        if cues[j][1]<=cues[j][0]: cues[j][1]=cues[j][0]+0.05
    (EDIT/"master4.srt").write_text("\n".join(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n" for k,(a,b,txt) in enumerate(cues,1)))
    print(f"TOTAL {offset:.1f}s | {len(cues)} cues")
    (EDIT/"concat4.txt").write_text("\n".join(f"file '{p.resolve()}'" for p in manifest))
    joined=EDIT/"joined4.mp4"
    r=subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(EDIT/"concat4.txt"),
        "-c","copy","-movflags","+faststart",str(joined)],capture_output=True,text=True)
    if r.returncode: print("ERRO concat\n",r.stderr[-1200:]); sys.exit(1)
    srt_esc=str((EDIT/"master4.srt").resolve()).replace("\\","\\\\").replace(":",r"\:").replace("'",r"\'")
    final=EDIT/"final_v4.mp4"
    r=subprocess.run(["ffmpeg","-y","-i",str(joined),
        "-vf",f"subtitles='{srt_esc}':force_style='{STYLE}'",
        "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",
        "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(final)],capture_output=True,text=True)
    if r.returncode: print("ERRO burn\n",r.stderr[-1200:]); sys.exit(1)
    print("OK ->",final,f"({probe_dur(final):.1f}s)")

if __name__=="__main__": main()
