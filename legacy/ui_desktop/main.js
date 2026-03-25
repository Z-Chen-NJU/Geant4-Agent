const { app, BrowserWindow, dialog, shell } = require("electron/main");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const HOST = process.env.G4_DESKTOP_HOST || "127.0.0.1";
const PORT = process.env.G4_DESKTOP_PORT || "8088";
const START_URL = `http://${HOST}:${PORT}`;
const REPO_ROOT = path.resolve(__dirname, "..", "..");

let bridgeProcess = null;

function pythonCandidates() {
  const candidates = [];
  const venvPython = path.resolve(REPO_ROOT, ".venv", "Scripts", "python.exe");
  if (fs.existsSync(venvPython)) {
    candidates.push({ command: venvPython, extraArgs: [] });
  }
  if (process.env.G4_DESKTOP_PYTHON) {
    candidates.push({ command: process.env.G4_DESKTOP_PYTHON, extraArgs: [] });
  }
  candidates.push({ command: "python", extraArgs: [] });
  candidates.push({ command: "py", extraArgs: [] });
  return candidates;
}

function attachBridgeLogging(child) {
  child.stdout.on("data", (chunk) => process.stdout.write(`[desktop-bridge] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[desktop-bridge] ${chunk}`));
  child.on("exit", (code) => {
    process.stderr.write(`[desktop-bridge] exited with code ${code}\n`);
    if (bridgeProcess === child) {
      bridgeProcess = null;
    }
  });
}

async function spawnBridge(candidate) {
  return await new Promise((resolve, reject) => {
    const args = [
      ...candidate.extraArgs,
      "-m",
      "ui.desktop.runtime_bridge",
      "--host",
      HOST,
      "--port",
      PORT,
    ];

    const child = spawn(candidate.command, args, {
      cwd: REPO_ROOT,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });

    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        attachBridgeLogging(child);
        resolve(child);
      }
    }, 700);

    child.once("error", (error) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(error);
      }
    });

    child.once("exit", (code) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error(`bridge bootstrap exited early with code ${code}`));
      }
    });
  });
}

async function startBridge() {
  if (bridgeProcess) {
    return bridgeProcess;
  }

  let lastError = null;
  for (const candidate of pythonCandidates()) {
    try {
      const child = await spawnBridge(candidate);
      bridgeProcess = child;
      return child;
    } catch (error) {
      lastError = error;
    }
  }

  throw new Error(`Unable to start Python desktop bridge. ${lastError ? String(lastError) : ""}`);
}

async function waitForBridge(timeoutMs = 20000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(`${START_URL}/api/runtime`);
      if (response.ok) {
        return;
      }
    } catch (_) {
      // bridge not ready yet
    }
    await new Promise((resolve) => setTimeout(resolve, 350));
  }
  throw new Error(`Desktop bridge did not become ready within ${timeoutMs} ms.`);
}

async function createMainWindow() {
  await startBridge();
  await waitForBridge();

  const win = new BrowserWindow({
    width: 1460,
    height: 980,
    minWidth: 1100,
    minHeight: 760,
    backgroundColor: "#11161b",
    autoHideMenuBar: false,
    title: "Geant4-Agent Desktop",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  await win.loadURL(START_URL);
}

app.whenReady().then(async () => {
  try {
    await createMainWindow();
  } catch (error) {
    dialog.showErrorBox("Geant4-Agent Desktop Startup Failed", String(error));
    app.quit();
    return;
  }

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createMainWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  if (bridgeProcess) {
    bridgeProcess.kill();
    bridgeProcess = null;
  }
});
