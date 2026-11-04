import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Card, Reveal, Rich, SANS, SERIF, Title, useIn } from "./theme";

// Graficos do video da TRI. Mesmo sistema da serie: area da esquerda, rosto no card da direita.
// Todos os tempos sao em segundos relativos ao inicio do grafico.
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const useT = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return f / fps;
};
const smooth = (t: number, a: number, d = 0.6) =>
  interpolate(t, [a, a + d], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });

// selo da origem do numero: o roteiro pede sempre na tela
export const Selo: React.FC<{ t: string; at?: number; forte?: boolean }> = ({ t, at = 0, forte }) => {
  const p = useIn(at);
  return (
    <div
      style={{
        display: "inline-block",
        opacity: p,
        transform: `scale(${0.9 + 0.1 * p})`,
        padding: "9px 18px",
        borderRadius: 999,
        fontFamily: SANS,
        fontSize: 22,
        fontWeight: 800,
        letterSpacing: 1.2,
        color: forte ? C.bg : C.green,
        background: forte ? C.green : C.greenDim,
        border: `2px solid ${C.green}`,
      }}
    >
      {t}
    </div>
  );
};

// ---------- Bloco 4: curva da q91 com os candidatos reais por faixa ----------
const W4 = 880;
const H4 = 600;
const M4 = { l: 100, r: 20, t: 14, b: 62 };
const x4 = (n: number) => M4.l + ((n - 300) / 600) * (W4 - M4.l - M4.r);
const y4 = (p: number) => H4 - M4.b - (p / 100) * (H4 - M4.t - M4.b);
// q91 (a=3,42 b=0,81 c=0,40), nota -> teta pela reta de Natureza do dossie (secao 10)
const curva91 = (n: number) => {
  const th = ((n + 64.4) / 1.131 - 500) / 100;
  return 100 * (0.4 + 0.6 / (1 + Math.exp(-3.42 * (th - 0.81))));
};
const PATH91 = Array.from({ length: 121 }, (_, i) => {
  const n = 300 + i * 5;
  return `${i ? "L" : "M"}${x4(n).toFixed(1)} ${y4(curva91(n)).toFixed(1)}`;
}).join(" ");

type Faixa4 = { rot: string; n: number; a: number; z: number; curva: number; real: number; tb: number; tc: number; tr: number };

export const Curva: React.FC<{ b: Record<string, number>; faixas: Faixa4[]; extras: [number, number][] }> = ({ b, faixas, extras }) => {
  const t = useT();
  const desenho = smooth(t, b.curva, 1.6);
  const atual = [...faixas].reverse().find((f) => t >= f.tb);
  const fimBanda = b.final;
  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <Title at={0.15} t={"Cada questão tem uma *curva*"} size={68} />
      <div style={{ position: "absolute", top: 92, left: 0, right: 0, height: 56, display: "flex", alignItems: "center", gap: 14 }}>
        <Selo t="NATUREZA 2025 · Q91 · AMARELO" at={b.tag} forte />
        <Reveal at={b.assunto} style={{ fontFamily: SANS, fontSize: 28, color: C.mute }}>
          Física: transferência de calor
        </Reveal>
      </div>

      <svg width={W4} height={H4} style={{ position: "absolute", left: 0, top: 170, overflow: "visible" }}>
        {[0, 25, 50, 75, 100].map((p) => (
          <g key={p}>
            <line x1={M4.l} x2={W4 - M4.r} y1={y4(p)} y2={y4(p)} stroke={C.line} strokeWidth={p === 0 ? 3 : 1.5} />
            <text x={M4.l - 14} y={y4(p) + 8} textAnchor="end" fontFamily={SANS} fontSize={22} fill={C.mute}>
              {p}%
            </text>
          </g>
        ))}
        {[300, 400, 500, 600, 700, 800, 900].map((n) => (
          <text key={n} x={x4(n)} y={H4 - M4.b + 32} textAnchor="middle" fontFamily={SANS} fontSize={22} fill={C.mute}>
            {n}
          </text>
        ))}
        {/* eixos acendem quando ele fala */}
        <text
          x={(M4.l + W4) / 2}
          y={H4 - 2}
          textAnchor="middle"
          fontFamily={SANS}
          fontSize={26}
          fontWeight={800}
          fill={t >= b.h && t < b.v ? C.green : C.text}
          opacity={smooth(t, b.h, 0.3)}
        >
          nível do aluno (nota)
        </text>
        <text
          transform={`translate(${M4.l - 84},${(H4 - M4.b) / 2}) rotate(-90)`}
          textAnchor="middle"
          fontFamily={SANS}
          fontSize={26}
          fontWeight={800}
          fill={t >= b.v && t < b.tag ? C.green : C.text}
          opacity={smooth(t, b.v, 0.3)}
        >
          chance de acertar
        </text>

        {/* faixa da fala */}
        {atual && t < fimBanda && (
          <rect x={x4(atual.a)} width={x4(atual.z) - x4(atual.a)} y={M4.t} height={H4 - M4.t - M4.b} fill={C.greenDim} opacity={smooth(t, atual.tb, 0.3)} />
        )}

        <path d={PATH91} fill="none" stroke={C.green} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - desenho} style={{ filter: `drop-shadow(0 0 10px ${C.green}66)` }} />

        {/* ponto previsto (anel) + candidatos reais (bolinha branca) */}
        {faixas.map((f) => {
          const pc = smooth(t, f.tc, 0.25);
          const pr = smooth(t, f.tr, 0.25);
          return (
            <g key={f.rot}>
              <circle cx={x4(f.n)} cy={y4(curva91(f.n))} r={14 * pc} fill="none" stroke={C.green} strokeWidth={4} opacity={pc} />
              <circle cx={x4(f.n)} cy={y4(f.real)} r={11 * pr} fill={C.text} stroke={C.bg} strokeWidth={3} />
            </g>
          );
        })}
        {extras.map(([n, real], i) => {
          const p = smooth(t, b.final + i * 0.22, 0.25);
          return <circle key={n} cx={x4(n)} cy={y4(real)} r={11 * p} fill={C.text} stroke={C.bg} strokeWidth={3} />;
        })}
      </svg>

      {/* painel curva x reais */}
      <div style={{ position: "absolute", left: 915, top: 190, width: 435 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.45fr 1fr 1fr", gap: 8, fontFamily: SANS, fontSize: 24, fontWeight: 800, opacity: smooth(t, faixas[0].tb, 0.4), marginBottom: 12 }}>
          <span style={{ color: C.mute }}>faixa</span>
          <span style={{ color: C.green }}>◯ curva</span>
          <span style={{ color: C.text }}>● reais</span>
        </div>
        {faixas.map((f) => {
          const on = atual?.rot === f.rot && t < fimBanda;
          return (
            <Reveal key={f.rot} at={f.tb}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1.45fr 1fr 1fr",
                  gap: 8,
                  alignItems: "center",
                  padding: "16px 14px",
                  marginBottom: 12,
                  borderRadius: 18,
                  background: on ? C.greenDim : C.card,
                  border: `2px solid ${on ? C.green : C.line}`,
                }}
              >
                <span style={{ fontFamily: SANS, fontSize: 25, color: C.text, fontWeight: 700, lineHeight: 1.15 }}>{f.rot}</span>
                <span style={{ fontFamily: "Anton", fontSize: 54, color: C.green, opacity: smooth(t, f.tc, 0.25) }}>{f.curva}%</span>
                <span style={{ fontFamily: "Anton", fontSize: 54, color: C.text, opacity: smooth(t, f.tr, 0.25) }}>{f.real}%</span>
              </div>
            </Reveal>
          );
        })}
        <Reveal at={b.final} style={{ marginTop: 16 }}>
          <Card style={{ padding: 22, borderColor: C.green }}>
            <div style={{ fontFamily: SERIF, fontSize: 36, color: C.text, fontWeight: 600, lineHeight: 1.15 }}>
              <Rich t={"Teoria e candidatos reais quase se *sobrepõem*"} />
            </div>
          </Card>
        </Reveal>
        <Reveal at={b.ressalva} style={{ marginTop: 12, fontFamily: SANS, fontSize: 24, color: C.mute }}>
          Nem sempre encaixa assim.
        </Reveal>
      </div>

      <div style={{ position: "absolute", left: 0, top: 802, fontFamily: SANS, fontSize: 21, color: C.mute, opacity: smooth(t, faixas[0].tr, 0.4) }}>
        Bolinhas: microdados do INEP, Enem 2025 · Curva: parâmetros oficiais, cálculo nosso
      </div>
    </div>
  );
};

// ---------- Bloco 8: 3 questoes, multiplicacao e plausibilidade ----------
const QUESTOES = [
  { q: "93", nivel: "fácil" },
  { q: "92", nivel: "média" },
  { q: "127", nivel: "difícil" },
];
const Marca: React.FC<{ ok: boolean; o: number }> = ({ ok, o }) => (
  <span style={{ fontFamily: SANS, fontSize: 30, lineHeight: "44px", fontWeight: 900, color: ok ? C.green : C.red, opacity: o }}>{ok ? "✓ acertou" : "✗ errou"}</span>
);
const Termo: React.FC<{ v: string; rot: string; at: number; final?: boolean }> = ({ v, rot, at, final }) => {
  const p = useIn(at);
  return (
    <div style={{ textAlign: "center", opacity: p, transform: `translateY(${(1 - p) * 18}px) scale(${0.85 + 0.15 * p})`, width: final ? 230 : 200 }}>
      <div style={{ fontFamily: "Anton", fontSize: final ? 112 : 88, lineHeight: 1.05, color: final ? C.green : C.text }}>{v}</div>
      <div style={{ fontFamily: SANS, fontSize: 23, color: final ? C.green : C.mute, fontWeight: 700, marginTop: 4 }}>{rot}</div>
    </div>
  );
};
const Sinal: React.FC<{ s: string; at: number }> = ({ s, at }) => (
  <div style={{ fontFamily: SANS, fontSize: 52, color: C.mute, fontWeight: 300, opacity: useIn(at), paddingBottom: 30 }}>{s}</div>
);
const Linha8: React.FC<{ nota: number; v: string[]; res: string; t: number[] }> = ({ nota, v, res, t }) => (
  <Card style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "26px 28px", opacity: useIn(t[0]) }}>
    <div style={{ width: 150, fontFamily: SANS, fontSize: 26, color: C.mute, fontWeight: 700 }}>
      nota
      <div style={{ fontFamily: "Anton", fontSize: 76, color: C.text, lineHeight: 1.1 }}>{nota}</div>
    </div>
    <Termo v={v[0]} rot="acertar a fácil" at={t[1]} />
    <Sinal s="×" at={t[2]} />
    <Termo v={v[1]} rot="acertar a média" at={t[2]} />
    <Sinal s="×" at={t[3]} />
    <Termo v={v[2]} rot="errar a difícil" at={t[3]} />
    <Sinal s="=" at={t[4]} />
    <Termo v={res} rot="responder assim" at={t[4]} final />
  </Card>
);

const NOTAS = [400, 500, 600, 700, 800, 900];
const PRODUTO = [3.4, 8.5, 18.9, 36, 28.5, 11.7];
const PLAUS = [7, 26, 40, 24, 3, 0.1];
const INVERTIDO = [42, 44, 13, 1, 0, 0];

export const Multiplica: React.FC<{ b: Record<string, number> }> = ({ b }) => {
  const t = useT();
  const aFinal = smooth(t, b.puxa, 1.6);
  const aInv = smooth(t, b.invCai, 1.4);
  const vals = NOTAS.map((_, i) => {
    const v = interpolate(aFinal, [0, 1], [PRODUTO[i], PLAUS[i]]);
    return interpolate(aInv, [0, 1], [v, INVERTIDO[i]]);
  });
  const A = interpolate(t, [b.barras - 0.4, b.barras], [1, 0], clamp);
  const B = interpolate(t, [b.barras - 0.1, b.barras + 0.4], [0, 1], clamp);
  const trocou = smooth(t, b.invMarca, 0.3);
  const X0 = 60;
  const DX = 225;
  const xNota = (n: number) => X0 + 90 + ((n - 400) / 100) * DX;
  const media = interpolate(aInv, [0, 1], [591, 473]);
  const pMedia = smooth(t, b.media, 0.5);
  const legenda = t < b.info ? "chance de responder exatamente assim" : t < b.invMarca ? "plausibilidade, com a informação inicial" : "plausibilidade, com o padrão invertido";
  const iTop = vals.indexOf(Math.max(...vals));
  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {t < b.titulo ? (
        <Title at={0.2} t={"A parte que *quase ninguém* explica"} size={60} />
      ) : (
        <Title at={b.titulo} t={"A conta é uma *multiplicação*, não uma soma"} size={60} />
      )}
      <div style={{ position: "absolute", top: 92, left: 0, display: "flex", gap: 14, alignItems: "center" }}>
        <Selo t="NATUREZA 2024 · AMARELO" at={b.q0 - 0.6} />
      </div>
      {/* as 3 questoes */}
      <div style={{ position: "absolute", top: 156, left: 0, right: 0, display: "flex", gap: 16 }}>
        {QUESTOES.map((q, i) => {
          const certo = i < 2;
          return (
            <Reveal key={q.q} at={b.q0 + i * b.qd} style={{ flex: 1 }}>
              <div style={{ background: C.card, border: `2px solid ${C.line}`, borderRadius: 20, padding: "14px 20px", display: "flex", alignItems: "center", height: 76, boxSizing: "border-box" }}>
                <span style={{ fontFamily: "Anton", fontSize: 42, color: C.text }}>q{q.q}</span>
                <span style={{ fontFamily: SANS, fontSize: 26, color: C.mute, marginLeft: 12 }}>{q.nivel}</span>
                <span style={{ marginLeft: "auto", position: "relative", width: 170, height: 44, textAlign: "right" }}>
                  <span style={{ position: "absolute", right: 0, whiteSpace: "nowrap" }}>
                    <Marca ok={certo} o={smooth(t, certo ? b.acertou : b.errou, 0.25) * (1 - trocou)} />
                  </span>
                  <span style={{ position: "absolute", right: 0, whiteSpace: "nowrap" }}>
                    <Marca ok={!certo} o={trocou} />
                  </span>
                </span>
              </div>
            </Reveal>
          );
        })}
      </div>

      {/* enquanto apresenta as questoes: x no lugar do + */}
      {t < b.pergunta && (
        <div style={{ position: "absolute", top: 300, left: 0, right: 0, height: 480, display: "flex", alignItems: "center", justifyContent: "center", gap: 170, fontFamily: SANS, opacity: smooth(t, 0.4, 0.5) * (1 - smooth(t, b.pergunta - 0.4, 0.4)) }}>
          <div style={{ position: "relative", fontSize: 240, fontWeight: 300, color: C.mute, lineHeight: 1 }}>
            +
            <div style={{ position: "absolute", left: -20, right: -20, top: "52%", height: 12, borderRadius: 6, background: C.red, transform: "rotate(-24deg)" }} />
          </div>
          <div style={{ fontSize: 360, fontWeight: 300, color: C.green, lineHeight: 1, textShadow: `0 0 50px ${C.green}77` }}>×</div>
        </div>
      )}

      {/* etapa A: multiplicacao linha a linha */}
      <div style={{ position: "absolute", top: 262, left: 0, right: 0, opacity: A }}>
        <Reveal at={b.pergunta} style={{ fontFamily: SERIF, fontSize: 40, color: C.text, marginBottom: 24, fontWeight: 600 }}>
          <Rich t={"Pra cada nota possível: qual a *chance de responder assim*?"} />
        </Reveal>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <Linha8 nota={400} v={["18%", "26%", "72%"]} res="3%" t={b.l400 as unknown as number[]} />
          <Linha8 nota={700} v={["92%", "74%", "53%"]} res="36%" t={b.l700 as unknown as number[]} />
        </div>
      </div>

      {/* etapa B: barras */}
      <div style={{ position: "absolute", top: 262, left: 0, right: 0, height: 560, opacity: B }}>
        <div style={{ fontFamily: SANS, fontSize: 28, fontWeight: 800, color: C.green }}>{legenda}</div>
        <svg width={1350} height={520} style={{ position: "absolute", top: 10, overflow: "visible" }}>
          <line x1={X0} x2={1350 - X0} y1={440} y2={440} stroke={C.line} strokeWidth={3} />
          {NOTAS.map((n, i) => {
            const h = (vals[i] / 48) * 370;
            const top = i === iTop;
            return (
              <g key={n}>
                <rect x={xNota(n) - 75} y={440 - h} width={150} height={h} rx={10} fill={top ? C.green : C.greenDim} stroke={C.green} strokeWidth={2} />
                <text x={xNota(n)} y={440 - h - 14} textAnchor="middle" fontFamily="Anton" fontSize={46} fill={top ? C.green : C.text}>
                  {Math.round(vals[i])}%
                </text>
                <text x={xNota(n)} y={482} textAnchor="middle" fontFamily={SANS} fontSize={30} fontWeight={800} fill={C.text}>
                  {n}
                </text>
              </g>
            );
          })}
          {/* marcador da media */}
          <g opacity={pMedia} transform={`translate(${xNota(media)},0)`}>
            <path d="M0 490 L-11 506 L11 506 Z" fill={C.text} />
            <rect x={-62} y={505} width={124} height={40} rx={20} fill={C.text} />
            <text x={0} y={534} textAnchor="middle" fontFamily={SANS} fontSize={25} fontWeight={800} fill={C.bg}>
              média
            </text>
          </g>
        </svg>
      </div>

      {/* mensagens das barras */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 824 }}>
        {t >= b.info && t < b.media && (
          <Reveal at={b.info} style={{ fontFamily: SANS, fontSize: 28, color: C.text }}>
            + informação inicial: como os concluintes de 2009 se distribuíam
          </Reveal>
        )}
        {t >= b.sustentou && t < b.selo && (
          <Reveal at={b.sustentou} style={{ fontFamily: SERIF, fontSize: 38, color: C.text, fontWeight: 600 }}>
            <Rich t={"O acerto na difícil *não sustentou* uma nota alta"} />
          </Reveal>
        )}
        {t >= b.selo && (
          <Reveal at={b.selo}>
            <Selo t="CÁLCULO NOSSO · PARÂMETROS OFICIAIS · SÓ 6 NOTAS" />
          </Reveal>
        )}
      </div>
    </div>
  );
};

// ---------- Bloco 9: a montanha que afina ----------
type Passo = { n: number; q: string; ok: boolean; m: number; sd: number; at: number };
const W9 = 930;
const H9 = 610;
const x9 = (n: number) => 30 + ((n - 300) / 600) * (W9 - 60);
const BASE9 = 540;

export const Montanha: React.FC<{ b: Record<string, number>; passos: Passo[] }> = ({ b, passos }) => {
  const t = useT();
  let i = -1;
  passos.forEach((p, k) => {
    if (t >= p.at) i = k;
  });
  const atual = i >= 0 ? passos[i] : null;
  const ant = i > 0 ? passos[i - 1] : atual;
  const mov = atual ? smooth(t, atual.at, 0.55) : 0;
  const m = atual && ant ? interpolate(mov, [0, 1], [ant.m, atual.m]) : 500;
  const sd = atual && ant ? interpolate(mov, [0, 1], [ant.sd, atual.sd]) : 110;
  const nasce = atual ? smooth(t, passos[0].at, 0.6) : 0;
  const K = 12300;
  const altura = (K / sd) * nasce;
  const pts: string[] = [];
  for (let n = 300; n <= 900; n += 4) {
    const y = BASE9 - altura * Math.exp(-0.5 * ((n - m) / sd) ** 2);
    pts.push(`${x9(n).toFixed(1)},${y.toFixed(1)}`);
  }
  const area = `M${x9(300)},${BASE9} L${pts.join(" L")} L${x9(900)},${BASE9} Z`;
  const fim = t >= b.reparo;
  const prog = atual ? atual.n / 44 : 0;
  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <Title at={0.15} t={"A cada resposta, a montanha *afina*"} size={64} />
      <div style={{ position: "absolute", top: 92, left: 0, display: "flex", gap: 14 }}>
        <Selo t="SIMULAÇÃO" at={b.selo} forte />
        <Selo t="ALUNO INVENTADO · QUESTÕES REAIS · NATUREZA 2024" at={b.selo + 0.5} />
      </div>
      <svg width={W9} height={H9} style={{ position: "absolute", top: 170, left: 0, overflow: "visible" }}>
        <defs>
          <linearGradient id="mt" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor={C.green} stopOpacity={0.55} />
            <stop offset="1" stopColor={C.green} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <line x1={x9(300)} x2={x9(900)} y1={BASE9} y2={BASE9} stroke={C.line} strokeWidth={3} />
        {[300, 400, 500, 600, 700, 800, 900].map((n) => (
          <text key={n} x={x9(n)} y={BASE9 + 34} textAnchor="middle" fontFamily={SANS} fontSize={23} fill={C.mute}>
            {n}
          </text>
        ))}
        <text x={W9 / 2} y={BASE9 + 70} textAnchor="middle" fontFamily={SANS} fontSize={24} fontWeight={800} fill={C.text}>
          nota em Natureza
        </text>
        <path d={area} fill="url(#mt)" stroke={C.green} strokeWidth={5} strokeLinejoin="round" style={{ filter: `drop-shadow(0 0 12px ${C.green}55)` }} />
        {/* nivel real do aluno */}
        <g opacity={smooth(t, b.real, 0.4)}>
          <line x1={x9(700)} x2={x9(700)} y1={30} y2={BASE9} stroke={C.text} strokeWidth={3} strokeDasharray="9 9" />
          <text x={x9(700) - 12} y={24} textAnchor="end" fontFamily={SANS} fontSize={26} fontWeight={800} fill={C.text}>
            nível real: 700
          </text>
        </g>
        {/* estimativa */}
        {atual && (
          <g opacity={nasce} transform={`translate(${x9(m)},0)`}>
            <line x1={0} x2={0} y1={BASE9 - altura} y2={BASE9} stroke={C.green} strokeWidth={3} />
            <circle cx={0} cy={BASE9 - altura} r={9} fill={C.green} stroke={C.bg} strokeWidth={3} />
          </g>
        )}
      </svg>

      {/* painel */}
      <div style={{ position: "absolute", left: 960, top: 190, width: 390 }}>
        <Reveal at={passos[0].at}>
          <Card style={{ padding: 26 }}>
            <div style={{ fontFamily: SANS, fontSize: 25, color: C.mute, fontWeight: 700 }}>nota até aqui</div>
            <div style={{ fontFamily: "Anton", fontSize: 138, color: C.green, lineHeight: 1.08 }}>{Math.round(m)}</div>
            <div style={{ fontFamily: SANS, fontSize: 42, color: C.text, fontWeight: 800 }}>margem ±{Math.round(sd)}</div>
          </Card>
        </Reveal>
        <Reveal at={passos[0].at + 0.15} style={{ marginTop: 18 }}>
          <Card style={{ padding: 24 }}>
            <div style={{ fontFamily: SANS, fontSize: 25, color: C.mute, fontWeight: 700 }}>
              respondidas: <span style={{ color: C.text, fontWeight: 900 }}>{atual?.n ?? 0} de 44</span>
            </div>
            <div style={{ height: 14, borderRadius: 7, background: C.line, overflow: "hidden", margin: "12px 0 16px" }}>
              <div style={{ width: `${prog * 100}%`, height: "100%", background: C.green }} />
            </div>
            {atual && (
              <div style={{ fontFamily: SANS, fontSize: 32, fontWeight: 900, color: atual.ok ? C.green : C.red }}>
                {atual.q}: {atual.ok ? "✓ certa" : "✗ errada"}
              </div>
            )}
          </Card>
        </Reveal>
        <Reveal at={b.reparo} style={{ marginTop: 18 }}>
          <Card style={{ padding: 22, borderColor: C.green }}>
            <div style={{ fontFamily: SERIF, fontSize: 36, color: C.text, fontWeight: 600, lineHeight: 1.15 }}>
              {fim && t >= b.medida ? <Rich t={"Toda medida *tem erro*"} /> : <Rich t={"Era *700*, saiu com *722*"} />}
            </div>
          </Card>
        </Reveal>
      </div>
    </div>
  );
};

export const GRAPHICST: Record<string, React.FC<any>> = { Curva, Multiplica, Montanha };
