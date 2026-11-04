"""A/B de gancho: mesmo corpo, ganchos diferentes -> um final por variante (pro Reel de teste decidir).
Uso: python ab_hooks.py <proj> '<kills_json>' '<hooks_json>' [--keep-others] [--fx fx.json]
  hooks_json = {"A": [[s,e]], "B": [[s,e]]}   (tempos na FONTE; [] = ordem original, sem gancho movido)
  Padrao: ganchos sao TAKES ALTERNATIVOS da mesma frase -> o corpo perde todos os ganchos.
  --keep-others: gancho = frase do meio puxada pro inicio (cold open) -> o corpo so perde o gancho da variante.
  --fx fx.json = {"overlays": [{"file": ..., "src_time": t}], "sfx": [{"file": ..., "src_time": t, "db": -6}]}
                 overlay fixo (titulo): {"file": "x/titulo.png", "start_in_output": 0, "duration": "all"}
Cada variante vira <proj>/ab_<nome>/ (src.mov e transcript sao links pro original) e roda
solo_build -> clean_srt -> resync. Saida: <proj>/ab_<nome>/edit/final_sync.mp4
Overlays/SFX do --fx ficam presos na PALAVRA (src_time) e cada variante recalcula o tempo de saida."""
import json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline import out_time

ROOT = Path("/Users/mac-matteo/marketing machine")
TOOLS = Path(__file__).resolve().parent
PY = str(ROOT / "video-use/.venv/bin/python")
BIG = 1e6

proj = sys.argv[1]
kills = json.loads(sys.argv[2])
hooks = json.loads(sys.argv[3])
base = ROOT / proj
fx = json.loads(Path(sys.argv[sys.argv.index("--fx") + 1]).read_text()) if "--fx" in sys.argv else {}
keep_others = "--keep-others" in sys.argv
all_hooks = [r for rs in hooks.values() for r in rs]


def run(*a):
    r = subprocess.run([PY, *map(str, a)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr[-1500:]); raise SystemExit(1)
    return r.stdout.strip()


def variant_dir(name):
    d = base / f"ab_{name}"
    (d / "edit").mkdir(parents=True, exist_ok=True)
    for link, target in [(d / "src.mov", base / "src.mov"), (d / "edit/transcripts", base / "edit/transcripts")]:
        if not link.exists():
            os.symlink(target, link)
    return d


def complement(rs):
    """KILLS que deixam so os trechos rs."""
    out, cur = [], 0.0
    for s, e in sorted(rs):
        out.append([cur, s]); cur = e
    out.append([cur, BIG])
    return out


for name, hook in hooks.items():
    d = variant_dir(name)
    rel = d.relative_to(ROOT)
    # 1) ranges do gancho sozinho (mesmo corte de silencio)
    hook_ranges = []
    if hook:
        run(TOOLS / "solo_build.py", rel, json.dumps(kills + complement(hook)))
        hook_ranges = json.loads((d / "edit/edl.json").read_text())["ranges"]
    # 2) corpo sem o(s) gancho(s)
    print(name, "corpo:", run(TOOLS / "solo_build.py", rel, json.dumps(kills + (hook if keep_others else all_hooks))))
    edl = json.loads((d / "edit/edl.json").read_text())
    edl["ranges"] = hook_ranges + edl["ranges"]
    edl["total_duration_s"] = round(sum(r["end"] - r["start"] for r in edl["ranges"]), 3)
    rr = [(r["start"], r["end"]) for r in edl["ranges"]]
    for key in ("overlays", "sfx"):
        items = []
        for it in fx.get(key, []):
            it = dict(it)
            if "src_time" in it:                      # preso na palavra -> recalcula
                t = out_time(rr, it["src_time"])
                if t is None:
                    continue
                it["start_in_output" if key == "overlays" else "time"] = t
            if it.get("duration") == "all":           # titulo: video todo
                it["duration"] = edl["total_duration_s"]
            if not it["file"].startswith("/"):
                it["file"] = str(base / it["file"])
            items.append(it)
        edl[key] = items
    (d / "edit/edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    run(TOOLS / "clean_srt.py", rel)
    print(name, run(TOOLS / "resync.py", rel), f"({edl['total_duration_s']}s)")
