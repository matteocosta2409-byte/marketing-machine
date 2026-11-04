# Checklist do revisor (subagente `revisor-video`)

Entrada: pasta `review/` do `tools/review_pack.py` (review.md + hook.jpg, timeline.jpg, ev_*.jpg) e o edl.json.
O revisor NÃO edita; devolve lista de defeitos com tempo e correção sugerida. Severidade: BLOQUEIA / AJUSTE / OK.

## Automático (review.md): tudo em "ATENÇÃO" é defeito
Cor bt709, FPS = fonte, -14 LUFS ±1, TP ≤ -1, sem pausa >0.3s, legenda sem sobreposição/duplicada, sem "Matheus".

## Olhando os quadros
- [ ] Gancho: título/imagem já na tela no quadro 0? Título é gancho (não rótulo)?
- [ ] Nenhum gráfico/ícone/imagem cobre o ROSTO (olhos/boca).
- [ ] Gráfico não encosta na legenda (zona inferior) nem no título (topo).
- [ ] Legenda: 1 linha, itálica branca, legível, sem palavra cortada.
- [ ] Palavra de impacto: poucas, uma por vez, verde #2BE86B, faz sentido com a fala do momento.
- [ ] Imagens: cantos retos, sem pop, sem texto em inglês, sem marca d'água, cor natural (não avermelhada).
- [ ] Cortes: sem pulo de cabeça virando pro roteiro no fim de take; sem quadro preto/congelado longo.
- [ ] Fim: tem CTA.
