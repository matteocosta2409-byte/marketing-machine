import React from "react";
import { Composition } from "remotion";
import { Impacto, calcImpacto, impactoDefaults } from "./Impacto";
import { Titulo, tituloDefaults } from "./Titulo";
import { Enem, calcEnem, enemDefaults } from "./enem/Enem";
import { Thumb, thumbDefaults } from "./enem/Thumb";

// Canvas 1080x1920 (Reels). Pra fonte 4K vertical renderizar com --scale=2.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Impacto"
        component={Impacto}
        durationInFrames={39}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={impactoDefaults}
        calculateMetadata={calcImpacto}
      />
      {/* still: npx remotion still Titulo -> PNG; resync cola o PNG pelo video todo */}
      <Composition
        id="Titulo"
        component={Titulo}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={tituloDefaults}
      />
      {/* thumbnail do YouTube: npx remotion still Thumb --props=... */}
      <Composition id="Thumb" component={Thumb} durationInFrames={1} fps={30} width={1280} height={720} defaultProps={thumbDefaults} />
      {/* YouTube horizontal: edicao completa (A-cut + graficos + rosto em card). Render com --codec h264 */}
      <Composition
        id="Enem"
        component={Enem}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={enemDefaults}
        calculateMetadata={calcEnem}
      />
    </>
  );
};
