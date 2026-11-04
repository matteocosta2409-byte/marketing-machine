# Reels colagem ("Deixa eu adivinhar") — ref instagram.com/p/DercufHR25s

Analisado 29/10/2026 (analyze_ref): 30.7s, take único selfie, 170 palavras/min, zero pausa >0.3s, -14 LUFS, SEM título, sem música perceptível.
Formato do texto: "Deixa eu adivinhar." + lista rápida de traços do público (identidade) + "Se você é essa pessoa, parabéns, você encontrou seu perfil" (CTA seguir).

## Edição
- **Cortes**: só silêncio/erro (corte-silencio-metodo). Os "cortes" que o analisador acha são as fotos entrando — câmera é 1 plano.
- **Legenda**: 1 palavra por vez, minúscula, sem pontuação, amarelo-limão #E6EE4A, pequena, no meio do peito (~66% da altura), sem caixa.
  `python tools/clean_srt.py <proj> --palavra` + no edl:
  `"subtitle_style": "FontName=Helvetica,FontSize=9,Bold=0,PrimaryColour=&H004AEEE6,OutlineColour=&H90000000,BorderStyle=1,Outline=0.5,Shadow=0,Alignment=2,MarginV=95"`
  (substitui a itálica branca padrão SÓ nesse formato.)
- **Fotos**: CADA traço falado = 1 foto que entra na palavra, encostada nas anteriores (grupo de 2–3), corte seco, cantos retos, sem borda, sem pop. Grupo some quando o próximo grupo da mesma zona entra. Duas zonas alternando/simultâneas: `topo` (acima da cabeça, ~10–34% H) e `peito` (~66–88% H).
  Fotos sempre já presentes desde ~1s (gancho visual cedo). Imagem inteira, sem crop de rosto/logo. Fotos pessoais primeiro (fotos-pessoais-cards), depois Bing/Pinterest (imagens-aura-pinterest).
  `python tools/colagem.py <proj> edit/colagem.json` (formato no topo do script) → grava overlays no edl → `python tools/resync.py <proj>`.
- **Sem** título, sem Impacto/Remotion, sem SFX (a ref não tem pop).
- Áudio loudnorm -14 (resync já faz). Revisor normal (presets/revisor.md), ignorando a regra de título.

## Gravação (o que depende do Matteo)
- Take único, selfie/câmera na mão ou tripé perto, espaço livre acima da cabeça (fotos do topo).
- Falar rápido, lista de traços concretos e visuais (cada traço vira foto: "Vale do Silício", "Y Combinator", "filosofia").
- Fechar com CTA de identidade ("se você é essa pessoa... encontrou seu perfil").

Teste: solo_idiota/colagem_test/edit/final_sync.mp4 (29/10/2026).
