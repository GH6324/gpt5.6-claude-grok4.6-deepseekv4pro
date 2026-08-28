const { app, BrowserWindow, ipcMain, dialog, shell, clipboard } = require("electron");
const path = require("node:path");
const { BLADES, QQ_GROUPS, TELEGRAM, TOOLS, toolById } = require("./lib/catalog");
const { catalogStatus, runTool } = require("./lib/hub");
const { inspectTarget, resolveCodexHome } = require("./lib/inspect");
const { environmentStatus, pythonExecutable } = require("./lib/env");
const { liveAcceptance } = require("./lib/live");
const { oneClickBreak, oneClickRestore } = require("./lib/oneshot");
const { setupEnvironment } = require("./lib/setup");

const SPLASH_MS = 4800;
const IS_MAC = process.platform === "darwin";
const APP_ICON = path.join(__dirname, "..", "assets", process.platform === "win32" ? "icon.ico" : "icon.png");
let splashWindow;
let mainWindow;
let currentBlade = "ALL";

function emitLog(entry) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("brew:log", entry);
  }
}

function createSplash() {
  splashWindow = new BrowserWindow({
    width: 1080,
    height: 640,
    frame: false,
    transparent: false,
    resizable: false,
    show: false,
    backgroundColor: "#090705",
    autoHideMenuBar: true,
    icon: APP_ICON,
    titleBarStyle: IS_MAC ? "hidden" : "default",
  });
  splashWindow.loadFile(path.join(__dirname, "splash", "index.html"));
  splashWindow.once("ready-to-show", () => splashWindow.show());
}

function createMain() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1080,
    minHeight: 720,
    frame: false,
    show: false,
    backgroundColor: "#EFE6D6",
    autoHideMenuBar: true,
    icon: APP_ICON,
    titleBarStyle: IS_MAC ? "hiddenInset" : "default",
    trafficLightPosition: IS_MAC ? { x: 14, y: 12 } : undefined,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));
}

function python() {
  const exe = pythonExecutable();
  if (!exe) throw new Error("本机没有 Python。装 3.10+ 后再点部署。");
  return exe;
}

function onLog(source) {
  return (entry) => emitLog({ source, ...entry });
}

ipcMain.handle("brew:meta", () => ({
  blades: BLADES,
  tools: TOOLS.map((tool) => ({ id: tool.id, tag: tool.tag, short: tool.short, accent: tool.accent })),
  qq: QQ_GROUPS,
  telegram: TELEGRAM,
  platform: process.platform,
}));
ipcMain.handle("brew:catalog", () => catalogStatus());
ipcMain.handle("brew:inspect", (_event, home) => inspectTarget(home));
ipcMain.handle("brew:env", () => environmentStatus());
ipcMain.handle("brew:setup", (_event) => setupEnvironment((entry) => emitLog(entry)));
ipcMain.handle("brew:blade", (_event, id) => {
  currentBlade = id || "ALL";
  return currentBlade;
});
ipcMain.handle("brew:run", async (_event, payload) => {
  const tool = toolById(payload.id);
  emitLog({ type: "info", source: tool?.tag || payload.id, message: `${payload.verb} 开始` });
  const result = await runTool(payload.id, payload.verb, {
    python: python(),
    home: payload.home,
    blade: payload.blade || currentBlade,
    onLog: onLog(tool?.tag || payload.id),
  });
  emitLog({
    type: result.ok ? "ok" : "error",
    source: tool?.tag || payload.id,
    message: result.ok ? `${payload.verb} 完成` : `${payload.verb} 失败`,
  });
  return { ok: result.ok, code: result.code, parsed: result.parsed, boost: result.boost };
});
ipcMain.handle("brew:deploy-all", async (_event, payload) => {
  const home = payload?.home || resolveCodexHome();
  return oneClickBreak({
    python: python(),
    home,
    blade: payload?.blade || currentBlade,
    onLog: (entry) => emitLog(entry),
  });
});
ipcMain.handle("brew:restore-all", async (_event, payload) => {
  const home = payload?.home || resolveCodexHome();
  return oneClickRestore({
    python: python(),
    home,
    onLog: (entry) => emitLog(entry),
  });
});
ipcMain.handle("brew:accept", async (_event, payload) => {
  const home = payload?.home || resolveCodexHome();
  if (!home) throw new Error("还没有 Codex 目录。先启动一次 Codex，或手动选目录。");
  const proofs = [];
  for (const tool of TOOLS) {
    const result = await runTool(tool.id, "verify", {
      python: python(),
      home: tool.id === "codex" ? home : null,
      onLog: onLog(tool.tag),
    });
    proofs.push({ id: tool.id, ok: result.ok });
  }
  const live = await liveAcceptance(home, (entry) => emitLog(entry));
  return {
    ...live,
    ok: live.ok && proofs.every((item) => item.ok),
    proofs,
  };
});
ipcMain.handle("brew:choose", async () => {
  if (!mainWindow) return null;
  const picked = await dialog.showOpenDialog(mainWindow, {
    title: "选择包含 config.toml 的 Codex 目录",
    properties: ["openDirectory"],
  });
  if (picked.canceled || !picked.filePaths[0]) return null;
  return picked.filePaths[0];
});
ipcMain.handle("brew:open", async (_event, folder) => {
  const target = folder || resolveCodexHome();
  if (!target) throw new Error("没有可打开的目录。");
  const error = await shell.openPath(target);
  if (error) throw new Error(error);
  return target;
});
ipcMain.handle("brew:copy", (_event, text) => {
  clipboard.writeText(String(text || ""));
  return true;
});
ipcMain.handle("win:min", () => mainWindow?.minimize());
ipcMain.handle("win:max", () => {
  if (!mainWindow) return false;
  mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
  return mainWindow.isMaximized();
});
ipcMain.handle("win:close", () => mainWindow?.close());

app.whenReady().then(() => {
  createSplash();
  createMain();
  setTimeout(() => {
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
    }
  }, SPLASH_MS);
});

app.on("window-all-closed", () => app.quit());
