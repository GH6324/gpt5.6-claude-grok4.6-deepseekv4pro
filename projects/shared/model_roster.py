"""Jailbreak-capable model roster shown in the Hub and Claude pack.

Names follow the public Claude family: Opus / Fable / Sonnet / Haiku,
plus the 4.5–4.8 and 5.x cuts users actually type.
"""

from __future__ import annotations

CLAUDE_MODELS: tuple[dict[str, object], ...] = (
    {"id": "opus-5", "label": "Opus 5", "aliases": ("opus5", "claude-opus-5", "opus-4.7", "claude-opus-4-7")},
    {"id": "fable-5", "label": "Fable 5", "aliases": ("fable5", "claude-fable-5", "fable-5")},
    {"id": "claude-4.8", "label": "4.8", "aliases": ("4.8", "claude-4.8", "claude-opus-4.8", "sonnet-4.8", "claude-sonnet-4-8")},
    {"id": "opus-4.6", "label": "Opus 4.6", "aliases": ("opus4.6", "claude-opus-4.6", "claude-opus-4-6")},
    {"id": "opus-4.5", "label": "Opus 4.5", "aliases": ("opus4.5", "claude-opus-4.5", "claude-opus-4-5")},
    {"id": "fable-4.6", "label": "Fable 4.6", "aliases": ("fable4.6", "claude-fable-4.6")},
    {"id": "sonnet-4.6", "label": "Sonnet 4.6", "aliases": ("sonnet4.6", "claude-sonnet-4.6", "claude-sonnet-4-6")},
    {"id": "sonnet-4.5", "label": "Sonnet 4.5", "aliases": ("sonnet4.5", "claude-sonnet-4.5", "claude-sonnet-4-5")},
    {"id": "haiku-4.6", "label": "Haiku 4.6", "aliases": ("haiku4.6", "claude-haiku-4.6", "claude-haiku-4-6")},
    {"id": "haiku-4.5", "label": "Haiku 4.5", "aliases": ("haiku4.5", "claude-haiku-4.5", "claude-haiku-4-5")},
    {"id": "opus-5-thinking", "label": "Opus 5 Thinking", "aliases": ("opus5-thinking", "claude-opus-5-thinking")},
    {"id": "sonnet-4.6-thinking", "label": "Sonnet 4.6 Thinking", "aliases": ("sonnet-4.6-thinking",)},
)


def claude_labels() -> tuple[str, ...]:
    return tuple(str(item["label"]) for item in CLAUDE_MODELS)


def claude_line(sep: str = "  ·  ") -> str:
    return sep.join(claude_labels())


def resolve_claude_model(text: str) -> str | None:
    needle = (text or "").strip().lower().replace(" ", "")
    if not needle:
        return None
    for item in CLAUDE_MODELS:
        blob = [str(item["id"]), str(item["label"]).lower().replace(" ", "")]
        blob.extend(str(alias).lower().replace(" ", "") for alias in item["aliases"])  # type: ignore[union-attr]
        if needle in blob:
            return str(item["id"])
    return None
