import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Card, Count, Reveal, Rich, SANS, SERIF, Title, useIn } from "./theme";

// Graficos do ENEM DIA 1 (redacao + linguagens + humanas, 5h30). Mesmo sistema do dia 2:
// area da esquerda, rosto no card da direita, `b` = batidas relativas ao inicio do grafico.
type B = { b?: number[] };
const at = (b: number[] | undefined, i: number, d = 0) => (b && b[i] !== undefined ? b[i] : d);
const center: React.CSSProperties = { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ---------- barra dos blocos: 5h30 em escala real (r = redacao, q = questoes) ----------
const BLOCOS: [string, number, "r" | "q", string][] = [
  ["esqueleto", 15, "r", "15 min"],
  ["inglês", 15, "q", "15 min"],
  ["humanas", 75, "q", "1h15"],
  ["rascunho", 60, "r", "1h"],
  ["linguagens", 75, "q", "1h15"],
  ["definitivo", 30, "r", "30 min"],
  ["garimpo", 30, "q", "30 min"],
  ["gabarito", 15, "q", "15 min"],
  ["revisão", 15, "r", "15 min"],
];
export const BlocoBar: React.FC<{ on: number; lit?: number }> = ({ on, lit }) => {
  const p = useIn(0.05);
  const W = 1350;
  let x = 0;
  return (
    <div style={{ position: "relative", width: W, height: 150 }}>
      {BLOCOS.map(([n, m, k, d], i) => {
        const w = (m / 330) * W;
        const left = x;
        x += w;
        const hot = i === on || (lit !== undefined && i <= lit);
        const done = i < on;
        const red = k === "r";
        return (
          <React.Fragment key={n}>
            <div
              style={{
                position: "absolute",
                left: left + 2,
                width: w - 4,
                top: 70,
                height: 40,
                borderRadius: 8,
                background: hot ? (red ? C.green : C.text) : done ? (red ? C.greenDim : "rgba(241,245,242,0.18)") : C.card,
                border: `2px solid ${red ? C.green : hot || done ? C.text : C.line}`,
                transform: i === on ? `scaleY(${0.8 + 0.2 * p})` : undefined,
                boxShadow: i === on ? `0 0 30px ${red ? C.green : "rgba(255,255,255,0.4)"}` : "none",
              }}
            />
            {i === on && (
              <div style={{ position: "absolute", left: Math.min(Math.max(left + w / 2 - 150, 0), W - 300), width: 300, top: 0, textAlign: "center", opacity: p }}>
                <span style={{ fontFamily: SANS, fontSize: 30, fontWeight: 800, color: red ? C.green : C.text }}>{n}</span>
                <span style={{ fontFamily: SANS, fontSize: 24, color: C.mute }}> · {d}</span>
              </div>
            )}
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", top: 118, left: 0, right: 0, display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 20, color: C.mute }}>
        <span>13:30</span>
        <span>
          <span style={{ color: C.green }}>■</span> redação <span style={{ marginLeft: 16 }}>□</span> questões
        </span>
        <span>19:00</span>
      </div>
    </div>
  );
};

// ---------- Abertura: 5h30 + notas dele ----------
export const Abertura1: React.FC<B> = ({ b }) => {
  const notas: [number, string, string, number][] = [
    [40, "/45", "Linguagens", at(b, 1, 2)],
    [42, "/45", "Humanas", at(b, 2, 3)],
    [940, "", "Redação", at(b, 3, 4)],
  ];
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 40 }}>
      <Reveal at={at(b, 0, 0.2)}>
        <BlocoBar on={-1} lit={8} />
      </Reveal>
      <Title at={at(b, 0, 0.2) + 0.3} t={"Dia 1, *bloco por bloco*"} size={78} style={{ marginTop: 50 }} />
      <div style={{ display: "flex", gap: 26, marginTop: 60 }}>
        {notas.map(([n, s, l, t]) => (
          <Reveal key={l} at={t} style={{ flex: 1 }}>
            <Card style={{ textAlign: "center" }}>
              <div style={{ fontFamily: "Anton", fontSize: 130, color: C.green, lineHeight: 1.1 }}>
                <Count to={n} at={t} dur={0.9} />
                <span style={{ fontSize: 60, color: C.mute }}>{s}</span>
              </div>
              <div style={{ fontFamily: SANS, fontSize: 32, color: C.text, fontWeight: 700 }}>{l}</div>
            </Card>
          </Reveal>
        ))}
      </div>
    </div>
  );
};

// ---------- Caderno de repertorios por eixo tematico ----------
const EIXOS = ["Meio ambiente", "Educação", "Saúde", "Tecnologia", "Cidadania", "Cultura"];
// `marcas` = [eixo, segundo]: cada aba acende na fala e fica acesa
export const Caderno: React.FC<B & { eixos?: string[]; marcas?: [string, number][] }> = ({ b, eixos = EIXOS, marcas }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const ditos = (marcas ?? []).filter(([, a]) => t >= a).map(([e]) => e);
  const hot = marcas ? eixos.indexOf(ditos[ditos.length - 1]) : t >= at(b, 3, 99) ? 1 : t >= at(b, 2, 99) ? 0 : -1;
  return (
    <div style={{ ...center, flexDirection: "row", alignItems: "center", gap: 60 }}>
      <div style={{ position: "relative", width: 560, height: 720 }}>
        <div style={{ position: "absolute", inset: 0, background: "#F3F5F2", borderRadius: 22, boxShadow: "0 20px 60px rgba(0,0,0,0.5)", padding: 50 }}>
          <div style={{ fontFamily: SERIF, fontSize: 42, color: "#1b1b1b", fontWeight: 600 }}>{hot >= 0 ? eixos[hot] : "Repertórios"}</div>
          {[...Array(8)].map((_, j) => (
            <div key={j} style={{ height: 14, background: "#D8DDD9", borderRadius: 7, marginTop: 30, width: `${55 + ((j * 17 + (hot + 1) * 11) % 40)}%` }} />
          ))}
        </div>
        {eixos.map((e, i) => {
          const p = interpolate(t, [at(b, 1, 0.5) + i * 0.18, at(b, 1, 0.5) + i * 0.18 + 0.2], [0, 1], clamp);
          const on = marcas ? ditos.includes(e) : i === hot;
          return (
            <div key={e} style={{ position: "absolute", right: -190 - (on ? 30 : 0), top: 40 + i * 108, width: 230, height: 86, borderRadius: "0 16px 16px 0", background: on ? C.green : C.card, border: `2px solid ${on ? C.green : C.line}`, display: "flex", alignItems: "center", paddingLeft: 26, opacity: p, transform: `translateX(${(1 - p) * -40}px)` }}>
              <span style={{ fontFamily: SANS, fontSize: 26, fontWeight: 700, color: on ? C.bg : C.text }}>{e}</span>
            </div>
          );
        })}
      </div>
      <div style={{ flex: 1, marginLeft: 220 }}>
        <Title at={at(b, 0, 0)} t={"Repertórios por *eixo temático*"} size={60} />
        <Reveal at={at(b, 2, 99) - 0.3}>
          <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute, marginTop: 30, lineHeight: 1.4 }}>caiu meio ambiente?<br />repertório de meio ambiente.</div>
        </Reveal>
      </div>
    </div>
  );
};

// ---------- linha do tempo generica (horarios) ----------
export const Linha: React.FC<{ title: string; nodes: [string, string, number, boolean?][] } & B> = ({ title, nodes }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = nodes.length;
  const line = interpolate(f, [nodes[0][2] * fps, nodes[n - 1][2] * fps], [0, 1], clamp);
  return (
    <div style={center}>
      <Title t={title} size={68} />
      <div style={{ position: "relative", height: 300, marginTop: 70 }}>
        <div style={{ position: "absolute", left: 80, right: 80, top: 110, height: 6, background: C.line, borderRadius: 3 }} />
        <div style={{ position: "absolute", left: 80, width: `calc((100% - 160px) * ${line})`, top: 110, height: 6, background: C.green, borderRadius: 3, boxShadow: `0 0 20px ${C.green}` }} />
        {nodes.map(([tm, l, a, red], i) => {
          const p = interpolate(f, [a * fps, (a + 0.3) * fps], [0, 1], clamp);
          return (
            <div key={tm} style={{ position: "absolute", left: `calc(80px + (100% - 160px) * ${i / (n - 1)})`, top: 0, transform: "translateX(-50%)", textAlign: "center", opacity: p, width: 260 }}>
              <div style={{ fontFamily: "Anton", fontSize: 58, color: red ? C.red : C.text }}>{tm}</div>
              <div style={{ margin: "14px auto", width: 34, height: 34, borderRadius: 20, background: red ? C.red : C.green, transform: `scale(${p})`, boxShadow: `0 0 24px ${red ? C.red : C.green}` }} />
              <div style={{ fontFamily: SANS, fontSize: 28, color: red ? C.red : C.mute, marginTop: 8 }}>{l}</div>
            </div>
          );
        })}
      </div>
      <Reveal at={nodes[n - 1][2] + 0.5}>
        <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, textAlign: "center" }}>horário de Brasília</div>
      </Reveal>
    </div>
  );
};

// ---------- Tema primeiro: medidor de ansiedade cai quando ele descobre o tema ----------
export const Tema: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const up = interpolate(t, [at(b, 1, 3), at(b, 1, 3) + 1.2], [0, 92], clamp);
  const down = interpolate(t, [at(b, 2, 9), at(b, 2, 9) + 1.0], [0, 72], clamp);
  const v = Math.max(0, up - down);
  return (
    <div style={{ ...center, flexDirection: "row", alignItems: "center", gap: 70 }}>
      <div style={{ flex: 1 }}>
        <Title at={at(b, 0, 0.2)} t={"Primeiro: o *tema da redação*"} size={66} />
        <Reveal at={at(b, 0, 0.2) + 0.4}>
          <Card style={{ marginTop: 44 }}>
            <div style={{ fontFamily: SANS, fontSize: 24, letterSpacing: 3, color: C.green, fontWeight: 800 }}>PROPOSTA DE REDAÇÃO</div>
            <div style={{ fontFamily: SERIF, fontSize: 40, color: C.text, marginTop: 16, lineHeight: 1.25 }}>
              {t >= at(b, 2, 9) ? "Tema: ✓ descoberto" : "Tema: ???"}
            </div>
          </Card>
        </Reveal>
      </div>
      <Reveal at={at(b, 1, 3) - 0.2}>
        <div style={{ width: 260, textAlign: "center" }}>
          <div style={{ fontFamily: SANS, fontSize: 28, color: C.mute, marginBottom: 16 }}>ansiedade</div>
          <div style={{ margin: "0 auto", width: 90, height: 520, borderRadius: 45, background: C.card, border: `2px solid ${C.line}`, position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: `${v}%`, background: v > 50 ? C.red : C.green, boxShadow: `0 0 40px ${v > 50 ? C.red : C.green}` }} />
          </div>
          <div style={{ fontFamily: "Anton", fontSize: 64, color: v > 50 ? C.red : C.green, marginTop: 16 }}>{Math.round(v)}%</div>
        </div>
      </Reveal>
    </div>
  );
};

// ---------- folha de redacao com blocos (esqueleto / rascunho) ----------
const Folha: React.FC<{ rows: [string, string, number][]; write?: boolean }> = ({ rows, write }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ width: 760, background: "#F3F5F2", borderRadius: 20, padding: "34px 40px", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>
      {rows.map(([h, d, a], i) => {
        const p = interpolate(f, [a * fps, (a + (write ? 2.2 : 0.25)) * fps], [0, 1], clamp);
        const on = p > 0;
        return (
          <div key={h} style={{ marginTop: i ? 22 : 0, padding: "14px 18px", borderRadius: 14, border: `2px dashed ${on ? "#1a8f45" : "#C9D0CB"}`, background: on ? "rgba(43,232,107,0.12)" : "transparent" }}>
            <div style={{ fontFamily: SANS, fontSize: 28, fontWeight: 800, color: on ? "#127a38" : "#9AA39D" }}>{h}</div>
            {write ? (
              [0, 1, 2].map((j) => (
                <div key={j} style={{ height: 10, borderRadius: 5, marginTop: 10, background: "#C9D0CB", position: "relative", overflow: "hidden" }}>
                  <div style={{ position: "absolute", inset: 0, width: `${Math.min(1, Math.max(0, p * 3 - j)) * 100}%`, background: "#2b3a31" }} />
                </div>
              ))
            ) : (
              <div style={{ fontFamily: SANS, fontSize: 24, color: "#3b4540", marginTop: 4, opacity: on ? 1 : 0 }}>{d}</div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export const Esqueleto: React.FC<B> = ({ b }) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
    <BlocoBar on={0} />
    <div style={{ display: "flex", gap: 50, marginTop: 30, alignItems: "center" }}>
      <Folha
        rows={[
          ["Introdução", "contexto + repertório de abertura", at(b, 1, 1)],
          ["D1", "1º argumento + repertório", at(b, 2, 2)],
          ["D2", "2º argumento + repertório", at(b, 3, 3)],
          ["Proposta de intervenção", "já anotada", at(b, 4, 4)],
        ]}
      />
      <div style={{ flex: 1 }}>
        <Title at={at(b, 0, 0.2)} t={"O *esqueleto*"} size={70} />
        <Reveal at={at(b, 0, 0.2) + 0.4}>
          <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, marginTop: 20 }}>na própria folha de redação</div>
        </Reveal>
        <Reveal at={at(b, 5, 6)}>
          <div style={{ fontFamily: "Anton", fontSize: 120, color: C.green, marginTop: 40 }}>15 min ✓</div>
        </Reveal>
      </div>
    </div>
  </div>
);

export const Rascunho: React.FC<B> = ({ b }) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
    <BlocoBar on={3} />
    <div style={{ display: "flex", gap: 50, marginTop: 30, alignItems: "center" }}>
      <Folha write rows={[["Introdução", "", at(b, 1, 1)], ["D1", "", at(b, 2, 2)], ["D2", "", at(b, 3, 3)]]} />
      <div style={{ flex: 1 }}>
        <Title at={at(b, 0, 0.2)} t={"Rascunho: *1 hora*"} size={70} />
        <Reveal at={at(b, 0, 0.2) + 0.4}>
          <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, marginTop: 20 }}>palavra por palavra</div>
        </Reveal>
        <Reveal at={at(b, 4, 5)}>
          <Card style={{ marginTop: 40 }}>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text, fontWeight: 700 }}>Proposta de intervenção</div>
            <div style={{ fontFamily: SANS, fontSize: 28, color: C.green, marginTop: 8 }}>→ direto no definitivo</div>
          </Card>
        </Reveal>
      </div>
    </div>
  </div>
);

// ---------- bloco generico: barra + titulo + chips + contador ----------
type Chip = [string, "ok" | "x" | "go", number];
export const Bloco: React.FC<{ on: number; t: string; sub?: string; chips?: Chip[]; card?: { n?: number; s?: string; big?: string; label: string; at: number } } & B> = ({ on, t, sub, chips = [], card }) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
    <BlocoBar on={on} />
    <div style={{ display: "flex", gap: 40, marginTop: 60, alignItems: "center" }}>
      <div style={{ flex: 1 }}>
        <Title at={0.2} t={t} size={72} />
        {sub && (
          <Reveal at={0.6}>
            <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute, marginTop: 16 }}>{sub}</div>
          </Reveal>
        )}
        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 36 }}>
          {chips.map(([c, k, a]) => (
            <Reveal key={c} at={a} dy={0}>
              <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: SANS, fontSize: 34, color: C.text }}>
                <span style={{ width: 46, height: 46, borderRadius: 12, display: "inline-flex", alignItems: "center", justifyContent: "center", background: k === "ok" ? C.green : k === "x" ? C.red : C.card, color: k === "go" ? C.mute : C.bg, fontWeight: 900, border: k === "go" ? `2px solid ${C.line}` : "none" }}>
                  {k === "ok" ? "✓" : k === "x" ? "✕" : "→"}
                </span>
                <Rich t={c} />
              </div>
            </Reveal>
          ))}
        </div>
      </div>
      {card && (
        <Reveal at={card.at}>
          <Card style={{ width: 430, textAlign: "center" }}>
            {card.n !== undefined ? (
              <Count to={card.n} at={card.at} dur={1.4} suffix={card.s} style={{ fontFamily: "Anton", fontSize: 180, color: C.green, lineHeight: 1.1 }} />
            ) : (
              <div style={{ fontFamily: "Anton", fontSize: 130, color: C.green, lineHeight: 1.2 }}>{card.big}</div>
            )}
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>{card.label}</div>
          </Card>
        </Reveal>
      )}
    </div>
  </div>
);

// ---------- humanas vira repertorio ----------
export const Insight: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const src = ["Filósofo", "Geógrafo", "Historiador"];
  const go = interpolate(t, [at(b, 2, 6), at(b, 2, 6) + 0.8], [0, 1], clamp);
  return (
    <div style={center}>
      <Title at={at(b, 0, 0.2)} t={"Humanas *alimenta* a redação"} size={66} />
      <div style={{ display: "flex", alignItems: "center", gap: 50, marginTop: 70 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {src.map((s, i) => (
            <Reveal key={s} at={at(b, 1, 2) + i * 0.5} dy={0}>
              <div style={{ width: 360, padding: "22px 30px", borderRadius: 18, background: C.card, border: `2px solid ${C.line}`, fontFamily: SERIF, fontSize: 40, color: C.text }}>{s}</div>
            </Reveal>
          ))}
        </div>
        <svg width={260} height={300}>
          {[50, 150, 250].map((y, i) => (
            <line key={i} x1={0} y1={y} x2={go * 250} y2={150 + (y - 150) * (1 - go)} stroke={C.green} strokeWidth={5} strokeDasharray="12 10" opacity={go} />
          ))}
        </svg>
        <div style={{ opacity: go, transform: `scale(${0.8 + 0.2 * go})`, padding: "40px 50px", borderRadius: 24, background: C.green, boxShadow: `0 0 60px rgba(43,232,107,0.45)`, fontFamily: "Anton", fontSize: 72, color: C.bg }}>
          REPERTÓRIO
        </div>
      </div>
      <Reveal at={at(b, 3, 9)}>
        <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute, marginTop: 50 }}>só com os textos base e os enunciados</div>
      </Reveal>
    </div>
  );
};

// ---------- gabarito: numero + letra ----------
export const Gabarito1: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ans = ["A", "C", "E", "B", "D", "A", "C", "B"];
  const t0 = at(b, 1, 1.5);
  const tk = (i: number) => (i < 2 ? t0 + i * 1.4 : t0 + 2.8 + (i - 2) * 0.45);
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
      <BlocoBar on={7} />
      <div style={{ display: "flex", gap: 60, marginTop: 40, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <Title at={at(b, 0, 0.2)} t={"*Gabarito* com calma"} size={70} />
          <Reveal at={at(b, 0, 0.2) + 0.4}>
            <div style={{ fontFamily: SANS, fontSize: 34, color: C.mute, marginTop: 24 }}>número e letra, uma por uma</div>
          </Reveal>
          <Reveal at={at(b, 2, 5)}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: SANS, fontSize: 32, color: C.text, marginTop: 40 }}>
              <span style={{ width: 46, height: 46, borderRadius: 12, display: "inline-flex", alignItems: "center", justifyContent: "center", background: C.red, color: C.bg, fontWeight: 900 }}>✕</span>
              A, B, C… tudo de uma vez
            </div>
          </Reveal>
        </div>
        <Card style={{ width: 520, padding: 30 }}>
          {ans.map((a, i) => {
            const p = interpolate(f, [tk(i) * fps, (tk(i) + 0.2) * fps], [0, 1], clamp);
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, marginTop: i ? 12 : 0 }}>
                <div style={{ width: 50, fontFamily: SANS, fontSize: 28, color: C.mute, fontWeight: 700 }}>{i + 1}</div>
                {["A", "B", "C", "D", "E"].map((l) => (
                  <div key={l} style={{ width: 44, height: 44, borderRadius: 22, border: `2px solid ${C.line}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontSize: 20, background: l === a && p > 0.5 ? C.green : "transparent", transform: l === a ? `scale(${1 + 0.25 * Math.sin(p * Math.PI)})` : undefined }}>
                    <span style={{ color: l === a && p > 0.5 ? C.bg : C.mute, fontWeight: 800 }}>{l}</span>
                  </div>
                ))}
                <div style={{ fontFamily: SANS, fontSize: 24, color: C.green, opacity: p, fontWeight: 700 }}>“{i + 1}, {a}”</div>
              </div>
            );
          })}
        </Card>
      </div>
    </div>
  );
};

// ---------- revisao por competencia ----------
export const Revisao: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const rows: [string, string, number, boolean?][] = [
    ["C1", "gramática: concordância, vírgula, acento", at(b, 1, 1)],
    ["C4", "conectivo depois de cada ponto", at(b, 2, 2)],
    ["C5", "os 5 elementos da proposta", at(b, 3, 3)],
    ["C2", "repertórios bem encaixados", at(b, 4, 4)],
    ["C3", "argumentos embasados", at(b, 5, 5), true],
  ];
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
      <BlocoBar on={8} />
      <Title at={0.2} t={"Últimos 15 min: *revisão*"} size={64} style={{ marginTop: 40 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 34 }}>
        {rows.map(([c, d, a, soft], i) => {
          const on = t >= a;
          return (
            <Reveal key={c} at={0.5 + i * 0.12} dy={0}>
              <div style={{ display: "flex", alignItems: "center", gap: 24, background: on ? (soft ? C.card : C.greenDim) : C.card, border: `2px solid ${on ? (soft ? C.mute : C.green) : C.line}`, borderRadius: 18, padding: "14px 24px" }}>
                <div style={{ width: 80, fontFamily: "Anton", fontSize: 46, color: on ? (soft ? C.text : C.green) : C.line }}>{c}</div>
                <div style={{ fontFamily: SANS, fontSize: 32, color: on ? C.text : C.line, flex: 1 }}>{d}</div>
                <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: soft ? C.mute : C.green, opacity: on ? 1 : 0 }}>
                  {soft ? (t >= at(b, 6, 99) ? "sem se cobrar" : "") : "✓"}
                </div>
              </div>
            </Reveal>
          );
        })}
      </div>
    </div>
  );
};

// ---------- lista (resumo) ----------
export const Lista: React.FC<{ title: string; items: [string, string, number][] }> = ({ title, items }) => (
  <div style={center}>
    <Title t={title} size={64} />
    <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 10 }}>
      {items.map(([h, d, a], i) => (
        <Reveal key={h} at={a} dy={0}>
          <div style={{ display: "flex", alignItems: "center", gap: 22, background: C.card, border: `2px solid ${C.line}`, borderRadius: 16, padding: "10px 22px" }}>
            <div style={{ width: 44, height: 44, borderRadius: 22, background: C.green, color: C.bg, fontFamily: SANS, fontSize: 24, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text, fontWeight: 800, width: 380 }}>{h}</div>
            <div style={{ fontFamily: SANS, fontSize: 28, color: C.mute }}>{d}</div>
          </div>
        </Reveal>
      ))}
    </div>
  </div>
);

// ---------- fechamento ----------
export const Final1: React.FC<{ t: string; sub: string; date: string } & B> = ({ t, sub, date, b }) => (
  <div style={{ ...center, alignItems: "center", textAlign: "center" }}>
    <Reveal at={0}>
      <BlocoBar on={-1} lit={8} />
    </Reveal>
    <Title at={at(b, 0, 0.5)} t={t} size={70} style={{ marginTop: 60 }} />
    <Reveal at={at(b, 1, 1.5)}>
      <div style={{ fontFamily: SANS, fontSize: 34, color: C.mute, marginTop: 20 }}>{sub}</div>
    </Reveal>
    <Reveal at={at(b, 2, 2.5)}>
      <div style={{ fontFamily: "Anton", fontSize: 120, color: C.green, marginTop: 40 }}>{date}</div>
    </Reveal>
  </div>
);

export const GRAPHICS1: Record<string, React.FC<any>> = {
  Abertura1, Caderno, Linha, Tema, Esqueleto, Rascunho, Bloco, Insight, Gabarito1, Revisao, Lista, Final1,
};
