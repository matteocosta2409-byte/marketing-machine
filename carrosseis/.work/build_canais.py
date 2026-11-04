"""Canais do YouTube que eu usei — 2 carrosséis (1º e 2º dia do ENEM). Motor em render_canais.py.
Dados dos canais conferidos no YouTube em 2026-10-25."""
import os
from render_canais import channel_slide, cover_slide, cta_slide, ROOT

# (avatar, nome, @, inscritos · vídeos)
CH = {
    "equaciona": ("equaciona.jpg", "Equaciona", "@equacionamatematica", "1,91 mi de inscritos · 2,3 mil vídeos"),
    "boaro": ("boaro.jpg", "Professor Boaro", "@professorboaro", "1,47 mi de inscritos · 2,5 mil vídeos"),
    "universo": ("universo-narrado.jpg", "Universo Narrado", "@UniversoNarrado", "1,25 mi de inscritos · 2 mil vídeos"),
    "goulart": ("guilherme-goulart.jpg", "Guilherme Goulart", "@ProfGuiGoulart", "898 mil inscritos · 1 mil vídeos"),
    "samuel": ("samuel-cunha.jpg", "Samuel Cunha", "@professorsamuelcunha", "1,9 mi de inscritos · 608 vídeos"),
    "cafe": ("cafe-com-quimica.jpg", "Café com Química", "@profmichelquimica", "370 mil inscritos · 568 vídeos"),
    "felipe": ("felipe-pereira.jpg", "Felipe Pereira", "@prof.felipepereira", "77,4 mil inscritos"),
    "parabolica": ("parabolica.jpg", "Parabólica", "@Parabólica", "1,41 mi de inscritos · 2,7 mil vídeos"),
    "marcilio": ("ricardo-marcilio.jpg", "Ricardo Marcílio", "@profricardomarcilio", "1,41 mi de inscritos · 2,8 mil vídeos"),
    "hexag": ("hexag.jpg", "Hexag Solidário", "cursinhoparamedicina.com.br", "apostilas + listas · de graça"),
}

HEXAG = "Cursinho de SP que libera o **material didático inteiro** na internet: apostilas do ano anterior e listas de questões. O complemento perfeito pras aulas."
FOOT = "*E que me fizeram passar em 1º lugar em Medicina, 2x"
SEGUE = "Me segue (@matteo.rocha_) e **salva esse post** pra não perder."

DIA1 = dict(
    out="canais-1-dia",
    title_y=500,  # abaixo do rosto
    cover=(("mirror-selfie-shaka", (0.5, 0.4)),
           "Os canais do ~youtube~ que eu usei pro **1º dia do ENEM**"),
    channels=[  # (foto de fundo, canal, matéria, frase)
        (("livro-aberto-mesa",), "felipe", "Linguagens",
         "Especialista na prova de Linguagens do ENEM. Estudando pelo canal dele, saí de mais ou menos 35 pra **40 acertos no dia oficial.**"),
        (("estudo-noturno-mesa",), "parabolica", "História, Sociologia e Filosofia",
         "Tem vídeo de absolutamente tudo. A playlist de **História do Brasil** varre a matéria inteira em aulas de mais ou menos 1 hora. Dá pra maratonar tranquilamente."),
        (("escritorio-trabalho",), "marcilio", "Geografia",
         "Pegada forte de geografia social, mas explica geopolítica muito bem. Estudei todo o **Oriente Médio** com ele e fez total diferença."),
    ],
    bonus=("biblioteca-cursinho",),
    cta=(("biblioteca-estantes",), "Quer os do 2º dia?",
         ["Matemática, Física, Química e Biologia **já estão no meu perfil.**", SEGUE]),
)

DIA2 = dict(
    out="canais-2-dia",
    title_y=50, title_size=60,  # título nas árvores, acima da cabeça
    cover=(("unb-rosto-pintado", (0.5, 0.4)),
           "Os canais do ~youtube~ que eu usei pro **2º dia do ENEM**"),
    channels=[
        (("estudo-matematica-mesa",), "equaciona", "Matemática",
         "Curso completo de matemática do ensino médio, organizado em playlists. Fechei toda a parte de **polinômios** direto pelo canal dele."),
        (("questoes-monitor",), "boaro", "Física",
         "Módulos completos de física **de graça**, matando toda a base que você precisa."),
        (("cadernos-escritos",), "goulart", "Biologia",
         "Tem tudo o que você precisa, de forma muito aprofundada. Assisti bastante **botânica** com ele e o conteúdo é extremamente palpável."),
        (("estudo-biblioteca-grupo",), "samuel", "Biologia",
         "Outro gigante da biologia, com aula de **praticamente todo o conteúdo** do ensino médio."),
        (("estudo-cafe-tablet",), "cafe", "Química",
         "O canal perfeito pra **descomplicar os conceitos** de química."),
    ],
    bonus=("material-do-not-touch",),
    cta=(("setup-estudo-quarto",), "Quer os do 1º dia?",
         ["Humanas e Linguagens **já estão no meu perfil.**", SEGUE]),
)

def build(c):
    out = os.path.join(ROOT, "output", c["out"])
    os.makedirs(out, exist_ok=True)
    bg, title = c["cover"]
    slides = [cover_slide(bg, title, FOOT, title_y=c["title_y"], title_size=c.get("title_size", 64))]
    n = len(c["channels"])
    for k, (bg, key, subj, cap) in enumerate(c["channels"], 1):
        slides.append(channel_slide(bg, k, n, *CH[key], cap, subject=subj))
    slides.append(channel_slide(c["bonus"], None, None, *CH["hexag"], HEXAG, subject="BÔNUS: material pra treinar"))
    bg, title, body = c["cta"]
    slides.append(cta_slide(bg, title, body))
    for i, s in enumerate(slides, 1):
        s.save(os.path.join(out, f"{i:02d}.jpg"), quality=95)
    print("ok", out, len(slides))

if __name__ == "__main__":
    build(DIA1)
    build(DIA2)
