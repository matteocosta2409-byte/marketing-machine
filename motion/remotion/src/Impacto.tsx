import React from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import "./fonts";

// Verde da marca do Matteo
export const VERDE = "#2BE86B";

export type ImpactoProps = {
  // "word" = palavra grande; "counter" = numero subindo de 0 ate `to`
  kind: "word" | "counter";
  text: string;
  to?: number;
  prefix?: string;
  suffix?: string;
  color?: string;
  // centro vertical na tela 1080x1920 (zona do peito ~1330, acima da legenda)
  y?: number;
  size?: number;
  seconds?: number;
  // quadrado preto gravado (find_slots.py, px 1080x1920): painel preenche o retangulo e o texto vai dentro
  box?: { x: number; y: number; w: number; h: number };
};

export const impactoDefaults: ImpactoProps = {
  kind: "word",
  text: "AÇÃO",
  color: VERDE,
  y: 1330,
  size: 190,
  seconds: 1.3,
};

export const calcImpacto: CalculateMetadataFunction<ImpactoProps> = ({ props }) => ({
  durationInFrames: Math.round((props.seconds ?? 1.3) * 30),
});

export const Impacto: React.FC<ImpactoProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // entrada: pop com leve overshoot (spring), saida: fade nos ultimos 6 quadros
  const pop = spring({ frame, fps, config: { damping: 11, stiffness: 180, mass: 0.7 } });
  const scale = interpolate(pop, [0, 1], [0.55, 1]);
  const opacity = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  let label = p.text;
  if (p.kind === "counter") {
    const up = spring({ frame, fps, config: { damping: 30, stiffness: 60 }, durationInFrames: 18 });
    label = `${p.prefix ?? ""}${Math.round((p.to ?? 0) * up)}${p.suffix ?? ""}`;
  }

  if (p.box) {
    const b = p.box;
    const fit = Math.min(b.h * 0.55, (b.w * 1.6) / Math.max(label.length, 2));
    return (
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            left: b.x,
            top: b.y,
            width: b.w,
            height: b.h,
            background: "#0b0b0b",
            borderTop: `${Math.max(6, b.h * 0.03)}px solid ${p.color ?? VERDE}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: interpolate(frame, [0, 4], [0, 1], { extrapolateRight: "clamp" }) * opacity,
          }}
        >
          <div
            style={{
              fontFamily: "Anton",
              fontSize: fit,
              color: p.color ?? VERDE,
              textTransform: "uppercase",
              transform: `scale(${scale})`,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {label}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: (p.y ?? 1330) - (p.size ?? 190) * 0.6,
          textAlign: "center",
          fontFamily: "Anton",
          fontSize: p.size ?? 190,
          lineHeight: 1.2,
          color: p.color ?? VERDE,
          textTransform: "uppercase",
          transform: `scale(${scale})`,
          opacity,
          // sombra suave pra ler em cima da camiseta/fundo, sem contorno grosso
          textShadow: "0 6px 24px rgba(0,0,0,0.55)",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
