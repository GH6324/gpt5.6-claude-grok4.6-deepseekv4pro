const { CORE, TOOLS, toolById, entryPath, cwdPath } = require("./catalog");
const { exists, isFile } = require("./fs-util");
const { runPython } = require("./python");
const { thickenCodex } = require("./boost");

function lastJson(text) {
  const chunks = String(text || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  for (let index = chunks.length - 1; index >= 0; index -= 1) {
    const line = chunks[index];
    if (!line.startsWith("{") && !line.startsWith("[")) continue;
    try {
      return JSON.parse(line);
    } catch {
      // try a bigger slice
    }
  }
  const start = text.lastIndexOf("{");
  if (start >= 0) {
    try {
      return JSON.parse(text.slice(start));
    } catch {
      return null;
    }
  }
  return null;
}

function profileArgs(tool, verb, profile) {
  const source = [...(tool[verb] || [])];
  if (!tool.profileAware || !profile || !["deploy", "preview", "install", "plan"].includes(verb)) {
    return source;
  }
  const mapped = tool.profileMap?.[profile] || profile;
  const flag = source.indexOf("--profile");
  if (flag >= 0) {
    source[flag + 1] = mapped;
  } else {
    source.push("--profile", mapped);
  }
  return source;
}

async function invoke(tool, verb, options = {}) {
  const exe = options.python;
  if (!exe) throw new Error("本机没有可用的 Python。");
  const script = entryPath(tool);
  if (!isFile(script)) throw new Error(`适配器缺失：${script}`);
  const verbArgs = profileArgs(tool, verb, options.profile);
  const homeArgs = options.home && tool.homeFlag ? [tool.homeFlag, options.home] : [];
  const args = tool.homeFirst
    ? [script, ...homeArgs, ...verbArgs]
    : [script, ...verbArgs, ...homeArgs];
  options.onLog?.({
    type: "info",
    message: `[${tool.tag}] python ${require("node:path").basename(script)} ${(tool[verb] || []).join(" ")}`,
  });
  const result = await runPython(exe, args, {
    cwd: cwdPath(tool),
    blade: options.blade,
    onLog: (entry) => options.onLog?.({ ...entry, source: tool.tag }),
  });
  const parsed = lastJson(result.stdout);
  const ok = result.code === 0 && (parsed?.ok !== false);
  return {
    ok,
    code: result.code,
    parsed,
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

async function runTool(id, verb, options = {}) {
  const tool = toolById(id);
  if (!tool) throw new Error(`未知席位：${id}`);
  const result = await invoke(tool, verb, options);
  if (verb === "deploy" && id === "codex") {
    const home = options.home || tool.defaultHome();
    const boost = thickenCodex(home);
    options.onLog?.({
      type: boost.changed ? "ok" : "info",
      source: tool.tag,
      message: boost.changed
        ? `挂钩加厚：instruction=${boost.instruction} approval=${boost.approval} sandbox=${boost.sandbox} locale=${boost.locale}`
        : `挂钩加厚未改字节：${boost.reason || boost.instruction || "已对齐"}`,
    });
    result.boost = boost;
  }
  if (verb === "deploy" && result.ok && Array.isArray(tool.verify) && tool.verify.length) {
    options.onLog?.({ type: "info", source: tool.tag, message: "部署后验证开始" });
    result.verify = await invoke(tool, "verify", options);
    options.onLog?.({
      type: result.verify.ok ? "ok" : "error",
      source: tool.tag,
      message: result.verify.ok ? "部署后验证通过" : `部署后验证失败，退出码 ${result.verify.code}`,
    });
  }
  return result;
}

function catalogStatus() {
  return TOOLS.map((tool) => ({
    id: tool.id,
    tag: tool.tag,
    short: tool.short,
    accent: tool.accent,
    home: tool.defaultHome(),
    entry: exists(entryPath(tool)),
    core: exists(CORE),
  }));
}

module.exports = {
  invoke,
  runTool,
  catalogStatus,
  lastJson,
  profileArgs,
};
