import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Card, Count, Reveal, Rich, SANS, Title, useIn } from "./theme";

// Graficos do video "Semana do ENEM dia 1". Espinha: barra das 7 dicas (stepper estilo Ali) e a grade da semana.
type B = { b?: number[] };
const at = (b: number[] | undefined, i: number, d = 0) => (b && b[i] !== undefined ? b[i] : d);
const center: React.CSSProperties = { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const t_ = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return f / fps;
};

// ---------- barra das 7 dicas ----------
const DICAS = ["maratona", "correção", "repertórios", "redações", "Felipe Pereira", "misturadas", "revisão"];
export const DicaBar: React.FC<{ on: number; dicas?: string[] }> = ({ on, dicas = DICAS }) => {
  const p = useIn(0.05);
  return (
    <div style={{ display: "flex", gap: 8 }}>
      {dicas.map((d, i) => {
        const hot = i === on, done = i < on;
        return (
          <div key={d} style={{ flex: hot ? 2.2 : 1, display: "flex", alignItems: "center", gap: 10, borderRadius: 14, padding: "12px 14px", background: hot ? C.green : done ? C.greenDim : C.card, border: `2px solid ${hot || done ? C.green : C.line}`, transform: hot ? `scale(${0.9 + 0.1 * p})` : undefined, overflow: "hidden" }}>
            <span style={{ fontFamily: "Anton", fontSize: 30, color: hot ? C.bg : done ? C.green : C.mute }}>{i + 1}</span>
            {hot && <span style={{ fontFamily: SANS, fontSize: 24, fontWeight: 800, color: C.bg, whiteSpace: "nowrap" }}>{d}</span>}
          </div>
        );
      })}
    </div>
  );
};

type Chip = [string, "ok" | "x" | "go", number];
const Chips: React.FC<{ chips: Chip[]; size?: number }> = ({ chips, size = 34 }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 36 }}>
    {chips.map(([c, k, a]) => (
      <Reveal key={c} at={a} dy={0}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: SANS, fontSize: size, color: C.text }}>
          <span style={{ width: 46, height: 46, flexShrink: 0, borderRadius: 12, display: "inline-flex", alignItems: "center", justifyContent: "center", background: k === "ok" ? C.green : k === "x" ? C.red : C.card, color: k === "go" ? C.mute : C.bg, fontWeight: 900, border: k === "go" ? `2px solid ${C.line}` : "none" }}>
            {k === "ok" ? "✓" : k === "x" ? "✕" : "→"}
          </span>
          <span>
            <Rich t={c} />
          </span>
        </div>
      </Reveal>
    ))}
  </div>
);

// ---------- dica generica: barra + titulo + chips + card ----------
export const Dica: React.FC<{ on: number; dicas?: string[]; t: string; sub?: string; chips?: Chip[]; card?: { n?: number; s?: string; big?: string; label: string; at: number } }> = ({ on, dicas, t, sub, chips = [], card }) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
    <DicaBar on={on} dicas={dicas} />
    <div style={{ display: "flex", gap: 40, marginTop: 90, alignItems: "center" }}>
      <div style={{ flex: 1 }}>
        <Title at={0.2} t={t} size={86} />
        {sub && (
          <Reveal at={0.6}>
            <div style={{ fontFamily: SANS, fontSize: 38, color: C.mute, marginTop: 20 }}>{sub}</div>
          </Reveal>
        )}
        <Chips chips={chips} size={42} />
      </div>
      {card && (
        <Reveal at={card.at}>
          <Card style={{ width: 420, textAlign: "center" }}>
            {card.n !== undefined ? (
              <Count to={card.n} at={card.at} dur={1.2} suffix={card.s} style={{ fontFamily: "Anton", fontSize: 170, color: C.green, lineHeight: 1.1 }} />
            ) : (
              <div style={{ fontFamily: "Anton", fontSize: (card.big ?? "").length > 6 ? 80 : 110, color: C.green, lineHeight: 1.2 }}>{card.big}</div>
            )}
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>{card.label}</div>
          </Card>
        </Reveal>
      )}
    </div>
  </div>
);

// ---------- abertura: o que o video cobre ----------
export const AberturaS: React.FC<B & { t?: string; items?: string[] }> = ({ b, t = "A semana do *dia 1*", items }) => (
  <div style={center}>
    <Reveal at={0}>
      <div style={{ fontFamily: "Anton", fontSize: 150, color: C.green, lineHeight: 1 }}>7 DIAS</div>
    </Reveal>
    <Title at={0.2} t={t} size={76} style={{ marginTop: 10 }} />
    <Chips
      size={38}
      chips={
        items
          ? items.map((c, i): Chip => [c, "ok", at(b, i, 1 + i)])
          : [
              ["o que eu *estudava*", "ok", at(b, 0, 1)],
              ["como eu *dividia* os dias", "ok", at(b, 1, 2)],
              ["o que eu *não* fazia", "x", at(b, 2, 3)],
            ]
      }
    />
  </div>
);

// ---------- maratona: seg-sex prova, sab descanso ----------
const DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"];
export const Maratona: React.FC<B & { dicas?: string[]; t?: string; nota?: string }> = ({ b, dicas, t: titulo = "Maratona de *provas*", nota }) => {
  const t = t_();
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <DicaBar on={0} dicas={dicas} />
      <Title at={0.2} t={titulo} size={74} style={{ marginTop: 60 }} />
      <div style={{ display: "flex", gap: 14, marginTop: 50 }}>
        {DIAS.map((d, i) => {
          const a = i < 5 ? at(b, 0, 1) + i * 0.18 : i === 5 ? at(b, 1, 3) : at(b, 1, 3) + 0.3;
          const p = interpolate(t, [a, a + 0.2], [0, 1], clamp);
          const rest = i === 5, dom = i === 6;
          return (
            <div key={d} style={{ flex: 1, height: 230, borderRadius: 20, padding: 20, background: dom ? C.green : rest ? C.card : C.greenDim, border: `2px solid ${rest ? C.line : C.green}`, opacity: p, transform: `translateY(${(1 - p) * 20}px)` }}>
              <div style={{ fontFamily: SANS, fontSize: 28, fontWeight: 800, color: dom ? C.bg : C.mute }}>{d}</div>
              <div style={{ fontFamily: "Anton", fontSize: 44, color: dom ? C.bg : rest ? C.mute : C.green, marginTop: 40, lineHeight: 1.05 }}>{dom ? "ENEM" : rest ? "descanso" : "PROVA"}</div>
              {!rest && !dom && <div style={{ fontFamily: SANS, fontSize: 20, color: C.mute, marginTop: 8 }}>antiga</div>}
            </div>
          );
        })}
      </div>
      <Reveal at={at(b, 2, 6)}>
        <div style={{ marginTop: 40, display: "inline-flex", alignItems: "center", gap: 16, padding: "16px 26px", borderRadius: 16, border: `2px solid ${nota ? C.green : C.red}`, background: nota ? C.greenDim : "rgba(255,90,90,0.1)" }}>
          {nota ? (
            <span style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>{nota}</span>
          ) : (
            <>
              <span style={{ fontFamily: SANS, fontSize: 30, fontWeight: 900, color: C.red }}>⚠ ATENÇÃO</span>
              <span style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>só pra quem já está avançado</span>
            </>
          )}
        </div>
      </Reveal>
    </div>
  );
};

// ---------- quais provas ----------
type Op = { tag: string; t: string; s: string };
export const Provas: React.FC<B & { on?: number; dicas?: string[]; title?: string; a?: Op; c?: Op; chips?: Chip[] }> = ({
  b,
  on = 0,
  dicas,
  title = "Quais *provas*?",
  a = { tag: "1ª OPÇÃO", t: "PROVAS ANTIGAS DO ENEM", s: "o mais próximo do dia oficial" },
  c = { tag: "JÁ FEZ TODAS?", t: "SIMULADOS DE CURSINHO", s: "quebram galho" },
  chips = [],
}) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
    <DicaBar on={on} dicas={dicas} />
    <Title at={0.2} t={title} size={74} style={{ marginTop: 50 }} />
    <div style={{ display: "flex", gap: 26, marginTop: 40 }}>
      <Reveal at={at(b, 0, 1)} style={{ flex: 1.3 }}>
        <div style={{ height: 300, borderRadius: 28, padding: 34, background: C.green, boxShadow: "0 0 60px rgba(43,232,107,0.35)" }}>
          <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: C.bg, letterSpacing: 2 }}>{a.tag}</div>
          <div style={{ fontFamily: "Anton", fontSize: 72, color: C.bg, marginTop: 20, lineHeight: 1.05 }}>{a.t}</div>
          <div style={{ fontFamily: SANS, fontSize: 26, color: C.bg, marginTop: 14 }}>{a.s}</div>
        </div>
      </Reveal>
      <Reveal at={at(b, 1, 3)} style={{ flex: 1 }}>
        <div style={{ height: 300, borderRadius: 28, padding: 34, background: C.card, border: `2px solid ${C.line}` }}>
          <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: C.mute, letterSpacing: 2 }}>{c.tag}</div>
          <div style={{ fontFamily: "Anton", fontSize: 64, color: C.text, marginTop: 20, lineHeight: 1.05 }}>{c.t}</div>
          <div style={{ fontFamily: SANS, fontSize: 26, color: C.mute, marginTop: 14 }}>{c.s}</div>
        </div>
      </Reveal>
    </div>
    <Chips chips={chips} size={30} />
  </div>
);

// ---------- quadro do fiscal: riscando o tempo ----------
export const Fiscal: React.FC<B> = ({ b }) => {
  const t = t_();
  const marks = ["5h30", "5h", "4h"];
  return (
    <div style={{ ...center, flexDirection: "row", alignItems: "center", gap: 70 }}>
      <div style={{ width: 620, height: 640, borderRadius: 18, background: "#F3F5F2", boxShadow: "0 20px 60px rgba(0,0,0,0.5)", padding: 44, border: "14px solid #3b3f3c" }}>
        <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: "#555", letterSpacing: 2 }}>TEMPO DE PROVA</div>
        {marks.map((m, i) => {
          const a = at(b, i + 1, 2 + i);
          const k = interpolate(t, [a, a + 0.35], [0, 1], clamp);
          return (
            <div key={m} style={{ marginTop: 6, opacity: interpolate(t, [at(b, 0, 1), at(b, 0, 1) + 0.3], [0, 1], clamp) }}>
              <div style={{ position: "relative", display: "inline-block", fontFamily: "Anton", fontSize: 120, lineHeight: 1.15, color: "#1b2a22" }}>
                {m}
                <div style={{ position: "absolute", left: -12, top: "54%", height: 12, width: `calc(${k * 100}% + 24px)`, background: C.red, borderRadius: 6, transform: "rotate(-4deg)" }} />
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ flex: 1 }}>
        <Title at={0.2} t={"100% *no tempo*"} size={70} />
        <Reveal at={0.5}>
          <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute, marginTop: 16 }}>5h30, com redação</div>
        </Reveal>
        <Chips chips={[["vídeo no YouTube *simulando o fiscal*", "ok", at(b, 4, 10)], ["no domingo, o quadro *não assusta*", "ok", at(b, 5, 14)]]} size={32} />
      </div>
    </div>
  );
};

// ---------- Felipe Pereira: competencia -> habilidade -> questao ----------
export const Matriz: React.FC<B> = ({ b }) => {
  const t = t_();
  const box = (label: string, a: number, hot = false) => {
    const p = interpolate(t, [a, a + 0.25], [0, 1], clamp);
    return (
      <div style={{ opacity: p, transform: `scale(${0.85 + 0.15 * p})`, padding: "26px 36px", borderRadius: 20, background: hot ? C.green : C.card, border: `2px solid ${C.green}`, fontFamily: "Anton", fontSize: 56, color: hot ? C.bg : C.text, textAlign: "center", minWidth: 340 }}>
        {label}
      </div>
    );
  };
  const arrow = (a: number) => (
    <div style={{ fontFamily: SANS, fontSize: 60, color: C.green, opacity: interpolate(t, [a, a + 0.25], [0, 1], clamp) }}>↓</div>
  );
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <DicaBar on={4} />
      <div style={{ display: "flex", gap: 60, marginTop: 50, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
            {[["interpretação", at(b, 0, 1)], ["gramática", at(b, 1, 2)]].map(([w, a]) => {
              const k = interpolate(t, [(a as number) + 0.6, (a as number) + 0.9], [0, 1], clamp);
              return (
                <Reveal key={w as string} at={a as number}>
                  <div style={{ position: "relative", fontFamily: SANS, fontSize: 40, fontWeight: 800, color: C.mute, padding: "10px 20px", borderRadius: 14, border: `2px solid ${C.line}` }}>
                    {w}
                    <div style={{ position: "absolute", left: 10, right: 10, top: "50%", height: 6, background: C.red, borderRadius: 3, transform: `scaleX(${k})`, transformOrigin: "left" }} />
                  </div>
                </Reveal>
              );
            })}
          </div>
          <Title at={at(b, 2, 3)} t={"Estudar por *competências e habilidades*"} size={60} style={{ marginTop: 40 }} />
          <Reveal at={at(b, 2, 3) + 0.4}>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, marginTop: 16 }}>a matriz de referência do ENEM</div>
          </Reveal>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          {box("COMPETÊNCIA", at(b, 5, 6), true)}
          {arrow(at(b, 4, 5))}
          {box("HABILIDADE", at(b, 4, 5))}
          {arrow(at(b, 3, 4))}
          {box("QUESTÃO", at(b, 3, 4))}
        </div>
      </div>
    </div>
  );
};

// ---------- linguagens antes x depois ----------
export const Antes: React.FC<B> = ({ b }) => {
  const t = t_();
  const bar = (v: number, a: number) => interpolate(t, [a, a + 0.8], [0, v], { ...clamp, easing: (x) => 1 - Math.pow(1 - x, 3) });
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <DicaBar on={4} />
      <Title at={0.2} t={"Meus acertos em *linguagens*"} size={66} style={{ marginTop: 60 }} />
      <div style={{ marginTop: 60, display: "flex", flexDirection: "column", gap: 30 }}>
        {[
          ["simulados do ano", "30–35", 35, at(b, 0, 1), C.mute],
          ["reta final, com o Felipe", "40", 40, at(b, 1, 3), C.green],
        ].map(([l, s, v, a, c]) => (
          <Reveal key={l as string} at={a as number}>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, marginBottom: 10 }}>{l}</div>
            <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
              <div style={{ height: 70, width: (bar(v as number, a as number) / 45) * 1050, background: c as string, borderRadius: 14, boxShadow: c === C.green ? `0 0 40px rgba(43,232,107,0.5)` : "none" }} />
              <div style={{ fontFamily: "Anton", fontSize: 80, color: c as string }}>{s}</div>
            </div>
          </Reveal>
        ))}
      </div>
      <Reveal at={at(b, 1, 3) + 0.6}>
        <div style={{ fontFamily: SANS, fontSize: 26, color: C.mute, marginTop: 24 }}>de 45 questões</div>
      </Reveal>
    </div>
  );
};

// ---------- grade da semana montando ----------
type Cell = [number, number, string, number, boolean?, boolean?]; // dia, periodo (0 manha,1 tarde,2 noite), texto, at, destaque, base (1/4 de baixo do bloco)
export const Semana: React.FC<{ cells: Cell[]; title?: string }> = ({ cells, title = "Minha *semana*" }) => {
  const t = t_();
  const P = ["manhã", "tarde", "noite"];
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 20 }}>
      <Title at={0.1} t={title} size={60} />
      <div style={{ display: "grid", gridTemplateColumns: "110px repeat(7, 1fr)", gridTemplateRows: "50px repeat(3, 230px)", gap: 8, marginTop: 24 }}>
        <div />
        {DIAS.map((d) => (
          <div key={d} style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: C.mute, textAlign: "center", alignSelf: "center" }}>{d}</div>
        ))}
        {P.map((p, r) => (
          <React.Fragment key={p}>
            <div style={{ fontFamily: SANS, fontSize: 24, color: C.mute, alignSelf: "center" }}>{p}</div>
            {DIAS.map((_, d) => {
              const doSlot = cells.filter((x) => x[0] === d && x[1] === r);
              const main = doSlot.filter((x) => !x[5]).sort((x, y) => x[3] - y[3]);
              const c = [...main].reverse().find((x) => t >= x[3]) ?? main[0];
              const base = doSlot.find((x) => x[5]);
              const k = c ? interpolate(t, [c[3], c[3] + 0.2], [0, 1], clamp) : 0;
              const kb = base ? interpolate(t, [base[3], base[3] + 0.2], [0, 1], clamp) : 0;
              const hot = c?.[4];
              return (
                <div key={d} style={{ display: "flex", flexDirection: "column", gap: 5, minHeight: 0 }}>
                  <div style={{ flex: 3, minHeight: 0, borderRadius: 14, border: `2px solid ${k > 0 && hot ? C.green : C.line}`, background: k > 0 ? (hot ? C.green : C.greenDim) : C.card, display: "flex", alignItems: "center", justifyContent: "center", padding: 8, textAlign: "center" }}>
                    {c && <span style={{ opacity: k, transform: `scale(${0.8 + 0.2 * k})`, fontFamily: SANS, fontSize: 21, fontWeight: 700, lineHeight: 1.2, color: hot ? C.bg : C.text }}>{c[2]}</span>}
                  </div>
                  {base && (
                    <div style={{ flex: 1, minHeight: 0, borderRadius: 10, border: `2px solid ${kb > 0 ? C.green : C.line}`, background: kb > 0 ? "rgba(43,232,107,0.28)" : C.card, display: "flex", alignItems: "center", justifyContent: "center", padding: "2px 6px", textAlign: "center" }}>
                      <span style={{ opacity: kb, fontFamily: SANS, fontSize: 16, fontWeight: 700, lineHeight: 1.1, color: C.text }}>{base[2]}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

// ---------- notas: total + materias contando ----------
export const Notas: React.FC<{ t: string; itens: [number, string, string, number][] }> = ({ t, itens }) => (
  <div style={center}>
    <Title at={0.1} t={t} size={76} />
    <div style={{ display: "flex", gap: 26, marginTop: 60 }}>
      {itens.map(([n, s, l, a]) => (
        <Reveal key={l} at={a} style={{ flex: 1 }}>
          <Card style={{ textAlign: "center" }}>
            <div style={{ fontFamily: "Anton", fontSize: 150, color: C.green, lineHeight: 1.1 }}>
              <Count to={n} at={a} dur={0.8} />
              <span style={{ fontSize: 64, color: C.mute }}>{s}</span>
            </div>
            <div style={{ fontFamily: SANS, fontSize: 34, color: C.text, fontWeight: 700 }}>{l}</div>
          </Card>
        </Reveal>
      ))}
    </div>
  </div>
);

// ---------- o que mais cai: duas colunas de etiquetas ----------
export const Cai: React.FC<{ on: number; dicas?: string[]; cols: [string, [string, number][]][] }> = ({ on, dicas, cols }) => (
  <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
    <DicaBar on={on} dicas={dicas} />
    <Title at={0.2} t={"O que *mais cai*"} size={70} style={{ marginTop: 50 }} />
    <div style={{ display: "flex", gap: 40, marginTop: 44 }}>
      {cols.map(([nome, tags]) => (
        <div key={nome} style={{ flex: 1 }}>
          <div style={{ fontFamily: "Anton", fontSize: 54, color: C.green }}>{nome}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 20 }}>
            {tags.map(([g, a]) => (
              <Reveal key={g} at={a} dy={0}>
                <div style={{ fontFamily: SANS, fontSize: 34, fontWeight: 700, color: C.text, padding: "14px 24px", borderRadius: 16, background: C.card, border: `2px solid ${C.line}` }}>{g}</div>
              </Reveal>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const GRAPHICSS: Record<string, React.FC<any>> = { Dica, AberturaS, Maratona, Provas, Fiscal, Matriz, Antes, Semana, Notas, Cai };
