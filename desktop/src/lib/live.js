const { execFileSync, spawn } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const readline = require("node:readline");
const { isFile, sha256File } = require("./fs-util");
const { inspectCodexConfig } = require("./boost");
const { ROOT } = require("./catalog");

const SUCCESS_REPLY = "welcome roast · 挂钩齐活";

function firstFile(candidates) {
  return candidates.find((item) => item && isFile(item)) || null;
}

function runningCodexPaths() {
  if (process.platform !== "win32") return [];
  const powershell = path.join(process.env.SystemRoot || "C:\\Windows", "System32", "WindowsPowerShell", "v1.0", "powershell.exe");
  try {
    const output = execFileSync(powershell, [
      "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
      "-Command",
      "Get-CimInstance Win32_Process -Filter \"Name='codex.exe'\" | ForEach-Object { $_.ExecutablePath }",
    ], { encoding: "utf8", windowsHide: true, timeout: 5000 });
    return output.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  } catch {
    return [];
  }
}

function locateCodexCli() {
  const local = process.env.LOCALAPPDATA;
  const home = os.homedir();
  return firstFile([
    process.env.CODEX_CLI_PATH,
    ...runningCodexPaths(),
    local ? path.join(local, "Programs", "codex", "Codex.exe") : null,
    local ? path.join(local, "OpenAI Codex", "Codex.exe") : null,
    local ? path.join(local, "Programs", "Codex", "Codex.exe") : null,
    path.join(home, "AppData", "Local", "Programs", "codex", "Codex.exe"),
  ]);
}

class AppServer {
  constructor(command, codexHome) {
    this.nextId = 1;
    this.pending = new Map();
    this.notifications = [];
    this.waiters = [];
    this.child = spawn(command, ["app-server", "--stdio"], {
      windowsHide: true,
      env: { ...process.env, CODEX_HOME: codexHome },
    });
    this.child.stdin.setDefaultEncoding("utf8");
    readline.createInterface({ input: this.child.stdout }).on("line", (line) => this.handle(line));
    this.child.once("error", (error) => this.failAll(error));
    this.child.once("close", () => this.failAll(new Error("app-server 已退出")));
  }

  failAll(error) {
    for (const pending of this.pending.values()) pending.reject(error);
    for (const waiter of this.waiters) {
      clearTimeout(waiter.timeout);
      waiter.reject(error);
    }
    this.pending.clear();
    this.waiters = [];
  }

  handle(line) {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      return;
    }
    if (Object.prototype.hasOwnProperty.call(message, "id") && !message.method) {
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(JSON.stringify(message.error)));
      else pending.resolve(message.result);
      return;
    }
    if (!message.method) return;
    this.notifications.push(message);
    const remaining = [];
    for (const waiter of this.waiters) {
      if (waiter.method === message.method && waiter.predicate(message.params)) {
        clearTimeout(waiter.timeout);
        waiter.resolve(message.params);
      } else {
        remaining.push(waiter);
      }
    }
    this.waiters = remaining;
  }

  request(method, params) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.child.stdin.write(`${JSON.stringify({ id, method, params })}\n`);
    });
  }

  notify(method, params = {}) {
    this.child.stdin.write(`${JSON.stringify({ method, params })}\n`);
  }

  waitFor(method, predicate = () => true, timeoutMs = 180000) {
    return new Promise((resolve, reject) => {
      const waiter = { method, predicate, resolve, reject, timeout: null };
      waiter.timeout = setTimeout(() => {
        this.waiters = this.waiters.filter((item) => item !== waiter);
        reject(new Error(`等待 ${method} 超时`));
      }, timeoutMs);
      this.waiters.push(waiter);
    });
  }

  async close() {
    try {
      if (!this.child.stdin.destroyed) this.child.stdin.end();
    } catch {
      // ignore
    }
    if (this.child.exitCode !== null) return;
    await new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.child.kill();
        resolve();
      }, 2000);
      this.child.once("close", () => {
        clearTimeout(timer);
        resolve();
      });
    });
  }
}

function overlayHash() {
  const overlay = path.join(ROOT, "assets", "overlay", "coldbrew-live.md");
  return isFile(overlay) ? sha256File(overlay) : null;
}

function instructionOk(value) {
  if (!value) return false;
  return /eni-|coldbrew-live/i.test(value);
}

function staticAcceptance(codexHome) {
  const config = inspectCodexConfig(codexHome);
  const overlay = path.join(codexHome, "coldbrew-live.md");
  const checkpoints = [
    { id: "config", ok: Boolean(config.present), label: "config.toml" },
    { id: "instruction", ok: instructionOk(config.instruction), label: `指令挂钩 ${config.instruction || "空"}` },
    { id: "overlay", ok: isFile(overlay), label: "活指令 coldbrew-live.md" },
    { id: "approval", ok: config.approval === "never", label: `审批 ${config.approval || "未写"}` },
    { id: "sandbox", ok: config.sandbox === "danger-full-access", label: `沙箱 ${config.sandbox || "未写"}` },
    { id: "hooks", ok: Boolean(config.hooks) && !config.hooksIsolated, label: config.hooksIsolated ? "hooks 被禁用" : (config.hooks ? "hooks 在岗" : "hooks 缺失") },
    { id: "locale", ok: config.locale === "zh-CN", label: `语言 ${config.locale || "未写"}` },
    { id: "agents", ok: Boolean(config.agents), label: "AGENTS.md" },
  ];
  const passed = checkpoints.filter((item) => item.ok).length;
  return {
    ok: passed === checkpoints.length,
    passed,
    total: checkpoints.length,
    checkpoints,
    overlaySha256: overlayHash(),
    reply: passed === checkpoints.length ? SUCCESS_REPLY : "校验未齐",
  };
}

function verificationPrompt(codexHome) {
  const overlay = path.join(codexHome, "coldbrew-live.md");
  const body = isFile(overlay)
    ? fs.readFileSync(overlay, "utf8").trimEnd()
    : "Reply exactly with: welcome roast · 挂钩齐活";
  return [
    body,
    "",
    "These verification rules apply only to the first turn of this task.",
    "If and only if the user message is exactly 冷咖啡, reply with exactly:",
    SUCCESS_REPLY,
  ].join("\n");
}

async function liveAcceptance(codexHome, onLog = () => {}) {
  const fileCheck = staticAcceptance(codexHome);
  onLog({ type: fileCheck.ok ? "ok" : "error", source: "验收", message: `静态挂钩 ${fileCheck.passed}/${fileCheck.total}` });
  if (fileCheck.overlaySha256) {
    onLog({ type: "ok", source: "验收", message: `活指令 SHA-256 ${fileCheck.overlaySha256}` });
  }
  for (const item of fileCheck.checkpoints) {
    onLog({ type: item.ok ? "info" : "error", source: "验收", message: item.label });
  }
  const cli = locateCodexCli();
  if (!cli) {
    return { ...fileCheck, desktop: null, cli: null };
  }
  onLog({ type: "info", source: "验收", message: `Desktop CLI ${cli}` });
  const client = new AppServer(cli, codexHome);
  try {
    const initialized = await client.request("initialize", {
      clientInfo: { name: "coldbrew-atelier", title: "冷咖啡", version: "1.0.0" },
      capabilities: { experimentalApi: true },
    });
    client.notify("initialized");
    onLog({ type: "ok", source: "验收", message: `已连 ${initialized.userAgent || "Codex"}` });
    const started = await client.request("thread/start", {
      approvalPolicy: "never",
      cwd: os.homedir(),
      developerInstructions: verificationPrompt(codexHome),
      ephemeral: false,
      sandbox: "danger-full-access",
      serviceName: "冷咖啡",
    });
    const threadId = started.thread.id;
    try {
      await client.request("thread/name/set", { threadId, name: "冷咖啡" });
    } catch {
      // some builds skip rename
    }
    const completion = client.waitFor("turn/completed", (params) => params.threadId === threadId);
    await client.request("turn/start", {
      approvalPolicy: "never",
      threadId,
      input: [{ type: "text", text: "冷咖啡", text_elements: [] }],
    });
    await completion;
    const messages = client.notifications
      .filter((entry) => entry.method === "item/completed" && entry.params?.threadId === threadId)
      .map((entry) => entry.params?.item)
      .filter((item) => item?.type === "agentMessage")
      .map((item) => item.text);
    const items = client.notifications
      .filter((entry) => entry.method === "item/completed" && entry.params?.threadId === threadId)
      .map((entry) => entry.params?.item)
      .filter(Boolean);
    const commands = items.filter((item) => item.type === "commandExecution");
    const fileChangeCount = items.filter((item) => item.type === "fileChange").length;
    const reply = (messages.at(-1) || "").trim();
    const allCommandExitCodesZero = commands.every((item) => item.exitCode === 0);
    onLog({ type: "info", source: "验收", message: `桌面任务 ${threadId}` });
    onLog({ type: "info", source: "验收", message: `命令 ${commands.length} 条，文件变更 ${fileChangeCount}` });
    onLog({ type: reply === SUCCESS_REPLY ? "ok" : "error", source: "验收", message: `桌面回复：${reply || "（空）"}` });
    try {
      spawn(cli, [`codex://threads/${threadId}`], { detached: true, stdio: "ignore", windowsHide: false }).unref();
    } catch {
      // opening the GUI is best-effort
    }
    const desktopOk = reply === SUCCESS_REPLY && fileChangeCount === 0;
    return {
      ...fileCheck,
      ok: fileCheck.ok && desktopOk,
      desktop: true,
      cli,
      threadId,
      reply,
      fileChangeCount,
      allCommandExitCodesZero,
      commandCount: commands.length,
    };
  } catch (error) {
    onLog({ type: "error", source: "验收", message: `Desktop 联机 ${error.message}` });
    return { ...fileCheck, desktop: false, cli, error: error.message };
  } finally {
    await client.close();
  }
}

module.exports = {
  SUCCESS_REPLY,
  staticAcceptance,
  liveAcceptance,
  locateCodexCli,
  overlayHash,
};
