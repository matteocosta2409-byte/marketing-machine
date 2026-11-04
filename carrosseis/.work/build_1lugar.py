#!/usr/bin/env python3
# Carrossel "4 dicas de estudo de quem passou em 1º lugar em Medicina, 2x" no estilo página de livro.
import os
from render_livro import cover_slide, body_slide, WORK

OUT = os.path.join(WORK, "..", "output", "1lugar-4-decisoes")
os.makedirs(OUT, exist_ok=True)

slides = []

# 1 — capa
slides.append(cover_slide(
    "4 dicas de estudo de quem passou",
    "em 1º lugar em Medicina, 2x:",
    seed=11, hl1=False, hl2=True))

# 2 — intro
slides.append(body_slide([
    "Todo mundo procura o cronograma perfeito, os professores perfeitos, os métodos milagrosos…",
    "Eu sou adepto do **básico MUITO bem feito.**",
    "Isso não exige talento nenhum, só constância e direção.",
], seed=22))

# 3 — dica 1
slides.append(body_slide([
    "**Dica 1: provas antigas, o máximo que puder.**",
    "A maioria dos candidatos faz 2 ou 3 anos de provas antigas. Na prova em que passei em 1º, eu fiz 20 anos.",
    "E nem era tanto sobre treinar mais, eu já sabia bem os conteúdos. Era sobre entender **o padrão de recorrência da prova:** quais temas sempre caem e como caem.",
    "Isso é uma vantagem enorme. Enquanto quem fez menos provas antigas travava em questões difíceis que sempre caem, eu resolvia com facilidade, porque já tinha visto aquele conteúdo várias vezes.",
], seed=33))

# 4 — dica 2
slides.append(body_slide([
    "**Dica 2: flashcards, todo santo dia.**",
    "Terminei o ano em que passei com um baralho de 4 mil cards, e fazia uns 100 por dia, sem falta.",
    "Flashcard de tudo que eu achava que ia esquecer: fórmulas, conceitos importantes, decorebas chatas e questões que errei (funcionava como meu caderno de erros).",
    "Revisar isso todo santo dia me deixava com **a matéria na ponta da língua,** mesmo o que eu tinha estudado meses antes.",
], seed=44))

# 5 — dica 3
slides.append(body_slide([
    "**Dica 3: estude como se precisasse dar uma aula daquela matéria depois.**",
    "Muda completamente a forma como você estuda, porque você precisa ter certeza de que está entendendo tudo. Afinal, vai ter que **explicar em termos simples** depois.",
    "Einstein já dizia: “se você não consegue explicar algo para uma criança, é porque não entendeu direito.”",
], seed=55))

# 6 — dica 4
slides.append(body_slide([
    "**Dica 4: sono é inegociável.**",
    "Eu nunca troquei 1 segundo de sono por estudo. Nenhum.",
    "É no sono que a memória de longo prazo se consolida. Estudar até tarde e dormir 5 horas é **jogar fora parte do que você acabou de estudar** — e destruir seu foco no dia seguinte.",
    "Trocar sono por estudo é o pior negócio do vestibular.",
], seed=66))

# 7 — fechamento
slides.append(body_slide([
    "Resumo: nenhuma dessas 4 dicas tem nada de mirabolante. Muito provavelmente você já ouviu vários aprovados falando isso.",
    "Então se certifica de que, depois desse post, **você vai mudar de comportamento de vez** e começar a aplicar o que aprende nas redes sociais sobre como estudar pra ser aprovado.",
    "**Salva esse post** pra reler na próxima vez que pensar em virar a noite estudando.",
    "E me segue pra mais sobre estudo, vestibular e medicina.",
], seed=77))

for i, s in enumerate(slides, 1):
    p = os.path.join(OUT, f"slide-{i:02d}.jpg")
    s.save(p, quality=92)
    print("ok", p)
