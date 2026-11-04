# Preset: reels-yap (Reels vertical, ele falando pra câmera)

## 1. Entrada
- Bruto chega no Drive `Raw Reels`. iPhone: vertical 2160x3840 (rot 90) ou HDR HLG. Câmera frontal ESPELHADA: manter.
- Normalizar: `ffmpeg -r 30 -i raw -c:v ... <proj>/src.mov` (o `-r 30` na ENTRADA evita PTS quebrado).
- Transcrever: `video-use/helpers/transcribe.py <proj>/src.mov --edit-dir <proj>/edit --language pt`.
- Corrigir **Matheus → Matteo**. "app content" = "yap".

## 2. Corte (ritmo)
- Melhor take de cada frase; retake = ele repete a frase → fica a ÚLTIMA. Fala "corta"/rosnado → cortar o trecho.
- Silêncio: buraco entre palavras ≥0.30 + silencedetect -32dB d=0.18 (combinado; Scribe esconde pausa). KEEP 0.06, PAD 0.04.
- Cabeça virando pro roteiro no fim do take → congelar no último quadro de frente (tpad clone), áudio intacto.
- Muitos cortes → SEMPRE render em passe único (`resync.py`), nunca concat demuxer.
- Validar: nenhuma pausa >0.3s (review_pack checa).

## 3. Legenda
- Branca, itálica, caixa natural, rodapé central, sem caixa (contorno fino + sombra). UMA linha por vez, ≤2 palavras.
- Vertical 2160x3840: FontSize=10, MarginV=45. Horizontal 1920x1080: 15/60.
- Realce de keyword em verde só se ele pedir (#2BE86B, ASS).

## 4. Título (abertura)
- Sempre GANCHO (promessa/tensão, 1ª pessoa), nunca rótulo. Ex.: "Eu li X pra você não precisar".
- SF Pro branca **GRANDE e bold** (74px/800 a 1080, aprovado 28/10/2026 no lugar do pequeno 50/600), topo y≈120,
  sombra forte sem contorno, headline em 2 linhas (quebra manual com \n; >74 quebra em 3) + kicker opcional.
  Gerar: `motion.py` com `{"id":"titulo","comp":"Titulo","still":true,"props":{...}}` → PNG → overlay com `duration`.
- Na tela desde o quadro 0. Variantes de título = A/B (ele já fez: final vs final_B).

## 5. Layout (quando usar o quê)
- Padrão: câmera cheia, gráfico na zona do PEITO (y≈1250–1450 em 1080x1920) ou ao lado da cabeça. NUNCA no rosto.
- Frase de MAIOR impacto: punch-in (scale 1.2, y_offset -50, corte seco), legenda não escala.
- Fala de app/tela: B-roll tela cheia blur-fill na frase; legenda por cima.
- Vídeo 16:9 indo pro Reels: tarjas (imagens em cima, legenda embaixo).
- Quadrado preto gravado (`find_slots.py`) = lugar do gráfico: `Impacto` com `box`.
- Zona da legenda (y>1500) é proibida pra gráfico (review_pack avisa).

## 6. Gráficos (1 por ideia, poucos)
- **Palavra de impacto** (Remotion `Impacto` word): Anton maiúscula, verde #2BE86B, pop spring, 1 por vez.
  Duração = até o FIM da oração (`seconds`), nunca invade a ideia seguinte (ex.: "AÇÃO" sai antes de "inteligência").
  Só nas palavras-chave do argumento (3–5 por Reel de 30s). Nunca todas as palavras.
- **Número** → `Impacto` counter (sobe 0→N): "70%", "10x", "380→940".
- **Ícone de app**: só o ícone (apple-touch-icon), sem barra/texto, só na 1ª menção. Anki = `assets/icons/anki.png`.
- **Imagem/foto**: cantos RETOS, sem pop, sem sombra, corte seco; gancho já no quadro 0; nada em inglês;
  foto pessoal (carrosseis/fotos, cursinho) antes de foto da internet; rosto/logo = imagem inteira, sem crop.
- NÃO usar: explainer de sigla, letter-spacing largo, fonte script, borda arredondada em imagem.

## 7. Áudio
- Voz -14 LUFS, TP -1 (no resync).
- SFX: `assets/sfx/pop.wav` em cada entrada de gráfico/ícone, -6 dB; nunca 2 pops a <0.4s um do outro.
- Música: só se ele pedir; -20 dB sob a voz; royalty-free (Pixabay/YT Audio Library; Uppbeat exige crédito).

## 8. Cor e formato
- Tudo SDR BT.709 via `tools/sdr.py` (HDR do iPhone → foto vermelha se não). Nunca gradear foto.
- FPS saída = entrada (30). Resolução = da fonte.

## 9. Fechamento e entrega
- Termina com CTA "já me segue". Se não gravou: `tools/add_cta.py`.
- Gancho com "comenta [PALAVRA]" → robô de DM (dm-chat) precisa da palavra cadastrada.
- Entrega: Drive `Edited Reels/Semana N - DD-MM-AAAA` (segunda-feira). Postar: Reel de teste primeiro.
