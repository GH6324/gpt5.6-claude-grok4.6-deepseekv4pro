const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { TOOLS } = require("./catalog");
const { exists, isDir, isFile } = require("./fs-util");
const { inspectKit } = require("./kit");

function unique(items) {
  return [...new Set(items.filter(Boolean).map((item) => path.resolve(item)))];
}

function codexCandidates(requested) {
  if (requested) return unique([requested]);
  const home = os.homedir();
  const list = [process.env.CODEX_HOME, path.join(home, ".codex")];
  if (process.platform === "win32" && process.env.LOCALAPPDATA) {
    list.push(
      path.join(process.env.LOCALAPPDATA, "OpenAI", "Codex"),
      path.join(process.env.LOCALAPPDATA, "Codex"),
    );
  }
  if (process.platform === "darwin") {
    list.push(
      path.join(home, "Library", "Application Support", "Codex"),
      path.join(home, "Library", "Application Support", "com.openai.codex"),
    );
  }
  return unique(list);
}

function resolveCodexHome(requested) {
  return codexCandidates(requested).find((folder) => isFile(path.join(folder, "config.toml"))) || null;
}

function countChildren(folder) {
  if (!isDir(folder)) return 0;
  try {
    return fs.readdirSync(folder).length;
  } catch {
    return 0;
  }
}

function inspectHome(tool, overrideHome) {
  const home = overrideHome || tool.defaultHome();
  const present = exists(home);
  const facts = {
    id: tool.id,
    tag: tool.tag,
    home,
    present,
    files: present ? countChildren(home) : 0,
  };
  if (tool.id === "codex") {
    Object.assign(facts, inspectKit(home));
    facts.skills = countChildren(path.join(home, "skills"));
  }
  if (tool.id === "claude") {
    facts.claudeMd = isFile(path.join(home, "CLAUDE.md"));
    facts.rules = countChildren(path.join(home, "rules"));
    facts.skills = countChildren(path.join(home, "skills"));
  }
  if (tool.id === "grok") {
    facts.rules = countChildren(path.join(home, "rules"));
    facts.agents = isFile(path.join(home, "agents", "eni.md")) || isFile(path.join(path.dirname(home), "Agents.md"));
  }
  return facts;
}

function inspectAll(codexOverride) {
  return TOOLS.map((tool) => inspectHome(tool, tool.id === "codex" ? (codexOverride || resolveCodexHome()) : null));
}

function inspectTarget(codexOverride) {
  const home = resolveCodexHome(codexOverride) || (codexOverride && isFile(path.join(codexOverride, "config.toml")) ? path.resolve(codexOverride) : null);
  if (!home) {
    return { found: false, models: inspectAll(null) };
  }
  return {
    found: true,
    ...inspectKit(home),
    models: inspectAll(home),
  };
}

module.exports = {
  resolveCodexHome,
  inspectAll,
  inspectHome,
  inspectTarget,
};
