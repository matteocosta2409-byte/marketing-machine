"""6 livros que mudaram minha vida — conteúdo. Motor em render_livros_matt.py."""
import os
from render_livros_matt import book_slide, cover_slide

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(ROOT, "livros", "capas")
OUT = os.path.join(ROOT, "output", "6-livros")

COVER = dict(photo=os.path.join(ROOT, "fotos", "mirror-selfie-livro-2.jpg"), rotate=0,
             title="6 livros que\nmudaram\nminha vida:", focus=(0.3, 0.4), size=96, cy=0.865)

# (título, frase de cima, capa, frase de baixo com **destaque**, seta)
# frases aprovadas pelo Matteo em 2026-10-25 (Tolstói = rascunho que ele aprovou)
BOOKS = [
    ("O Almanaque de Naval Ravikant", "Investidor-anjo do Twitter e da Uber e cofundador da AngelList.",
     "almanaque-naval-ravikant.jpg",
     "Mudou meu jeito de pensar dinheiro. **Um livro que eu, sem dúvida, vou reler.**", "left"),
    ("Crime e Castigo", "Minha introdução aos clássicos.",
     "crime-e-castigo.jpg",
     "Sempre que alguém me pergunta qual é meu livro favorito de literatura, **é o primeiro que me vem à mente.**", "bottom_right"),
    ("Por Que Nós Dormimos", "Eu achava que dormir pouco era sinal de esforço.",
     "por-que-nos-dormimos.jpg",
     "Se eu pudesse dar um conselho pra quem quer melhorar em qualquer área da vida, seria: **priorize o seu sono.**", "down"),
    ("O Mito do Empreendedor", "O livro que me apresentou ao empreendedorismo.",
     "mito-do-empreendedor.jpg",
     "Essencial pra qualquer founder. Mostra que **ser bom em algo não tem nada a ver com ter sucesso com uma empresa daquele nicho.**", "right"),
    ("O Verdadeiro Criador de Tudo", "O autor foi nomeado em 2004 pela Scientific American um dos 20 maiores cientistas da atualidade.",
     "o-verdadeiro-criador-de-tudo.jpg",
     "Pouquíssimo valorizado no Brasil, mas é de um autor que eu gosto muito. **Vale muito a leitura.**", "bottom_left"),
    ("De Quanta Terra Precisa o Homem?", "Um conto curto do Tolstói. Dá pra ler numa tarde.",
     "de-quanta-terra-precisa-um-homem-kindle.jpg",
     "Me fez repensar **o quanto é suficiente** antes de querer sempre mais.", "left"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cover_slide(**COVER).save(os.path.join(OUT, "01.jpg"), quality=95)
    for i, (t, top, cap, bot, arr) in enumerate(BOOKS, 2):
        book_slide(t, top, os.path.join(CAPAS, cap), bot, arr, seed=i).save(os.path.join(OUT, f"{i:02d}.jpg"), quality=95)
    print("ok", OUT)
