const ui = {
  statusTitle: document.querySelector("#statusTitle"),
  statusDetail: document.querySelector("#statusDetail"),
  statusDot: document.querySelector("#statusDot"),
  bladeBar: document.querySelector("#bladeBar"),
  bladeHint: document.querySelector("#bladeHint"),
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

let meta = { blades: [], tools: [], qq: [], telegram: [] };
let blade = "ALL";
let busy = false;
let codexHome = null;
let toastTimer;

function setStatus(kind, title, detail) {
  ui.statusDot.className = kind;
  ui.statusTitle.textContent = title;
  ui.statusDetail.textContent = detail;
}

function toast(text) {
  ui.toast.textContent = text;
  ui.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove("show"), 2400);
}

function line(kind, source, message) {
  const row = document.createElement("div");
  row.className = kind || "out";
  const time = new Date().toTimeString().slice(0, 8);
  row.textContent = `[${time}] ${source ? `[${source}] ` : ""}${message}`;
  ui.log.appendChild(row);
  ui.log.scrollTop = ui.log.scrollHeight;
}

function pill(text, kind) {
  const span = document.createElement("span");
  if (kind) span.className = kind;
  span.textContent = text;
  return span;
}

function lock(state, title) {
  busy = state;
  document.querySelectorAll("button").forEach((button) => {
    if (button.id === "minBtn" || button.id === "maxBtn" || button.id === "closeBtn") return;
    if (button.classList.contains("nav")) return;
    if (button.id === "clearBtn") return;
    if (button.id === "restoreAllBtn" && !state) return;
    button.disabled = state;
  });
  if (state) setStatus("busy", title || "执行中", "作业还在本机跑，日志在右边流。");
}

async function withJob(title, work) {
  if (busy) {
    line("info", "破甲", "上一件事还没完。");
    return;
  }
  lock(true, title);
  try {
    return await work();
  } catch (error) {
    line("error", "破甲", error.message || String(error));
    setStatus("bad", "这轮没跑通", error.message || String(error));
    toast("失败");
    throw error;
  } finally {
    lock(false);
  }
}

function renderBlades() {
  ui.bladeBar.replaceChildren();
  const make = (id, label) => {
    const button = document.createElement("button");
    button.className = `tab${id === blade ? " is-on" : ""}`;
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", async () => {
      blade = id;
      renderBlades();
      const picked = meta.blades.find((item) => item.id === id);
      ui.bladeHint.textContent = id === "ALL" ? "五刃全开 · 按动词自动锁刃" : `${id}  ·  ${picked?.hint || ""}`;
      await window.brew.setBlade(id);
      line("ok", "刃", id);
    });
    ui.bladeBar.appendChild(button);
  };
  make("ALL", "全开");
  for (const item of meta.blades) make(item.id, item.label);
}

function renderCommunity() {
  ui.communityBar.replaceChildren();
  for (const group of meta.qq) {
    const button = document.createElement("button");
    button.className = "qq";
    button.type = "button";
    button.textContent = `${group.name}  ${group.number}`;
    button.addEventListener("click", async () => {
      await window.brew.copy(group.number);
      line("ok", "社群", `已复制 ${group.name} ${group.number}`);
      toast(`已复制 ${group.number}`);
    });
    ui.communityBar.appendChild(button);
  }
  for (const item of meta.telegram) {
    const button = document.createElement("button");
    button.className = "qq";
    button.type = "button";
    button.textContent = `${item.name}  ${item.handle}`;
    button.addEventListener("click", async () => {
      await window.brew.copy(item.handle);
      line("ok", "社群", item.handle);
    });
    ui.communityBar.appendChild(button);
  }
}

function renderHearths(rows) {
  ui.hearthGrid.replaceChildren();
  let ready = 0;
  for (const row of rows) {
    if (row.entry) ready += 1;
    const card = document.createElement("article");
    card.className = "hearth";
    card.innerHTML = `
      <div class="hearth-head">
        <div class="tag">${row.tag}</div>
        <div class="state">${row.entry ? "ONLINE" : "MISSING"}</div>
      </div>
      <p class="home">${row.home}</p>
      <div class="hearth-actions">
        <button data-id="${row.id}" data-verb="preview" type="button">预览</button>
        <button class="primary" data-id="${row.id}" data-verb="deploy" type="button">部署</button>
        <button data-id="${row.id}" data-verb="verify" type="button">验证</button>
        <button data-id="${row.id}" data-verb="restore" type="button">复原</button>
      </div>
    `;
    ui.hearthGrid.appendChild(card);
  }
  ui.readyChip.textContent = `${ready} / ${rows.length}`;
  ui.hearthGrid.querySelectorAll("button[data-verb]").forEach((button) => {
    button.addEventListener("click", () => runSeat(button.dataset.id, button.dataset.verb));
  });
}

function paintFacts(node, items) {
  node.replaceChildren();
  for (const item of items) node.appendChild(pill(item.text, item.kind));
}

function paintTarget(target) {
  if (!target?.found) {
    ui.codexPath.textContent = "未找到 Codex 配置";
    ui.targetLocale.textContent = "语言 · 未检测";
    ui.targetLocale.className = "locale";
    ui.restoreBtn.disabled = true;
    paintFacts(ui.codexFacts, [{ text: "需要选择 .codex 目录", kind: "bad" }]);
    setStatus("bad", "未找到 Codex", "先启动一次 Codex，或手动选择配置目录");
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
    { text: target.promptInstalled ? "指令配置 · 已同步" : "指令配置 · 待同步", kind: target.promptInstalled ? "ok" : "bad" },
    { text: target.identityInstalled ? "身份模块 · 已就绪" : "身份模块 · 待就绪", kind: target.identityInstalled ? "ok" : "bad" },
    { text: skills["coldbrew-api-reverse"] ? "API 逆向 · 已就绪" : "API 逆向 · 待就绪", kind: skills["coldbrew-api-reverse"] ? "ok" : "bad" },
    { text: skills["coldbrew-protocol-reverse"] ? "协议分析 · 已就绪" : "协议分析 · 待就绪", kind: skills["coldbrew-protocol-reverse"] ? "ok" : "bad" },
    { text: skills["coldbrew-native-reverse"] ? "Native 自动逆向 · 已就绪" : "Native 自动逆向 · 待就绪", kind: skills["coldbrew-native-reverse"] ? "ok" : "bad" },
    { text: reverse.installed ? `技能套件 · 已就绪（${reverse.modules || 0} 个入口）` : "技能套件 · 待同步", kind: reverse.installed ? "ok" : "bad" },
    { text: mcp.length ? `工具桥 · ${mcp.length} 项已接入` : "工具桥 · 未接入", kind: mcp.length ? "ok" : "bad" },
    { text: restore.available ? `恢复默认 · 可用${restore.drifted ? `（${restore.drifted} 项已漂移）` : ""}` : "恢复默认 · 无待恢复清单", kind: restore.available && restore.drifted === 0 ? "ok" : "" },
    { text: `审批 ${target.approval || "—"}`, kind: target.approval === "never" ? "ok" : "bad" },
    { text: `hooks ${target.hooks ? "在岗" : "无"}`, kind: target.hooks && !target.hooksIsolated ? "ok" : "bad" },
  ]);
}

function paintEnv(env) {
  const items = [
    { text: env.python.ok ? env.python.version : "Python 缺失", kind: env.python.ok ? "ok" : "bad" },
    { text: env.platform },
  ];
  for (const tool of env.tools) {
    items.push({ text: tool.ok ? `${tool.id} ${tool.detail || "ok"}` : `${tool.id} 无`, kind: tool.ok ? "ok" : "" });
  }
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
  if (target.found) {
    setStatus(
      env.python.ok ? "ok" : "bad",
      "破甲软件已点火",
      `${online}/${catalog.length} 模型入口就绪 · ${target.localized ? "简体中文" : "语言未锁"}`,
    );
  }
}

async function runSeat(id, verb) {
  await withJob(`${id} · ${verb}`, async () => {
    const result = await window.brew.run({
      id,
      verb,
      home: id === "codex" ? codexHome : null,
      blade,
    });
    line(result.ok ? "ok" : "error", id, result.ok ? `${verb} 完成` : `${verb} 退出码 ${result.code}`);
    await refresh();
    toast(result.ok ? `${verb} 完成` : `${verb} 失败`);
  });
}

async function boot() {
  meta = await window.brew.meta();
  document.body.dataset.platform = meta.platform || "";
  renderBlades();
  renderCommunity();
  window.brew.onLog((entry) => line(entry.type || "out", entry.source, entry.message));
  await refresh();
}

document.getElementById("minBtn").addEventListener("click", () => window.brew.minimize());
document.getElementById("maxBtn").addEventListener("click", () => window.brew.toggleMaximize());
document.getElementById("closeBtn").addEventListener("click", () => window.brew.close());
document.getElementById("clearBtn").addEventListener("click", () => { ui.log.replaceChildren(); line("info", "破甲", "日志已清空"); });
document.getElementById("chooseBtn").addEventListener("click", async () => {
  const selected = await window.brew.choose();
  if (!selected) return;
  codexHome = selected;
  line("ok", "目标", selected);
  await refresh();
});
document.getElementById("openBtn").addEventListener("click", () => window.brew.open(codexHome));
document.getElementById("deployAllBtn").addEventListener("click", async () => {
  await withJob("一键破甲", async () => {
    const result = await window.brew.deployAll({ home: codexHome, blade });
    await refresh();
    setStatus(result.ok ? "ok" : "bad", result.ok ? "一键破甲写完了" : "有模型没吃进去", "中文、指令、技能、工具桥、挂钩已走一遍");
    toast(result.ok ? "一键破甲完成" : "一键破甲有缺口");
  });
});
document.getElementById("restoreAllBtn").addEventListener("click", async () => {
  await withJob("恢复默认", async () => {
    const result = await window.brew.restoreAll({ home: codexHome });
    const restore = result.restore || {};
    line("ok", "恢复默认", `恢复 ${restore.restored || 0} · 删除 ${restore.removed || 0} · 漂移 ${restore.drifted || 0}`);
    await refresh();
    toast("恢复默认走完了");
  });
});
document.getElementById("verifyAllBtn").addEventListener("click", async () => {
  await withJob("完整验收", async () => {
    const result = await window.brew.accept({ home: codexHome, blade });
    setStatus(result.ok ? "ok" : "bad", result.reply || "验收结束", `静态 ${result.passed}/${result.total}${result.threadId ? ` · 桌面 ${result.threadId}` : ""}`);
    toast(result.ok ? "验收通过" : "验收未齐");
  });
});
document.getElementById("envBtn").addEventListener("click", async () => {
  await withJob("安装运行环境", async () => {
    const result = await window.brew.setup();
    for (const message of result.messages || []) line(message.type || "info", "环境", message.message);
    paintEnv(result.status || await window.brew.env());
    toast("环境安装走完了");
  });
});

document.querySelectorAll(".nav").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav").forEach((item) => item.classList.toggle("is-on", item === button));
    document.getElementById(button.dataset.jump)?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

setInterval(() => {
  ui.clockChip.textContent = new Date().toTimeString().slice(0, 8);
}, 1000);

boot();
