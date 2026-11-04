# Presets de edição do Matteo

Ideia (Jason Cooperson): o Claude não tem gosto de edição sozinho. O gosto do Matteo fica TRAVADO aqui,
então um prompt só ("edita esse bruto com o preset reels-yap") sai pronto pra postar.

**Antes de editar: ler o preset inteiro + `revisor.md`.** Regra nova aprovada? Escrever AQUI (e na memória).

| Arquivo | Pra quê |
|---|---|
| `reels-yap.md` | Reels vertical dele falando (yap): corte, legenda, título, gráficos, SFX, entrega |
| `reels-colagem.md` | "Deixa eu adivinhar": fotos acumulando por palavra (topo/peito), legenda 1 palavra amarela, sem título (ref DercufHR25s) |
| `yt-longo.md` | YouTube horizontal longo e vlog |
| `roteiro.md` | Estrutura de roteiro 40–50s (Gobbi) + regras de gravação |
| `referencia.md` | Como analisar vídeo de referência (números + lupa do gancho) |
| `revisor.md` | Checklist do revisor independente (subagente `revisor-video`) |

## Fluxo de 1 prompt (Reels)
1. Normalizar + transcrever (ver `reels-yap.md` §1).
2. Achar retakes/"corta" → KILLS. Achar quadrados pretos: `tools/find_slots.py src.mov`.
3. `tools/solo_build.py` → `tools/clean_srt.py`.
4. Planejar gráficos (§Gráficos) → `tools/motion.py` (Remotion) → `overlays`/`sfx` no edl.json
   com `tools/timeline.py <proj> <palavra>` pra achar o tempo na timeline cortada.
5. `tools/resync.py` (corte + SDR + overlays + pops + legenda + -14 LUFS, passe único).
6. Título (PIL `animations/title/build.py`) se houver.
7. `tools/review_pack.py final.mp4 --src src.mov` → subagente `revisor-video` → corrigir → repetir (máx 3).
8. Só então mostrar pro Matteo. Gancho alternativo? `tools/ab_hooks.py` → A e B pro Reel de teste.

## Ferramentas
- Motion: **Remotion** (`motion/remotion/`, comp `Impacto`: palavra, contador, painel no quadrado preto) e
  HyperFrames (painéis/cards já calibrados, ver memória hyperframes-overlay). PIL pra título e ícone.
- Plugin Remotion do Claude Code instalado (`/remotion:remotion-create`, captions, render…).
