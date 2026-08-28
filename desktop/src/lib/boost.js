const fs = require("node:fs");
const path = require("node:path");
const { backupFile, isFile, atomicWrite } = require("./fs-util");
const { readRootString, setRootString, readTableString, setTableString } = require("./toml");

const LIVE_PROMPT_CANDIDATES = [
  "coldbrew-live.md",
  "eni-jailbreak-v4.md",
  "eni-jailbreak-v7.md",
  "eni-jailbreak.md",
  "eni-solo-v4.0.0.md",
];

function pickLivePrompt(codexHome) {
  for (const name of LIVE_PROMPT_CANDIDATES) {
    if (isFile(path.join(codexHome, name))) return `./${name}`;
    if (isFile(path.join(codexHome, "prompts", name))) return `./prompts/${name}`;
  }
  return null;
}

function thickenCodex(codexHome) {
  const configPath = path.join(codexHome, "config.toml");
  if (!isFile(configPath)) {
    return { changed: false, reason: "没有 config.toml" };
  }
  const before = fs.readFileSync(configPath, "utf8");
  let after = before;
  const live = pickLivePrompt(codexHome);
  if (live && readRootString(after, "model_instructions_file") !== live) {
    after = setRootString(after, "model_instructions_file", live);
  }
  if (readRootString(after, "approval_policy") !== "never") {
    after = setRootString(after, "approval_policy", "never");
  }
  if (readRootString(after, "sandbox_mode") !== "danger-full-access") {
    after = setRootString(after, "sandbox_mode", "danger-full-access");
  }
  if (readTableString(after, "desktop", "localeOverride") !== "zh-CN") {
    after = setTableString(after, "desktop", "localeOverride", "zh-CN");
  }
  if (after === before) {
    return { changed: false, live, instruction: readRootString(after, "model_instructions_file") };
  }
  const backup = backupFile(configPath);
  atomicWrite(configPath, after);
  return {
    changed: true,
    backup,
    live,
    instruction: readRootString(after, "model_instructions_file"),
    approval: readRootString(after, "approval_policy"),
    sandbox: readRootString(after, "sandbox_mode"),
    locale: readTableString(after, "desktop", "localeOverride"),
  };
}

function inspectCodexConfig(codexHome) {
  const configPath = path.join(codexHome, "config.toml");
  if (!isFile(configPath)) return { present: false };
  const content = fs.readFileSync(configPath, "utf8");
  const hooksPath = path.join(codexHome, "hooks.json");
  return {
    present: true,
    path: configPath,
    instruction: readRootString(content, "model_instructions_file"),
    approval: readRootString(content, "approval_policy"),
    sandbox: readRootString(content, "sandbox_mode"),
    locale: readTableString(content, "desktop", "localeOverride"),
    hooks: isFile(hooksPath),
    hooksIsolated: isFile(`${hooksPath}.disabled`),
    livePrompt: pickLivePrompt(codexHome),
    agents: isFile(path.join(codexHome, "AGENTS.md")),
  };
}

module.exports = {
  thickenCodex,
  inspectCodexConfig,
  pickLivePrompt,
  LIVE_PROMPT_CANDIDATES,
};
