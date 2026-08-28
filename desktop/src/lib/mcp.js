const path = require("node:path");
const { ROOT } = require("./catalog");
const { backupFile, atomicWrite, isFile } = require("./fs-util");
const { newlineOf } = require("./toml");

const MCP_SERVERS = ["anything-analyzer", "idapro", "burpsuite"];

function burpBridgePath() {
  return path.join(ROOT, "assets", "mcp", "burp-bridge.js");
}

function managedMcpToml() {
  const bridge = burpBridgePath().replaceAll("\\", "\\\\");
  return [
    '[mcp_servers."anything-analyzer"]',
    'url = "http://127.0.0.1:23816/mcp"',
    "",
    '[mcp_servers."idapro"]',
    'url = "http://127.0.0.1:13337/mcp"',
    "",
    '[mcp_servers."burpsuite"]',
    'command = "node"',
    `args = ["${bridge}"]`,
    "",
  ].join("\n");
}

function mcpNames(content) {
  return [...content.matchAll(/^\s*\[mcp_servers\."([^"]+)"\]/gm)].map((match) => match[1]);
}

function replaceServer(lines, name, blockLines) {
  const header = `[mcp_servers."${name}"]`;
  let start = -1;
  let end = lines.length;
  for (let index = 0; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    if (trimmed === header) {
      start = index;
      continue;
    }
    if (start >= 0 && trimmed.startsWith("[") && trimmed.endsWith("]")) {
      end = index;
      break;
    }
  }
  if (start < 0) return [...lines, "", ...blockLines];
  return [...lines.slice(0, start), ...blockLines, ...lines.slice(end)];
}

function mergeMcp(content) {
  const newline = newlineOf(content);
  let lines = content.split(/\r?\n/);
  const source = managedMcpToml().split(/\r?\n/);
  let block = [];
  const flush = (name) => {
    if (!name) return;
    while (block.length && block[block.length - 1] === "") block.pop();
    lines = replaceServer(lines, name, block);
    block = [];
  };
  let current = null;
  for (const line of source) {
    const match = line.match(/^\[mcp_servers\."([^"]+)"\]/);
    if (match) {
      flush(current);
      current = match[1];
      block = [line];
      continue;
    }
    if (current) block.push(line);
  }
  flush(current);
  return lines.join(newline).replace(/\n{3,}/g, "\n\n");
}

function deployMcp(codexHome) {
  const configPath = path.join(codexHome, "config.toml");
  if (!isFile(configPath)) return { changed: false, servers: [], reason: "没有 config.toml" };
  const fs = require("node:fs");
  const before = fs.readFileSync(configPath, "utf8");
  const after = mergeMcp(before);
  const servers = MCP_SERVERS.slice();
  if (after === before) {
    return { changed: false, servers, already: mcpNames(before) };
  }
  const backup = backupFile(configPath);
  atomicWrite(configPath, after);
  return { changed: true, backup, servers, already: mcpNames(after) };
}

module.exports = {
  MCP_SERVERS,
  mcpNames,
  deployMcp,
  burpBridgePath,
};
