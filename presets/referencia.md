# Análise de referência

Comando: `python tools/analyze_ref.py <link ou arquivo> --out <scratchpad>/ref_x` (vídeo NÃO fica no PC).
Gera números (cortes/min, plano médio, LUFS, palavras/min, fala dos 10s) + `hook_0-3s.jpg`, `hook_3-10s.jpg`, `shots.jpg`.

Depois eu LEIO as imagens e respondo (prompt Gobbi + lupa claude-watch):
1. Ritmo: cortes/min, palavras/min, pausas removidas?
2. Layout: câmera, gráficos, legenda; quando vai pra tela cheia.
3. Visual: tipografia, cores, estilo dos gráficos.
4. Movimento: como entra/sai, transições.
5. Áudio: LUFS, música, SFX.
6. Gancho quadro a quadro (0–10s): o que muda na tela × o que é falado; tipo de gancho.
7. **O que reproduzo com o pipeline × o que depende do Matteo** (gravar diferente, asset, fonte).

Jump cut de talking head tem score baixo: se os cortes parecerem poucos, rodar com `--scene 0.06`.
