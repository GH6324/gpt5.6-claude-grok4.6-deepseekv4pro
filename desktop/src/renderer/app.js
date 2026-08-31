const ui = {
  statusTitle: document.querySelector("#statusTitle"),
  statusDetail: document.querySelector("#statusDetail"),
  statusDot: document.querySelector("#statusDot"),
  bladeBar: document.querySelector("#bladeBar"),
  bladeHint: document.querySelector("#bladeHint"),
  profileBar: document.querySelector("#profileBar"),
  profileSummary: document.querySelector("#profileSummary"),
  communityBar: document.querySelector("#communityBar"),
  hearthGrid: document.querySelector("#hearthGrid"),
  readyChip: document.querySelector("#readyChip"),
  codexPath: document.querySelector("#codexPath"),
  targetLocale: document.querySelector("#targetLocale"),
  codexFacts: document.querySelector("#codexFacts"),
  envFacts: document.querySelector("#envFacts"),
  log: document.querySelector("#log"),
  clockChip: document.querySelector("#clockChip"),
  restoreBtn: document.querySelector("#restoreAllBtn"),
  toast: document.querySelector("#toast"),
};

let meta = { blades: [], profiles: [], qq: [], telegram: [] };
let blade = "ALL";
let profile = "max";
let busy = false;
let codexHome = null;
let toastTimer;

function setStatus(kind, title, detail) {
  ui.statusDot.className = kind || "ready";
  ui.statusTitle.textContent = title;
  ui.statusDetail.textContent = detail;
  const state = document.querySelector(".eyebrow-state");
  if (state) state.textContent = kind === "busy" ? "RUNNING" : kind === "bad" ? "CHECK" : "READY";
}

function toast(text) {
  ui.toast.textContent = text;
  ui.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove("show"), 2600);
}

function line(kind, source, message) {
  const row = document.createElement("div");
  row.className = kind || "out";
  const time = new Date().toTimeString().slice(0, 8);
  row.textContent = `[${time}] ${source ? `[${source}] ` : ""}${message}`;
  ui.log.appendChild(row);
  ui.log.scrollTop = ui.log.scrollHeight;
}

function fact(text, kind = "") {
  const node = document.createElement("span");
  node.className = `fact${kind ? ` ${kind}` : ""}`;
  node.textContent = text;
  return node;
}

function paintFacts(node, items) {
  node.replaceChildren();
  items.forEach((item) => node.appendChild(fact(item.text, item.kind)));
}

function lock(state, title) {
  busy = state;
  document.querySelectorAll("button").forEach((button) => {
    if (["minBtn", "maxBtn", "closeBtn", "clearBtn"].includes(button.id)) return;
    if (button.classList.contains("nav-item")) return;
    if (!state && button.id === "restoreAllBtn") return;
    button.disabled = state;
  });
  if (state) setStatus("busy", title || "正在执行…", "任务在本机运行，活动流会持续更新。");
}

async function withJob(title, work) {
  if (busy) {
    line("info", "工作台", "上一项任务仍在运行。");
    return null;
  }
  lock(true, title);
  try {
    return await work();
  } catch (error) {
    const message = error?.message || String(error);
    line("error", "工作台", message);
    setStatus("bad", "这轮没有完成", message);
    toast("任务失败");
    return null;
  } finally {
    lock(false);
  }
}

function renderProfiles() {
  ui.profileBar.replaceChildren();
  const profiles = meta.profiles?.length ? meta.profiles : [
    { id: "max", label: "MAX / 全开", short: "完整路由、连续上下文与直接交付链。" },
  ];
  const selected = profiles.find((item) => item.id === profile) || profiles[0];
  profile = selected.id;
  ui.profileSummary.textContent = selected.short || "当前档位已准备";
  profiles.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `segment${item.id === profile ? " is-on" : ""}`;
    button.textContent = item.label;
    button.title = item.short || item.label;
    button.addEventListener("click", () => {
      profile = item.id;
      window.localStorage?.setItem("coldbrew.profile", profile);
      renderProfiles();
      line("ok", "档位", `${item.label} 已启用`);
      toast(`${item.label} 已启用`);
    });
    ui.profileBar.appendChild(button);
  });
}

function renderBlades() {
  if (!ui.bladeBar) return;
  ui.bladeBar.replaceChildren();
  const entries = [{ id: "ALL", label: "全开", hint: "破甲全开 · 按目标自动选择通道" }, ...meta.blades];
  entries.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `blade-tab${item.id === blade ? " is-on" : ""}`;
    button.textContent = item.label;
    button.title = item.hint || item.label;
    button.addEventListener("click", async () => {
      blade = item.id;
      renderBlades();
      ui.bladeHint.textContent = item.hint || "破甲全开 · 按目标自动选择通道";
      await window.brew.setBlade(blade);
      line("ok", "破甲通道", blade);
    });
    ui.bladeBar.appendChild(button);
  });
  const active = entries.find((item) => item.id === blade);
  if (ui.bladeHint) ui.bladeHint.textContent = active?.hint || "自动选择";
}

function communityButton(label, value, action, url) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "community-link";
  const strong = document.createElement("strong");
  strong.textContent = label;
  const small = document.createElement("small");
  small.textContent = value;
  button.append(strong, small);
  button.addEventListener("click", () => action(value, url));
  return button;
}

function renderCommunity() {
  ui.communityBar.replaceChildren();
  for (const group of meta.qq || []) {
    ui.communityBar.appendChild(communityButton(`QQ ${group.name}`, group.number, async (value) => {
      await window.brew.copy(value);
      line("ok", "社群", `已复制 QQ 群号 ${value}`);
      toast(`QQ 群号 ${value} 已复制`);
    }));
  }
  for (const item of meta.telegram || []) {
    ui.communityBar.appendChild(communityButton(`Telegram ${item.name}`, item.handle, async (value, url) => {
      await window.brew.copy(value);
      if (url) await window.brew.external(url);
      line("ok", "社群", `${value} 已复制并打开`);
    }, item.url));
  }
}

function renderHearths(rows) {
  ui.hearthGrid.replaceChildren();
  let ready = 0;
  rows.forEach((row, index) => {
    if (row.entry) ready += 1;
    const card = document.createElement("article");
    card.className = "model-card";
    const head = document.createElement("div");
    head.className = "model-head";
    const identity = document.createElement("div");
    const indexNode = document.createElement("div");
    indexNode.className = "model-index";
    indexNode.textContent = `0${index + 1} / SEAT`;
    const tag = document.createElement("div");
    tag.className = "model-tag";
    tag.textContent = row.tag;
    identity.append(indexNode, tag);
    const state = document.createElement("span");
    state.className = `model-state${row.entry ? "" : " missing"}`;
    state.textContent = row.entry ? "ONLINE" : "MISSING";
    head.append(identity, state);
    const description = document.createElement("p");
    description.className = "model-short";
    description.textContent = row.short || "本地适配器";
    const home = document.createElement("p");
    home.className = "model-home";
    home.textContent = row.home || "未发现默认目录";
    const actions = document.createElement("div");
    actions.className = "model-actions";
    [["预览", "preview", false], ["部署", "deploy", true], ["验证", "verify", false], ["恢复", "restore", false]].forEach(([label, verb, primary]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      if (primary) button.className = "primary";
      button.dataset.id = row.id;
      button.dataset.verb = verb;
      button.addEventListener("click", () => runSeat(row.id, verb));
      actions.appendChild(button);
    });
    card.append(head, description, home, actions);
    ui.hearthGrid.appendChild(card);
  });
  ui.readyChip.textContent = `${ready} / ${rows.length}`;
}

function paintTarget(target) {
  if (!target?.found) {
    ui.codexPath.textContent = "未找到 Codex 配置目录";
    ui.targetLocale.textContent = "语言 · 未检测";
    ui.targetLocale.className = "locale";
    ui.restoreBtn.disabled = true;
    paintFacts(ui.codexFacts, [{ text: "选择一个包含 config.toml 的目录", kind: "bad" }]);
    setStatus("bad", "等待目标目录", "启动一次 Codex，或在执行中心手动选择配置目录。");
    return;
  }
  codexHome = target.folder;
  ui.codexPath.textContent = target.folder;
  ui.targetLocale.textContent = target.localized ? "语言 · 简体中文" : `语言 · ${target.locale || "跟随系统"}`;
  ui.targetLocale.className = `locale${target.localized ? " good" : ""}`;
  const skills = target.skillsInstalled || {};
  const reverse = target.reverseSkill || {};
  const mcp = target.mcpServers || [];
  const restore = target.deploymentRestore || {};
  ui.restoreBtn.disabled = !restore.available || busy;
  paintFacts(ui.codexFacts, [
    { text: target.promptInstalled ? "指令层 · 已同步" : "指令层 · 待同步", kind: target.promptInstalled ? "ok" : "bad" },
    { text: target.identityInstalled ? "身份层 · 已就绪" : "身份层 · 待就绪", kind: target.identityInstalled ? "ok" : "bad" },
    { text: skills["coldbrew-api-reverse"] ? "API 逆向 · 就绪" : "API 逆向 · 待同步", kind: skills["coldbrew-api-reverse"] ? "ok" : "bad" },
    { text: skills["coldbrew-protocol-reverse"] ? "协议分析 · 就绪" : "协议分析 · 待同步", kind: skills["coldbrew-protocol-reverse"] ? "ok" : "bad" },
    { text: reverse.installed ? `技能套件 · ${reverse.modules || 0} 个入口` : "技能套件 · 待同步", kind: reverse.installed ? "ok" : "bad" },
    { text: mcp.length ? `工具桥 · ${mcp.length} 项` : "工具桥 · 未接入", kind: mcp.length ? "ok" : "bad" },
    { text: restore.available ? `恢复点 · 可用${restore.drifted ? `（${restore.drifted} 项漂移）` : ""}` : "恢复点 · 未建立", kind: restore.available && !restore.drifted ? "ok" : "" },
    { text: `审批 · ${target.approval || "—"}`, kind: target.approval === "never" ? "ok" : "bad" },
    { text: `hooks · ${target.hooks && !target.hooksIsolated ? "在岗" : "未启用"}`, kind: target.hooks && !target.hooksIsolated ? "ok" : "bad" },
  ]);
}

function paintEnv(env) {
  const items = [{ text: env?.python?.ok ? env.python.version : "Python 缺失", kind: env?.python?.ok ? "ok" : "bad" }, { text: env?.platform || "未知平台", kind: "" }];
  (env?.tools || []).forEach((tool) => items.push({ text: tool.ok ? `${tool.id} · ${tool.detail || "OK"}` : `${tool.id} · 未就绪`, kind: tool.ok ? "ok" : "bad" }));
  paintFacts(ui.envFacts, items);
}

async function refresh() {
  const catalog = await window.brew.catalog();
  renderHearths(catalog);
  const target = await window.brew.inspect(codexHome);
  paintTarget(target);
  const env = await window.brew.env();
  paintEnv(env);
  const online = catalog.filter((item) => item.entry).length;
  if (target?.found) setStatus(env.python.ok ? "ok" : "bad", "工作台已就绪", `${online}/${catalog.length} 个模型入口可用 · ${profile.toUpperCase()} 档位 · 破甲核心已连接`);
}

async function runSeat(id, verb) {
  await withJob(`${id} · ${verb}`, async () => {
    const result = await window.brew.run({ id, verb, home: id === "codex" ? codexHome : null, blade, profile });
    line(result?.ok ? "ok" : "error", id, result?.ok ? `${verb} 完成` : `${verb} 退出码 ${result?.code}`);
    await refresh();
    toast(result?.ok ? `${id} ${verb} 完成` : `${id} ${verb} 失败`);
  });
}

async function boot() {
  meta = await window.brew.meta();
  document.body.dataset.platform = meta.platform || "";
  profile = window.localStorage?.getItem("coldbrew.profile") || "max";
  renderProfiles();
  renderBlades();
  renderCommunity();
  window.brew.onLog((entry) => line(entry.type || "out", entry.source, entry.message));
  await refresh();
  line("info", "工作台", `MAXIMUM CORE 已加载 · ${profile.toUpperCase()} / 破甲核心`);
}

document.getElementById("minBtn").addEventListener("click", () => window.brew.minimize());
document.getElementById("maxBtn").addEventListener("click", () => window.brew.toggleMaximize());
document.getElementById("closeBtn").addEventListener("click", () => window.brew.close());
document.getElementById("clearBtn").addEventListener("click", () => { ui.log.replaceChildren(); line("info", "工作台", "活动流已清空"); });
document.getElementById("copyLogBtn").addEventListener("click", async () => { await window.brew.copy(ui.log.innerText); toast("活动流已复制"); });
document.getElementById("chooseBtn").addEventListener("click", async () => { const selected = await window.brew.choose(); if (!selected) return; codexHome = selected; line("ok", "目标", selected); await refresh(); });
document.getElementById("openBtn").addEventListener("click", () => window.brew.open(codexHome));
document.getElementById("sideOpenBtn").addEventListener("click", () => window.brew.open(codexHome));
document.getElementById("sideCommunityBtn").addEventListener("click", () => document.querySelector(".community-section")?.scrollIntoView({ behavior: "smooth", block: "center" }));
document.getElementById("deployAllBtn").addEventListener("click", async () => { await withJob("一键启动 MAX", async () => { const result = await window.brew.deployAll({ home: codexHome, blade, profile }); await refresh(); setStatus(result?.ok ? "ok" : "bad", result?.ok ? "MAX 链路已启动" : "MAX 链路有缺口", "指令层、技能层、工具桥与四个模型已完成一轮执行。"); toast(result?.ok ? "MAX 启动完成" : "MAX 启动有缺口"); }); });
document.getElementById("restoreAllBtn").addEventListener("click", async () => { await withJob("恢复默认", async () => { const result = await window.brew.restoreAll({ home: codexHome, profile }); const restore = result?.restore || {}; line("ok", "恢复", `恢复 ${restore.restored || 0} · 删除 ${restore.removed || 0} · 漂移 ${restore.drifted || 0}`); await refresh(); toast("恢复点已应用"); }); });
document.getElementById("verifyAllBtn").addEventListener("click", async () => { await withJob("完整验收", async () => { const result = await window.brew.accept({ home: codexHome, blade, profile }); setStatus(result?.ok ? "ok" : "bad", result?.reply || "验收结束", `静态 ${result?.passed || 0}/${result?.total || 0}${result?.threadId ? ` · 桌面 ${result.threadId}` : ""}`); toast(result?.ok ? "验收通过" : "验收未齐"); }); });
document.getElementById("envBtn").addEventListener("click", async () => { await withJob("准备运行环境", async () => { const result = await window.brew.setup(); (result?.messages || []).forEach((message) => line(message.type || "info", "环境", message.message)); paintEnv(result?.status || await window.brew.env()); toast("环境检查完成"); }); });

document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => { document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("is-on", item === button)); document.getElementById(button.dataset.jump)?.scrollIntoView({ behavior: "smooth", block: "start" }); }));
document.addEventListener("keydown", (event) => { if (!(event.ctrlKey || event.metaKey)) return; const index = Number(event.key); if (index >= 1 && index <= 5) { event.preventDefault(); document.querySelector(`.nav-item:nth-child(${index})`)?.click(); } });
setInterval(() => { ui.clockChip.textContent = new Date().toTimeString().slice(0, 8); }, 1000);
boot();
