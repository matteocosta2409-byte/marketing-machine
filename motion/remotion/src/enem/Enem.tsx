import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, SANS } from "./theme";
import { GRAPHICS, Lower } from "./graphics";
import { OVERLAYS, Ov } from "./overlays";
import { GRAPHICS1 } from "./graphics1";
import { GRAPHICSS } from "./graphicsS";
import { GRAPHICST } from "./graphicsT";

// Edicao completa estilo Ali Abdaal: video A-cut em tela cheia; nos graficos o rosto encolhe pro card da direita.
// Todos os tempos em segundos na timeline do A-cut.
export type Seg = { from: number; to: number; g: string; props?: Record<string, unknown> };
export type Zoom = { from: number; to: number; s: number };
export type Sfx = { t: number; f: string; v?: number };
export type EnemProps = {
  video: string;
  duration: number;
  segs: Seg[];
  lowers: { from: number; to: number; name: string; role: string }[];
  zooms: Zoom[];
  sfx: Sfx[];
  music?: { f: string; v: number };
  ovs?: Ov[];
  // video-rascunho sem gravacao: video "" vira um quadro vazio; voz = audio de teste; legendas = frase na tela
  voz?: string;
  legendas?: { from: number; to: number; t: string }[];
};

export const enemDefaults: EnemProps = { video: "enem/acut.mp4", duration: 10, segs: [], lowers: [], zooms: [], sfx: [] };

export const calcEnem: CalculateMetadataFunction<EnemProps> = ({ props }) => ({
  durationInFrames: Math.ceil(props.duration * 30),
});

const PIP = { x: 1490, y: 290, w: 370, h: 500 };
const RAMP = 0.33; // s da transicao tela cheia <-> card

// junta graficos colados (gap < 0.4s) num bloco so, pro rosto nao ficar subindo e descendo
const merge = (segs: Seg[]) => {
  const out: [number, number][] = [];
  [...segs].sort((a, b) => a.from - b.from).forEach((s) => {
    const l = out[out.length - 1];
    if (l && s.from - l[1] < 0.4) l[1] = Math.max(l[1], s.to);
    else out.push([s.from, s.to]);
  });
  return out;
};

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

export const Enem: React.FC<EnemProps> = ({ video, segs, lowers, zooms, sfx, music, ovs = [], voz, legendas = [] }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const blocks = merge(segs);
  let pip = 0;
  for (const [a, b] of blocks) {
    const v = Math.min(
      interpolate(t, [a, a + RAMP], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      interpolate(t, [b - RAMP, b], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    );
    pip = Math.max(pip, v);
  }
  const e = ease(pip);
  const box = {
    left: interpolate(e, [0, 1], [0, PIP.x]),
    top: interpolate(e, [0, 1], [0, PIP.y]),
    width: interpolate(e, [0, 1], [1920, PIP.w]),
    height: interpolate(e, [0, 1], [1080, PIP.h]),
    radius: interpolate(e, [0, 1], [0, 28]),
  };
  // punch-in so com o rosto em tela cheia (corte seco, sem animar)
  const z = zooms.find((zz) => t >= zz.from && t < zz.to);
  const zs = z && pip === 0 ? z.s : 1;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {/* fundo dos graficos: escuro com brilho verde e grade sutil */}
      <AbsoluteFill
        style={{
          opacity: e,
          background: `radial-gradient(1200px 700px at 20% 15%, rgba(43,232,107,0.10), transparent 60%), radial-gradient(900px 600px at 90% 100%, rgba(43,232,107,0.07), transparent 60%), ${C.bg}`,
        }}
      >
        <AbsoluteFill
          style={{
            backgroundImage: `linear-gradient(${C.line}55 1px, transparent 1px), linear-gradient(90deg, ${C.line}55 1px, transparent 1px)`,
            backgroundSize: "64px 64px",
            maskImage: "radial-gradient(circle at 40% 50%, black, transparent 75%)",
          }}
        />
      </AbsoluteFill>

      {segs.map((s, i) => {
        const G = GRAPHICS[s.g] ?? GRAPHICS1[s.g] ?? GRAPHICSS[s.g] ?? GRAPHICST[s.g];
        const from = Math.round(s.from * fps);
        const dur = Math.max(1, Math.round((s.to - s.from) * fps));
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <GraphicFrame dur={dur}>
              <G {...(s.props || {})} />
            </GraphicFrame>
          </Sequence>
        );
      })}

      {/* rosto */}
      <div
        style={{
          position: "absolute",
          left: box.left,
          top: box.top,
          width: box.width,
          height: box.height,
          borderRadius: box.radius,
          overflow: "hidden",
          boxShadow: e > 0 ? `0 30px 80px rgba(0,0,0,${0.6 * e}), 0 0 0 ${3 * e}px ${C.green}` : "none",
        }}
      >
        {video ? (
          <OffthreadVideo
            src={staticFile(video)}
            style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zs})`, transformOrigin: "50% 38%" }}
          />
        ) : (
          <div style={{ width: "100%", height: "100%", background: C.card, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: SANS, textAlign: "center" }}>
            <div style={{ fontSize: 48, fontWeight: 800, color: C.text }}>Matteo</div>
            <div style={{ fontSize: 24, color: C.mute, marginTop: 8 }}>sua gravação entra aqui</div>
          </div>
        )}
      </div>

      {ovs.map((o, i) => {
        const O = OVERLAYS[o.k];
        const { from: a, to: z, k, ...rest } = o;
        return (
          <Sequence key={`o${i}`} from={Math.round(a * fps)} durationInFrames={Math.max(1, Math.round((z - a) * fps))} layout="none">
            <AbsoluteFill>
              <O {...rest} />
            </AbsoluteFill>
          </Sequence>
        );
      })}

      {lowers.map((l, i) => (
        <Sequence key={`l${i}`} from={Math.round(l.from * fps)} durationInFrames={Math.round((l.to - l.from) * fps)} layout="none">
          <Lower name={l.name} role={l.role} />
        </Sequence>
      ))}

      {legendas.filter((l) => t >= l.from && t < l.to).map((l) => (
        <div key={l.from} style={{ position: "absolute", left: 60, width: 1390, bottom: 26, display: "flex", justifyContent: "center" }}>
          <div style={{ background: "rgba(0,0,0,0.82)", color: "#fff", borderRadius: 14, padding: "10px 24px", fontFamily: SANS, fontSize: 31, fontWeight: 600, lineHeight: 1.22, textAlign: "center" }}>{l.t}</div>
        </div>
      ))}

      {voz && <Audio src={staticFile(voz)} />}
      {sfx.map((s, i) => (
        <Sequence key={`s${i}`} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={30} layout="none">
          <Audio src={staticFile(s.f)} volume={s.v ?? 0.5} />
        </Sequence>
      ))}
      {music && <Audio src={staticFile(music.f)} volume={music.v} loop />}
    </AbsoluteFill>
  );
};

// area do grafico (esquerda) com fade curto na entrada/saida
const GraphicFrame: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const f = useCurrentFrame();
  const o = Math.min(
    interpolate(f, [4, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    interpolate(f, [dur - 8, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  );
  return (
    <div style={{ position: "absolute", left: 80, top: 60, width: 1350, height: 960, opacity: o }}>
      {children}
    </div>
  );
};
