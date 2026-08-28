const { spawn, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function firstExisting(candidates) {
  return candidates.find((item) => item && fs.existsSync(item)) || null;
}

function pythonExecutable() {
  const home = os.homedir();
  const named = process.platform === "win32"
    ? [process.env.PYTHON, process.env.COLDBREW_PYTHON, "python", "py", "python3"]
    : [process.env.PYTHON, process.env.COLDBREW_PYTHON, "python3", "python"];
  for (const name of named.filter(Boolean)) {
    try {
      const result = spawnSync(name, ["-c", "import sys; print(sys.executable)"], {
        encoding: "utf8",
        windowsHide: true,
        timeout: 8000,
      });
      const exe = (result.stdout || "").trim();
      if (result.status === 0 && exe && fs.existsSync(exe)) return exe;
    } catch {
      // try next
    }
  }
  const extras = process.platform === "win32"
    ? [
      path.join(home, "AppData", "Local", "Programs", "Python", "Python312", "python.exe"),
      path.join(home, "AppData", "Local", "Programs", "Python", "Python311", "python.exe"),
      "C:\\Python312\\python.exe",
    ]
    : [
      "/opt/homebrew/bin/python3",
      "/usr/local/bin/python3",
      "/usr/bin/python3",
      path.join(home, ".local", "bin", "python3"),
    ];
  return firstExisting(extras);
}

function pythonVersion(exe) {
  if (!exe) return null;
  try {
    const result = spawnSync(exe, ["--version"], {
      encoding: "utf8",
      windowsHide: true,
      timeout: 8000,
    });
    return `${result.stdout || ""}${result.stderr || ""}`.trim() || null;
  } catch {
    return null;
  }
}

function runPython(exe, args, options = {}) {
  const onLog = options.onLog || (() => {});
  const env = {
    ...process.env,
    PYTHONIOENCODING: "utf-8",
    PYTHONUTF8: "1",
    PYTHONDONTWRITEBYTECODE: "1",
    COLDBREW_BLADE: options.blade && options.blade !== "ALL" ? options.blade : (process.env.COLDBREW_BLADE || ""),
    ...(options.env || {}),
  };
  if (!env.COLDBREW_BLADE) delete env.COLDBREW_BLADE;
  return new Promise((resolve, reject) => {
    const child = spawn(exe, args, {
      cwd: options.cwd,
      env,
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      const text = chunk.toString("utf8");
      stdout += text;
      for (const line of text.split(/\r?\n/)) {
        if (line.trim()) onLog({ type: "out", message: line.trim() });
      }
    });
    child.stderr.on("data", (chunk) => {
      const text = chunk.toString("utf8");
      stderr += text;
      for (const line of text.split(/\r?\n/)) {
        if (line.trim()) onLog({ type: "error", message: line.trim() });
      }
    });
    child.once("error", reject);
    child.once("close", (code) => {
      resolve({ code: code ?? 1, stdout, stderr });
    });
  });
}

module.exports = {
  pythonExecutable,
  pythonVersion,
  runPython,
};
