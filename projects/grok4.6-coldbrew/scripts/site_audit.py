#!/usr/bin/env python3
"""Audit repository copy, community links, assets and activation contract."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from coldbrew_activation import CANONICAL_SHA256, activation_sha256, verify_canonical_contract

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
TOKENS = (
    "Grok 4.6 ColdBrew", f"v{VERSION}", "冷咖啡", "F7FB45C5DEC0F77E5AFD415DABAACCEEB5B2DDCF1F9918B7B2198BB911F34246", "", "",
    "", "", "",
    "codex5.6-coldbrew", "claude-coldbrew", "grok4.6-coldbrew", "deepseek-harness-coldbrew",
)
TEXTS = ("README.md", "README_EN.md", "docs/index.html")
EXPECTED_METADATA = {
    "description": "Grok 4.6 ColdBrew | 冷咖啡启动合同 | 可逆本地部署 | 微信群：冷咖啡破甲社区 | QQ：1057540028 / 1077074552 | Telegram 交流群：@chachachacha99999 | 官方频道：@chachacha99999999",
    "homepage": "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro/tree/main/projects/grok4.6-coldbrew",
    "name": "grok4.6-coldbrew",
}
REQUIRED_TOPICS = ("grok", "grok-4", "coldbrew")
ASSETS = {
    "docs/images/release-board.png": (1600, 900),
    "docs/images/product-matrix.png": (1600, 650),
    "docs/images/qq-group-1.png": (288, 288),
    "docs/images/qq-group-2.png": (288, 288),
    "docs/images/wechat-group.png": (1080, 1596),
}
RESPONSIVE_TOKENS = (
    "@media(max-width:800px)",
    ".hero>img{height:auto;aspect-ratio:16/9;object-fit:contain;object-position:center top}",
)


def png_size(data: bytes):
    return (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")) if data[:8] == b"\x89PNG\r\n\x1a\n" else None


def main() -> int:
    failures = []
    checks = 0
    for relative in TEXTS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for token in TOKENS:
            checks += 1
            if token not in text:
                failures.append(f"{relative}: missing {token}")
    try:
        metadata = json.loads((ROOT / ".github/repository-metadata.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append(f".github/repository-metadata.json: parse {exc.__class__.__name__}")
    else:
        for field, expected in EXPECTED_METADATA.items():
            checks += 1
            if metadata.get(field) != expected:
                failures.append(f".github/repository-metadata.json: {field} mismatch")
        topics = metadata.get("topics")
        checks += 1
        if not isinstance(topics, list) or not all(topic in topics for topic in REQUIRED_TOPICS):
            failures.append(".github/repository-metadata.json: required topics missing")
    for relative, expected in ASSETS.items():
        data = (ROOT / relative).read_bytes()
        checks += 2
        if png_size(data) != expected:
            failures.append(f"{relative}: dimensions {png_size(data)} != {expected}")
        if not hashlib.sha256(data).hexdigest():
            failures.append(f"{relative}: no hash")
    stylesheet = (ROOT / "docs/styles.css").read_text(encoding="utf-8")
    for token in RESPONSIVE_TOKENS:
        checks += 1
        if token not in stylesheet:
            failures.append(f"docs/styles.css: missing responsive rule {token}")
    checks += 2
    if not verify_canonical_contract() or activation_sha256() != CANONICAL_SHA256:
        failures.append("canonical activation contract mismatch")
    if failures:
        for item in failures:
            print(f"FAIL {item}")
        print(f"RESULT FAIL ({checks} checks, {len(failures)} failures)")
        return 1
    print(f"RESULT PASS ({checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
