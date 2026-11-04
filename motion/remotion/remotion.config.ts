// Overlays do Matteo: saem SEMPRE com alpha (ProRes 4444) pra compor por cima do video no ffmpeg.
import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
// EDIT_FULL=1 -> edicao completa opaca em h264 (comp Enem); sem isso, overlay com alpha
if (!process.env.EDIT_FULL) {
  Config.setVideoImageFormat("png");
  Config.setPixelFormat("yuva444p10le");
  Config.setCodec("prores");
  Config.setProResProfile("4444");
}
