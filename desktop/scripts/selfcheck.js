const { TOOLS, CORE, entryPath } = require("../src/lib/catalog");
const { exists, isFile } = require("../src/lib/fs-util");
const { pythonExecutable, pythonVersion } = require("../src/lib/python");
const { environmentStatus } = require("../src/lib/env");

const misses = TOOLS.filter((tool) => !isFile(entryPath(tool))).map((tool) => tool.id);
const python = pythonExecutable();
const env = environmentStatus();
const report = {
  core: exists(CORE),
  python: python ? pythonVersion(python) : null,
  seats: TOOLS.map((tool) => ({ id: tool.id, entry: isFile(entryPath(tool)) })),
  misses,
  envReady: env.python.ok,
};
console.log(JSON.stringify(report, null, 2));
if (!report.core || misses.length) process.exit(2);
