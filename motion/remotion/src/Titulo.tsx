import React from "react";
import { AbsoluteFill } from "remotion";

// Titulo de abertura aprovado (out/2026: versao MAIOR): SF Pro branca no TOPO, sombra sem contorno,
// headline ate 2 linhas + kicker 1 linha mais leve. Sem animacao: na tela desde o quadro 0.
export type TituloProps = {
  headline: string;
  kicker?: string;
  top?: number;
  // padrao aprovado (28/10/2026): 74 / 800 / sombra 0.85 / top 120. Antigo pequeno: 50 / 600 / 0.6 / 150.
  // 88 quebra em 3 linhas e encosta no cabelo: manter <= 74 e headline em 2 linhas
  size?: number;
  weight?: number;
  shadow?: number;
};

export const tituloDefaults: TituloProps = {
  headline: "O idiota impaciente >\no gênio que pensa demais",
  kicker: "",
  top: 120,
};

export const Titulo: React.FC<TituloProps> = ({ headline, kicker, top, size = 74, weight = 800, shadow = 0.85 }) => (
  <AbsoluteFill>
    <div
      style={{
        position: "absolute",
        top: top ?? 120,
        left: 40,
        right: 40,
        textAlign: "center",
        fontFamily: "-apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif",
        color: "white",
        textShadow: `0 ${size * 0.05}px ${size * 0.3}px rgba(0,0,0,${shadow})`,
      }}
    >
      <div style={{ fontSize: size, fontWeight: weight, lineHeight: 1.12, whiteSpace: "pre-line" }}>{headline}</div>
      {kicker ? (
        <div style={{ fontSize: size * 0.74, fontWeight: 500, marginTop: 10, opacity: 0.92 }}>{kicker}</div>
      ) : null}
    </div>
  </AbsoluteFill>
);
