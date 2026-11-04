# Preset: yt-longo (YouTube horizontal) e vlog

## Talking head educacional
- 16:9 1920x1080, SEM título, SEM legenda queimada (srt separado se quiser).
- Cortar silêncio ≥0.5s (ganho principal). EDL automático: `video-use/helpers/generate_edl.py`. Validar 3–5 min antes do todo.
- Gráficos: HyperFrames/Remotion explicativos sincronizados (painel de tópicos, card de app no canto inf. esquerdo).
  Cadência: 1 gráfico a cada ~20–40s, push-in (punch-in) nas frases-chave.
- Música -20 dB sob a voz (opcional). Voz -14 LUFS.
- **Entrega: `tools/export_yt4k.py final.mp4`** → 3840x2160 a partir do 1080 (YouTube dá codec/bitrate melhor
  pra upload 4K = mais nítido). Conferir disco e upload do Drive (arquivo ~3x maior).

## Vlog
- Template `tools/vlog_build5.py`: intro VLOG verde (#3DA35D) trocando fonte, música Sunset Ballin (crédito Uppbeat),
  labels verdes de exercício, legenda itálica, corte do tapa, NÃO cortar silêncio interno.
- Ler brutos copiando pro disco local (mount do Drive corrompe frame). Entrega CRF 23. Prévia 480p.

## Estilo-alvo: Ali Abdaal + Dan Martell (estudado 29/10/2026)
Refs: Ali szVXpM7VVMg, BNRfzI6E1Es, C0jOKDJtK9s · Dan 6poBPhfB-WY (1.7M), DlQyXhjH2jE (1.5M).
Medido (scene-detect, subestima jump cut): Ali corta 1/7s no gancho e 1/10–13s no corpo; Dan 1/2s no gancho e 1/3–4s no corpo.
**Meta do Matteo: base Ali (gráfico explicando) + ritmo/gancho Dan (cold open montado, B-roll, reframe).**

### Gancho (primeiros 30–60s)
- Dan: abre com PERGUNTA + montagem de fotos/B-roll a cada 1–2s com logo/rótulo ("What do these great minds have in common?"
  → Ford, Disney, Musk) → REFRAME em texto riscado ("~~Dropouts~~ → Legends", "~~Save time~~ → Change how life feels")
  → história pessoal com FOTOS DE ARQUIVO dele (efeito filme/VHS, data no canto) → inimigo nomeado ("shelf help")
  → framework com NOME (SELF system, 7 passos) → "Coming up..." com prévia de tela → passo 1.
- Dan contrário: "Most finance content tells you X. Today, the exact opposite."
- Ali: dor + credencial curta ("15 anos, livro best-seller") + agenda numerada em cards (1, 2, 3) ou "13 tips, let's get into it".
- Sem vinheta. Primeira frase já é o gancho, frase de impacto em texto na tela.

### Visual Ali (explicação)
- Fundo creme claro (off-white) com cards brancos de sombra suave; acento coral. Rosto vira card arredondado à direita (= nosso Enem, mas ele usa fundo CLARO).
- Stepper de progresso no topo/meio ("Tip 1 · 2 · 3" com bolinhas numa linha) entre seções = capítulo.
- Ícones 3D/emoji em cards brancos, setas tracejadas ligando conceitos (diagrama nó → nó), ✕ vermelho / ✓ verde comparando.
- Título serif com a palavra-chave colorida em itálico, também por cima do vídeo em tela cheia ("The World's Best *Personal*").
- Pílulas brancas com logo (Google, Reddit, ChatGPT) que surgem ao lado dele na fala.
- Desenho à mão (iPad, caneta verde) por cima do vídeo: curvas, setas, listas numeradas escritas.
- Print de chat/artigo como documento com trecho grifado; B-roll dele trabalhando com rosto em PiP.

### Visual Dan (cinema)
- Cenário quente (madeira, luminárias), câmera fixa + punch-ins frequentes; alterna plano com e sem mesa.
- Gráficos ESCUROS azul-marinho com glow (cards de vidro, botões, UI fake), sans bold branca com sombra.
- Quadro branco filmado de cima, mão escrevendo a lista "7 Things to Buy" — volta a cada item (marcador de capítulo).
- Lower third de pessoa citada: nome bold + cargo pequeno (ex.: "Richard Branson / Founder, Virgin Group").
- Estudo/artigo: print com fundo desfocado e número grifado em laranja ("19.000+ adults over 50").
- Frase-chave em itálico serif com última palavra em cor ("The number one investment is *skills*"); legenda kinetic palavra a palavra só nas frases fortes.
- Pílulas de checklist do lado dele (☑ Learn it ☑ Do it ☑ Teach it), tag "Pro Tip", caixa CTA "Prompt below in the description".
- MUITO B-roll: fotos antigas, vídeos dele na vida (surf, neve), stock cinematográfico; cada frase concreta ganha imagem.

### Regras práticas pra nós
1. Gancho montado estilo Dan: 1 imagem/B-roll a cada 1–2s nos primeiros 20s, reframe riscado, foto pessoal (aprovação UnB, cursinho: ver fotos-pessoais-cards).
2. Framework com nome + stepper fixo (ex.: barra das horas do ENEM) = espinha do vídeo.
3. Nunca >8s de rosto parado sem evento (punch-in, pílula, texto, B-roll). Nunca >2s de card só com título.
4. Gráfico explicativo estilo Ali (card + rosto PiP) para conceitos; B-roll tela cheia estilo Dan para histórias.
5. Números/estudos sempre com fonte na tela (print grifado).
6. Fim: resumo rápido + CTA curto, sem enrolar.
