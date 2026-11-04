#!/usr/bin/env python3
# Capa e último slide dos rankings: capa sem o "Q" enfeitado do itálico, CTA com BANCO e Black Friday.
# Os demais slides vêm de scripts/enem/post_ranking/gerar_livro.py, no repo do Chiron.
import os
from render_livro import WORK, body_slide, cover_slide

FINAL = [
    "**Salva esse post** pra escolher a prova certa na hora de treinar.",
    "Comenta **“BANCO”** e eu te mando a minha plataforma, com o banco de questões do ENEM.",
    "E fica ligado no meu perfil que teremos a **maior Black Friday de mentorias do Brasil.**",
]

for nome, slug in [("Linguagens", "linguagens"), ("Humanas", "humanas"), ("Natureza", "natureza"), ("Matemática", "matematica")]:
    out = os.path.join(WORK, "..", "output", f"ranking-enem-{slug}")
    img = cover_slide("O ranking das provas", f"do ENEM em {nome}:", seed=3, size=80,
                      hl1=False, hl2=True, sub="(As provas que você deveria | estar treinando, da mais fácil | para a mais difícil)")
    img.save(os.path.join(out, "01.jpg"), quality=94)
    body_slide(FINAL, seed=51).save(os.path.join(out, "06.jpg"), quality=94)
    print("ok", slug)
