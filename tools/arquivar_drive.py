"""Muda arquivos pesados do Mac pro Drive, organizados, sem apagar nada sem confirmacao.
plan   -> gera manifesto (origem -> destino) em ARQUIVO_DRIVE.json
copy N -> copia o lote N pro Drive e espera subir (xattr item-id do Drive for Desktop)
apaga so com `delete arquivo_com_ids`, depois de conferir na nuvem (search_files)."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

H = Path.home()
MM = H / "marketing machine"
DL = H / "Downloads"
D = H / "Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/Meu Drive/2026"
MAN = MM / "ARQUIVO_DRIVE.json"
MEDIA = {".mov", ".mp4", ".m4v", ".mkv", ".webm", ".mp3", ".wav"}
MIN = 20 * 1024 * 1024
XA = "com.google.drivefs.item-id#S"


def plan():
    its = []
    def add(src, dst, lote):
        its.append({"src": str(src), "dst": str(dst), "size": src.stat().st_size, "lote": lote})
    # 1: midia pesada de projetos antigos (scripts e edl ficam no Mac)
    base = D / "Personal Branding/Arquivo Mac/marketing machine"
    for pasta in sorted(p for p in MM.iterdir() if p.is_dir() and (p.name.startswith("solo_") or p.name in ("cortes", "arco do empreendedor"))):
        for r, _, fs in os.walk(pasta):
            for f in fs:
                p = Path(r) / f
                if p.suffix.lower() in MEDIA and p.stat().st_size >= MIN and not p.is_symlink():
                    add(p, base / p.relative_to(MM), 1)
    # 2: Downloads pesados (nao jogos)
    def dl(nome, dest):
        p = DL / nome
        if p.exists():
            add(p, D / dest / p.name, 2)
    vid = "Personal Branding/Vídeos do Mac"
    for n in ["ENEM d2 - amostra 2min.mp4", "Vlog 1 - dia nos socios (v4).mp4", "IMG_3126.MOV", "o primeiro passo pra passar em medicina.mp4",
              "o que eu faria na reta final pro enem.mp4", "vao te zoar do que voce le (v1 longa).mp4", "o arco do estudante de medicina empreendedor.mp4",
              "quanto custa lancar um app na apple.mp4"]:
        dl(n, vid)
    for n in ["Aula 1 - C1.mp4", "Aula 2 - C2.mp4", "Aula 3 - C3.mp4", "Aula 4 - C4.mp4", "Aula 5 - C5.mp4"]:
        dl(f"AulasRedacao/{n}", "CHIRON Vest/Aulas Redação")
    for n in ["Mario López - Semiologia Médica - 4 Ed.pdf", "Porto - Semiologia médica - 7 Ed - 2014.pdf", "Robbins & Cotran Patologia.pdf"]:
        dl(n, "Livros/Medicina")
    dl("The New Psycho-Cybernetics by Maxwell Maltz  (1).epub", "Livros")
    for n in ["Farmacologia-20261017T171011Z-1-001.zip", "3 Cardiovascular-20261007T160458Z-1-001.zip"]:
        dl(n, "UnB/Estudos")
    for n in ["drive-download-20260908T152848Z-1-001.zip", "drive-download-20260908T152848Z-1-002.zip", "WhatsApp-2.26.35.18.dmg", "KindleForMac-installer-1.40.65626.dmg"]:
        dl(n, "Gaveta/Downloads do Mac")
    # 3: jogos, um a um
    j = "Jogos Wii e Switch"
    for n in ["Compactados/Super Mario Galaxy 2 (USA) (En,Fr,Es).nkit.iso", "Compactados/SMBW.nsp"]:
        p = DL / n
        if p.exists():
            add(p, D / j / p.name, 3)
    for sub, n in [("Super Mario 3D All-Stars (NSP) (Base Game)-2", "Super Mario 3D All-Stars [010049900F546000][v0].nsp"),
                   ("Super Mario Odyssey (Base Game)", "Super Mario Odyssey [0100000000010000][v0].nsp")]:
        p = DL / sub / n
        if p.exists():
            add(p, D / j / sub / n, 3)
    MAN.write_text(json.dumps(its, ensure_ascii=False, indent=1))
    for l in (1, 2, 3):
        x = [i for i in its if i["lote"] == l]
        print(f"lote {l}: {len(x)} arquivos, {sum(i['size'] for i in x) / 2**30:.1f} GB")


def item_id(p):
    r = subprocess.run(["xattr", "-p", XA, str(p)], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def copy(lote):
    its = json.loads(MAN.read_text())
    for it in [i for i in its if i["lote"] == lote]:
        src, dst = Path(it["src"]), Path(it["dst"])
        if it.get("id") or not src.exists():
            continue
        while shutil.disk_usage(H).free < 5 * 2**30:
            print("pausa: menos de 5 GB livres", flush=True)
            time.sleep(60)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and dst.stat().st_size != it["size"]:  # nunca sobrescrever no Drive
            dst = dst.with_name(f"{dst.stem} (mac){dst.suffix}")
            it["dst"] = str(dst)
        if not dst.exists():
            shutil.copyfile(src, dst)
        limite = time.time() + 1800 + it["size"] / 2**30 * 1800
        while not item_id(dst) and time.time() < limite:
            time.sleep(10)
        it["id"] = item_id(dst)
        print(("OK " if it["id"] else "SEM_ID ") + it["id"] + " " + dst.name, flush=True)
        MAN.write_text(json.dumps(its, ensure_ascii=False, indent=1))
    print(f"LOTE {lote} FIM", flush=True)


def delete(path_ids):
    ok = set(json.loads(Path(path_ids).read_text()))  # {id: tamanho} conferidos na nuvem
    tam = json.loads(Path(path_ids).read_text())
    its = json.loads(MAN.read_text())
    n = b = 0
    for it in its:
        src = Path(it["src"])
        if it.get("id") in ok and tam[it["id"]] == it["size"] and src.exists():
            src.unlink()
            it["apagado"] = True
            n += 1
            b += it["size"]
    MAN.write_text(json.dumps(its, ensure_ascii=False, indent=1))
    print(f"apagados {n} arquivos, {b / 2**30:.1f} GB; faltam {sum(1 for i in its if not i.get('apagado'))}")


if __name__ == "__main__":
    a = sys.argv[1]
    plan() if a == "plan" else copy(int(sys.argv[2])) if a == "copy" else delete(sys.argv[2])
