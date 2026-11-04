// postador — fila de posts do Matteo (IG Reel de teste → validação → Reel normal, TikTok, Shorts).
//
// Mesmo desenho do ig-agendador do chiron-gestor (Isaac): a API do Instagram não agenda,
// então a fila fica no banco e o pg_cron chama esta função de minuto em minuto.
//
// FLUXO DE UM POST
//   1. agendar: cria o post + publicações (ig_teste sempre; tiktok/youtube se pedir).
//   2. ig_teste sai no horário como Reel de TESTE (trial_params MANUAL: só não-seguidores).
//   3. Matteo olha o desempenho no painel e decide:
//        validar   → cria a publicação ig_normal (Reel normal, no feed) no próximo horário da grade
//        descartar → fim; o vídeo sai do bucket
//   4. O vídeo sai do bucket quando não há mais nada a fazer com ele (plano grátis = 1 GB).
//
// ESTADOS DE CADA PUBLICAÇÃO
//   pendente → criando → preparando → publicando → publicado   (ou erro / cancelado)
//   Travou no meio (criando/publicando há >10 min) = erro, sem repostar sozinho (evita duplicado).
//
// POST {}                       → rodada normal (cron)
// POST { acao: "metricas" }     → puxa insights dos posts dos últimos 10 dias (cron a cada 2 h)
// POST { acao: "renovar" }      → renova o token do Instagram (cron semanal)
// POST { acao: ... }            → API do painel/CLI (ver "api" lá embaixo)
// Toda chamada precisa do cabeçalho x-postador-token = config.postador_token.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

const GRAPH = "https://graph.instagram.com/v23.0";
const TIKTOK = "https://open.tiktokapis.com/v2";
const BUCKET = "videos";
const ANTECEDENCIA_MIN = 15; // IG/YouTube: prepara antes, publica na hora
const MAX_TENTATIVAS = 3;
const DESTINOS = ["ig_teste", "ig_normal", "tiktok", "youtube"];
const FINAIS = ["publicado", "erro", "cancelado"];

type Post = {
  id: string; tipo: string; titulo: string; legenda: string; youtube_titulo: string | null;
  arquivo: string | null; publicar_em: string | null; decisao: string | null;
};
type Pub = {
  id: string; post_id: string; destino: string; publicar_em: string; status: string;
  container_id: string | null; media_id: string | null; tentativas: number;
  atualizado_em: string; publicado_em: string | null; metricas: Record<string, unknown> | null;
  posts?: Post;
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

// ---------------------------------------------------------------- config -----
async function cfg(chave: string): Promise<string> {
  const { data } = await supabase.from("config").select("valor").eq("chave", chave).maybeSingle();
  return data?.valor ?? "";
}
async function setCfg(chave: string, valor: string) {
  await supabase.from("config").upsert({ chave, valor, atualizado_em: new Date().toISOString() });
}
const cfgJson = async <T>(chave: string, padrao: T): Promise<T> => {
  try { return JSON.parse(await cfg(chave)) as T; } catch { return padrao; }
};

// Muda o status só se a linha ainda estiver no status esperado (duas rodadas não pegam a mesma).
async function trocar(p: Pub, de: string, campos: Record<string, unknown>): Promise<boolean> {
  const { data } = await supabase.from("publicacoes")
    .update({ ...campos, atualizado_em: new Date().toISOString() })
    .eq("id", p.id).eq("status", de).select("id");
  return (data ?? []).length > 0;
}

async function falhou(p: Pub, de: string, motivo: string) {
  const tent = p.tentativas + 1;
  await trocar(p, de, {
    status: tent >= MAX_TENTATIVAS ? "erro" : "pendente",
    erro: motivo, tentativas: tent, container_id: null,
  });
}

// -------------------------------------------------------------- instagram ----
async function graph(path: string, params: Record<string, string> = {}, metodo = "GET") {
  const corpo = new URLSearchParams({ ...params, access_token: await cfg("ig_token") });
  const res = metodo === "GET"
    ? await fetch(`${GRAPH}/${path}?${corpo}`)
    : await fetch(`${GRAPH}/${path}`, { method: "POST", body: corpo });
  const dados = await res.json().catch(() => ({}));
  if (!res.ok || dados.error) throw new Error(dados.error?.message ?? `HTTP ${res.status}`);
  return dados;
}

async function linkVideo(post: Post): Promise<string> {
  if (!post.arquivo) throw new Error("o vídeo já saiu do bucket");
  const { data, error } = await supabase.storage.from(BUCKET).createSignedUrl(post.arquivo, 3 * 3600);
  if (error || !data) throw new Error(`link do vídeo: ${error?.message ?? "sem link"}`);
  return data.signedUrl;
}

async function criarContainerIG(p: Pub, post: Post): Promise<string> {
  const params: Record<string, string> = {
    media_type: "REELS",
    video_url: await linkVideo(post),
    caption: post.legenda,
    share_to_feed: "true",
  };
  // Teste = só para não-seguidores. MANUAL: nunca gradua sozinho (o "normal" é um post à parte).
  if (p.destino === "ig_teste") params.trial_params = JSON.stringify({ graduation_strategy: "MANUAL" });
  const r = await graph(`${await cfg("ig_user_id")}/media`, params, "POST");
  return r.id as string;
}

// ---------------------------------------------------------------- youtube ----
async function tokenYouTube(): Promise<string> {
  const [id, secret, refresh] = await Promise.all([cfg("yt_client_id"), cfg("yt_client_secret"), cfg("yt_refresh_token")]);
  if (!id || !secret || !refresh) throw new Error("YouTube não conectado (faltam yt_client_id/yt_client_secret/yt_refresh_token)");
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    body: new URLSearchParams({ client_id: id, client_secret: secret, refresh_token: refresh, grant_type: "refresh_token" }),
  });
  const d = await res.json().catch(() => ({}));
  if (!res.ok || !d.access_token) throw new Error(`token do YouTube: ${d.error_description ?? d.error ?? res.status}`);
  return d.access_token as string;
}

// Upload resumable. Vertical e até 3 min = Short. Futuro: privado + publishAt (o YouTube publica na hora).
async function enviarYouTube(p: Pub, post: Post): Promise<string> {
  const token = await tokenYouTube();
  if (!post.arquivo) throw new Error("o vídeo já saiu do bucket");
  const { data: video, error } = await supabase.storage.from(BUCKET).download(post.arquivo);
  if (error || !video) throw new Error(`baixar vídeo: ${error?.message ?? "sem arquivo"}`);
  const quando = new Date(p.publicar_em);
  const status = quando.getTime() > Date.now() + 2 * 60_000
    ? { privacyStatus: "private", publishAt: quando.toISOString(), selfDeclaredMadeForKids: false }
    : { privacyStatus: "public", selfDeclaredMadeForKids: false };
  const tipo = video.type || "video/mp4";
  const titulo = (post.youtube_titulo || post.titulo).slice(0, 100);
  const inicio = await fetch(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": tipo,
        "X-Upload-Content-Length": String(video.size),
      },
      body: JSON.stringify({
        snippet: {
          title: titulo, description: post.legenda.slice(0, 4900), categoryId: "27", // 27 = Educação
          defaultLanguage: "pt-BR", defaultAudioLanguage: "pt-BR",
        },
        status,
      }),
    },
  );
  const destino = inicio.headers.get("location");
  if (!inicio.ok || !destino) {
    const d = await inicio.json().catch(() => ({}));
    throw new Error(`YouTube: ${d.error?.message ?? `HTTP ${inicio.status}`}`);
  }
  const envio = await fetch(destino, { method: "PUT", headers: { "Content-Type": tipo }, body: video });
  const d = await envio.json().catch(() => ({}));
  if (!envio.ok || !d.id) throw new Error(`YouTube: ${d.error?.message ?? `HTTP ${envio.status}`}`);
  return d.id as string;
}

// ----------------------------------------------------------------- tiktok ----
// Access token dura 24 h; o refresh token (365 dias) pode girar a cada renovação.
async function tokenTikTok(): Promise<string> {
  const expira = Number(await cfg("tt_access_expira") || 0);
  const atual = await cfg("tt_access_token");
  if (atual && expira > Date.now() + 5 * 60_000) return atual;
  const [key, secret, refresh] = await Promise.all([cfg("tt_client_key"), cfg("tt_client_secret"), cfg("tt_refresh_token")]);
  if (!key || !secret || !refresh) throw new Error("TikTok não conectado (faltam tt_client_key/tt_client_secret/tt_refresh_token)");
  const res = await fetch(`${TIKTOK}/oauth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ client_key: key, client_secret: secret, grant_type: "refresh_token", refresh_token: refresh }),
  });
  const d = await res.json().catch(() => ({}));
  if (!res.ok || !d.access_token) throw new Error(`token do TikTok: ${d.error_description ?? d.error ?? res.status}`);
  await setCfg("tt_access_token", d.access_token);
  await setCfg("tt_access_expira", String(Date.now() + Number(d.expires_in ?? 86400) * 1000));
  if (d.refresh_token) await setCfg("tt_refresh_token", d.refresh_token);
  return d.access_token as string;
}

async function tiktok(path: string, token: string, body: unknown) {
  const res = await fetch(`${TIKTOK}/${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json; charset=UTF-8" },
    body: JSON.stringify(body),
  });
  const d = await res.json().catch(() => ({}));
  if (!res.ok || (d.error?.code && d.error.code !== "ok")) {
    throw new Error(`TikTok: ${d.error?.message || d.error?.code || `HTTP ${res.status}`}`);
  }
  return d.data ?? {};
}

// Direct Post com FILE_UPLOAD (o PULL_FROM_URL exige domínio verificado no TikTok).
// Até ≤64 MB vai num pedaço só; o bucket já limita a 50 MB.
// App sem auditoria do TikTok: só posta como privado (tt_privacidade = SELF_ONLY).
async function enviarTikTok(post: Post): Promise<string> {
  const token = await tokenTikTok();
  if (!post.arquivo) throw new Error("o vídeo já saiu do bucket");
  const { data: video, error } = await supabase.storage.from(BUCKET).download(post.arquivo);
  if (error || !video) throw new Error(`baixar vídeo: ${error?.message ?? "sem arquivo"}`);
  const tamanho = video.size;
  const ini = await tiktok("post/publish/video/init/", token, {
    post_info: {
      title: post.legenda.slice(0, 2200),
      privacy_level: (await cfg("tt_privacidade")) || "SELF_ONLY",
      disable_comment: false, disable_duet: false, disable_stitch: false,
    },
    source_info: { source: "FILE_UPLOAD", video_size: tamanho, chunk_size: tamanho, total_chunk_count: 1 },
  });
  const envio = await fetch(ini.upload_url, {
    method: "PUT",
    headers: {
      "Content-Type": video.type || "video/mp4",
      "Content-Length": String(tamanho),
      "Content-Range": `bytes 0-${tamanho - 1}/${tamanho}`,
    },
    body: video,
  });
  if (!envio.ok) throw new Error(`TikTok upload: HTTP ${envio.status}`);
  return ini.publish_id as string;
}

// ----------------------------------------------------------------- rodada ----
async function postDe(id: string): Promise<Post> {
  const { data, error } = await supabase.from("posts").select("*").eq("id", id).single();
  if (error || !data) throw new Error(`post ${id} não encontrado`);
  return data as Post;
}

async function rodada() {
  const agora = Date.now();
  const log: string[] = [];

  // 1) travados no meio (a função caiu): não republica sozinho
  const { data: travados } = await supabase.from("publicacoes").select("*")
    .in("status", ["criando", "publicando"])
    .lt("atualizado_em", new Date(agora - 10 * 60_000).toISOString());
  for (const p of (travados ?? []) as Pub[]) {
    await trocar(p, p.status, { status: "erro", erro: `parou em '${p.status}' — conferir se saiu antes de repostar` });
    log.push(`${p.destino} ${p.id} travado`);
  }

  // 2) pendentes perto da hora. TikTok não agenda: só sai na hora exata.
  const { data: pendentes } = await supabase.from("publicacoes").select("*, posts(*)")
    .eq("status", "pendente")
    .lte("publicar_em", new Date(agora + ANTECEDENCIA_MIN * 60_000).toISOString())
    .order("publicar_em").limit(8);
  let uploadsPesados = 0; // YouTube/TikTok baixam o vídeo inteiro: um por rodada
  for (const p of (pendentes ?? []) as Pub[]) {
    const post = p.posts!;
    if (p.destino === "tiktok" && new Date(p.publicar_em).getTime() > agora) continue;
    if (new Date(p.publicar_em).getTime() < agora - 3 * 3600_000) {
      await trocar(p, "pendente", { status: "erro", erro: "perdeu o horário (mais de 3 h de atraso) — reagendar" });
      log.push(`${p.destino} ${p.id} atrasado`);
      continue;
    }
    if (p.destino !== "ig_teste" && p.destino !== "ig_normal") {
      if (uploadsPesados++ > 0) continue;
    }
    if (!(await trocar(p, "pendente", { status: "criando" }))) continue;
    try {
      if (p.destino === "youtube") {
        const id = await enviarYouTube(p, post);
        await trocar(p, "criando", {
          status: "publicado", media_id: id, permalink: `https://youtube.com/shorts/${id}`,
          publicado_em: p.publicar_em, erro: null,
        });
        log.push(`youtube ${p.id} → ${id}`);
      } else if (p.destino === "tiktok") {
        const id = await enviarTikTok(post);
        await trocar(p, "criando", { status: "preparando", container_id: id, erro: null });
        log.push(`tiktok ${p.id} enviado ${id}`);
      } else {
        const id = await criarContainerIG(p, post);
        await trocar(p, "criando", { status: "preparando", container_id: id, erro: null });
        log.push(`${p.destino} ${p.id} container ${id}`);
      }
    } catch (e) {
      const msg = (e as Error).message;
      // YouTube/TikTok: uma tentativa só (o envio pode ter entrado mesmo com erro de resposta).
      if (p.destino === "youtube" || p.destino === "tiktok") {
        await trocar(p, "criando", { status: "erro", erro: msg, tentativas: p.tentativas + 1 });
      } else {
        await falhou(p, "criando", `criar container: ${msg}`);
      }
      log.push(`${p.destino} ${p.id} erro: ${msg}`);
    }
  }

  // 3) preparando → publica (IG) ou confere (TikTok)
  const { data: preparando } = await supabase.from("publicacoes").select("*")
    .eq("status", "preparando").order("publicar_em");
  // A API do IG tem limite de chamadas por hora (~200): consultar todo container a cada minuto estoura
  // e aí o publish volta "unexpected error". Só consulta o que já está na hora, 2 por rodada, 1 publish.
  let publicouIG = false, consultasIG = 0;
  for (const p of (preparando ?? []) as Pub[]) {
    if (p.destino === "tiktok") {
      try {
        const token = await tokenTikTok();
        const st = await tiktok("post/publish/status/fetch/", token, { publish_id: p.container_id });
        if (st.status === "PUBLISH_COMPLETE" || st.status === "SEND_TO_USER_INBOX") {
          const idPost = (st.publicaly_available_post_id ?? [])[0];
          await trocar(p, "preparando", {
            status: "publicado", media_id: idPost ? String(idPost) : p.container_id,
            publicado_em: new Date().toISOString(), erro: null,
          });
          log.push(`tiktok ${p.id} publicado`);
        } else if (st.status === "FAILED") {
          await trocar(p, "preparando", { status: "erro", erro: `TikTok: ${st.fail_reason ?? "falhou"}` });
        } else if (new Date(p.atualizado_em).getTime() < agora - 30 * 60_000) {
          await trocar(p, "preparando", { status: "erro", erro: `TikTok parado em ${st.status}` });
        }
      } catch (e) {
        log.push(`tiktok ${p.id} status: ${(e as Error).message}`);
      }
      continue;
    }

    if (new Date(p.publicar_em).getTime() > agora || publicouIG || consultasIG++ >= 2) continue;
    let st: { status_code?: string; status?: string };
    try {
      st = await graph(p.container_id!, { fields: "status_code,status" });
    } catch (e) {
      log.push(`${p.id} status: ${(e as Error).message}`);
      continue;
    }
    if (st.status_code === "ERROR" || st.status_code === "EXPIRED") {
      await falhou(p, "preparando", `processamento: ${st.status ?? st.status_code}`);
      continue;
    }
    if (st.status_code !== "FINISHED") {
      log.push(`${p.destino} ${p.id} ${st.status_code} aguardando`);
      continue;
    }
    if (!(await trocar(p, "preparando", { status: "publicando" }))) continue;
    publicouIG = true;
    try {
      const pub = await graph(`${await cfg("ig_user_id")}/media_publish`, { creation_id: p.container_id! }, "POST");
      let permalink: string | null = null;
      try { permalink = (await graph(pub.id, { fields: "permalink" })).permalink ?? null; } catch { /* conforto */ }
      await trocar(p, "publicando", {
        status: "publicado", media_id: pub.id, permalink, publicado_em: new Date().toISOString(), erro: null,
      });
      log.push(`${p.destino} ${p.id} publicado ${pub.id}`);
    } catch (e) {
      const msg = (e as Error).message;
      // Limite de chamadas = o pedido nem foi executado: volta e tenta na próxima rodada.
      if (/request limit/i.test(msg)) { await trocar(p, "publicando", { status: "preparando" }); continue; }
      // Fora isso não volta pra fila: o publish pode ter saído mesmo com erro de resposta.
      await trocar(p, "publicando", { status: "erro", erro: `publicar: ${msg} — conferir no IG` });
    }
  }

  await limpar(log);
  await fotoSeguidores(log);
  return log;
}

// Total de seguidores 1x por hora: o "follower_count" diário da Meta chega com 1–2 dias de atraso,
// então o painel usa a diferença entre essas fotos pros dias que a Meta ainda não fechou.
async function fotoSeguidores(log: string[]) {
  const { data } = await supabase.from("seguidores").select("em").order("em", { ascending: false }).limit(1);
  if (data?.[0] && Date.now() - new Date(data[0].em).getTime() < 55 * 60_000) return;
  try {
    const me = await graph("me", { fields: "followers_count" });
    await supabase.from("seguidores").insert({ total: me.followers_count });
  } catch (e) {
    log.push(`seguidores: ${(e as Error).message}`);
  }
}

// O vídeo sai do bucket assim que todas as publicações chegam num estado final (o bucket grátis é 1 GB
// e um lote de 40 cortes passa disso). Se validar depois, o postador.py sobe de novo do Drive ("anexar").
async function limpar(log: string[]) {
  const { data } = await supabase.from("posts").select("id, arquivo, decisao, publicacoes(destino, status, publicado_em)")
    .not("arquivo", "is", null).limit(50);
  for (const post of data ?? []) {
    const pubs = (post.publicacoes ?? []) as { destino: string; status: string; publicado_em: string | null }[];
    if (!pubs.length || pubs.some((x) => !FINAIS.includes(x.status))) continue;
    if (pubs.some((x) => x.status === "erro")) continue; // dá pra repostar sem subir de novo
    await supabase.storage.from(BUCKET).remove([post.arquivo]).catch(() => null);
    await supabase.from("posts").update({ arquivo: null }).eq("id", post.id);
    log.push(`${post.id} vídeo apagado do bucket`);
  }
}

// --------------------------------------------------------------- métricas ----
const METRICAS_IG = ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions",
  "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"];

async function insightsIG(mediaId: string): Promise<Record<string, number>> {
  const ler = (d: { data?: { name: string; values?: { value: number }[]; total_value?: { value: number } }[] }) =>
    Object.fromEntries((d.data ?? []).map((m) => [m.name, m.total_value?.value ?? m.values?.[0]?.value ?? 0]));
  try {
    return ler(await graph(`${mediaId}/insights`, { metric: METRICAS_IG.join(",") }));
  } catch {
    // Meta muda nome de métrica sem aviso: uma por uma, ignorando as que falharem.
    const out: Record<string, number> = {};
    for (const m of METRICAS_IG) {
      try { Object.assign(out, ler(await graph(`${mediaId}/insights`, { metric: m }))); } catch { /* sem essa */ }
    }
    return out;
  }
}

async function metricas() {
  const log: string[] = [];
  const { data } = await supabase.from("publicacoes").select("*")
    .eq("status", "publicado").not("media_id", "is", null)
    .gte("publicado_em", new Date(Date.now() - 10 * 86400_000).toISOString())
    .or(`metricas_em.is.null,metricas_em.lt.${new Date(Date.now() - 100 * 60_000).toISOString()}`)
    .limit(30);
  for (const p of (data ?? []) as Pub[]) {
    try {
      let m: Record<string, unknown> = {};
      if (p.destino.startsWith("ig_")) m = await insightsIG(p.media_id!);
      else if (p.destino === "youtube") {
        const r = await fetch(`https://www.googleapis.com/youtube/v3/videos?part=statistics&id=${p.media_id}`,
          { headers: { Authorization: `Bearer ${await tokenYouTube()}` } });
        const s = (await r.json()).items?.[0]?.statistics ?? {};
        m = { views: Number(s.viewCount ?? 0), likes: Number(s.likeCount ?? 0), comments: Number(s.commentCount ?? 0) };
      } else continue; // TikTok: precisa do escopo video.list (fase 2)
      // Foto de 24 h: é ela que se compara na hora de validar (todo teste com o mesmo tempo de vida).
      const idadeH = (Date.now() - new Date(p.publicado_em!).getTime()) / 3600_000;
      const antigas = (p.metricas ?? {}) as Record<string, unknown>;
      const novo: Record<string, unknown> = { ...m, h24: antigas.h24 ?? (idadeH >= 22 ? m : undefined) };
      await supabase.from("publicacoes").update({ metricas: novo, metricas_em: new Date().toISOString() }).eq("id", p.id);
      log.push(`${p.destino} ${p.id} ok`);
    } catch (e) {
      log.push(`${p.destino} ${p.id} métricas: ${(e as Error).message}`);
    }
  }
  return log;
}

// Token do Instagram (login do Instagram) dura 60 dias; renovar toda semana mantém vivo.
async function renovar() {
  const tok = await cfg("ig_token");
  const r = await fetch(`https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${tok}`);
  const d = await r.json().catch(() => ({}));
  if (!r.ok || !d.access_token) throw new Error(d.error?.message ?? `HTTP ${r.status}`);
  await setCfg("ig_token", d.access_token);
  return { ok: true, expira_em_dias: Math.round(Number(d.expires_in ?? 0) / 86400) };
}

// ------------------------------------------------------------------- api -----
// Horário de São Paulo (UTC-3 fixo, sem horário de verão desde 2019).
function proximoHorario(hhmm: string, depoisDe: number): string {
  const dia = new Date(depoisDe - 3 * 3600_000).toISOString().slice(0, 10);
  let t = new Date(`${dia}T${hhmm}:00-03:00`).getTime();
  while (t < depoisDe) t += 86400_000;
  return new Date(t).toISOString();
}

async function api(b: Record<string, any>) {
  switch (b.acao) {
    case "upload": {
      const { data, error } = await supabase.storage.from(BUCKET).createSignedUploadUrl(String(b.caminho), { upsert: true });
      if (error || !data) throw new Error(error?.message ?? "sem link");
      return { url: data.signedUrl };
    }
    case "agendar": {
      const p = b.post ?? {};
      const destinos: string[] = (b.destinos ?? await cfgJson("destinos_padrao", ["ig_teste"]))
        .filter((d: string) => DESTINOS.includes(d) && d !== "ig_normal");
      if (!destinos.includes("ig_teste")) destinos.unshift("ig_teste"); // tudo passa pelo teste
      const { data: post, error } = await supabase.from("posts").insert({
        tipo: p.tipo, titulo: p.titulo, legenda: p.legenda ?? "", youtube_titulo: p.youtube_titulo ?? null,
        arquivo: p.arquivo, origem: p.origem ?? null, publicar_em: p.publicar_em, nota: p.nota ?? null,
      }).select().single();
      if (error) throw new Error(error.message);
      const { error: e2 } = await supabase.from("publicacoes").insert(
        destinos.map((d) => ({ post_id: post.id, destino: d, publicar_em: p.publicar_em })),
      );
      if (e2) throw new Error(e2.message);
      return { post_id: post.id, destinos };
    }
    case "listar": {
      // Posts com qualquer publicação na janela + todos os testes esperando decisão.
      const { data: pubs } = await supabase.from("publicacoes").select("post_id")
        .gte("publicar_em", b.de).lt("publicar_em", b.ate);
      const { data: espera } = await supabase.from("publicacoes").select("post_id, posts!inner(decisao)")
        .eq("destino", "ig_teste").eq("status", "publicado").is("posts.decisao", null);
      const ids = [...new Set([...(pubs ?? []), ...(espera ?? [])].map((x) => x.post_id))];
      const { data: posts } = ids.length
        ? await supabase.from("posts").select("*, publicacoes(*)").in("id", ids)
        : { data: [] };
      // Base de comparação: views em 24 h dos testes (e posts normais) dos últimos 60 dias, por tipo.
      const { data: base } = await supabase.from("publicacoes").select("destino, metricas, publicado_em, posts!inner(tipo)")
        .in("destino", ["ig_teste", "ig_normal"]).eq("status", "publicado").not("metricas", "is", null)
        .gte("publicado_em", new Date(Date.now() - 60 * 86400_000).toISOString());
      return { posts, base, grade_teste: await cfgJson("grade_teste", {}), grade_normal: await cfgJson("grade_normal", {}) };
    }
    case "historico": {
      const { data } = await supabase.from("posts").select("*, publicacoes(*)")
        .gte("publicar_em", b.de).lt("publicar_em", b.ate).order("publicar_em");
      return { posts: data };
    }
    case "validar": {
      const post = await postDe(String(b.post_id));
      if (post.decisao) throw new Error(`já decidido: ${post.decisao}`);
      if (!post.arquivo) throw new Error("sem_arquivo: o vídeo já saiu do bucket — o postador.py sobe de novo do Drive");
      const grade = await cfgJson<Record<string, string>>("grade_normal", {});
      const quando = b.publicar_em ?? proximoHorario(grade[post.tipo] ?? "19:30", Date.now() + 30 * 60_000);
      const { error } = await supabase.from("publicacoes")
        .insert({ post_id: post.id, destino: "ig_normal", publicar_em: quando });
      if (error) throw new Error(error.message);
      await supabase.from("posts").update({ decisao: "normal", decidido_em: new Date().toISOString() }).eq("id", post.id);
      return { ok: true, publicar_em: quando };
    }
    case "post": return await postDe(String(b.post_id));
    case "anexar": {
      await supabase.from("posts").update({ arquivo: String(b.arquivo) }).eq("id", String(b.post_id));
      return { ok: true };
    }
    case "descartar": {
      await supabase.from("posts").update({ decisao: "descartado", decidido_em: new Date().toISOString() })
        .eq("id", String(b.post_id)).is("decisao", null);
      return { ok: true };
    }
    case "cancelar": {
      const { data } = await supabase.from("publicacoes").update({ status: "cancelado" })
        .eq("id", String(b.publicacao_id)).eq("status", "pendente").select("id");
      return { ok: (data ?? []).length > 0 };
    }
    case "reagendar": {
      const { data } = await supabase.from("publicacoes")
        .update({ status: "pendente", publicar_em: b.publicar_em, tentativas: 0, erro: null, container_id: null })
        .eq("id", String(b.publicacao_id)).in("status", ["pendente", "erro"]).select("id");
      return { ok: (data ?? []).length > 0 };
    }
    case "config": {
      if (b.chave === "postador_token") throw new Error("não pelo painel");
      await setCfg(String(b.chave), String(b.valor));
      return { ok: true };
    }
    case "config_ver": {
      const { data } = await supabase.from("config").select("chave, valor, atualizado_em");
      const secreta = (k: string) => /token|secret|key/.test(k);
      return Object.fromEntries((data ?? []).map((c) => [c.chave, secreta(c.chave) ? `•••• (${c.atualizado_em.slice(0, 10)})` : c.valor]));
    }
    case "testar_ig": return await graph("me", { fields: "username,followers_count,media_count" });
    case "importar": {
      // Posts antigos (já publicados) para a base de comparação do painel.
      let n = 0;
      for (const it of b.itens ?? []) {
        const { data: ja } = await supabase.from("publicacoes").select("id").eq("media_id", it.media_id).maybeSingle();
        if (ja) continue;
        const { data: post } = await supabase.from("posts").insert({
          tipo: it.tipo ?? "antigo", titulo: it.titulo, legenda: it.legenda ?? "", publicar_em: it.publicado_em, decisao: "normal",
        }).select().single();
        await supabase.from("publicacoes").insert({
          post_id: post!.id, destino: it.destino ?? "ig_normal", publicar_em: it.publicado_em, status: "publicado",
          media_id: it.media_id, permalink: it.permalink, publicado_em: it.publicado_em, metricas: it.metricas ?? null,
        });
        n++;
      }
      return { importados: n };
    }
    case "seguidores": {
      const { data } = await supabase.from("seguidores").select("em, total")
        .gte("em", new Date(Date.now() - Number(b.dias ?? 30) * 86400_000).toISOString()).order("em");
      return data ?? [];
    }
    case "metricas": return { log: await metricas() };
    case "renovar": return await renovar();
    default: throw new Error(`ação desconhecida: ${b.acao}`);
  }
}

Deno.serve(async (req) => {
  const esperado = await cfg("postador_token");
  if (!esperado || req.headers.get("x-postador-token") !== esperado) return json({ error: "Não autorizado." }, 401);
  try {
    const b = await req.json().catch(() => ({}));
    if (b?.acao) return json(await api(b));
    return json({ ok: true, log: await rodada() });
  } catch (e) {
    console.error(e);
    return json({ error: (e as Error).message }, 500);
  }
});
