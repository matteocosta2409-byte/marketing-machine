"""Export de entrega pro YouTube longo: sobe 1080p -> 4K (lanczos) pra o YT dar o codec/bitrate melhor.
Truque do Jason Cooperson: timeline 1080 -> export 3840x2160. Mesmo gravado em 1080 fica mais nitido no YT.
Uso: python export_yt4k.py <final.mp4> [saida.mp4]   (CRF 18 ~ 35-50 Mbps em talking head; AAC 320k; bt709)
Obs.: arquivo fica ~3x maior; conferir disco livre e upload do Drive (ver vlog-yt-pipeline)."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdr import OUT_TAGS

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_4k.mp4")
cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", "scale=3840:2160:flags=lanczos,format=yuv420p",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-level", "5.1", *OUT_TAGS,
       "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(dst)]
r = subprocess.run(cmd, capture_output=True, text=True)
print("OK ->", dst if r.returncode == 0 else r.stderr[-1500:])
