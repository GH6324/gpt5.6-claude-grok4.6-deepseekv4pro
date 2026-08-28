const fs = require("node:fs");
const path = require("node:path");
const {
  isFile,
  isDir,
  backupFile,
  atomicWrite,
  pathFingerprint,
  sameFingerprint,
  copyTree,
} = require("./fs-util");

const MANIFEST_NAME = ".coldbrew-deploy-manifest.json";
const APP = "coldbrew";
const VERSION = 1;

function manifestPath(folder) {
  return path.join(folder, MANIFEST_NAME);
}

function entry(role, target, existed, backup) {
  return {
    role,
    path: path.resolve(target),
    existed: Boolean(existed),
    backup: backup || null,
    after: pathFingerprint(target),
  };
}

function writeManifest(folder, entries, extra = {}) {
  const payload = {
    app: APP,
    version: VERSION,
    createdAt: new Date().toISOString(),
    entries,
    ...extra,
  };
  const file = manifestPath(folder);
  atomicWrite(file, `${JSON.stringify(payload, null, 2)}\n`);
  return file;
}

function readManifest(folder) {
  const file = manifestPath(folder);
  if (!isFile(file)) return null;
  try {
    const data = JSON.parse(fs.readFileSync(file, "utf8"));
    if (data.app !== APP || data.version !== VERSION || !Array.isArray(data.entries)) return null;
    return data;
  } catch {
    return null;
  }
}

function inspectRestore(folder) {
  const manifest = readManifest(folder);
  if (!manifest) return { available: false, drifted: 0, entries: 0 };
  let drifted = 0;
  for (const item of manifest.entries) {
    const now = pathFingerprint(item.path);
    if (!sameFingerprint(item.after, now)) drifted += 1;
  }
  return { available: true, drifted, entries: manifest.entries.length, createdAt: manifest.createdAt };
}

function restoreFromManifest(folder) {
  const manifest = readManifest(folder);
  if (!manifest) {
    return { available: false, restored: 0, removed: 0, drifted: 0, errors: [] };
  }
  let restored = 0;
  let removed = 0;
  let drifted = 0;
  const errors = [];
  for (const item of manifest.entries) {
    try {
      const now = pathFingerprint(item.path);
      if (now && item.after && !sameFingerprint(item.after, now)) {
        drifted += 1;
        continue;
      }
      if (item.existed && item.backup && (isFile(item.backup) || isDir(item.backup))) {
        fs.rmSync(item.path, { recursive: true, force: true });
        if (isDir(item.backup)) copyTree(item.backup, item.path);
        else {
          fs.mkdirSync(path.dirname(item.path), { recursive: true });
          fs.copyFileSync(item.backup, item.path);
        }
        restored += 1;
      } else if (!item.existed && (isFile(item.path) || isDir(item.path))) {
        fs.rmSync(item.path, { recursive: true, force: true });
        removed += 1;
      }
    } catch (error) {
      errors.push({ path: item.path, error: error.message });
    }
  }
  const archived = `${manifestPath(folder)}.restored-${Date.now()}`;
  try {
    fs.renameSync(manifestPath(folder), archived);
  } catch {
    fs.rmSync(manifestPath(folder), { force: true });
  }
  return {
    available: true,
    restored,
    removed,
    drifted,
    errors,
    archivedManifest: archived,
  };
}

module.exports = {
  MANIFEST_NAME,
  entry,
  writeManifest,
  readManifest,
  inspectRestore,
  restoreFromManifest,
  backupFile,
};
