const { spawnSync } = require("node:child_process");
const os = require("node:os");
const path = require("node:path");
const { CORE, TOOLS, entryPath } = require("./catalog");
const { exists, isFile } = require("./fs-util");
const { pythonExecutable, pythonVersion } = require("./python");

const LOOKUPS = [
  { id: "Python", cmd: process.platform === "win32" ? "python" : "python3", args: ["--version"] },
  { id: "Git", cmd: "git", args: ["--version"] },
  { id: "Node", cmd: "node", args: ["-v"] },
  { id: "strings", cmd: "strings", args: ["--version"] },
  { id: "jadx", cmd: "jadx", args: ["--version"] },
  { id: "frida", cmd: "frida", args: ["--version"] },
  { id: "adb", cmd: "adb", args: ["version"] },
];

function probe(cmd, args) {
  try {
    const result = spawnSync(cmd, args, {
      encoding: "utf8",
      windowsHide: true,
      timeout: 6000,
    });
    if (result.error) return { ok: false };
    const text = `${result.stdout || ""}${result.stderr || ""}`.trim().split(/\r?\n/)[0] || "";
    return { ok: result.status === 0 || Boolean(text), detail: text.slice(0, 120) };
  } catch {
    return { ok: false };
  }
}

function environmentStatus() {
  const python = pythonExecutable();
  const tools = LOOKUPS.map((item) => ({ id: item.id, ...probe(item.cmd, item.args) }));
  const seats = TOOLS.map((tool) => ({
    id: tool.id,
    tag: tool.tag,
    entry: isFile(entryPath(tool)),
    home: exists(tool.defaultHome()),
  }));
  return {
    platform: `${os.platform()}-${os.arch()}`,
    hostname: os.hostname(),
    python: python ? { ok: true, path: python, version: pythonVersion(python) } : { ok: false },
    tools,
    seats,
    core: exists(CORE),
    atelier: path.resolve(__dirname, "..", ".."),
  };
}

module.exports = {
  environmentStatus,
  pythonExecutable,
};
