const { spawn } = require("node:child_process");
const path = require("node:path");
const { ROOT } = require("./catalog");
const { environmentStatus } = require("./env");
const { pythonExecutable } = require("./python");

function powerShell() {
  return path.join(process.env.SystemRoot || "C:\\Windows", "System32", "WindowsPowerShell", "v1.0", "powershell.exe");
}

function runScript(scriptPath, onLog) {
  return new Promise((resolve, reject) => {
    const child = spawn(powerShell(), [
      "-NoLogo",
      "-NoProfile",
      "-NonInteractive",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      scriptPath,
    ], {
      cwd: path.dirname(scriptPath),
      windowsHide: true,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });
    child.stdout.on("data", (chunk) => {
      for (const line of chunk.toString("utf8").split(/\r?\n/)) {
        if (line.trim()) onLog({ type: "out", source: path.basename(scriptPath), message: line.trim() });
      }
    });
    child.stderr.on("data", (chunk) => {
      for (const line of chunk.toString("utf8").split(/\r?\n/)) {
        if (line.trim()) onLog({ type: "error", source: path.basename(scriptPath), message: line.trim() });
      }
    });
    child.once("error", reject);
    child.once("close", (code) => resolve({ script: path.basename(scriptPath), code: code ?? 1 }));
  });
}

async function setupEnvironment(onLog = () => {}) {
  const messages = [];
  const python = pythonExecutable();
  if (!python) {
    messages.push({ type: "error", message: "没有 Python，环境安装停在这里。" });
    return { messages, status: environmentStatus(), results: [] };
  }
  const install = path.join(ROOT, "assets", "env", "install.ps1");
  const verify = path.join(ROOT, "assets", "env", "verify.ps1");
  onLog({ type: "info", source: "环境", message: "安装逆向 Python 依赖" });
  const results = [];
  results.push(await runScript(install, onLog));
  onLog({ type: "info", source: "环境", message: "校验逆向依赖" });
  results.push(await runScript(verify, onLog));
  const failed = results.filter((item) => item.code !== 0);
  messages.push({
    type: failed.length ? "error" : "ok",
    message: failed.length
      ? `环境安装有失败：${failed.map((item) => `${item.script}=${item.code}`).join(", ")}`
      : "环境安装完成，pip 依赖已落本机",
  });
  return { messages, status: environmentStatus(), results };
}

module.exports = {
  setupEnvironment,
};
