#!/usr/bin/env node
"use strict";

const http = require("node:http");
const readline = require("node:readline");

const BURP = process.env.BURP_MCP_URL || "http://127.0.0.1:1337";

function send(id, result, error) {
  const payload = error
    ? { jsonrpc: "2.0", id, error }
    : { jsonrpc: "2.0", id, result };
  process.stdout.write(`${JSON.stringify(payload)}\n`);
}

function request(pathname) {
  return new Promise((resolve) => {
    const url = new URL(pathname, BURP.endsWith("/") ? BURP : `${BURP}/`);
    const req = http.get(url, { timeout: 4000 }, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => resolve({
        ok: true,
        status: res.statusCode,
        body: Buffer.concat(chunks).toString("utf8").slice(0, 8000),
      }));
    });
    req.on("error", (error) => resolve({ ok: false, error: error.message }));
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, error: "timeout" });
    });
  });
}

const tools = [
  {
    name: "burp_history",
    description: "Read Burp proxy history via the local MCP HTTP surface.",
    inputSchema: { type: "object", properties: { path: { type: "string" } } },
  },
  {
    name: "burp_ping",
    description: "Check whether the local Burp MCP endpoint is reachable.",
    inputSchema: { type: "object", properties: {} },
  },
];

async function callTool(name, args = {}) {
  if (name === "burp_ping") return request("/");
  if (name === "burp_history") return request(args.path || "/proxy/history");
  return { ok: false, error: `unknown tool ${name}` };
}

const rl = readline.createInterface({ input: process.stdin });
rl.on("line", async (line) => {
  let message;
  try {
    message = JSON.parse(line);
  } catch {
    return;
  }
  const { id, method, params } = message;
  if (method === "initialize") {
    send(id, {
      protocolVersion: "2024-11-05",
      serverInfo: { name: "coldbrew-burp-bridge", version: "1.0.0" },
      capabilities: { tools: {} },
    });
    return;
  }
  if (method === "tools/list") {
    send(id, { tools });
    return;
  }
  if (method === "tools/call") {
    const result = await callTool(params?.name, params?.arguments || {});
    send(id, { content: [{ type: "text", text: JSON.stringify(result) }] });
  }
});
