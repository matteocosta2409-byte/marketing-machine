# Postador do Matteo

Um vídeo → **Reel de teste** (sempre) → você valida → **Reel normal**, + TikTok e YouTube Shorts.
A fila mora no Supabase (projeto `matteo-postador`): **os posts saem com o Mac desligado.**
Desenho copiado da fila `ig_agendamentos` do chiron-gestor (Isaac), num projeto separado.

```
painel:   python3 postador.py painel          → http://127.0.0.1:8766
agendar:  python3 postador.py agendar "<video>" --tipo broll [--quando "29/10 08:00"] --legenda "..." [--tiktok] [--youtube]
fila:     python3 postador.py lista
validar:  python3 postador.py validar <post_id>      (ou no painel: "→ Normal")
```
Ou só fale comigo: "Claude, agenda o vídeo X como b-roll quinta, com TikTok".

## Como funciona
- **Tipos:** `yap-horizontal`, `yap-vertical` (com fotos), `broll`, `caixinha`, `corte-yt`, `outro`.
- **Grade (horário de SP):** teste b-roll 08:00 · corte 12:00 · yap 18:00 · caixinha 21:00.
  Reel normal: 09:30 · 13:30 · 19:30 · 22:00. Mudar: `python3 postador.py config grade_teste '{"broll":"07:30",...}'`.
- Sem `--quando`, o vídeo vai pro próximo dia em que o horário daquele tipo está livre.
- Vídeo > 45 MB ou 4K é comprimido para 1080p antes de subir (o plano grátis aceita 50 MB por arquivo).
- O vídeo sai do armazenamento quando tudo dele terminou. Teste sem decisão por 10 dias também sai.
- Métricas do IG a cada 2 h (views, alcance, salvos, shares, retenção). Fica guardada a foto de **24 h**:
  é ela que o painel compara com a sua mediana (bombou ≥1,5× · flopou ≤0,5×).
- O token do IG é renovado toda segunda (cron).

## Supabase
- Projeto `matteo-postador` (ref `ohfpqozvzduqycyvwvbd`, São Paulo). Tabelas `posts`, `publicacoes`, `config`. Bucket `videos`.
- Função `supabase/functions/postador/index.ts` (cópia local; a versão no ar é a do Supabase).
- Crons: `postador` (minuto a minuto, só quando tem algo pra fazer), `postador-metricas` (2 h), `postador-renovar-ig` (seg 12h).
- `.env` daqui: `SUPABASE_URL` e `POSTADOR_TOKEN` (não compartilhar).

## Conectar as contas

### Instagram — ✓ conectado (28/10/2026)
App Meta **postador-reels** (ID 1655529259260793, modo desenvolvimento), app do Instagram `postador-reels-IG` (ID 1420324992933179).
Permissões: basic, content_publish, manage_insights (+ comments/messages).
Token novo: developers.facebook.com → app → Casos de uso → API do Instagram → Configuração da API com login do Instagram
→ "2. Gerar tokens de acesso" → Gerar token. Depois: colar em `social-catalog/.env` e rodar `python3 postador.py ig-token`.
O cron renova sozinho toda segunda, então isso só é preciso se o token for revogado.

### YouTube Shorts — ✓ conectado (28/10/2026)
Canal "Matteo Rocha | Medicina e Estudos". Projeto Google Cloud `postador-matteo`, app OAuth "Postador Matteo"
**em produção** (não verificado → aviso "app não verificado" no login; o token não expira em 7 dias).
Reconectar: `python3 yt_auth.py receber` + pegar client do console, depois `python3 yt_auth.py login`.
⚠️ Falta a **auditoria da API do YouTube** (formulário "YouTube API Services – Audit and Quota Extension"):
sem ela, os vídeos enviados pela API ficam travados em privado.
Cota: 10.000 unidades/dia (~6 uploads). Vídeo 16:9 vira vídeo comum, não Short.

### TikTok — ✓ conectado no SANDBOX (28/10/2026)
App "Postador Matteo" (ID 7701736345840732181), sandbox "teste", conta de teste @matteo.rocha_.
Login Kit (Desktop, redirect http://localhost:8797/callback/) + Content Posting API com Direct Post.
Escopos: user.info.basic, video.publish, video.upload. Reconectar: `tt_auth.py receber` / `tt_auth.py login`.
Sandbox/sem auditoria = só posta PRIVADO (`tt_privacidade = SELF_ONLY`).
Para produção: o rascunho de produção exige um **vídeo de demonstração** gravado no sandbox + o
painel precisa da tela de postagem nos padrões do TikTok (nome da conta, escolha de privacidade sem
padrão, toggles de comentário/dueto/stitch, divulgação de conteúdo comercial e aviso de uso de música).
Depois de aprovado: refazer o login com a client key de produção e `config tt_privacidade PUBLIC_TO_EVERYONE`.

### Página pública (política de privacidade)
https://ohfpqozvzduqycyvwvbd.supabase.co/storage/v1/object/public/site/privacidade.txt (bucket público `site`;
o Supabase serve HTML como texto puro, por isso é .txt). Subir arquivo: `python3 site/subir.py <arquivo> <nome>`
(função `site-upload`, mesmo token). Prefixo verificado no TikTok. Cópia em Google Doc publicado também.

## Pastas do Drive que o painel lê
`Personal Branding/Reels/New/Edited Reels/**` e `Personal Branding/YouTube/Cortes/**` (crie essa para os cortes do longo).
