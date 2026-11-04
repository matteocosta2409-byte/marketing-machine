import React from "react";
import { continueRender, delayRender, getInputProps, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// Tema escuro + verde da marca (#2BE86B). Titulos serifados (New York) no estilo Ali Abdaal, palavra-chave em verde.
const TEMAS = {
  escuro: { bg: "#0B0E0C", card: "#131915", line: "#22302A", text: "#F1F5F2", mute: "#86948C", green: "#2BE86B", greenDim: "rgba(43,232,107,0.16)", red: "#FF5A5A" },
  medio: { bg: "#1C2B23", card: "#28392F", line: "#3D5346", text: "#FFFFFF", mute: "#B4C4BA", green: "#3DF07A", greenDim: "rgba(61,240,122,0.22)", red: "#FF6B6B" },
  claro: { bg: "#F4F6F1", card: "#FFFFFF", line: "#D5DDD6", text: "#14211A", mute: "#5C6B62", green: "#14A04C", greenDim: "rgba(20,160,76,0.14)", red: "#D93636" },
};
// tema via props do render (--props tema): sem prop = escuro, igual aos videos ja entregues
export const C = TEMAS[(getInputProps().tema as keyof typeof TEMAS) ?? "escuro"] ?? TEMAS.escuro;
export const SANS = '-apple-system, "SF Pro Display", "Helvetica Neue", sans-serif';
export const SERIF = '"NY", "New York", Georgia, serif';

const h = delayRender("fontes NY");
Promise.all([
  new FontFace("NY", `url(${staticFile("NewYork.ttf")})`).load(),
  new FontFace("NY", `url(${staticFile("NewYorkItalic.ttf")})`, { style: "italic" }).load(),
  new FontFace("Anton", `url(${staticFile("Anton.ttf")})`).load(),
])
  .then((fs) => {
    fs.forEach((f) => document.fonts.add(f));
    continueRender(h);
  })
  .catch((e) => {
    console.error(e);
    continueRender(h);
  });

// entrada com mola a partir do segundo `at` (relativo ao inicio da Sequence)
export const useIn = (at = 0, damping = 14) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - at * fps, fps, config: { damping, mass: 0.7 } });
};

export const Reveal: React.FC<{ at?: number; dy?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  at = 0,
  dy = 24,
  children,
  style,
}) => {
  const p = useIn(at);
  return (
    <div style={{ opacity: interpolate(p, [0, 1], [0, 1]), transform: `translateY(${(1 - p) * dy}px)`, ...style }}>
      {children}
    </div>
  );
};

// "Texto com *destaque*" -> destaque em verde italico
export const Rich: React.FC<{ t: string }> = ({ t }) => (
  <>
    {t.split(/(\*[^*]+\*)/).map((s, i) =>
      s.startsWith("*") ? (
        <span key={i} style={{ color: C.green, fontStyle: "italic" }}>
          {s.slice(1, -1)}
        </span>
      ) : (
        <span key={i}>{s}</span>
      ),
    )}
  </>
);

export const Title: React.FC<{ t: string; at?: number; size?: number; style?: React.CSSProperties }> = ({
  t,
  at = 0,
  size = 64,
  style,
}) => (
  <Reveal at={at} style={{ fontFamily: SERIF, fontSize: size, color: C.text, fontWeight: 600, lineHeight: 1.1, ...style }}>
    <Rich t={t} />
  </Reveal>
);

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: C.card,
      border: `2px solid ${C.line}`,
      borderRadius: 28,
      padding: 32,
      boxShadow: "0 20px 60px rgba(0,0,0,0.45)",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Count: React.FC<{ to: number; at?: number; dur?: number; style?: React.CSSProperties; suffix?: string }> = ({
  to,
  at = 0,
  dur = 1.2,
  style,
  suffix = "",
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const v = interpolate(f, [at * fps, (at + dur) * fps], [0, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (x) => 1 - Math.pow(1 - x, 3),
  });
  return (
    <span style={style}>
      {Math.round(v)}
      {suffix}
    </span>
  );
};
