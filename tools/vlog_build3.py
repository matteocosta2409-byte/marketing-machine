"""Builder VLOG v3: intro estilo referencia (teaser + 'VLOG' verde PERSISTENTE que
pula/da pop + musica aura 'The Complex') + vlog completo TUDO HORIZONTAL tela cheia
(sem blur), clipes verticais girados pro landscape certo, legendas + labels de treino.
"""
import json, subprocess, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJ = Path("/Users/mac-matteo/marketing machine/vlog_yt1")
RAW = Path("/Users/mac-matteo/Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/"
           "Meu Drive/2026/Personal Branding/YouTube/Raw/Vlog 1 ")
EDIT = PROJ / "edit"; SEG = PROJ / "seg"; SEG.mkdir(parents=True, exist_ok=True)
TR = EDIT / "transcripts"
MUSIC = PROJ / "the_complex.mp3"
SCR = Path("/private/tmp/claude-501/-Users-mac-matteo-marketing-machine/0a2f6991-e245-4c81-865f-0c4025b08c92/scratchpad")
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
W, H, FPS = 1920, 1080, 30
GREEN = (61, 163, 93, 255)

STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")
GREEN_TAG = r"{\an8\b1\i0\fs22\c&H005DA33D&\3c&H00000000&\bord3}"

# clipes landscape com flag de rotacao errada -> -noautorotate (+180 p/ alguns)
ROT = {
    "IMG_9955": ("noauto", ",vflip,hflip"),
    "IMG_9958": ("noauto", ",vflip,hflip"),
    "IMG_9986": ("noauto", ""),
    "IMG_0002": ("noauto", ""),
}

# cover-crop tela cheia (tudo ja e 16:9 apos girar) -> fit exato
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

# ---------- INTRO (teaser + VLOG persistente pulando/pop) ----------
CLIP = 0.80
TEASER = [
    ("IMG_9968", 3.9,  (0.50,0.50)),
    ("IMG_9974", 27.5, (0.30,0.36)),
    ("IMG_9966", 11.0, (0.70,0.60)),
    ("IMG_0002", 7.0,  (0.46,0.30)),
    ("IMG_9986", 4.0,  (0.52,0.58)),
    ("IMG_0007", 9.0,  (0.34,0.42)),
    ("IMG_0004", 5.0,  (0.62,0.50)),
]
INTRO_DUR = CLIP*len(TEASER)

def build_intro(out):
    # overlay frames
    big = ImageFont.truetype(FONT, 300)
    tmp = ImageDraw.Draw(Image.new("RGBA",(10,10)))
    bb = tmp.textbbox((0,0),"VLOG",font=big,stroke_width=10)
    layer = Image.new("RGBA",(bb[2]-bb[0]+40,bb[3]-bb[1]+40),(0,0,0,0))
    dl = ImageDraw.Draw(layer)
    dl.text((20-bb[0]+6,20-bb[1]+8),"VLOG",font=big,fill=(0,0,0,110),stroke_width=10,stroke_fill=(0,0,0,110))
    dl.text((20-bb[0],20-bb[1]),"VLOG",font=big,fill=GREEN,stroke_width=10,stroke_fill=(255,255,255,255))
    FR = SCR/"introframes3"; FR.mkdir(exist_ok=True)
    for f in FR.glob("*.png"): f.unlink()
    NF = int(round(INTRO_DUR*FPS))
    for i in range(NF):
        t=i/FPS; ci=min(int(t/CLIP),len(TEASER)-1); local=t-ci*CLIP
        cx,cy=TEASER[ci][2]
        sc_=1.28-0.28*((local/0.14)*(2-local/0.14)) if local<0.14 else 1.0
        nw,nh=max(1,int(layer.width*sc_)),max(1,int(layer.height*sc_))
        sc=layer.resize((nw,nh),Image.LANCZOS)
        cv=Image.new("RGBA",(W,H),(0,0,0,0))
        cv.alpha_composite(sc,(int(cx*W-nw/2),int(cy*H-nh/2)))
        cv.save(f"{FR}/f_{i:04d}.png")
    # normaliza teaser (mudo) + concat
    IS = SCR/"introsegs3"; IS.mkdir(exist_ok=True)
    segs=[]
    for i,(stem,s,_) in enumerate(TEASER):
        o=IS/f"s{i}.mp4"; normalize(stem,s,s+CLIP,o,mute=True); segs.append(o)
    (IS/"list.txt").write_text("\n".join(f"file '{p}'" for p in segs))
    traw=SCR/"teaser_raw3.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(IS/"list.txt"),"-c","copy",str(traw)],check=True,capture_output=True)
    # overlay + musica aura (The Complex, trecho com pegada ~20s in), fade out
    cmd=["ffmpeg","-y","-i",str(traw),"-framerate","30","-i",f"{FR}/f_%04d.png",
         "-ss","19","-i",str(MUSIC),
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

# ---------- MAIN ----------
MAIN = [
    ("IMG_9955",0.0,None,"talk"),("IMG_9956",0.0,None,"talk"),("IMG_9958",0.0,None,"talk"),
    ("IMG_9961",0.0,None,"talk"),("IMG_9962",0.0,None,"talk"),("IMG_9963",0.0,None,"broll"),
    ("IMG_9965",0.0,None,"talk"),("IMG_9966",0.0,None,"talk"),("IMG_9967",0.0,None,"talk"),
    ("IMG_9968",0.0,None,"talk"),("IMG_9969",0.0,None,"talk"),("IMG_9970",0.0,14.40,"talk"),
    ("IMG_9972",0.0,None,"talk"),
    ("IMG_9974",26.0,33.0,"exec:Supino"),("IMG_9976",6.0,13.0,"exec:Desenvolvimento"),
    ("IMG_9977",15.0,22.0,"exec:Elevação lateral"),("IMG_9978",6.0,13.0,"exec:Bíceps"),
    ("IMG_9979",0.0,None,"talk"),("IMG_9981",0.0,None,"talk"),("IMG_9985",0.0,None,"talk"),
    ("IMG_9986",0.0,None,"talk"),("IMG_9988",0.0,None,"talk"),
    ("IMG_9990",0.0,10.0,"broll"),("IMG_9993",0.0,10.0,"broll"),
    ("IMG_9999",0.0,None,"talk"),("IMG_0001",0.0,None,"talk"),("IMG_0002",0.0,None,"talk"),
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
    (EDIT/"master3.srt").write_text("\n".join(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n" for k,(a,b,txt) in enumerate(cues,1)))
    print(f"TOTAL {offset:.1f}s | {len(cues)} cues")
    (EDIT/"concat3.txt").write_text("\n".join(f"file '{p.resolve()}'" for p in manifest))
    joined=EDIT/"joined3.mp4"
    r=subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(EDIT/"concat3.txt"),
        "-c","copy","-movflags","+faststart",str(joined)],capture_output=True,text=True)
    if r.returncode: print("ERRO concat\n",r.stderr[-1200:]); sys.exit(1)
    srt_esc=str((EDIT/"master3.srt").resolve()).replace("\\","\\\\").replace(":",r"\:").replace("'",r"\'")
    final=EDIT/"final_v3.mp4"
    r=subprocess.run(["ffmpeg","-y","-i",str(joined),
        "-vf",f"subtitles='{srt_esc}':force_style='{STYLE}'",
        "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",
        "-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",str(final)],capture_output=True,text=True)
    if r.returncode: print("ERRO burn\n",r.stderr[-1200:]); sys.exit(1)
    print("OK ->",final,f"({probe_dur(final):.1f}s)")

if __name__=="__main__": main()
