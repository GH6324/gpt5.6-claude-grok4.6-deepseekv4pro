function newlineOf(content) {
  return content.includes("\r\n") ? "\r\n" : "\n";
}

function quote(value) {
  return JSON.stringify(String(value));
}

function firstTableIndex(lines) {
  for (let index = 0; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    if (trimmed.startsWith("[") && trimmed.endsWith("]")) return index;
  }
  return lines.length;
}

function readRootString(content, key) {
  const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const matcher = new RegExp(`^\\s*${escaped}\\s*=\\s*(["'])(.*?)\\1`);
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    if (trimmed.startsWith("[")) break;
    const match = line.match(matcher);
    if (match) return match[2];
  }
  return null;
}

function setRootString(content, key, value) {
  const newline = newlineOf(content);
  const lines = content.split(/\r?\n/);
  const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const matcher = new RegExp(`^\\s*${escaped}\\s*=`);
  const table = firstTableIndex(lines);
  for (let index = 0; index < table; index += 1) {
    if (matcher.test(lines[index])) {
      const commentIndex = lines[index].indexOf("#");
      const comment = commentIndex >= 0 ? `  ${lines[index].slice(commentIndex).trim()}` : "";
      lines[index] = `${key} = ${quote(value)}${comment}`;
      return lines.join(newline);
    }
  }
  const insert = `${key} = ${quote(value)}`;
  if (table >= lines.length) {
    const next = [...lines];
    if (next.length && next[next.length - 1].trim()) next.push("");
    next.push(insert);
    return next.join(newline);
  }
  const next = [...lines.slice(0, table), insert, "", ...lines.slice(table)];
  return next.join(newline);
}

function readTableString(content, table, key) {
  const lines = content.split(/\r?\n/);
  let inside = false;
  const keyMatcher = new RegExp(`^\\s*${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*=\\s*(["'])(.*?)\\1`);
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
      inside = trimmed.slice(1, -1).trim() === table;
      continue;
    }
    if (!inside || trimmed.startsWith("#")) continue;
    const match = line.match(keyMatcher);
    if (match) return match[2];
  }
  return null;
}

function setTableString(content, table, key, value) {
  const newline = newlineOf(content);
  const lines = content.split(/\r?\n/);
  const header = `[${table}]`;
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
  const assignment = `${key} = ${quote(value)}`;
  if (start < 0) {
    const next = [...lines];
    if (next.length && next[next.length - 1].trim()) next.push("");
    next.push(header, assignment, "");
    return next.join(newline);
  }
  const keyMatcher = new RegExp(`^\\s*${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*=`);
  const body = lines.slice(start + 1, end);
  let found = false;
  const rewritten = body.map((line) => {
    if (found || !keyMatcher.test(line)) return line;
    found = true;
    const commentIndex = line.indexOf("#");
    const comment = commentIndex >= 0 ? `  ${line.slice(commentIndex).trim()}` : "";
    return `${assignment}${comment}`;
  });
  if (!found) rewritten.push(assignment);
  return [...lines.slice(0, start + 1), ...rewritten, ...lines.slice(end)].join(newline);
}

module.exports = {
  newlineOf,
  readRootString,
  setRootString,
  readTableString,
  setTableString,
};
