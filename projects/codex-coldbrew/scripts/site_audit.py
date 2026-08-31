#!/usr/bin/env python3
"""Verify Codex ColdBrew's published documents, links, and static assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_URL = "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro/tree/main/projects/codex-coldbrew"
REPOSITORY_URL = "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro"
TELEGRAM_GROUP = "https://t.me/chachachacha99999"
TELEGRAM_CHANNEL = "https://t.me/chachachacha99999999"

EXPECTED_DESCRIPTION = (
    "Codex 破甲 · 冷咖啡 / ColdBrew | 原创 Codex 多层指令增强与可逆部署 Studio | "
    "微信群：冷咖啡破甲社区 | QQ：1057540028 / 1077074552 | "
    "Telegram 交流群：@chachachacha99999 | 官方频道：@chachacha99999999"
)

# The public page uses the two current QR exports.  Checksums make asset
# replacement visible without tying the audit to unrelated runtime material.
ASSETS = {
    "docs/images/qq-group-1.jpg": ("8FE90FC60F56AEB652DB3C324F85A8E67934E0839297C13A8238763D6F494814", (1284, 2283)),
    "docs/images/qq-group-2.jpg": ("6C550FBDE004826A90BE10A2B850B2E23895A0A1A1C2FE4BD64E9D993D7C1F9F", (1284, 2283)),
    "docs/images/codex-group-qr.png": ("FCBB5CFFE3EF23EE6CD5AA476F923C0CF639A50CD8EB3CACBD5C58C23EAB545E", (1080, 1596)),
    "docs/images/product-matrix.png": ("FD21F0BCDA529C60A6AC880358F576B0AA70A84BA4597133B8ED7DB04078A618", (1600, 650)),
    "docs/images/codex-coldbrew-start.png": ("528F679E0E07BC3CEE0C2AC7F43530E87D6BB13E59A212EB9E8E3B8FE967572E", (1240, 780)),
    "docs/images/codex-coldbrew-active.png": ("347707183DE766092286C53C323CE4FC6F91D0DB613E8FE32E5C78F7D50FAC1D", (1240, 780)),
    "docs/images/codex-release-board.png": ("EB1EACB904FD98CA3544F6D041C22B7466F20758F1D66BAA51EEE63D6F59F67F", (1600, 900)),
    "docs/images/ishii-coldbrew-avatar.png": ("1946C85F3E9C23995B7BA66DBDDE5AC11A69119BB0CC5E23E5332F94E975F0D5", (512, 512)),
}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def image_dimensions(data: bytes) -> tuple[int, int] | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if not data.startswith(b"\xff\xd8"):
        return None
    offset = 2
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 8 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            return None
        length = int.from_bytes(data[offset:offset + 2], "big")
        if length < 2 or offset + length > len(data):
            return None
        if marker in sof_markers and length >= 7:
            return int.from_bytes(data[offset + 5:offset + 7], "big"), int.from_bytes(data[offset + 3:offset + 5], "big")
        offset += length
    return None


def audit(root: Path) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []

    def record(ok: bool, target: str, detail: str) -> None:
        checks.append({"status": "PASS" if ok else "FAIL", "target": target, "detail": detail})

    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        record(False, "VERSION", f"utf8-read:{exc.__class__.__name__}")
        version = ""
    else:
        record(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "VERSION", f"semver:{version}")

    public_docs = ("README.md", "README_EN.md", "docs/PRODUCT.md", "docs/index.html")
    texts: dict[str, str] = {}
    for relative in public_docs:
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            record(False, relative, f"utf8-read:{exc.__class__.__name__}")
            continue
        texts[relative] = text
        record("\ufffd" not in text, relative, "no replacement character")
        record(re.search(r"\?{2,}", text) is None, relative, "no repeated ASCII question marks")

    for relative in ("README.md", "README_EN.md"):
        text = texts.get(relative, "")
        record(f"v{version}" in text, relative, f"current-version:v{version}")
        record(f"Codex-ColdBrew-Studio-v{version}" in text, relative, "current-artifact-stem")
        record("@chachachacha99999" in text and "@chachacha99999999" in text, relative, "telegram-community")
        record(PROJECT_URL in text, relative, "project-link")
        record("docs/images/qq-group-1.jpg" in text and "docs/images/qq-group-2.jpg" in text, relative, "current-qq-assets")

    product = texts.get("docs/PRODUCT.md", "")
    record(f"v{version}" in product, "docs/PRODUCT.md", f"current-version:v{version}")
    record(f"Codex-ColdBrew-Studio-v{version}" in product, "docs/PRODUCT.md", "current-artifact-stem")

    site = texts.get("docs/index.html", "")
    for token in (
        'lang="zh-CN"',
        'id="community"',
        "images/codex-release-board.png",
        "images/codex-coldbrew-start.png",
        "images/codex-coldbrew-active.png",
        "images/qq-group-1.jpg",
        "images/qq-group-2.jpg",
        TELEGRAM_GROUP,
        TELEGRAM_CHANNEL,
        PROJECT_URL,
        'rel="canonical" href="' + PROJECT_URL + '"',
        "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro/blob/main/projects/codex-coldbrew/LICENSE_POLICY.md",
    ):
        record(token in site, "docs/index.html", f"contains:{token}")
    record(f"v{version}" in site, "docs/index.html", f"current-version:v{version}")
    record('width="1240" height="780"' in site, "docs/index.html", "screenshot-intrinsic-dimensions")
    record('alt=""' in site and 'aria-label=' in site, "docs/index.html", "basic-accessibility")

    metadata_path = root / ".github" / "repository-metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        record(False, ".github/repository-metadata.json", f"parse:{exc.__class__.__name__}")
    else:
        record(metadata.get("description") == EXPECTED_DESCRIPTION, "repository description", "published description")
        record(metadata.get("homepage") == PROJECT_URL, "repository homepage", "project tree URL")
        topics = metadata.get("topics", [])
        record(isinstance(topics, list) and {"codex", "coldbrew"}.issubset(topics), "repository topics", "core topics")

    for relative, (expected_hash, expected_dimensions) in ASSETS.items():
        try:
            data = (root / relative).read_bytes()
        except OSError as exc:
            record(False, relative, f"read:{exc.__class__.__name__}")
            continue
        digest = hashlib.sha256(data).hexdigest().upper()
        dimensions = image_dimensions(data)
        record(digest == expected_hash, relative, f"sha256:{digest}")
        record(dimensions == expected_dimensions, relative, f"dimensions:{dimensions}")

    for relative in ("LICENSE_POLICY.md", "THIRD_PARTY_NOTICES.md"):
        path = root / relative
        record(path.is_file() and not path.is_symlink(), relative, "public-notice-present")

    wrong_telegram = "https://t.me/+4JaWWv6zXtRmMTNl"
    residue = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".html", ".json", ".css", ".js"}:
            try:
                if wrong_telegram in path.read_text(encoding="utf-8"):
                    residue.append(path.relative_to(root).as_posix())
            except (OSError, UnicodeError):
                pass
    record(not residue, "Telegram residue", f"files:{residue}")
    return checks


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    checks = audit(args.root.expanduser().resolve())
    failures = [check for check in checks if check["status"] == "FAIL"]
    if args.json:
        print(json.dumps({"ok": not failures, "checks": checks}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for check in checks:
            print(f"{check['status']} {check['target']}: {check['detail']}")
        print(f"RESULT {'PASS' if not failures else 'FAIL'} ({len(checks)} checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
