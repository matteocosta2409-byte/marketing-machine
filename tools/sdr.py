"""Cor certa nos renders: o iPhone grava HDR (HLG/BT.2020). Foto/PNG da internet e sRGB (SDR).
Se o video final sai marcado como HDR, o player interpreta as fotos coladas como HDR e elas
ficam saturadas/avermelhadas (tom de pele vermelho). Regra: TODO render sai SDR BT.709 e toda
imagem RGBA e convertida pra YUV com a matriz BT.709 antes do overlay.

Uso nos builders:
    from sdr import sdr_chain, OUT_TAGS, RGBA_709
    fc.append(f"[cv0]{sdr_chain(src)}[cv]")         # depois do concat
    fc.append(f"[k:v]{RGBA_709},setpts=...[img]")    # cada imagem/PNG antes do overlay
    cmd += OUT_TAGS                                  # nas opcoes de saida do ffmpeg
"""
import subprocess

OUT_TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
RGBA_709 = "format=rgba,scale=out_color_matrix=bt709:out_range=tv,format=yuva420p"
_TIN = {"arib-std-b67": "arib-std-b67", "smpte2084": "smpte2084"}


def transfer(path):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=color_transfer", "-of", "default=nw=1:nk=1", str(path)],
                          capture_output=True, text=True).stdout.strip().strip(",")


def sdr_chain(path):
    """Filtro HDR->SDR BT.709 (tonemap hable, npl=100 = rosto natural). 'null' se ja for SDR."""
    tin = _TIN.get(transfer(path))
    if not tin:
        return "format=yuv420p"
    return (f"zscale=tin={tin}:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
            "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
