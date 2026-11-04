import { continueRender, delayRender, staticFile } from "remotion";

// Anton = fonte das palavras de impacto (bold condensada, a mesma do kinetic aprovado)
const handle = delayRender("Carregando Anton");
const face = new FontFace("Anton", `url(${staticFile("Anton.ttf")})`);
face
  .load()
  .then((f) => {
    document.fonts.add(f);
    continueRender(handle);
  })
  .catch((err) => console.error(err));
