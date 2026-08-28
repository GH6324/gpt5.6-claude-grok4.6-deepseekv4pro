const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

function exists(filePath) {
  try {
    fs.accessSync(filePath);
    return true;
  } catch {
    return false;
  }
}

function isFile(filePath) {
  try {
    return fs.statSync(filePath).isFile();
  } catch {
    return false;
  }
}

function isDir(filePath) {
  try {
    return fs.statSync(filePath).isDirectory();
  } catch {
    return false;
  }
}

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function sha256File(filePath) {
  const digest = crypto.createHash("sha256");
  const fd = fs.openSync(filePath, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let n;
    do {
      n = fs.readSync(fd, buffer, 0, buffer.length, null);
      if (n) digest.update(buffer.subarray(0, n));
    } while (n);
  } finally {
    fs.closeSync(fd);
  }
  return digest.digest("hex");
}

function stamp() {
  const now = new Date();
  const pad = (value, size = 2) => String(value).padStart(size, "0");
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    "-",
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");
}

function backupPath(filePath) {
  return `${filePath}.brew-${stamp()}.bak`;
}

function backupFile(filePath) {
  if (!exists(filePath)) return null;
  const dest = backupPath(filePath);
  const stat = fs.lstatSync(filePath);
  if (stat.isDirectory()) {
    copyTree(filePath, dest);
    return dest;
  }
  fs.copyFileSync(filePath, dest);
  return dest;
}

function atomicWrite(filePath, content) {
  const temp = `${filePath}.brew-tmp-${process.pid}-${Date.now()}`;
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(temp, content, "utf8");
  fs.renameSync(temp, filePath);
}

function copyTree(source, destination) {
  const stat = fs.statSync(source);
  if (stat.isDirectory()) {
    fs.mkdirSync(destination, { recursive: true });
    for (const name of fs.readdirSync(source)) {
      copyTree(path.join(source, name), path.join(destination, name));
    }
    return;
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
}

function pathFingerprint(target) {
  try {
    const stat = fs.lstatSync(target);
    if (stat.isFile()) {
      return { kind: "file", size: stat.size, sha256: sha256File(target) };
    }
    if (!stat.isDirectory()) return { kind: "other", sha256: "" };
    const digest = crypto.createHash("sha256");
    const visit = (current, relative = "") => {
      for (const entry of fs.readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
        const child = path.join(current, entry.name);
        const rel = relative ? path.join(relative, entry.name) : entry.name;
        if (entry.isDirectory()) {
          digest.update(`d:${rel}\0`);
          visit(child, rel);
        } else if (entry.isFile()) {
          digest.update(`f:${rel}\0${sha256File(child)}\0`);
        }
      }
    };
    visit(target);
    return { kind: "directory", sha256: digest.digest("hex") };
  } catch {
    return null;
  }
}

function sameFingerprint(left, right) {
  return Boolean(left && right) && left.kind === right.kind && left.sha256 === right.sha256;
}

function countSkillEntrypoints(root) {
  if (!isDir(root)) return 0;
  let count = 0;
  const visit = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const child = path.join(current, entry.name);
      if (entry.isDirectory()) visit(child);
      else if (entry.name === "SKILL.md") count += 1;
    }
  };
  visit(root);
  return count;
}

function localColdBrewRoot() {
  const os = require("node:os");
  const home = os.homedir();
  if (process.platform === "darwin") {
    return path.join(home, "Library", "Application Support", "ColdBrew");
  }
  if (process.platform === "linux") {
    return path.join(process.env.XDG_DATA_HOME || path.join(home, ".local", "share"), "ColdBrew");
  }
  const base = process.env.LOCALAPPDATA || path.join(home, "AppData", "Local");
  return path.join(base, "ColdBrew");
}

module.exports = {
  exists,
  isFile,
  isDir,
  readText,
  sha256File,
  stamp,
  backupFile,
  atomicWrite,
  copyTree,
  pathFingerprint,
  sameFingerprint,
  countSkillEntrypoints,
  localColdBrewRoot,
};
