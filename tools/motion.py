"""Renderiza overlays do Remotion (ProRes 4444 com alpha) a partir de uma lista de eventos.
Uso: python motion.py <proj> <eventos.json> [--scale 2]
eventos.json = [{"id":"x70","comp":"Impacto","props":{"kind":"counter","to":70,"suffix":"%"}}, ...]
  {"id":"titulo","comp":"Titulo","still":true,"props":{"headline":"linha 1\nlinha 2","kicker":"(...)"}} -> PNG
Saida: <proj>/edit/motion/<id>.mov  (scale 2 = fonte 4K vertical 2160x3840; scale 1 = 1080x1920)"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path("/Users/mac-matteo/marketing machine")
REMOTION = ROOT / "motion/remotion"

proj = ROOT / sys.argv[1]
events = json.loads(Path(sys.argv[2]).read_text())
scale = sys.argv[sys.argv.index("--scale") + 1] if "--scale" in sys.argv else "2"
out_dir = proj / "edit/motion"
out_dir.mkdir(parents=True, exist_ok=True)

for ev in events:
    still = ev.get("still", False)
    out = out_dir / f"{ev['id']}.{'png' if still else 'mov'}"
    cmd = ["npx", "remotion", "still" if still else "render", ev.get("comp", "Impacto"), str(out),
           f"--props={json.dumps(ev.get('props', {}), ensure_ascii=False)}", f"--scale={scale}"]
    r = subprocess.run(cmd, cwd=REMOTION, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO", ev["id"], r.stderr[-1500:]); raise SystemExit(1)
    print("OK", out.name)
