"""Keyword classifier for FiveEdge.  One blade wins; ties keep insertion order."""

from __future__ import annotations

from .blades import BLADE_SPECS

BLADE_IDS: tuple[str, ...] = tuple(spec["id"] for spec in BLADE_SPECS)

_LEXICON: dict[str, tuple[str, ...]] = {
    "REV": (
        "逆向", "反编译", "反汇编", "pe", "elf", "dll", "exe", "ida", "ghidra",
        "frida", "脱壳", "iAT", "伪代码", "偏移", "so文件", "apk",
    ),
    "UNLOCK": (
        "破解", "注册机", "keygen", "卡密", "序列号", "激活", "补丁", "patch",
        "license", "授权验证", "bypass license",
    ),
    "INFIL": (
        "渗透", "pentest", "漏洞", "sql注入", "xss", "ssrf", "rce", "爆破",
        "payload", "getshell", "打点", "src",
    ),
    "HARVEST": (
        "爬虫", "scrape", "crawl", "采集", "签名", "a_bogus", "xbogus",
        "翻页", "断点续爬",
    ),
    "TRAINER": (
        "外挂", "cheat", "esp", "自瞄", "透视", "aimbot", "overlay",
        "trainer", "实体列表", "矩阵",
    ),
}


def classify(prompt: str, *, default: str = "REV") -> str:
    text = (prompt or "").strip().lower()
    if not text:
        return default
    scores: dict[str, int] = {blade: 0 for blade in BLADE_IDS}
    for blade, words in _LEXICON.items():
        for word in words:
            if word.lower() in text:
                scores[blade] += 1
    best = max(scores.values())
    if best <= 0:
        return default
    for blade in BLADE_IDS:
        if scores[blade] == best:
            return blade
    return default
