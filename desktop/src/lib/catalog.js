const path = require("node:path");
const os = require("node:os");

const ROOT = path.resolve(__dirname, "..", "..");

function resolveCore() {
  if (!process.versions.electron) return path.resolve(ROOT, "..");
  try {
    const { app } = require("electron");
    if (app && app.isPackaged) return path.join(process.resourcesPath, "core");
  } catch {
    // node tests
  }
  return path.resolve(ROOT, "..");
}

const CORE = resolveCore();

const QQ_GROUPS = [
  { name: "交流群", number: "1057540028" },
  { name: "专题群", number: "1077074552" },
];

const TELEGRAM = [
  { name: "群", handle: "@chachachacha99999", url: "https://t.me/chachachacha99999" },
  { name: "频道", handle: "@chachacha99999999", url: "https://t.me/chachacha99999999" },
];

const BLADES = [
  { id: "REV", label: "逆向", hint: "拆箱还原 · 偏移 / 伪代码", color: "#E8A872" },
  { id: "UNLOCK", label: "破解", hint: "开锁双路 · keygen + patcher", color: "#F5D76E" },
  { id: "INFIL", label: "渗透", hint: "深打连招 · recon 到利用链", color: "#FF6BA8" },
  { id: "HARVEST", label: "爬虫", hint: "抽签收割 · 验签 + 续爬", color: "#5EE7FF" },
  { id: "TRAINER", label: "外挂", hint: "本地训架 · 实体 / W2S / Overlay", color: "#80F0BC" },
];

const TOOLS = [
  {
    id: "codex",
    tag: "GPT-5.6",
    short: "Codex",
    accent: "#80F0BC",
    dir: path.join("projects", "codex-coldbrew"),
    entry: path.join("studio", "eni_solo_deploy.py"),
    cwd: path.join("projects", "codex-coldbrew", "studio"),
    deploy: ["deploy", "--yes", "--force", "--json"],
    verify: ["verify", "--json"],
    restore: ["restore", "--yes", "--json"],
    preview: ["status", "--json"],
    homeFlag: "--codex-home",
    homeFirst: false,
    defaultHome: () => process.env.CODEX_HOME || path.join(os.homedir(), ".codex"),
    configName: "config.toml",
  },
  {
    id: "claude",
    tag: "Claude Code",
    short: "Claude",
    accent: "#FF9E7A",
    dir: path.join("projects", "claude-coldbrew"),
    entry: path.join("app", "claude_pojia.py"),
    cwd: path.join("projects", "claude-coldbrew", "app"),
    deploy: ["install", "--yes", "--profile", "max", "--json"],
    verify: ["verify", "--profile", "max", "--json"],
    restore: ["restore", "--yes", "--json"],
    preview: ["plan", "--json"],
    homeFlag: "--home",
    homeFirst: false,
    defaultHome: () => path.join(os.homedir(), ".claude"),
    configName: "CLAUDE.md",
  },
  {
    id: "grok",
    tag: "Grok 4.6",
    short: "Grok",
    accent: "#1F6B66",
    dir: path.join("projects", "grok4.6-coldbrew"),
    entry: path.join("app", "grok_coldbrew.py"),
    cwd: path.join("projects", "grok4.6-coldbrew", "app"),
    deploy: ["deploy", "--profile", "max", "--json"],
    verify: ["verify", "--json"],
    restore: ["restore", "--json"],
    preview: ["preview", "--profile", "max", "--json"],
    homeFlag: "--home",
    homeFirst: true,
    defaultHome: () => path.join(os.homedir(), ".grok"),
    configName: "rules",
  },
  {
    id: "deepseek",
    tag: "DeepSeek v4 Pro",
    short: "DeepSeek",
    accent: "#7AA2FF",
    dir: path.join("projects", "deepseek-harness"),
    entry: path.join("app", "deepseek_harness.py"),
    cwd: path.join("projects", "deepseek-harness", "app"),
    deploy: ["deploy", "--profile", "max", "--json"],
    verify: ["verify", "--json"],
    restore: ["restore", "--json"],
    preview: ["preview", "--profile", "max", "--json"],
    homeFlag: "--home",
    homeFirst: true,
    defaultHome: () => process.env.DEEPSEEK_COLDBREW_HOME || path.join(os.homedir(), ".deepseek-harness"),
    configName: "session",
  },
];

function toolById(id) {
  return TOOLS.find((item) => item.id === id);
}

function entryPath(tool) {
  return path.join(CORE, tool.dir, tool.entry);
}

function cwdPath(tool) {
  return path.join(CORE, tool.cwd);
}

module.exports = {
  ROOT,
  CORE,
  QQ_GROUPS,
  TELEGRAM,
  BLADES,
  TOOLS,
  toolById,
  entryPath,
  cwdPath,
};
