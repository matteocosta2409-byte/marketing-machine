import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Card, Count, Reveal, Rich, SANS, SERIF, Title, useIn } from "./theme";

// Cada grafico ocupa a area da esquerda (1380x960) enquanto o rosto fica no card da direita.
// `b` = batidas em segundos (relativas ao inicio do grafico), alinhadas com a fala.
type B = { b?: number[] };
const at = (b: number[] | undefined, i: number, d = 0) => (b && b[i] !== undefined ? b[i] : d);
const center: React.CSSProperties = { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" };

// ---------- Abertura: relogio de 5h dividido em 5 fatias ----------
export const Abertura: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const R = 250, cx = 330, cy = 480;
  const labels = ["Natureza", "Matemática", "As que ficaram", "", "Garimpo"];
  const arc = (a0: number, a1: number, r: number) => {
    const p = (a: number) => [cx + r * Math.sin(a), cy - r * Math.cos(a)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `M ${cx} ${cy} L ${x0} ${y0} A ${r} ${r} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${x1} ${y1} Z`;
  };
  return (
    <div style={{ ...center, flexDirection: "row", alignItems: "center", gap: 40 }}>
      <svg width={660} height={960}>
        <circle cx={cx} cy={cy} r={R + 14} fill="none" stroke={C.line} strokeWidth={4} />
        {[0, 1, 2, 3, 4].map((i) => {
          const s = at(b, 0, 0.2) + i * 0.35;
          const p = interpolate(f, [s * fps, (s + 0.4) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const a0 = (i / 5) * Math.PI * 2, a1 = a0 + ((Math.PI * 2) / 5) * p;
          return p > 0 ? (
            <path key={i} d={arc(a0, Math.max(a0 + 0.001, a1 - 0.03), R)} fill={i % 2 ? "rgba(43,232,107,0.55)" : C.green} opacity={0.35 + 0.13 * i} />
          ) : null;
        })}
        <circle cx={cx} cy={cy} r={110} fill={C.bg} />
        <text x={cx} y={cy + 30} textAnchor="middle" fill={C.text} style={{ fontFamily: "Anton", fontSize: 96 }}>5h</text>
        <text x={cx} y={cy + 76} textAnchor="middle" fill={C.mute} style={{ fontFamily: SANS, fontSize: 26 }}>90 questões</text>
      </svg>
      <div style={{ flex: 1 }}>
        <Title at={at(b, 1, 1.4)} t={"O plano do *2º dia*"} size={86} />
        <Reveal at={at(b, 1, 1.4) + 0.3}>
          <div style={{ fontFamily: SANS, fontSize: 34, color: C.mute, marginTop: 24 }}>hora por hora</div>
        </Reveal>
        <Reveal at={at(b, 1, 1.4) + 0.6}>
          <div style={{ display: "flex", gap: 12, marginTop: 36, flexWrap: "wrap" }}>
            {labels.filter(Boolean).map((l) => (
              <span key={l} style={{ fontFamily: SANS, fontSize: 24, color: C.green, border: `2px solid ${C.green}`, borderRadius: 40, padding: "8px 18px" }}>{l}</span>
            ))}
          </div>
        </Reveal>
      </div>
    </div>
  );
};

// ---------- Lower third (por cima do rosto em tela cheia) ----------
export const Lower: React.FC<{ name: string; role: string }> = ({ name, role }) => {
  const p = useIn(0.1);
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <div style={{ position: "absolute", left: 90, bottom: 110, transform: `translateX(${(1 - p) * -60}px)`, opacity: p }}>
      <div style={{ display: "flex", alignItems: "stretch", gap: 18 }}>
        <div style={{ width: 8, background: C.green, borderRadius: 4 }} />
        <div style={{ background: "rgba(11,14,12,0.82)", borderRadius: 16, padding: "16px 28px" }}>
          <div style={{ fontFamily: SERIF, fontSize: 52, color: C.text, fontWeight: 600 }}>{name}</div>
          <div style={{ fontFamily: SANS, fontSize: 28, color: C.green, marginTop: 4 }}>{role}</div>
        </div>
      </div>
      <span style={{ display: "none" }}>{f + durationInFrames}</span>
    </div>
  );
};

// ---------- Aquecimento: 5 questoes faceis + barra enchendo ----------
export const Aquecimento: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = at(b, 1, 1.2);
  const fill = interpolate(f, [s * fps, (s + 2.4) * fps], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={center}>
      <Title at={at(b, 0, 0)} t={"Antes de sair de casa: *aquecer*"} size={68} />
      <Reveal at={at(b, 0, 0) + 0.3}>
        <Card style={{ marginTop: 50, display: "flex", alignItems: "center", gap: 50 }}>
          <div style={{ fontFamily: "Anton", fontSize: 120, color: C.green, lineHeight: 1 }}>11:00</div>
          <div>
            <div style={{ fontFamily: SANS, fontSize: 40, color: C.text, fontWeight: 700 }}>5 questões fáceis de matemática</div>
            <div style={{ display: "flex", gap: 14, marginTop: 20 }}>
              {[0, 1, 2, 3, 4].map((i) => {
                const p = interpolate(f, [(s + i * 0.45) * fps, (s + i * 0.45 + 0.2) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                return (
                  <div key={i} style={{ width: 58, height: 58, borderRadius: 14, border: `3px solid ${p > 0.5 ? C.green : C.line}`, background: p > 0.5 ? C.greenDim : "transparent", display: "flex", alignItems: "center", justifyContent: "center", color: C.green, fontSize: 36, fontFamily: SANS, fontWeight: 800, transform: `scale(${1 + 0.15 * Math.sin(p * Math.PI)})` }}>
                    {p > 0.5 ? "✓" : ""}
                  </div>
                );
              })}
            </div>
          </div>
        </Card>
      </Reveal>
      <Reveal at={s}>
        <div style={{ marginTop: 44, fontFamily: SANS, fontSize: 30, color: C.mute, display: "flex", justifyContent: "space-between" }}>
          <span>cérebro</span>
          <span style={{ color: C.green, fontWeight: 700 }}>{Math.round(fill)}% aquecido</span>
        </div>
        <div style={{ marginTop: 14, height: 30, borderRadius: 20, background: C.card, border: `2px solid ${C.line}`, overflow: "hidden" }}>
          <div style={{ width: `${fill}%`, height: "100%", background: `linear-gradient(90deg, #1a8f45, ${C.green})`, boxShadow: `0 0 30px ${C.green}` }} />
        </div>
      </Reveal>
    </div>
  );
};

// ---------- Linha do tempo do dia ----------
export const DiaTimeline: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const nodes = [
    ["11:00", "aquecimento"],
    ["12:00", "portão abre"],
    ["13:00", "portão fecha"],
    ["13:30", "prova começa"],
    ["18:30", "fim"],
  ];
  const t0 = at(b, 0, 0.3);
  const step = b && b.length > 1 ? null : 0.6;
  const tn = (i: number) => (step === null ? at(b, i, t0 + i * 0.6) : t0 + i * step);
  const line = interpolate(f, [tn(0) * fps, tn(4) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={center}>
      <Title t={"O *domingo* da prova"} size={68} />
      <div style={{ position: "relative", height: 380, marginTop: 70 }}>
        <div style={{ position: "absolute", left: 60, right: 60, top: 110, height: 6, background: C.line, borderRadius: 3 }} />
        <div style={{ position: "absolute", left: 60, width: `calc((100% - 120px) * ${line})`, top: 110, height: 6, background: C.green, borderRadius: 3, boxShadow: `0 0 20px ${C.green}` }} />
        {nodes.map(([t, l], i) => {
          const p = interpolate(f, [tn(i) * fps, (tn(i) + 0.3) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const hot = i === 2;
          return (
            <div key={t} style={{ position: "absolute", left: `calc(60px + (100% - 120px) * ${i / 4})`, top: 0, transform: "translateX(-50%)", textAlign: "center", opacity: p, width: 240 }}>
              <div style={{ fontFamily: "Anton", fontSize: 54, color: hot ? C.red : C.text }}>{t}</div>
              <div style={{ margin: "14px auto", width: 34, height: 34, borderRadius: 20, background: hot ? C.red : C.green, transform: `scale(${p})`, boxShadow: `0 0 24px ${hot ? C.red : C.green}` }} />
              <div style={{ fontFamily: SANS, fontSize: 28, color: hot ? C.red : C.mute, marginTop: 8 }}>{l}</div>
            </div>
          );
        })}
      </div>
      <Reveal at={tn(4) + 0.5}>
        <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute, textAlign: "center" }}>horário de Brasília</div>
      </Reveal>
    </div>
  );
};

// ---------- Folhear a prova ----------
export const Folhear: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tags = [["gráfico", 0], ["imagem", 2], ["conta longa", 4], ["texto grande", 6]] as const;
  const t0 = at(b, 0, 0.2);
  const flip = interpolate(f, [t0 * fps, (t0 + 3.2) * fps], [0, 7], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ ...center, flexDirection: "row", alignItems: "center", gap: 70 }}>
      <div style={{ position: "relative", width: 520, height: 700 }}>
        {[...Array(8)].map((_, i) => {
          const k = Math.min(1, Math.max(0, flip - i));
          return (
            <div key={i} style={{ position: "absolute", inset: 0, background: "#F3F5F2", borderRadius: 18, boxShadow: "0 10px 40px rgba(0,0,0,0.5)", transformOrigin: "left center", transform: `perspective(1600px) rotateY(${-k * 165}deg) translateX(${i * 3}px)`, zIndex: 20 - i, padding: 40, opacity: k > 0.98 ? 0 : 1 }}>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "#222" }}>QUESTÃO {91 + i * 6}</div>
              {[...Array(9)].map((__, j) => (
                <div key={j} style={{ height: 14, background: "#D8DDD9", borderRadius: 7, marginTop: 22, width: `${60 + ((i * 7 + j * 13) % 40)}%` }} />
              ))}
              {i % 2 === 0 && <div style={{ marginTop: 30, height: 160, borderRadius: 12, background: "linear-gradient(135deg,#cfe9d8,#9fd4b2)" }} />}
            </div>
          );
        })}
      </div>
      <div style={{ flex: 1 }}>
        <Title at={t0} t={"Primeiro: *folhear* a prova inteira"} size={60} />
        <div style={{ display: "flex", flexDirection: "column", gap: 18, marginTop: 40 }}>
          {tags.map(([t, k], i) => (
            <Reveal key={t} at={at(b, i + 1, t0 + 0.4 + (k as number) * 0.4)} dy={0}>
              <span style={{ display: "inline-block", fontFamily: SANS, fontSize: 32, color: C.bg, background: C.green, borderRadius: 12, padding: "10px 22px", fontWeight: 700, transform: `translateX(${i * 30}px)` }}>{t}</span>
            </Reveal>
          ))}
        </div>
      </div>
    </div>
  );
};

// ---------- TRI: titulo + 3 parametros + coerencia ----------
export const TRI: React.FC<B> = ({ b }) => {
  const items = [
    ["Dificuldade", "quanto você precisa saber", "▲"],
    ["Discriminação", "separa quem sabe de quem não sabe", "⇅"],
    ["Acerto ao acaso", "a chance do chute", "🎲"],
  ];
  return (
    <div style={center}>
      <Reveal at={at(b, 0, 0)}>
        <div style={{ fontFamily: "Anton", fontSize: 150, color: C.green, lineHeight: 1 }}>TRI</div>
      </Reveal>
      <Title at={at(b, 0, 0) + 0.2} t={"Teoria de *Resposta* ao Item"} size={56} />
      <div style={{ display: "flex", gap: 26, marginTop: 60 }}>
        {items.map(([t, d, ic], i) => (
          <div key={t} style={{ flex: 1, position: "relative" }}>
          {/* slots vazios numerados assim que ele fala "tres caracteristicas" (nao deixar o titulo sozinho) */}
          <Reveal at={at(b, 5, 99) + i * 0.15} style={{ position: "absolute", inset: 0 }}>
            <div style={{ height: 270, borderRadius: 28, border: `3px dashed ${C.line}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Anton", fontSize: 110, color: C.line }}>{i + 1}</div>
          </Reveal>
          <Reveal at={at(b, i + 1, 1 + i)}>
            <Card style={{ height: 270 }}>
              <div style={{ width: 70, height: 70, borderRadius: 18, background: C.greenDim, color: C.green, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 38 }}>{ic}</div>
              <div style={{ fontFamily: SANS, fontSize: 38, color: C.text, fontWeight: 800, marginTop: 26 }}>{t}</div>
              <div style={{ fontFamily: SANS, fontSize: 27, color: C.mute, marginTop: 10, lineHeight: 1.3 }}>{d}</div>
            </Card>
          </Reveal>
          </div>
        ))}
      </div>
      <Reveal at={at(b, 4, 4.5)}>
        <div style={{ marginTop: 44, fontFamily: SERIF, fontSize: 50, color: C.text }}>
          <Rich t={"E o principal: *coerência*."} />
        </div>
      </Reveal>
    </div>
  );
};

// ---------- Aluno A x Aluno B: mesmos 30 acertos, notas diferentes ----------
const PAT_A = Array.from({ length: 45 }, (_, i) => (i < 26 ? i !== 9 && i !== 19 : [27, 29, 31, 33, 36, 40].includes(i)));
const PAT_B = Array.from({ length: 45 }, (_, i) => [1, 3, 4, 7, 10, 12, 15, 16, 18, 21, 22, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44].includes(i));
export const Alunos: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const row = (name: string, pat: boolean[], t: number) => (
    <Reveal at={t}>
      <div style={{ display: "flex", alignItems: "center", gap: 24, marginTop: 34 }}>
        <div style={{ width: 150, fontFamily: SANS, fontSize: 36, color: C.text, fontWeight: 800 }}>{name}</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(45, 17px)", gap: 5 }}>
          {pat.map((ok, i) => {
            const p = interpolate(f, [(t + i * 0.02) * fps, (t + i * 0.02 + 0.15) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <div key={i} style={{ width: 17, height: 34, borderRadius: 6, background: ok ? C.green : "transparent", border: `2px solid ${ok ? C.green : C.line}`, transform: `scale(${p})` }} />;
          })}
        </div>
        <div style={{ fontFamily: "Anton", fontSize: 50, color: C.text, marginLeft: 8 }}>30</div>
      </div>
    </Reveal>
  );
  const tA = at(b, 0, 0.3), tB = at(b, 1, 2.5), tS = at(b, 2, 5);
  const bar = (w: number, t: number) => interpolate(f, [t * fps, (t + 1) * fps], [0, w], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  return (
    <div style={center}>
      <Title t={"Mesmos acertos, *notas diferentes*"} size={62} />
      <div style={{ display: "flex", justifyContent: "space-between", marginLeft: 174, width: 45 * 22, marginTop: 30, fontFamily: SANS, fontSize: 24, color: C.mute }}>
        <span>← fáceis</span>
        <span>difíceis →</span>
      </div>
      {row("Aluno A", PAT_A, tA)}
      {row("Aluno B", PAT_B, tB)}
      <Reveal at={tS} style={{ marginTop: 56 }}>
        {[["A", 620, C.green], ["B", 380, C.mute]].map(([n, w, c]) => (
          <div key={n as string} style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 16 }}>
            <div style={{ width: 150, fontFamily: SANS, fontSize: 30, color: C.mute }}>nota {n}</div>
            <div style={{ height: 40, width: bar(w as number, tS), background: c as string, borderRadius: 10, boxShadow: n === "A" ? `0 0 30px ${C.green}` : "none" }} />
          </div>
        ))}
      </Reveal>
    </div>
  );
};

// ---------- Regra pratica (frase grande) ----------
export const Regra: React.FC<{ t: string; sub?: string } & B> = ({ t, sub, b }) => (
  <div style={{ ...center, alignItems: "flex-start" }}>
    <Reveal at={0}>
      <div style={{ fontFamily: SANS, fontSize: 30, letterSpacing: 4, color: C.green, fontWeight: 800 }}>REGRA PRÁTICA</div>
    </Reveal>
    <Title at={0.15} t={t} size={84} style={{ marginTop: 24 }} />
    {sub && (
      <Reveal at={at(b, 0, 1.2)}>
        <div style={{ fontFamily: SANS, fontSize: 36, color: C.mute, marginTop: 30 }}>{sub}</div>
      </Reveal>
    )}
  </div>
);

// ---------- Barra das horas (topo dos blocos de estrategia) ----------
const HOURS = ["1ª hora", "até 2h30", "2h30 → 4h", "última hora", "15 min"];
const HSUB = ["natureza teórica", "matemática rápida", "as que ficaram", "garimpar", "gabarito"];
export const HourBar: React.FC<{ on: number }> = ({ on }) => {
  const p = useIn(0.05);
  return (
    <div style={{ display: "flex", gap: 10 }}>
      {HOURS.map((h, i) => {
        const hot = i === on, done = i < on;
        return (
          <div key={h} style={{ flex: i === 2 ? 2 : 1, borderRadius: 14, padding: "14px 18px", background: hot ? C.green : done ? C.greenDim : C.card, border: `2px solid ${hot || done ? C.green : C.line}`, transform: hot ? `scale(${0.9 + 0.1 * p})` : undefined }}>
            <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 800, color: hot ? C.bg : done ? C.green : C.mute }}>{h}</div>
            <div style={{ fontFamily: SANS, fontSize: 20, color: hot ? C.bg : C.mute, marginTop: 2 }}>{HSUB[i]}</div>
          </div>
        );
      })}
    </div>
  );
};

// aparece em `a` e some antes de `z` (texto provisorio ate a lista entrar)
const Fade: React.FC<{ a: number; z: number; children: React.ReactNode }> = ({ a, z, children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = Math.min(
    interpolate(f, [a * fps, (a + 0.2) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    interpolate(f, [z * fps, (z + 0.2) * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  );
  return <div style={{ opacity: o }}>{children}</div>;
};

// ---------- Hora 1: natureza teorica ----------
export const Hora1: React.FC<B> = ({ b }) => {
  const chips: [string, boolean][] = [["Biologia", true], ["Química conceitual", true], ["Física rápida", true], ["Conta longa", false], ["Difícil", false]];
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <HourBar on={0} />
      <div style={{ display: "flex", gap: 40, marginTop: 70, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <Title at={0.2} t={"Natureza *teórica*"} size={70} />
          {b && b[6] !== undefined && (
            <div style={{ position: "relative", height: 0 }}>
              <div style={{ position: "absolute", top: 20, left: 0, right: 0, opacity: (b[0] ?? 0) <= 0 ? 0 : undefined }}>
                <Fade a={b[6]} z={b[0] - 0.2}>
                  <div style={{ fontFamily: SANS, fontSize: 36, color: C.mute }}>teóricas e conceituais</div>
                </Fade>
                <Fade a={b[7]} z={b[0] - 0.2}>
                  <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 50, color: C.green, marginTop: 18 }}>ou você sabe, ou não sabe.</div>
                </Fade>
              </div>
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 36 }}>
            {chips.map(([c, ok], i) => (
              <Reveal key={c} at={at(b, i, 0.8 + i * 0.5)} dy={0}>
                <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: SANS, fontSize: 34, color: ok ? C.text : C.mute }}>
                  <span style={{ width: 46, height: 46, borderRadius: 12, display: "inline-flex", alignItems: "center", justifyContent: "center", background: ok ? C.green : C.card, color: ok ? C.bg : C.mute, fontWeight: 900, border: ok ? "none" : `2px solid ${C.line}` }}>{ok ? "✓" : "→"}</span>
                  {c}
                  {!ok && <span style={{ fontSize: 26, color: C.mute }}>pro final</span>}
                </div>
              </Reveal>
            ))}
          </div>
        </div>
        <Reveal at={at(b, 5, 3.5)}>
          <Card style={{ width: 430, textAlign: "center" }}>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute }}>em 1 hora</div>
            <Count to={30} at={at(b, 5, 3.5)} dur={1.6} style={{ fontFamily: "Anton", fontSize: 190, color: C.green, lineHeight: 1.1 }} />
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>questões de natureza</div>
          </Card>
        </Reveal>
      </div>
    </div>
  );
};

// ---------- Hora 2: matriz facil/dificil x rapida/demorada ----------
export const Hora2: React.FC<B> = ({ b }) => {
  const cells = [
    ["Fácil + rápida", "AGORA", true],
    ["Fácil + demorada", "pro final", false],
    ["Difícil + rápida", "pro final", false],
    ["Difícil + demorada", "garimpo", false],
  ] as const;
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <HourBar on={1} />
      <div style={{ display: "flex", gap: 50, marginTop: 50, alignItems: "center" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, width: 820 }}>
          {cells.map(([t, a, hot], i) => (
            <Reveal key={t} at={at(b, i, 0.4 + i * 0.6)}>
              <div style={{ height: 230, borderRadius: 24, padding: 28, background: hot ? C.green : C.card, border: `2px solid ${hot ? C.green : C.line}`, boxShadow: hot ? `0 0 50px rgba(43,232,107,0.35)` : "none" }}>
                <div style={{ fontFamily: SANS, fontSize: 30, color: hot ? C.bg : C.mute, fontWeight: 600 }}>{t}</div>
                <div style={{ fontFamily: "Anton", fontSize: 76, color: hot ? C.bg : i === 3 ? C.green : C.text, marginTop: 20 }}>{a}</div>
              </div>
            </Reveal>
          ))}
        </div>
        <Reveal at={at(b, 4, 3.4)}>
          <Card style={{ width: 430, textAlign: "center" }}>
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.mute }}>até aqui</div>
            <Count to={30} at={at(b, 4, 3.4)} dur={1.6} style={{ fontFamily: "Anton", fontSize: 190, color: C.green, lineHeight: 1.1 }} />
            <div style={{ fontFamily: SANS, fontSize: 30, color: C.text }}>de matemática</div>
            <div style={{ fontFamily: SANS, fontSize: 28, color: C.green, marginTop: 18, fontWeight: 700 }}>≈ 60 de 90 feitas</div>
          </Card>
        </Reveal>
      </div>
    </div>
  );
};

// ---------- Horas 3-4: pilhas alternando ----------
export const Hora34: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t0 = at(b, 0, 1);
  const k = Math.max(0, (f / fps - t0) / 0.7);
  const side = Math.floor(k) % 2;
  const pile = (name: string, n: number, i: number) => (
    <div style={{ textAlign: "center", width: 360 }}>
      <div style={{ position: "relative", height: 330 }}>
        {[...Array(7)].map((_, j) => (
          <div key={j} style={{ position: "absolute", left: 40, right: 40, bottom: j * 22, height: 170, borderRadius: 16, background: j === 6 && side === i && k > 0 ? C.green : C.card, border: `2px solid ${j === 6 && side === i && k > 0 ? C.green : C.line}` }} />
        ))}
      </div>
      <div style={{ fontFamily: "Anton", fontSize: 90, color: C.text, marginTop: 20 }}>{n}</div>
      <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute }}>{name}</div>
    </div>
  );
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <HourBar on={2} />
      <Title at={0.2} t={"Sobram *~30*: as demoradas"} size={62} style={{ marginTop: 50 }} />
      <Reveal at={0.6}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 60, marginTop: 30 }}>
          {pile("natureza", 15, 0)}
          <div style={{ fontFamily: SANS, fontSize: 80, color: C.green, transform: `scaleX(${side ? -1 : 1})` }}>⇄</div>
          {pile("matemática", 15, 1)}
        </div>
      </Reveal>
    </div>
  );
};

// ---------- Hora 5: garimpo. 10 questoes dificeis; a busca pula entre elas e cada acerto vira verde ----------
const ROTA = [2, 7, 0, 9, 4, 6, 1, 8];
const ACERTOS = [7, 9, 4, 1];
export const Garimpo: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const t0 = at(b, 3, 8), PASSO = 0.42;
  const atual = Math.floor((t - t0) / PASSO);
  const noAlvo = t >= t0 && atual < ROTA.length ? ROTA[atual] : -1;
  const quando = (i: number) => t0 + ROTA.indexOf(i) * PASSO;
  const n = ACERTOS.filter((i) => t >= quando(i)).length;
  const fila = (nome: string, de: number, entra: number) => (
    <div style={{ marginTop: 22 }}>
      <Reveal at={entra} dy={0}>
        <div style={{ fontFamily: SANS, fontSize: 28, fontWeight: 700, color: C.mute, marginBottom: 12 }}>{nome}</div>
      </Reveal>
      <div style={{ display: "flex", gap: 12 }}>
        {[0, 1, 2, 3, 4].map((k) => {
          const i = de + k;
          const certo = ACERTOS.includes(i) && t >= quando(i);
          const pop = certo ? interpolate(t, [quando(i), quando(i) + 0.22], [1.2, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
          const visto = ROTA.includes(i) && t >= quando(i);
          return (
            <Reveal key={i} at={entra + k * 0.08} dy={14}>
              <div style={{ width: 106, height: 126, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", background: certo ? C.green : C.card, border: `3px solid ${noAlvo === i ? C.text : certo ? C.green : C.line}`, transform: `scale(${pop})`, boxShadow: certo ? "0 0 34px rgba(43,232,107,0.55)" : "none", fontFamily: "Anton", fontSize: certo ? 52 : 46, color: certo ? C.bg : visto ? C.line : C.mute }}>
                {certo ? "+1" : "?"}
              </div>
            </Reveal>
          );
        })}
      </div>
    </div>
  );
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <HourBar on={3} />
      <div style={{ display: "flex", alignItems: "center", gap: 50, marginTop: 50 }}>
        <div style={{ flex: 1 }}>
          <Title at={at(b, 0, 0.2)} t={"*Garimpar* acertos"} size={76} />
          <Reveal at={at(b, 5, 3)}>
            <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute, marginTop: 22 }}>ninguém gabarita o dia 2</div>
          </Reveal>
          <Reveal at={t0}>
            <div style={{ fontFamily: "Anton", fontSize: 110, color: C.green, marginTop: 26, lineHeight: 1 }}>+{n}</div>
          </Reveal>
          <Reveal at={at(b, 4, 10)}>
            <div style={{ fontFamily: SERIF, fontSize: 44, color: C.text, marginTop: 20 }}>
              <Rich t={"cada acerto é *ouro*"} />
            </div>
          </Reveal>
        </div>
        <div>
          {fila("5 de natureza", 0, at(b, 1, 1))}
          {fila("5 de matemática", 5, at(b, 2, 2))}
        </div>
      </div>
    </div>
  );
};

// ---------- Gabarito: numero + letra, uma por uma ----------
export const Gabarito: React.FC<B> = ({ b }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ans = ["A", "C", "E", "B", "D", "A", "C", "B"];
  const t0 = at(b, 1, 1.5);
  return (
    <div style={{ ...center, justifyContent: "flex-start", paddingTop: 30 }}>
      <HourBar on={4} />
      <div style={{ display: "flex", gap: 60, marginTop: 50, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <Title at={at(b, 0, 0.2)} t={"*15 minutos* só pro gabarito"} size={66} />
          <Reveal at={at(b, 0, 0.2) + 0.4}>
            <div style={{ fontFamily: SANS, fontSize: 34, color: C.mute, marginTop: 24 }}>número e letra, uma por uma</div>
          </Reveal>
        </div>
        <Card style={{ width: 520, padding: 30 }}>
          {ans.map((a, i) => {
            const p = interpolate(f, [(t0 + i * 0.55) * fps, (t0 + i * 0.55 + 0.2) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, marginTop: i ? 12 : 0 }}>
                <div style={{ width: 70, fontFamily: SANS, fontSize: 28, color: C.mute, fontWeight: 700 }}>{91 + i}</div>
                {["A", "B", "C", "D", "E"].map((l) => (
                  <div key={l} style={{ width: 44, height: 44, borderRadius: 22, border: `2px solid ${C.line}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontSize: 20, color: C.mute, background: l === a && p > 0.5 ? C.green : "transparent", transform: l === a ? `scale(${1 + 0.25 * Math.sin(p * Math.PI)})` : undefined }}>
                    <span style={{ color: l === a && p > 0.5 ? C.bg : C.mute, fontWeight: 800 }}>{l}</span>
                  </div>
                ))}
                <div style={{ fontFamily: SANS, fontSize: 24, color: C.green, opacity: p, fontWeight: 700 }}>“{91 + i}, {a}”</div>
              </div>
            );
          })}
        </Card>
      </div>
    </div>
  );
};

// ---------- Resumo: lista numerada que vai montando ----------
export const Resumo: React.FC<B> = ({ b }) => {
  const items = [
    ["Antes", "5 questões fáceis pra aquecer"],
    ["1ª hora", "natureza teórica"],
    ["até 2h30", "matemática rápida"],
    ["2h30 → 4h", "as que ficaram, pulando"],
    ["Última hora", "garimpar acertos"],
    ["15 min", "fechar o gabarito"],
  ];
  return (
    <div style={center}>
      <Title t={"*Resumo*"} size={70} />
      <div style={{ marginTop: 34, display: "flex", flexDirection: "column", gap: 14 }}>
        {items.map(([h, d], i) => (
          <Reveal key={h} at={at(b, i, 0.4 + i * 0.8)} dy={0} style={{}}>
            <div style={{ display: "flex", alignItems: "center", gap: 24, background: C.card, border: `2px solid ${C.line}`, borderRadius: 18, padding: "16px 24px" }}>
              <div style={{ width: 54, height: 54, borderRadius: 27, background: C.green, color: C.bg, fontFamily: SANS, fontSize: 30, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
              <div style={{ fontFamily: SANS, fontSize: 34, color: C.text, fontWeight: 800, width: 230 }}>{h}</div>
              <div style={{ fontFamily: SANS, fontSize: 32, color: C.mute }}>{d}</div>
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  );
};

// ---------- Fechamento ----------
export const Final: React.FC<B> = ({ b }) => (
  <div style={{ ...center, alignItems: "center", textAlign: "center" }}>
    <Reveal at={0}>
      <div style={{ width: 1100 }}>
        <HourBar on={5} />
      </div>
    </Reveal>
    <Title at={at(b, 0, 0.6)} t={"Fáceis primeiro, *difícil* pro final."} size={70} style={{ marginTop: 70 }} />
    <Reveal at={at(b, 1, 1.6)}>
      <div style={{ fontFamily: "Anton", fontSize: 120, color: C.green, marginTop: 40 }}>15/11 · BOA PROVA</div>
    </Reveal>
  </div>
);

export const GRAPHICS: Record<string, React.FC<any>> = {
  Abertura, Aquecimento, DiaTimeline, Folhear, TRI, Alunos, Regra, Hora1, Hora2, Hora34, Garimpo, Gabarito, Resumo, Final,
};
