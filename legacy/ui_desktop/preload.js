const { contextBridge } = require("electron/renderer");

contextBridge.exposeInMainWorld("geant4Desktop", {
  shell: "chromium",
  bridgeMode: "localhost-http",
  version: "0.1.0",
});
