"""Keyword classifier for MAXIMUM CORE breakout channels. One route wins; ties keep insertion order."""

from __future__ import annotations

from .blades import BLADE_SPECS
from .talk_fold import fold_talk

BLADE_IDS: tuple[str, ...] = tuple(spec["id"] for spec in BLADE_SPECS)


def classify(prompt: str, *, default: str = "REV") -> str:
    folded = fold_talk(prompt)
    return folded["blade"] or default
