// DM chat — "comenta a palavra que eu te mando o link na DM" (estilo ManyChat).
// Desenho tirado do Chiron Chat do Isaac (chiron-chat-webhook + chiron-chat-varredura),
// só que enxuto: sem webhook da Meta, a varredura É o motor.
//
// Como funciona (cron "dm-chat", minuto a minuto, só com automação ligada):
//   1. Lê os últimos posts do IG; só relê os comentários do post cuja contagem mudou.
//   2. Comentário novo (depois da criação da automação) com a palavra → Private Reply:
//      UMA mensagem (texto + botão de link num "button template" só — a Meta recusa
//      uma 2ª mensagem no mesmo comentário) + resposta pública sorteada no comentário.
//   3. Todo comentário vai pra dm_comentarios: ninguém recebe a DM duas vezes.
// Regras da Meta: Private Reply só até 7 dias depois do comentário; texto ≤ 640; botão ≤ 20.
//
// Toda chamada precisa do cabeçalho x-postador-token = config.postador_token.
// POST {acao: "varrer" | "lista" | "criar" | "editar" | "log"}
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const GRAPH = "https://graph.instagram.com/v23.0";
const POSTS_VARRIDOS = 50; // lote de 12 Reels por dia: com menos, o post sai da varredura em 1 dia
const SETE_DIAS = 7 * 24 * 3600 * 1000;

type Automacao = {
  id: string; nome: string; palavras: string[]; post_ids: string[]; mensagem: string;
  botao_texto: string; link: string; respostas_publicas: string[]; ativo: boolean; criado_em: string;
};

// ---------------------------------------------------------------- config -----
const cache: Record<string, string> = {};
async function cfg(chave: string): Promise<string> {
  if (cache[chave]) return cache[chave];
  const { data } = await supabase.from("config").select("valor").eq("chave", chave).maybeSingle();
  if (!data?.valor) throw new Error(`config ${chave} vazia`);
  return (cache[chave] = data.valor);
}

async function graph(path: string, params: Record<string, string> = {}, corpo?: unknown) {
  const q = new URLSearchParams({ ...params, access_token: await cfg("ig_token") });
  const r = await fetch(`${GRAPH}/${path}?${q}`, corpo === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok || d.error) throw new Error(d.error?.message ?? `HTTP ${r.status}`);
  return d;
}

// --------------------------------------------------------------- casamento ---
// "Vídeo!" casa com "video"; "videos" NÃO casa com "video" (palavra inteira).
const normalizar = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function casa(texto: string, a: Automacao, mediaId: string): boolean {
  if (a.post_ids.length && !a.post_ids.includes(mediaId)) return false;
  const palavrasDoTexto = new Set(normalizar(texto).split(/[^a-z0-9]+/).filter(Boolean));
  return a.palavras.some((p) => {
    const alvo = normalizar(p).split(/[^a-z0-9]+/).filter(Boolean);
    return alvo.length > 0 && alvo.every((w) => palavrasDoTexto.has(w));
  });
}

// ------------------------------------------------------------------- envio ---
async function responder(a: Automacao, commentId: string) {
  const texto = a.mensagem.slice(0, 640);
  try {
    await graph("me/messages", {}, {
      recipient: { comment_id: commentId },
      message: { attachment: { type: "template", payload: {
        template_type: "button", text: texto,
        buttons: [{ type: "web_url", url: a.link, title: a.botao_texto.slice(0, 20) }],
      } } },
    });
  } catch (e) {
    // Meta recusou o template (não consome o Private Reply) → manda o link no texto.
    console.warn("dm-chat: template recusado, indo de texto puro:", (e as Error).message);
    await graph("me/messages", {}, {
      recipient: { comment_id: commentId },
      message: { text: `${texto}\n\n${a.link}`.slice(0, 1000) },
    });
  }
  const publicas = a.respostas_publicas.filter((s) => s.trim());
  if (publicas.length) {
    const resposta = publicas[Math.floor(Math.random() * publicas.length)];
    try { await graph(`${commentId}/replies`, { message: resposta }, {}); }
    catch (e) { console.warn("dm-chat: resposta pública falhou:", (e as Error).message); }
  }
}

// ---------------------------------------------------------------- varredura --
async function varrer() {
  const { data: autos } = await supabase.from("dm_automacoes").select("*").eq("ativo", true);
  const automacoes = (autos ?? []) as Automacao[];
  if (!automacoes.length) return { automacoes: 0 };

  const eu = await cfg("ig_user_id");
  const midias = new Map<string, number>();
  const recentes = await graph("me/media", { fields: "id,comments_count", limit: String(POSTS_VARRIDOS) });
  for (const m of recentes.data ?? []) midias.set(m.id, m.comments_count ?? 0);
  // Post fixado numa automação, mas fora dos últimos POSTS_VARRIDOS: busca a contagem dele também.
  for (const id of new Set(automacoes.flatMap((a) => a.post_ids))) {
    if (!midias.has(id)) {
      try { midias.set(id, (await graph(id, { fields: "comments_count" })).comments_count ?? 0); }
      catch (e) { console.warn(`dm-chat: post ${id} inacessível:`, (e as Error).message); }
    }
  }

  const { data: contagens } = await supabase.from("dm_midias").select("media_id, comments_count")
    .in("media_id", [...midias.keys()]);
  const antes = new Map((contagens ?? []).map((c) => [c.media_id, c.comments_count]));

  const res = { posts_lidos: 0, novos: 0, enviados: 0, erros: 0 };
  for (const [mediaId, total] of midias) {
    if (antes.get(mediaId) === total) continue;
    res.posts_lidos++;
    let ok = true;
    try {
      const comentarios: any[] = [];
      let pagina = await graph(`${mediaId}/comments`, { fields: "id,text,timestamp,from", limit: "50" });
      for (let i = 0; i < 5; i++) {
        comentarios.push(...(pagina.data ?? []));
        const prox = pagina.paging?.next;
        if (!prox) break;
        const r = await fetch(prox);
        pagina = await r.json();
        if (!r.ok) break;
      }
      const ids = comentarios.map((c) => c.id);
      const { data: vistos } = await supabase.from("dm_comentarios").select("comment_id").in("comment_id", ids);
      const jaVisto = new Set((vistos ?? []).map((v) => v.comment_id));

      for (const c of comentarios) {
        if (jaVisto.has(c.id) || String(c.from?.id) === eu) continue;
        res.novos++;
        const quando = new Date(c.timestamp).getTime();
        const a = Date.now() - quando < SETE_DIAS
          ? automacoes.find((x) => quando >= new Date(x.criado_em).getTime() && casa(c.text ?? "", x, mediaId))
          : undefined;
        // Grava ANTES de enviar: se der timeout no meio, ninguém recebe duas vezes.
        const { data: inserido } = await supabase.from("dm_comentarios").upsert({
          comment_id: c.id, media_id: mediaId, username: c.from?.username ?? null, texto: c.text ?? null,
          automacao_id: a?.id ?? null, comentado_em: c.timestamp,
        }, { onConflict: "comment_id", ignoreDuplicates: true }).select("comment_id");
        if (!a || !inserido?.length) continue;
        try {
          await responder(a, c.id);
          await supabase.from("dm_comentarios").update({ status: "enviado" }).eq("comment_id", c.id);
          res.enviados++;
        } catch (e) {
          await supabase.from("dm_comentarios").update({ status: "erro", erro: (e as Error).message })
            .eq("comment_id", c.id);
          res.erros++;
        }
      }
    } catch (e) {
      ok = false;
      console.error(`dm-chat: falha lendo o post ${mediaId}:`, (e as Error).message);
    }
    // Contagem só avança se o post foi lido inteiro; senão tenta de novo no próximo minuto.
    if (ok) await supabase.from("dm_midias").upsert({ media_id: mediaId, comments_count: total,
      atualizado_em: new Date().toISOString() });
  }
  return res;
}

// ------------------------------------------------------------------ painel ---
const CAMPOS = ["nome", "palavras", "post_ids", "mensagem", "botao_texto", "link", "respostas_publicas", "ativo"];
const soCampos = (o: Record<string, unknown>) =>
  Object.fromEntries(Object.entries(o).filter(([k, v]) => CAMPOS.includes(k) && v !== undefined));

async function lista() {
  const { data: autos } = await supabase.from("dm_automacoes").select("*").order("criado_em");
  const { data: cont } = await supabase.from("dm_comentarios").select("automacao_id, status")
    .not("automacao_id", "is", null);
  return (autos ?? []).map((a) => ({
    ...a,
    enviados: (cont ?? []).filter((c) => c.automacao_id === a.id && c.status === "enviado").length,
    erros: (cont ?? []).filter((c) => c.automacao_id === a.id && c.status === "erro").length,
  }));
}

Deno.serve(async (req) => {
  try {
    if (req.headers.get("x-postador-token") !== await cfg("postador_token")) {
      return new Response("não autorizado", { status: 401 });
    }
    const corpo = await req.json().catch(() => ({}));
    let saida: unknown;
    switch (corpo.acao) {
      case "varrer": saida = await varrer(); break;
      case "lista": saida = await lista(); break;
      case "criar": {
        const { data, error } = await supabase.from("dm_automacoes").insert(soCampos(corpo)).select().single();
        if (error) throw new Error(error.message);
        saida = data; break;
      }
      case "editar": {
        const { data, error } = await supabase.from("dm_automacoes").update(soCampos(corpo))
          .eq("id", corpo.id).select().single();
        if (error) throw new Error(error.message);
        saida = data; break;
      }
      case "log": {
        const { data } = await supabase.from("dm_comentarios").select("*")
          .order("criado_em", { ascending: false }).limit(corpo.limite ?? 30);
        saida = data; break;
      }
      default: return new Response(`ação desconhecida: ${corpo.acao}`, { status: 400 });
    }
    return Response.json(saida);
  } catch (e) {
    console.error("dm-chat:", (e as Error).message);
    return Response.json({ erro: (e as Error).message }, { status: 500 });
  }
});
