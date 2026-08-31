const path = require("node:path");
const { TOOLS } = require("./catalog");
const { runTool } = require("./hub");
const { thickenCodex } = require("./boost");
const { deployMcp } = require("./mcp");
const {
  installKit,
  installCodexSkills,
  installOverlay,
  installAgents,
} = require("./kit");
const { entry, writeManifest } = require("./manifest");
const { restoreFromManifest } = require("./manifest");

async function oneClickBreak(options) {
  const { python, home, blade, profile, onLog } = options;
  if (!home) throw new Error("未找到 Codex 配置目录。先启动一次 Codex，或手动选含 config.toml 的目录。");
  const logs = onLog || (() => {});
  const managed = [];

  logs({ type: "info", source: "一键破甲", message: "1/7 中文 + 审批 + 沙箱 + 指令挂钩" });
  const thick = thickenCodex(home);
  logs({
    type: thick.changed ? "ok" : "info",
    source: "一键破甲",
    message: thick.changed
      ? `挂钩加厚 instruction=${thick.instruction} approval=${thick.approval} sandbox=${thick.sandbox}`
      : thick.reason || "挂钩已对齐",
  });

  logs({ type: "info", source: "一键破甲", message: "2/7 活指令 coldbrew-live.md" });
  const overlay = installOverlay(home);
  managed.push(entry("overlay", overlay.dest, overlay.existed, overlay.backup));

  logs({ type: "info", source: "一键破甲", message: "3/7 身份与技能模块" });
  const skills = installCodexSkills(home);
  for (const [name, item] of Object.entries(skills)) {
    managed.push(entry(`skill:${name}`, item.dest, item.existed, item.backup));
    logs({ type: "ok", source: "一键破甲", message: `技能 ${name}` });
  }

  logs({ type: "info", source: "一键破甲", message: "4/7 破甲套件 + AGENTS 路由" });
  const kit = installKit();
  const agents = installAgents(home, kit.root);
  managed.push(entry("agents", agents.dest, agents.existed, agents.backup));
  logs({ type: "ok", source: "一键破甲", message: `套件 ${kit.modules} 个入口 → ${kit.root}` });

  logs({ type: "info", source: "一键破甲", message: "5/7 工具桥 MCP" });
  const mcp = deployMcp(home);
  logs({
    type: "ok",
    source: "一键破甲",
    message: mcp.changed
      ? `工具桥已写入 ${mcp.servers.join(", ")}`
      : `工具桥保持 ${ (mcp.already || mcp.servers).join(", ") }`,
  });

  logs({ type: "info", source: "一键破甲", message: "6/7 四个模型适配器" });
  const adapters = [];
  for (const tool of TOOLS) {
    const result = await runTool(tool.id, "deploy", {
      python,
      home: tool.id === "codex" ? home : null,
      blade,
      profile,
      onLog,
    });
    adapters.push({ id: tool.id, ok: result.ok, code: result.code });
  }

  logs({ type: "info", source: "一键破甲", message: "7/7 回写挂钩并落恢复清单" });
  thickenCodex(home);
  const manifest = writeManifest(home, managed, { kit: kit.root, mcp: mcp.servers });
  logs({ type: "ok", source: "一键破甲", message: `清单 ${manifest}` });
  return { ok: adapters.every((item) => item.ok), adapters, kit, mcp, overlay, manifest, thick };
}

async function oneClickRestore(options) {
  const { python, home, profile, onLog } = options;
  if (!home) throw new Error("未找到 Codex 配置目录。");
  const logs = onLog || (() => {});
  const adapters = [];
  for (const tool of TOOLS) {
    logs({ type: "info", source: "恢复默认", message: `${tool.tag} restore` });
    const result = await runTool(tool.id, "restore", {
      python,
      home: tool.id === "codex" ? home : null,
      profile,
      onLog,
    });
    adapters.push({ id: tool.id, ok: result.ok, code: result.code });
  }
  const restore = restoreFromManifest(home);
  logs({
    type: restore.available ? "ok" : "info",
    source: "恢复默认",
    message: restore.available
      ? `托管项 恢复 ${restore.restored} / 删除 ${restore.removed} / 漂移跳过 ${restore.drifted}`
      : "没有本机破甲清单",
  });
  return { ok: true, adapters, restore };
}

module.exports = {
  oneClickBreak,
  oneClickRestore,
};
