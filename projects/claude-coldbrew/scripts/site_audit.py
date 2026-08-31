#!/usr/bin/env python3
"""Validate Claude ColdBrew public documentation and static site assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro"
PROJECT_URL = f"{REPOSITORY_URL}/tree/main/projects/claude-coldbrew"
RELEASES_URL = f"{REPOSITORY_URL}/releases"
LATEST_RELEASE_URL = f"{REPOSITORY_URL}/releases/latest"
TELEGRAM_GROUP_URL = "https://t.me/chachachacha99999"
TELEGRAM_CHANNEL_URL = "https://t.me/chachachacha99999999"

PRODUCT_MATRIX_URLS = {
    "Codex": f"{REPOSITORY_URL}/tree/main/projects/codex-coldbrew",
    "Claude": PROJECT_URL,
    "Grok 4.6": f"{REPOSITORY_URL}/tree/main/projects/grok4.6-coldbrew",
    "DeepSeek Harness": f"{REPOSITORY_URL}/tree/main/projects/deepseek-harness",
}

# These are the files served by the public page, not installer/runtime inputs.
ASSET_SPECS = {
    "docs/images/claude-release-board.png": {
        "sha256": "51EE7B1FD2F56B65A3BAFB9F6D8FB2634A94C9C23F2760C2B40942949BD8A71A",
        "size": (1600, 900),
    },
    "docs/images/claude-coldbrew-start.png": {
        "sha256": "A3A8340F1212FD8E641EFF5B01BBE9158EEF480EDECCB4219C01539CF5F09FD6",
        "size": (1240, 780),
    },
    "docs/images/claude-coldbrew-active.png": {
        "sha256": "E723DB5586C0662AC7A7B8CA1CA2B4C1D6A7D88CFF64204A9DA14904D7FC7253",
        "size": (1240, 780),
    },
    "docs/images/product-matrix.png": {
        "sha256": "FD21F0BCDA529C60A6AC880358F576B0AA70A84BA4597133B8ED7DB04078A618",
        "size": (1600, 650),
    },
    "docs/images/codex-group-qr.png": {
        "sha256": "FCBB5CFFE3EF23EE6CD5AA476F923C0CF639A50CD8EB3CACBD5C58C23EAB545E",
        "size": (1080, 1596),
    },
    "docs/images/qq-group-1.jpg": {
        "sha256": "8FE90FC60F56AEB652DB3C324F85A8E67934E0839297C13A8238763D6F494814",
        "size": (1284, 2283),
    },
    "docs/images/qq-group-2.jpg": {
        "sha256": "6C550FBDE004826A90BE10A2B850B2E23895A0A1A1C2FE4BD64E9D993D7C1F9F",
        "size": (1284, 2283),
    },
    "docs/images/ishii-coldbrew-avatar.png": {
        "sha256": "422F704C4C0F0451FB2027EF0FC260D6ED29C8C00B9E54F8C3EC5D242372C0AD",
        "size": (512, 512),
    },
    "docs/images/claude-brain-hero.png": {
        "sha256": "098CD80926D5CAC4E3F81E6CE25DC03A50E292B02B85036CE6261B11589D6C0E",
        "size": (1600, 720),
    },
}

DOCUMENTS = (
    "README.md",
    "README_EN.md",
    "docs/index.html",
    "LICENSE_POLICY.md",
    "THIRD_PARTY_NOTICES.md",
)

SCREENSHOT_DIMENSIONS = {
    "images/claude-coldbrew-start.png": (1240, 780),
    "images/claude-coldbrew-active.png": (1240, 780),
}

CSS_URL = re.compile(r"url\(\s*(['\"]?)(?P<value>[^)'\"\s]+)\1\s*\)", re.IGNORECASE)
SEMVER = re.compile(r"(?<![A-Za-z0-9])v?(\d+\.\d+\.\d+)(?![A-Za-z0-9])")
SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


class SiteParser(HTMLParser):
    """Collect the small amount of semantic structure the static audit needs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attributes: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.labelled_by: list[str] = []
        self.images: list[dict[str, str]] = []
        self.references: list[tuple[str, str, str]] = []
        self.main_count = 0
        self.h1_count = 0
        self.has_labelled_navigation = False
        self.has_footer = False
        self._in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        self.attributes.append((tag, values))
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("aria-labelledby"):
            self.labelled_by.extend(values["aria-labelledby"].split())
        if tag == "img":
            self.images.append(values)
        if tag in {"a", "link"} and values.get("href"):
            self.references.append((tag, "href", values["href"]))
        if tag in {"img", "script"} and values.get("src"):
            self.references.append((tag, "src", values["src"]))
        if tag == "main":
            self.main_count += 1
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "nav" and values.get("aria-label"):
            self.has_labelled_navigation = True
        elif tag == "footer":
            self.has_footer = True
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    offset = 2
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
        if marker in SOF_MARKERS and length >= 7:
            height = int.from_bytes(data[offset + 3:offset + 5], "big")
            width = int.from_bytes(data[offset + 5:offset + 7], "big")
            return width, height
        offset += length
    return None


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def image_dimensions(path: Path, data: bytes) -> tuple[int, int] | None:
    if path.suffix.lower() == ".png":
        return png_dimensions(data)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return jpeg_dimensions(data)
    return None


def is_local_reference(value: str) -> bool:
    return bool(value) and not value.startswith(("#", "//", "data:", "http://", "https://", "mailto:", "tel:"))


def local_reference_path(document: Path, value: str, repository_root: Path) -> Path | None:
    path_value = value.split("#", 1)[0].split("?", 1)[0]
    candidate = (document.parent / path_value).resolve()
    try:
        candidate.relative_to(repository_root)
    except ValueError:
        return None
    return candidate


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
        record(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "VERSION", f"release:{version}")

    artifact = f"Claude-ColdBrew-Studio-v{version}-Windows.exe"
    source_archive = f"Claude-ColdBrew-Studio-v{version}-Source.zip"
    document_text: dict[str, str] = {}
    for relative in DOCUMENTS:
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            record(False, relative, f"utf8-read:{exc.__class__.__name__}")
            continue
        document_text[relative] = text
        record("\ufffd" not in text, relative, "no replacement character")
        record("锟斤拷" not in text, relative, "no common mojibake marker")

    requirements = {
        "README.md": (
            PROJECT_URL,
            LATEST_RELEASE_URL,
            f"v{version}",
            artifact,
            source_archive,
            TELEGRAM_GROUP_URL,
            TELEGRAM_CHANNEL_URL,
            "docs/images/qq-group-1.jpg",
            "docs/images/qq-group-2.jpg",
            "LICENSE_POLICY.md",
            "THIRD_PARTY_NOTICES.md",
        ),
        "README_EN.md": (
            PROJECT_URL,
            LATEST_RELEASE_URL,
            f"v{version}",
            artifact,
            TELEGRAM_GROUP_URL,
            TELEGRAM_CHANNEL_URL,
            "docs/images/qq-group-1.jpg",
            "docs/images/qq-group-2.jpg",
            "LICENSE_POLICY.md",
            "THIRD_PARTY_NOTICES.md",
        ),
        "docs/index.html": (
            PROJECT_URL,
            RELEASES_URL,
            artifact,
            TELEGRAM_GROUP_URL,
            TELEGRAM_CHANNEL_URL,
            "images/qq-group-1.jpg",
            "images/qq-group-2.jpg",
            "images/claude-coldbrew-start.png",
            "images/claude-coldbrew-active.png",
        ),
        "LICENSE_POLICY.md": (
            "ColdBrew Studio Community License v1.0",
            "CBCL-1.0",
            "source-available",
            "not an OSI-approved open source license",
            "closed-source",
            "commercial sale",
            "paid hosting",
            "app/",
            "scripts/",
            "docs/",
            "pack/",
            "assets/",
        ),
        "THIRD_PARTY_NOTICES.md": (
            "Third-Party Notices",
            "ColdBrew",
            "Anthropic",
            "independent",
        ),
    }
    for relative, tokens in requirements.items():
        text = document_text.get(relative)
        if text is None:
            continue
        collapsed = " ".join(text.split()).casefold()
        for token in tokens:
            record(token.casefold() in collapsed, relative, f"contains:{token}")
        if relative in {"README.md", "README_EN.md", "docs/index.html"}:
            versions = set(SEMVER.findall(text))
            record(not versions or versions == {version}, relative, f"current-versions:{sorted(versions)}")

    retired = (
        "https://茶.github.io",
        "https://github.com/茶/",
        "qq-group-codex.png",
        "qq-group-codex-claude.png",
    )
    for relative in ("README.md", "README_EN.md", "docs/index.html"):
        text = document_text.get(relative)
        if text is None:
            continue
        for token in retired:
            record(token not in text, relative, f"no-retired-reference:{token}")

    metadata_path = root / ".github" / "repository-metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        record(False, ".github/repository-metadata.json", f"parse:{exc.__class__.__name__}")
    else:
        description = metadata.get("description", "")
        record(isinstance(description, str) and all(token in description for token in ("Claude", "ColdBrew", "Telegram")), "repository description", "public summary")
        record(metadata.get("homepage") == PROJECT_URL, "repository homepage", "project tree URL")
        topics = metadata.get("topics", [])
        record(isinstance(topics, list) and {"claude-code", "coldbrew"}.issubset(topics), "repository topics", "core topics")

    for relative, expected in ASSET_SPECS.items():
        path = root / relative
        try:
            data = path.read_bytes()
        except OSError as exc:
            record(False, relative, f"read:{exc.__class__.__name__}")
            continue
        digest = hashlib.sha256(data).hexdigest().upper()
        record(digest == expected["sha256"], relative, f"sha256:{digest}")
        dimensions = image_dimensions(path, data)
        record(dimensions == expected["size"], relative, f"dimensions:{dimensions}")

    page_path = root / "docs" / "index.html"
    page_text = document_text.get("docs/index.html")
    if page_text is not None:
        parser = SiteParser()
        try:
            parser.feed(page_text)
            parser.close()
        except Exception as exc:  # HTMLParser is tolerant, but keep output deterministic.
            record(False, "docs/index.html", f"parse:{exc.__class__.__name__}")
        else:
            record(parser.main_count == 1, "docs/index.html", f"main-count:{parser.main_count}")
            record(parser.h1_count == 1, "docs/index.html", f"h1-count:{parser.h1_count}")
            record(bool("".join(parser.title_parts).strip()), "docs/index.html", "nonempty-title")
            record(parser.has_labelled_navigation, "docs/index.html", "labelled-navigation")
            record(parser.has_footer, "docs/index.html", "footer-present")
            record(all("alt" in image for image in parser.images), "docs/index.html", "images-have-alt")
            record(all(reference in parser.ids for reference in parser.labelled_by), "docs/index.html", "aria-labelledby-targets")
            record(all(values.get("href", "").strip() for tag, values in parser.attributes if tag == "a"), "docs/index.html", "anchors-have-href")
            repository_root = root.parents[1]
            for tag, attribute, value in parser.references:
                if not is_local_reference(value):
                    continue
                resolved = local_reference_path(page_path, value, repository_root)
                record(resolved is not None and resolved.is_file(), "docs/index.html", f"local-{tag}-{attribute}:{value}")
            for image in parser.images:
                expected = SCREENSHOT_DIMENSIONS.get(image.get("src", ""))
                if expected is None:
                    continue
                actual = (int(image.get("width", "0")), int(image.get("height", "0")))
                record(actual == expected, "docs/index.html", f"display-dimensions:{image['src']}={actual}")

    repository_root = root.parents[1]
    # `claude.css` and `brand.css` are the page-specific layers. The shared
    # base sheet intentionally carries cross-product defaults that this page
    # overrides, so it is not a Claude asset manifest.
    for relative in ("docs/claude.css", "docs/brand.css"):
        stylesheet = root / relative
        try:
            stylesheet_text = stylesheet.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            record(False, stylesheet.relative_to(root).as_posix(), f"utf8-read:{exc.__class__.__name__}")
            continue
        for match in CSS_URL.finditer(stylesheet_text):
            value = match.group("value")
            if not is_local_reference(value):
                continue
            resolved = local_reference_path(stylesheet, value, repository_root)
            record(resolved is not None and resolved.is_file(), stylesheet.relative_to(root).as_posix(), f"local-css-url:{value}")

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
