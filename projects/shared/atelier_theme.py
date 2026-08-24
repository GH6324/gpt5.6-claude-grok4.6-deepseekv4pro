"""Cold-coffee chrome: cream paper, roast orange, ice teal.

Brand: 冷咖啡. Product: AI 破甲越狱.
"""

from __future__ import annotations

from math import cos, pi, sin
from typing import Callable

import tkinter as tk
import tkinter.font as tkfont


VOID = "#EFE6D6"
INK = "#2A1810"
PLATE = "#FFF8F0"
PLATE2 = "#F3E4D0"
GOLD = "#C45C14"
GOLD_HI = "#E07028"
GOLD_DIM = "#A36A3A"
ICE = "#1F6B66"
ICE_HI = "#2A8A84"
IVORY = "#2A1810"
MUTE = "#7A6554"
HAIR = "#E2D3C1"
CRIMSON = "#B33A28"
OK = "#C45C14"
ESPRESSO = "#2A1810"
CREAM = "#F7EFE3"


def pick_fonts(root: tk.Misc) -> dict[str, str]:
    have = set(tkfont.families(root))

    def choose(*names: str, fallback: str) -> str:
        for name in names:
            if name in have:
                return name
        return fallback

    return {
        "display": choose("Segoe UI Variable Display", "Segoe UI", "Microsoft YaHei UI", fallback="Segoe UI"),
        "cn": choose("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", fallback="Segoe UI"),
        "mono": choose("Cascadia Mono", "Cascadia Code", "Consolas", fallback="Courier New"),
    }


class GoldButton(tk.Frame):
    """kind: ghost | solid | tab. Solid = roast, tab active = ice teal."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        *,
        fonts: dict[str, str],
        kind: str = "ghost",
        px: int = 16,
        py: int = 8,
    ) -> None:
        super().__init__(master, bg=HAIR, highlightthickness=0, padx=1, pady=1)
        self.kind = kind
        self.command = command
        self.fonts = fonts
        self._active = False
        self.label = tk.Label(self, text=text, font=(fonts["cn"], 10), padx=px, pady=py, cursor="hand2")
        self.label.pack(fill="both", expand=True)
        self.label.bind("<Button-1>", lambda _e: self.command())
        self.label.bind("<Enter>", lambda _e: self._paint(hover=True))
        self.label.bind("<Leave>", lambda _e: self._paint(hover=False))
        self._paint()

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)

    def set_active(self, on: bool) -> None:
        self._active = on
        self._paint()

    def _paint(self, hover: bool = False) -> None:
        if self.kind == "solid":
            bg, fg = (GOLD_HI if hover else GOLD), "#FFF8F0"
        elif self.kind == "tab" and self._active:
            bg, fg = (ICE_HI if hover else ICE), "#FFF8F0"
        elif hover:
            bg, fg = PLATE2, GOLD
        else:
            bg, fg = PLATE, GOLD if self.kind == "tab" else IVORY
        self.label.configure(bg=bg, fg=fg)


def plate(parent: tk.Misc, **kwargs: object) -> tk.Frame:
    return tk.Frame(parent, bg=PLATE, highlightthickness=1, highlightbackground=HAIR, **kwargs)  # type: ignore[arg-type]


def hairline(parent: tk.Misc, **pack) -> tk.Frame:
    line = tk.Frame(parent, bg=GOLD, height=2)
    if pack:
        line.pack(**pack)
    return line


def draw_crest(canvas: tk.Canvas, width: int, height: int, *, ink: str = GOLD) -> None:
    canvas.delete("crest")
    cx, cy = width / 2, height / 2
    r = min(width, height) * 0.36
    pts = []
    for i in range(5):
        a = -pi / 2 + i * 2 * pi / 5
        pts.extend((cx + r * cos(a), cy + r * sin(a)))
    canvas.create_polygon(*pts, fill="#3A2216", outline=ink, width=2, tags="crest")
    hole = max(4.0, r * 0.22)
    canvas.create_oval(cx - hole, cy - hole, cx + hole, cy + hole, outline="#E8C9A0", width=2, tags="crest")
