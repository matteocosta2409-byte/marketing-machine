import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, SANS } from "./theme";

// Thumbnail 1280x720: foto de aprovacao recortada, 3 linhas de copy (a do meio na caixa verde) e os acertos embaixo.
export type ThumbProps = { l1: string; l2: string; l3: string; notas: [string, string][]; dia?: string };
export const thumbDefaults: ThumbProps = { l1: "COMO DIVIDIR", l2: "AS 5H30", l3: "DO ENEM DIA 1", notas: [["40/45", "Linguagens"], ["42/45", "Humanas"], ["940", "Redação"]] };

const metal: React.CSSProperties = {
  backgroundImage: "linear-gradient(180deg, #FFFFFF 35%, #C9D2CC 100%)",
  WebkitBackgroundClip: "text",
  color: "transparent",
  filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.8))",
};

// folha da prova no canto (ilustracao, nao e a capa oficial)
const Folha: React.FC<{ dia: string }> = ({ dia }) => (
  <div style={{ position: "absolute", left: 1066, top: 416, width: 240, height: 360, transform: "rotate(6deg)", background: "linear-gradient(180deg, #E9FBEF 0%, #C4F0D2 100%)", borderRadius: 10, boxShadow: "-14px 16px 40px rgba(0,0,0,0.7)", padding: "12px 14px" }}>
    <div style={{ height: 20, width: 80, marginLeft: "auto", backgroundImage: "repeating-linear-gradient(90deg, #14211A 0 3px, transparent 3px 5px, #14211A 5px 6px, transparent 6px 10px)" }} />
    <div style={{ fontFamily: SANS, fontSize: 10, fontWeight: 800, color: "#14211A", marginTop: 6 }}>EXAME NACIONAL DO ENSINO MÉDIO</div>
    <div style={{ fontFamily: SANS, fontSize: 40, fontWeight: 900, letterSpacing: -2, lineHeight: 1.1, color: "#14211A", marginTop: 4 }}>enem2026</div>
    <div style={{ fontFamily: "Anton", fontSize: 30, color: "#0F7A38", marginTop: 2 }}>{dia}</div>
    {[...Array(9)].map((_, i) => (
      <div key={i} style={{ height: 7, borderRadius: 4, background: "#8FCFA5", marginTop: 11, width: `${60 + ((i * 17) % 35)}%` }} />
    ))}
  </div>
);

export const Thumb: React.FC<ThumbProps> = ({ l1, l2, l3, notas, dia = "1º DIA" }) => (
  <AbsoluteFill style={{ background: `radial-gradient(620px 560px at 24% 48%, #1FA855 0%, #0C4A28 45%, ${C.bg} 78%)`, overflow: "hidden" }}>
    <AbsoluteFill
      style={{
        backgroundImage: "linear-gradient(rgba(43,232,107,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(43,232,107,0.10) 1px, transparent 1px)",
        backgroundSize: "44px 44px",
        maskImage: "radial-gradient(circle at 75% 40%, black, transparent 70%)",
      }}
    />
    <Img src={staticFile("enem1/thumb_eu.png")} style={{ position: "absolute", left: -70, bottom: -6, height: 700, filter: "drop-shadow(0 0 30px rgba(0,0,0,0.55))" }} />
    <Folha dia={dia} />
    <div style={{ position: "absolute", left: 580, right: 96, top: 26, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ fontFamily: "Anton", fontSize: 88, lineHeight: 1.15, whiteSpace: "nowrap", ...metal }}>{l1}</div>
      <div style={{ margin: "6px 0 10px", padding: "2px 34px 8px", borderRadius: 22, background: "linear-gradient(180deg, #33F077 0%, #129A45 100%)", boxShadow: "0 0 50px rgba(43,232,107,0.55)", fontFamily: "Anton", fontSize: 134, lineHeight: 1.12, color: "#FFFFFF", textShadow: "0 5px 12px rgba(0,60,25,0.75)", whiteSpace: "nowrap" }}>{l2}</div>
      <div style={{ fontFamily: "Anton", fontSize: 88, lineHeight: 1.15, whiteSpace: "nowrap", ...metal }}>{l3}</div>
      <div style={{ display: "flex", gap: notas.length > 2 ? 8 : 12, marginTop: 22, marginRight: notas.length > 2 ? 44 : 0 }}>
        {notas.map(([n, l]) => (
          <div key={l} style={{ background: "#FFFFFF", borderRadius: 16, padding: notas.length > 2 ? "8px 11px 10px" : "8px 18px 10px", textAlign: "center", boxShadow: "0 10px 26px rgba(0,0,0,0.55)" }}>
            <div style={{ fontFamily: "Anton", fontSize: 52, lineHeight: 1.1, color: "#0F7A38" }}>{n}</div>
            <div style={{ fontFamily: SANS, fontSize: notas.length > 2 ? 19 : 22, fontWeight: 800, color: "#14211A" }}>{l}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 18, marginRight: notas.length > 2 ? 44 : 0, padding: "6px 24px 9px", borderRadius: 18, border: `4px solid ${C.green}`, background: "rgba(5,30,16,0.85)", boxShadow: "0 0 26px rgba(43,232,107,0.4)", fontFamily: "Anton", fontStyle: "italic", fontSize: 40, lineHeight: 1.15, color: C.green, whiteSpace: "nowrap" }}>1º LUGAR EM MEDICINA</div>
    </div>
  </AbsoluteFill>
);
