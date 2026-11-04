import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Rich, SANS, SERIF, useIn } from "./theme";

// Camada estilo Dan Martell por cima do rosto: fotos de arquivo em tela cheia, texto kinetic,
// reframe riscado, pilulas de checklist e telas de numero grande. Tempos `at` relativos ao inicio do overlay.
export type Ov = { from: number; to: number; k: string; [key: string]: unknown };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const sec = () => {
  const f = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return { f, fps, t: f / fps, dur: durationInFrames / fps };
};

// grao de filme + vinheta (fotos de arquivo)
const Grain: React.FC = () => {
  const { f } = sec();
  return (
    <>
      <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.13, mixBlendMode: "overlay" }}>
        <filter id={`g${f % 6}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={f % 6} />
        </filter>
        <rect width="100%" height="100%" filter={`url(#g${f % 6})`} />
      </svg>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%)" }} />
    </>
  );
};

const Bg: React.FC = () => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: `radial-gradient(1200px 700px at 30% 20%, rgba(43,232,107,0.12), transparent 60%), ${C.bg}`,
    }}
  >
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundImage: `linear-gradient(${C.line}55 1px, transparent 1px), linear-gradient(90deg, ${C.line}55 1px, transparent 1px)`,
        backgroundSize: "64px 64px",
        maskImage: "radial-gradient(circle at 50% 50%, black, transparent 75%)",
      }}
    />
  </div>
);

// ---------- foto de arquivo em tela cheia (corte seco, Ken Burns lento, legenda tipo lower third) ----------
const Photo: React.FC<{ src: string; title?: string; sub?: string; pos?: string }> = ({ src, title, sub, pos = "50% 50%" }) => {
  const { t, dur } = sec();
  const s = interpolate(t, [0, dur], [1.0, 1.07], clamp);
  const cap = useIn(0.15);
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", background: "#000" }}>
      <Img src={staticFile(src)} style={{ position: "absolute", inset: -60, width: "calc(100% + 120px)", height: "calc(100% + 120px)", objectFit: "cover", filter: "blur(40px) brightness(0.45) saturate(0.9)" }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${s})` }}>
        <Img src={staticFile(src)} style={{ height: 1080, maxWidth: 1920, objectFit: "cover", objectPosition: pos, boxShadow: "0 0 120px rgba(0,0,0,0.8)" }} />
      </div>
      <Grain />
      {title && (
        <div style={{ position: "absolute", left: 90, bottom: 100, opacity: cap, transform: `translateX(${(1 - cap) * -40}px)` }}>
          <div style={{ fontFamily: SANS, fontSize: 54, fontWeight: 800, color: "#fff", textShadow: "0 4px 30px rgba(0,0,0,0.8)" }}>{title}</div>
          <div style={{ height: 5, width: 90, background: C.green, borderRadius: 3, margin: "10px 0" }} />
          {sub && <div style={{ fontFamily: SANS, fontSize: 30, color: "#E6ECE8", textShadow: "0 2px 20px rgba(0,0,0,0.9)" }}>{sub}</div>}
        </div>
      )}
    </div>
  );
};

// ---------- tela de numero grande (gancho) ----------
const Big: React.FC<{ lines: { t: string; at: number; size?: number; c?: string }[] }> = ({ lines }) => {
  const { t } = sec();
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Bg />
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10 }}>
        {lines.map((l, i) => {
          const p = interpolate(t, [l.at, l.at + 0.12], [0, 1], clamp);
          return (
            <div key={i} style={{ fontFamily: "Anton", fontSize: l.size ?? 220, lineHeight: 1, color: l.c === "g" ? C.green : C.text, opacity: p, transform: `scale(${1.25 - 0.25 * p})`, textShadow: l.c === "g" ? `0 0 60px rgba(43,232,107,0.5)` : "none" }}>
              {l.t}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------- "comeca pela 1a e vai uma por uma ate acabar o tempo" ----------
const Race: React.FC<{ end?: number }> = ({ end = 3.9 }) => {
  const { t } = sec();
  const k = interpolate(t, [0.2, end], [0, 1], clamp);
  const q = Math.max(1, Math.round(1 + 89 * Math.pow(k, 1.6) * 0.62)); // nao chega na 90: o tempo acaba antes
  const mins = Math.round(interpolate(k, [0, 1], [13 * 60 + 30, 18 * 60 + 30]));
  const hh = `${Math.floor(mins / 60)}:${String(mins % 60).padStart(2, "0")}`;
  const over = t > end;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Bg />
      <div style={{ position: "absolute", left: 160, top: 250, width: 820 }}>
        {[0, 1, 2].map((j) => (
          <div key={j} style={{ position: "absolute", left: j * 26, top: j * 26, width: 700, height: 520, borderRadius: 24, background: "#F3F5F2", boxShadow: "0 20px 60px rgba(0,0,0,0.5)", zIndex: 3 - j, padding: 44, opacity: 1 - j * 0.25 }}>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 44, color: "#1b1b1b" }}>QUESTÃO {q + j}</div>
            {[...Array(7)].map((_, i) => (
              <div key={i} style={{ height: 18, background: "#D8DDD9", borderRadius: 9, marginTop: 28, width: `${55 + ((q * 7 + i * 13) % 40)}%` }} />
            ))}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", right: 170, top: 300, textAlign: "right" }}>
        <div style={{ fontFamily: SANS, fontSize: 34, color: C.mute }}>uma por uma…</div>
        <div style={{ fontFamily: "Anton", fontSize: 200, color: over ? C.red : C.text, lineHeight: 1.1 }}>{hh}</div>
        <div style={{ width: 520, height: 22, borderRadius: 11, background: C.card, border: `2px solid ${C.line}`, marginLeft: "auto", overflow: "hidden" }}>
          <div style={{ width: `${(1 - k) * 100}%`, height: "100%", background: k > 0.8 ? C.red : C.green }} />
        </div>
        <div style={{ fontFamily: "Anton", fontSize: 80, color: C.red, marginTop: 30, opacity: over ? 1 : 0 }}>ACABOU O TEMPO</div>
      </div>
    </div>
  );
};

// ---------- frase kinetic por cima do rosto (palavra por palavra) ----------
const Quote: React.FC<{ t: string; step?: number; size?: number; y?: number }> = ({ t: text, step = 0.14, size = 78, y = 120 }) => {
  const { t } = sec();
  const words = text.split(" ");
  let star = false;
  return (
    <div style={{ position: "absolute", left: 120, right: 120, bottom: y, textAlign: "center", fontFamily: SERIF, fontSize: size, fontWeight: 600, color: "#fff", lineHeight: 1.15, textShadow: "0 4px 40px rgba(0,0,0,0.85), 0 2px 8px rgba(0,0,0,0.6)" }}>
      {words.map((w, i) => {
        const open = w.startsWith("*");
        if (open) star = true;
        const hot = star;
        if (w.endsWith("*") || w.endsWith("*,") || w.endsWith("*.")) star = false;
        const p = interpolate(t, [i * step, i * step + 0.1], [0, 1], clamp);
        return (
          <span key={i} style={{ opacity: p, display: "inline-block", transform: `translateY(${(1 - p) * 14}px)`, color: hot ? C.green : "#fff", fontStyle: hot ? "italic" : "normal", marginRight: "0.25em" }}>
            {w.replace(/\*/g, "")}
          </span>
        );
      })}
    </div>
  );
};

// ---------- reframe: frase riscada -> frase nova ----------
const Strike: React.FC<{ a: string; b: string; tb: number }> = ({ a, b, tb }) => {
  const { t } = sec();
  const pa = useIn(0);
  const cut = interpolate(t, [tb - 0.35, tb - 0.05], [0, 1], clamp);
  const pb = useIn(tb);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 110, textAlign: "center", textShadow: "0 4px 40px rgba(0,0,0,0.85)" }}>
      <div style={{ position: "relative", display: "inline-block", fontFamily: SANS, fontWeight: 800, fontSize: 64, color: "#fff", opacity: pa * (1 - 0.45 * cut) }}>
        {a}
        <div style={{ position: "absolute", left: -10, top: "52%", height: 8, width: `calc(${cut * 100}% + 20px)`, background: C.red, borderRadius: 4 }} />
      </div>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 600, fontSize: 96, color: C.green, opacity: pb, transform: `scale(${0.85 + 0.15 * pb})`, marginTop: 18 }}>{b}</div>
    </div>
  );
};

// ---------- pilulas de checklist do lado do rosto ----------
const Pills: React.FC<{ items: { t: string; at: number; x?: boolean }[] }> = ({ items }) => (
  <div style={{ position: "absolute", right: 90, top: 300, display: "flex", flexDirection: "column", gap: 18, alignItems: "flex-end" }}>
    {items.map((it, i) => (
      <Pill key={i} {...it} />
    ))}
  </div>
);
const Pill: React.FC<{ t: string; at: number; x?: boolean }> = ({ t, at, x }) => {
  const p = useIn(at, 16);
  return (
    <div style={{ opacity: p, transform: `translateX(${(1 - p) * 60}px)`, display: "flex", alignItems: "center", gap: 16, background: "rgba(11,14,12,0.82)", border: `2px solid ${x ? C.red : C.green}`, borderRadius: 18, padding: "14px 26px", boxShadow: "0 16px 40px rgba(0,0,0,0.45)" }}>
      <span style={{ width: 38, height: 38, borderRadius: 10, background: x ? C.red : C.green, color: C.bg, display: "inline-flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 900, fontSize: 24 }}>{x ? "✕" : "✓"}</span>
      <span style={{ fontFamily: SANS, fontSize: 40, fontWeight: 700, color: C.text }}>
        <Rich t={t} />
      </span>
    </div>
  );
};

// ---------- print de fonte (ranking, artigo) com marca-texto verde passando nos trechos ----------
// hl em pixels da imagem original: [x, y, w, h, at]
const Shot: React.FC<{ src: string; w: number; h: number; hl: [number, number, number, number, number][]; zoom?: [number, number]; cap?: string }> = ({ src, w, h, hl, zoom, cap }) => {
  const { t, dur } = sec();
  const k = Math.min(1700 / w, 900 / h);
  const z = zoom ? interpolate(t, [0, 0.35, 1.5, dur], [1, 1, 1.8, 1.9], { ...clamp, easing: (x) => x * x * (3 - 2 * x) }) : interpolate(t, [0, dur], [1, 1.08], clamp);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Bg />
      <div style={{ position: "absolute", left: (1920 - w * k) / 2, top: (1080 - h * k) / 2 - 20, width: w * k, height: h * k, transform: `scale(${z})`, transformOrigin: zoom ? `${(zoom[0] / w) * 100}% ${(zoom[1] / h) * 100}%` : "50% 50%" }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: 18, overflow: "hidden", boxShadow: "0 30px 90px rgba(0,0,0,0.7)" }}>
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%" }} />
          {hl.map(([x, y, ww, hh, a], i) => {
            const p = interpolate(t, [a, a + 0.35], [0, 1], clamp);
            return <div key={i} style={{ position: "absolute", left: x * k, top: y * k, width: ww * k * p, height: hh * k, background: "rgba(43,232,107,0.55)", mixBlendMode: "multiply", borderRadius: 6 }} />;
          })}
        </div>
      </div>
      {cap && (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 40, textAlign: "center" }}>
          <span style={{ fontFamily: SANS, fontSize: 26, color: C.text, background: "rgba(11,14,12,0.85)", borderRadius: 12, padding: "10px 20px" }}>fonte: {cap}</span>
        </div>
      )}
    </div>
  );
};

export const OVERLAYS: Record<string, React.FC<any>> = { Photo, Big, Race, Quote, Strike, Pills, Shot };
// tipos que cobrem a tela toda (o rosto some por baixo)
export const FULL = new Set(["Photo", "Big", "Race", "Shot"]);
