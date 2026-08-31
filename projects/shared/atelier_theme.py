"""ColdBrew visual system shared by the model workbenches."""

from __future__ import annotations

from math import cos, pi, sin
from typing import Callable

import tkinter as tk
import tkinter.font as tkfont


# Graphite workspace with warm orange, teal, blue and yellow state accents.
VOID = "#0D1117"
INK = "#EDF3F5"
PLATE = "#151E28"
PLATE2 = "#1A2531"
GOLD = "#FF8F5A"
GOLD_HI = "#FFB07E"
GOLD_DIM = "#B9694B"
ICE = "#57D8C7"
ICE_HI = "#7AE8DA"
IVORY = "#EDF3F5"
MUTE = "#8FA2AD"
HAIR = "#273542"
CRIMSON = "#F06C6C"
OK = "#57D8C7"
ESPRESSO = "#0A0E13"
CREAM = "#EDF3F5"


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
    """Small themed button used by all model adapters."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        *,
        fonts: dict[str, str],
        kind: str = "ghost",
        px: int = 14,
        py: int = 7,
    ) -> None:
        super().__init__(master, bg=HAIR, highlightthickness=0, padx=1, pady=1)
        self.kind = kind
        self.command = command
        self.fonts = fonts
        self._active = False
        self.label = tk.Label(self, text=text, font=(fonts["cn"], 10), padx=px, pady=py, cursor="hand2")
        self.label.pack(fill="both", expand=True)
        self.label.bind("<Button-1>", lambda _event: self.command())
        self.label.bind("<Enter>", lambda _event: self._paint(hover=True))
        self.label.bind("<Leave>", lambda _event: self._paint(hover=False))
        self._paint()

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)

    def set_active(self, on: bool) -> None:
        self._active = on
        self._paint()

    def _paint(self, hover: bool = False) -> None:
        if self.kind == "solid":
            bg, fg = (GOLD_HI if hover else GOLD), "#111820"
        elif self.kind == "tab" and self._active:
            bg, fg = (ICE_HI if hover else ICE), "#0D1719"
        elif hover:
            bg, fg = PLATE2, INK
        else:
            bg, fg = PLATE, GOLD if self.kind == "tab" else MUTE
        self.label.configure(bg=bg, fg=fg)


def plate(parent: tk.Misc, **kwargs: object) -> tk.Frame:
    return tk.Frame(parent, bg=PLATE, highlightthickness=1, highlightbackground=HAIR, **kwargs)  # type: ignore[arg-type]


def hairline(parent: tk.Misc, **pack: object) -> tk.Frame:
    line = tk.Frame(parent, bg=GOLD, height=1)
    if pack:
        line.pack(**pack)
    return line


def draw_crest(canvas: tk.Canvas, width: int, height: int, *, ink: str = GOLD) -> None:
    canvas.delete("crest")
    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.36
    points: list[float] = []
    for index in range(5):
        angle = -pi / 2 + index * 2 * pi / 5
        points.extend((cx + radius * cos(angle), cy + radius * sin(angle)))
    canvas.create_polygon(*points, fill=PLATE2, outline=ink, width=2, tags="crest")
    hole = max(4.0, radius * 0.22)
    canvas.create_oval(cx - hole, cy - hole, cx + hole, cy + hole, outline=GOLD_HI, width=2, tags="crest")
