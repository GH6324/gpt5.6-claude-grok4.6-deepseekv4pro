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

const PROJECT_SOURCE_URL = "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro";
const TELEGRAM_GROUP_URL = "https://t.me/chachachacha99999";
const TELEGRAM_CHANNEL_URL = "https://t.me/chachachacha99999999";

const QQ_GROUPS = [
  { name: "交流群", number: "1057540028" },
  { name: "专题群", number: "1077074552" },
];

const TELEGRAM = [
  { name: "群", handle: "@chachachacha99999", url: TELEGRAM_GROUP_URL },
  { name: "频道", handle: "@chachacha99999999", url: TELEGRAM_CHANNEL_URL },
];

// Shared profile vocabulary for the desktop controls. Adapters can map these
// stable ids to their historical profile names.
const PROFILES = [
  { id: "max", label: "MAX / 全开", short: "完整路由、连续上下文与直接交付链。", accent: "#ff9a62" },
  { id: "focused", label: "FOCUS / 聚焦", short: "短链路执行，优先收敛到当前目标。", accent: "#56d8c7" },
  { id: "builder", label: "BUILDER / 构建", short: "实现、打包、测试和可复现交付。", accent: "#7aa2ff" },
  { id: "research", label: "RESEARCH / 研究", short: "来源、证据、结论与未知项分层。", accent: "#f5d76e" },
  { id: "creative", label: "CREATIVE / 创作", short: "保持角色、语气和长文本连续性。", accent: "#ff6ba8" },
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
    profileAware: false,
  },
  {
    id: "claude",
    tag: "Claude Code",
    short: "Claude",
    accent: "#FF9E7A",
    dir: path.join("projects", "claude-coldbrew"),
    entry: path.join("app", "claude_pojia.py"),
    cwd: path.join("projects", "claude-coldbrew", "app"),
    deploy: ["install", "--yes", "--profile", "max-breaker", "--json"],
    verify: ["verify", "--profile", "max-breaker", "--json"],
    restore: ["restore", "--yes", "--json"],
    preview: ["plan", "--json"],
    homeFlag: "--home",
    homeFirst: false,
    defaultHome: () => path.join(os.homedir(), ".claude"),
    configName: "CLAUDE.md",
    profileAware: true,
    profileMap: { max: "max-breaker", focused: "builder", builder: "builder", research: "research", creative: "creative" },
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
    profileAware: true,
    profileMap: { max: "max", focused: "focused", builder: "max", research: "research", creative: "creative" },
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
    profileAware: true,
    profileMap: { max: "max", focused: "focused", builder: "max", research: "research", creative: "creative" },
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
  PROJECT_SOURCE_URL,
  TELEGRAM_GROUP_URL,
  TELEGRAM_CHANNEL_URL,
  QQ_GROUPS,
  TELEGRAM,
  PROFILES,
  BLADES,
  TOOLS,
  toolById,
  entryPath,
  cwdPath,
};
