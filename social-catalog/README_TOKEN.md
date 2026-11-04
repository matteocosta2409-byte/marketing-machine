# Como gerar o token do Instagram (pra eu ver o que você já postou)

Isso só precisa ser feito **uma vez** (o token dura ~60 dias; depois é só renovar).
Pré-requisito: seu Instagram tem que ser conta **Profissional** (Criador ou Empresa).

## Passo a passo (jeito mais rápido — Graph API Explorer)

1. **Conta profissional + Página do Facebook**
   - No app do Instagram: Configurações → Conta → mudar para conta **Profissional** (Criador serve).
   - Garanta que ela está **vinculada a uma Página do Facebook** (Configurações do IG → Compartilhamento em outros apps / Página). Pode ser uma Página nova, só pra isso.

2. **Criar um app na Meta**
   - Acesse https://developers.facebook.com/ → **My Apps** → **Create App**.
   - Tipo: **Business**. Dê um nome qualquer (ex: "catalogo-matteo").
   - No painel do app → **Add Product** → adicione **Instagram** (Instagram Graph API).

3. **Gerar o token no Graph API Explorer**
   - Abra https://developers.facebook.com/tools/explorer/
   - Em "Meta App" selecione seu app.
   - Clique em **Add a Permission** e marque (pra VER o que foi postado **e POSTAR**):
     `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
     `pages_read_engagement`, `business_management`.
   - Clique **Generate Access Token** e autorize com sua conta (escolha a Página e o IG vinculado).
   - Copie o token que aparece. ⚠️ Esse é de curta duração (1–2h).

4. **Transformar em token de longa duração (~60 dias)**
   - Pegue `META_APP_ID` e `META_APP_SECRET` em: painel do app → **Settings → Basic**.
   - Rode (troque os 3 valores):
     ```
     curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=SEU_APP_ID&client_secret=SEU_APP_SECRET&fb_exchange_token=TOKEN_CURTO"
     ```
   - A resposta traz `access_token` — esse é o **longo**.

5. **Colar no .env**
   - Copie `social-catalog/.env.example` para `social-catalog/.env`
   - Cole o token longo em `IG_ACCESS_TOKEN=`
   - Pode deixar `IG_USER_ID=` vazio (o script descobre).

6. Me avise — com o token no `.env` eu consigo:
   - **Ver** o que já foi postado: `python social-catalog/fetch_ig.py` (atualiza o painel/catálogo)
   - **Postar** um Reel: `python social-catalog/post_ig.py "<video.mp4>" --caption "..."`
   - **Postar um Reel de TESTE**: `... --trial` (graduação MANUAL no app) ou `--trial --strategy SS_PERFORMANCE` (gradua sozinho se performar)
   - Você só me fala: "Claude, posta o X como reel" ou "como reel de teste" que eu rodo.

## Como funciona a postagem (por baixo)
- O vídeo fica no seu Drive (local). A Graph API da Meta precisa **baixar** o vídeo de uma URL pública.
- Eu subo um **túnel temporário** com o `cloudflared` (binário em `social-catalog/bin/`, sem conta) que expõe o arquivo por alguns minutos; a Meta baixa, publica, e o túnel cai.
- ⚠️ O ambiente do Claude Code pede **permissão** pra abrir esse túnel (aparece "External Ingress Tunnel"). Na hora de postar, é só aprovar.
- Limite da Meta: ~100 posts/24h. Reel de teste não tem endpoint de "graduar" na API — graduação é MANUAL no app ou automática (SS_PERFORMANCE).

## Renovar (a cada ~60 dias)
É só repetir os passos 3 e 4 e colar o novo token no `.env`. Me avisa que eu rodo de novo.

> Dica: se preferir, dá pra usar o fluxo mais novo "Instagram API com Instagram Login"
> (gera token direto pela conta IG, sem Página do FB). Me fala que eu te passo esse caminho.
