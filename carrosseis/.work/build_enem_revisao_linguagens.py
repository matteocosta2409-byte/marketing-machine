#!/usr/bin/env python3
# 3 carrosséis no estilo página de livro (motor render_livro.py):
# o que eu revisaria na última semana (1º e 2º dia) e como eu estudaria linguagens na semana final.
# Dados: PDFs ENEM_1o/2o_dia_o_que_mais_cai (GPS Chiron, 16 provas, 2018 a 2025).
import os
from render_livro import cover_slide, body_slide, WORK

SEGUE = "Me segue pra mais sobre estudo, vestibular e medicina."
FONTE = "Os números são do GPS Chiron: **16 provas do ENEM,** de 2018 a 2025, regular e PPL."

CARROSSEIS = {
    "revisao-1-dia": [
        ("O que eu revisaria na | última semana pro", "1º dia do ENEM:", "(Para fazer 40 em linguagens | e 42 em humanas*)", "*eram 43, mas errei uma na hora de passar pro gabarito"),
        ["Já fiz **40 em linguagens, 42 em humanas e 940 na redação.**",
         "Na última semana, não dá pra revisar tudo. Se fosse hoje, eu revisaria **só o que mais cai.**",
         FONTE],
        ["**Média de questões por prova:**",
         "Português e Literatura: **33,4**",
         "Geografia: **15,3**",
         "História: **14**",
         "Sociologia: 8,6",
         "Filosofia: 7,1",
         "Artes: 6,6",
         "Inglês ou espanhol: 5"],
        ["**1. Português e Literatura**",
         "80% das questões são de linguística e semântica textual. Eu começaria por **textos jornalísticos (16%), variação linguística (14%) e tipologia textual (13%).**",
         "Depois, tipos de argumento (9%) e coerência e concisão (9%).",
         "Em literatura, o foco seria **Modernismo e literatura contemporânea (18%).**"],
        ["**2. Geografia**",
         "Os grandes temas são **questões ambientais (22%) e agropecuária (21%).**",
         "Eu revisaria primeiro agropecuária brasileira (13%), problemas ambientais do Brasil (12%), problemas urbanos (8%) e sistemas agrários (8%)."],
        ["**3. História**",
         "O que mais cai é **Brasil:** República (27%), Colônia (19%) e Império (16%).",
         "Eu revisaria primeiro **Segundo Reinado (12%) e República Oligárquica (11%).**",
         "Depois, economia colonial e invasões holandesas (6%), e Era Vargas."],
        ["**4. Sociologia**",
         "**Cultura e etnia (27%),** Estado, democracia e cidadania (15%) e movimentos sociais (13%).",
         "**5. Filosofia**",
         "**Filosofia política: justiça e cidadania (18%),** ética e moral (15%) e Aristóteles (9%)."],
        ["**6. Artes**",
         "**Arte contemporânea (28%),** cultura de massa (16%) e panorama histórico da MPB (14%).",
         "**7. Inglês ou espanhol**",
         "Quase tudo é leitura de texto. Gramática isolada praticamente não cai, então eu **não gastaria essa semana decorando regra.**"],
        ["**Salva esse post** pra revisar na semana da prova.",
         "E manda pra alguém que vai fazer o ENEM no dia 8.",
         "Fiz um vídeo completo sobre a semana da prova, e a lista do que mais cai está na descrição. Tá no meu canal do YouTube (link na minha bio).",
         SEGUE],
    ],
    "revisao-2-dia": [
        ("O que eu revisaria na | última semana pro", "2º dia do ENEM:", "(Para fazer 40 em natureza | e 42 em matemática)", None),
        ["Já fiz **82 de 90** no 2º dia: 40 em natureza e 42 em matemática.",
         "Na última semana, não dá pra revisar tudo. Se fosse hoje, eu revisaria **só o que mais cai.**",
         FONTE],
        ["**Média de questões por prova:**",
         "Matemática: **45**",
         "Biologia: **16,4**",
         "Química: **14,6**",
         "Física: **14**",
         "Matemática é **metade da prova.** Se o tempo fosse curto, eu começaria por ela."],
        ["**1. Matemática: o que eu revisaria primeiro**",
         "**Razão, proporção e grandezas proporcionais (23%).** É o assunto que mais cai, disparado.",
         "**Porcentagem (13%).**",
         "**Estatística (13%).**"],
        ["**2. Matemática: o que vem depois**",
         "Funções do 1º grau (7%), cilindros (5%), prismas e volume (4%).",
         "Olhando pelos grandes temas: funções (11%), geometria espacial (11%), geometria plana (10%) e álgebra básica (9%)."],
        ["**3. Biologia**",
         "O maior tema é **ecologia (28%).** Depois vêm citologia (17%), fisiologia humana (15%) e genética (12%).",
         "Eu revisaria primeiro **problemas ambientais (14%),** relações ecológicas (7%) e biotecnologia e engenharia genética (7%)."],
        ["**4. Química**",
         "Eu revisaria primeiro **química descritiva ambiental (14%)** e **estequiometria: pureza, rendimento e excesso (10%).**",
         "Depois, oxirredução (6%), separação de misturas (6%), forças intermoleculares (5%) e pH e pOH (5%)."],
        ["**5. Física**",
         "Os maiores temas são **eletrodinâmica (21%) e dinâmica (19%).** Depois vêm termologia (15%) e ondulatória (14%).",
         "Eu revisaria primeiro **corrente elétrica (11%),** acústica (7%) e associação de resistores (7%)."],
        ["**Salva esse post** pra revisar na semana da prova.",
         "E manda pra alguém que vai fazer o ENEM no dia 15.",
         "Fiz um vídeo completo sobre a semana da prova, e a lista do que mais cai está na descrição. Tá no meu canal do YouTube (link na minha bio).",
         SEGUE],
    ],
    "linguagens-semana-final": [
        ("Como eu estudaria linguagens", "na semana final:", "(Saí de 30-35 acertos em simulados | pra 40 no dia oficial, com | pouquíssimos dias até a prova)", None),
        ["Linguagens nunca foi a minha facilidade. Nos simulados do ano, eu fazia **30, 35 acertos.**",
         "No dia oficial, fiz **40,** e passei dos 700 nessa área.",
         "Se faltasse uma semana de novo, é assim que eu estudaria."],
        ["**1. Pararia de pensar só em \"interpretação\" ou gramática.**",
         "Eu estudaria com base nas **competências e habilidades** da matriz de referência do ENEM.",
         "Cada questão testa uma habilidade, e cada habilidade pertence a uma competência. Quando você entende como a prova é montada, e não só o conteúdo, o rendimento sobe muito."],
        ["**2. Assistiria às aulas do professor Felipe Pereira.**",
         "Estão de graça no YouTube, e ele ensina linguagens exatamente a partir das competências.",
         "Foi no ano em que assisti às aulas de revisão dele que eu fiz **os 40 acertos.**"],
        ["**3. Faria questão separada por competência.**",
         "Não adianta só assistir à aula: eu faria bastante questão de linguagens, **dividida por competência e habilidade.**",
         "As listas estão liberadas na minha plataforma de estudos. O link está na descrição do meu vídeo sobre a semana da prova."],
        ["**4. Revisaria só o que mais cai.**",
         "Das 45 questões, **33,4 são de português e literatura,** em média, e 80% delas são de linguística e semântica textual.",
         "Eu focaria em **textos jornalísticos (16%), variação linguística (14%) e tipologia textual (13%).**",
         "Em inglês ou espanhol, quase tudo é leitura de texto."],
        ["**5. Faria muita questão misturada.**",
         "Linguagens, geografia, sociologia, história, tudo junto, como no 1º dia de verdade.",
         "Assim, os padrões de cobrança ficam **mais frescos na cabeça** e você marca mais rápido no dia da prova."],
        ["**6. Treinaria o jeito de fazer a prova.**",
         "Linguagens, pra mim, era **pouco a pouco, sempre pulando as que travavam.** Eu fazia umas 35 de primeira.",
         "As mais difíceis ficavam pro final, com calma, relendo várias vezes. Eu treinaria exatamente assim nas provas da semana."],
        ["**Salva esse post** pra seguir na semana da prova.",
         "E manda pra alguém que vai fazer o ENEM no dia 8.",
         "Fiz um vídeo completo sobre a semana da prova, tá no meu canal do YouTube (link na minha bio).",
         SEGUE],
    ],
}

if __name__ == "__main__":
    for k, (name, slides) in enumerate(CARROSSEIS.items()):
        out = os.path.join(WORK, "..", "output", name)
        os.makedirs(out, exist_ok=True)
        base = 100 * (k + 5)
        l1, l2, sub, note = slides[0]
        imgs = [cover_slide(l1, l2, seed=base + 1, hl1=False, hl2=True, sub=sub, note=note, size=80)]
        imgs += [body_slide(p, seed=base + 10 * i) for i, p in enumerate(slides[1:], 2)]
        for i, s in enumerate(imgs, 1):
            s.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=92)
        print("ok", name, len(imgs))
