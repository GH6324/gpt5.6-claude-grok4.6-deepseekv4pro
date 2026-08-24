"""Ice-white + navy chrome for ColdBrew Atelier.

Tk widgets only.  Adapters keep their own preview/deploy contracts.
"""

from __future__ import annotations

from typing import Callable

import tkinter as tk
import tkinter.font as tkfont


VOID = "#F4F7FB"
INK = "#FFFFFF"
PLATE = "#FFFFFF"
PLATE2 = "#E8F1FB"
GOLD = "#1F5EBA"
GOLD_HI = "#3B82F6"
GOLD_DIM = "#8DA9D4"
IVORY = "#17325A"
MUTE = "#5C738C"
HAIR = "#C5D6EA"
CRIMSON = "#C4473A"
OK = "#1F5EBA"


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
    """Hairline navy control. kind: ghost | solid | tab."""

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
        self.label = tk.Label(self, text=text, font=(fonts["cn"], 9), padx=px, pady=py, cursor="hand2")
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
        if self.kind == "solid" or (self.kind == "tab" and self._active):
            bg, fg = (GOLD_HI if hover else GOLD), "#FFFFFF"
        elif hover:
            bg, fg = PLATE2, GOLD
        else:
            bg, fg = PLATE, GOLD if self.kind == "tab" else IVORY
        self.label.configure(bg=bg, fg=fg)


def plate(parent: tk.Misc, **kwargs: object) -> tk.Frame:
    return tk.Frame(parent, bg=PLATE, highlightthickness=1, highlightbackground=HAIR, **kwargs)  # type: ignore[arg-type]


def hairline(parent: tk.Misc, **pack) -> tk.Frame:
    line = tk.Frame(parent, bg=GOLD, height=1)
    if pack:
        line.pack(**pack)
    return line


def draw_crest(canvas: tk.Canvas, width: int, height: int) -> None:
    canvas.delete("crest")
    cx, cy = width / 2, height / 2
    r = min(width, height) * 0.34
    pts = []
    for i in range(5):
        from math import cos, pi, sin

        a = -pi / 2 + i * 2 * pi / 5
        pts.extend((cx + r * cos(a), cy + r * sin(a)))
    canvas.create_polygon(*pts, fill="", outline=GOLD, width=2, tags="crest")
    hole = max(4.0, r * 0.22)
    ring = r * 1.18
    canvas.create_oval(cx - hole, cy - hole, cx + hole, cy + hole, outline=GOLD_HI, tags="crest")
    canvas.create_oval(cx - ring, cy - ring, cx + ring, cy + ring, outline=GOLD_DIM, tags="crest")
