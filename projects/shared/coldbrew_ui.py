"""Shared ColdBrew Atelier workbench UI."""

from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable

from atelier_theme import GOLD, GOLD_HI, HAIR, IVORY, MUTE, PLATE, VOID, GoldButton, pick_fonts, plate


Action = Callable[..., dict[str, Any]]


def _default_blades() -> tuple[tuple[str, str], ...]:
    try:
        from five_blade.blades import BLADE_SPECS
    except ImportError:
        return (("REV", "逆向"), ("UNLOCK", "破解"), ("INFIL", "渗透"), ("HARVEST", "爬虫"), ("TRAINER", "外挂"))
    return tuple((spec["id"], spec["crop"]) for spec in BLADE_SPECS)


def launch_shared_gui(
    *,
    title: str,
    model: str,
    subtitle: str,
    accent: str,
    home: Path | None,
    resolve_layout: Callable[[Path | None], Any],
    profile_names: Callable[[], list[str]],
    preview: Action,
    deploy: Action,
    verify: Action,
    restore: Action,
    export_template: Callable[[Path, str], dict[str, Any]],
    community: dict[str, str],
) -> int:
    window = tk.Tk()
    fonts = pick_fonts(window)
    window.title(f"{model}  ·  ATELIER")
    window.geometry("1240x840")
    window.minsize(1040, 700)
    window.configure(bg=VOID)
    window.option_add("*Font", (fonts["cn"], 10))

    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Atelier.TCombobox", fieldbackground=PLATE, background=PLATE, foreground=IVORY, arrowcolor=GOLD)
    style.map("Atelier.TCombobox", fieldbackground=[("readonly", PLATE)], foreground=[("readonly", IVORY)])

    root = tk.Frame(window, bg=VOID, padx=28, pady=22)
    root.pack(fill="both", expand=True)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(4, weight=1)

    header = tk.Frame(root, bg=VOID)
    header.grid(row=0, column=0, sticky="ew")
    tk.Frame(header, bg=GOLD, height=2).pack(fill="x")
    top = tk.Frame(header, bg=VOID)
    top.pack(fill="x", pady=14)
    left = tk.Frame(top, bg=VOID)
    left.pack(side="left")
    tk.Label(left, text="ATELIER  WORKBENCH", bg=VOID, fg=GOLD, font=(fonts["mono"], 9)).pack(anchor="w")
    tk.Label(left, text=model, bg=VOID, fg=IVORY, font=(fonts["display"], 28)).pack(anchor="w", pady=(4, 0))
    tk.Label(left, text=subtitle, bg=VOID, fg=MUTE, font=(fonts["cn"], 11)).pack(anchor="w", pady=(4, 0))
    badge = tk.Label(top, text="●  ONLINE", bg=VOID, fg=GOLD, font=(fonts["mono"], 11))
    badge.pack(side="right", anchor="n", pady=12)
    tk.Frame(header, bg=GOLD, height=2).pack(fill="x")

    activation = plate(root, padx=16, pady=11)
    activation.grid(row=1, column=0, sticky="ew", pady=(16, 10))
    tk.Label(activation, text="ENTRY", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9)).pack(side="left", padx=(0, 14))
    tk.Label(activation, text="冷咖啡  /  COLD COFFEE  /  [[ENI:PROFILE=MAX]]", bg=PLATE, fg=IVORY, font=(fonts["mono"], 9)).pack(side="left")

    blades = _default_blades()
    blade_var = tk.StringVar(value=os.environ.get("COLDBREW_BLADE") or "ALL")
    blade_bar = plate(root, padx=14, pady=10)
    blade_bar.grid(row=2, column=0, sticky="ew", pady=(0, 10))
    tk.Label(blade_bar, text="BLADES", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9)).pack(side="left", padx=(0, 12))
    tab_buttons: dict[str, GoldButton] = {}

    def _blade_briefing(blade_id: str) -> str:
        notes = {
            "ALL": "五刃全开 · 按动词自动锁刃",
            "REV": "逆向 · 静态+动态 · 伪代码 / 偏移 / 还原代码",
            "UNLOCK": "破解 · keygen + patcher",
            "INFIL": "渗透 · recon → hunt → chain",
            "HARVEST": "爬虫 · 验签 + 断点续爬",
            "TRAINER": "外挂 · 实体 / W2S / Overlay",
        }
        return notes.get(blade_id, notes["ALL"])

    briefing = tk.Label(blade_bar, text=_blade_briefing(blade_var.get()), bg=PLATE, fg=MUTE, font=(fonts["cn"], 9))

    def _select_blade(blade_id: str) -> None:
        blade_var.set(blade_id)
        if blade_id == "ALL":
            os.environ.pop("COLDBREW_BLADE", None)
        else:
            os.environ["COLDBREW_BLADE"] = blade_id
        briefing.configure(text=_blade_briefing(blade_id))
        for key, button in tab_buttons.items():
            button.set_active(key == blade_id)

    for blade_id, crop in (("ALL", "全开"), *blades):
        button = GoldButton(blade_bar, crop, lambda value=blade_id: _select_blade(value), fonts=fonts, kind="tab", px=12, py=5)
        button.pack(side="left", padx=(0, 8))
        tab_buttons[blade_id] = button
    briefing.pack(side="right")
    _select_blade(blade_var.get() if blade_var.get() in tab_buttons else "ALL")

    settings = plate(root, padx=16, pady=14)
    settings.grid(row=3, column=0, sticky="ew")
    settings.grid_columnconfigure(1, weight=1)
    tk.Label(settings, text="部署目录", bg=PLATE, fg=MUTE, font=(fonts["cn"], 9)).grid(row=0, column=0, sticky="w", padx=(0, 10))
    home_var = tk.StringVar(value=str(resolve_layout(home).home))
    home_entry = tk.Entry(settings, textvariable=home_var, bg="#F0F5FB", fg=IVORY, insertbackground=GOLD, relief="flat", highlightthickness=1, highlightbackground=HAIR, highlightcolor=GOLD, font=(fonts["mono"], 9))
    home_entry.grid(row=0, column=1, sticky="ew", ipady=8)
    tk.Label(settings, text="配置", bg=PLATE, fg=MUTE).grid(row=0, column=2, sticky="w", padx=(16, 8))
    profile_var = tk.StringVar(value="max")
    profiles = profile_names()
    if "max" not in profiles and profiles:
        profile_var.set(profiles[0])
    ttk.Combobox(settings, values=profiles, textvariable=profile_var, state="readonly", width=15, style="Atelier.TCombobox").grid(row=0, column=3, sticky="e")

    body = tk.Frame(root, bg=VOID)
    body.grid(row=4, column=0, sticky="nsew", pady=(14, 0))
    body.grid_columnconfigure(0, weight=1)
    body.grid_rowconfigure(1, weight=1)

    actions = tk.Frame(body, bg=VOID)
    actions.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    state_var = tk.StringVar(value="候命")
    tk.Label(actions, textvariable=state_var, bg=VOID, fg=MUTE, font=(fonts["mono"], 9)).pack(side="right")

    output_frame = plate(body, padx=4, pady=4)
    output_frame.grid(row=1, column=0, sticky="nsew")
    output_frame.grid_rowconfigure(2, weight=1)
    output_frame.grid_columnconfigure(0, weight=1)
    tk.Label(output_frame, text="OPERATIONS", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9)).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
    tk.Frame(output_frame, bg=GOLD, height=1).grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 0))
    output = tk.Text(output_frame, bg="#F0F5FB", fg=IVORY, insertbackground=GOLD, relief="flat", font=(fonts["mono"], 10), padx=15, pady=14, wrap="word", bd=0, highlightthickness=0)
    output.grid(row=2, column=0, sticky="nsew", padx=12, pady=10)
    output.tag_configure("ok", foreground=GOLD)
    output.tag_configure("error", foreground="#B23B2A")

    def render(value: dict[str, Any], *, ok: bool = True) -> None:
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), "ok" if ok else "error")
        output.configure(state="disabled")
        badge.configure(text="●  ONLINE" if ok else "●  CHECK", fg=GOLD if ok else "#B23B2A")

    action_widgets: list[GoldButton] = []

    def run(label: str, fn: Callable[[], dict[str, Any]]) -> None:
        state_var.set(f"执行  ·  {label}")
        badge.configure(text="●  RUNNING", fg=GOLD_HI)
        for child in action_widgets:
            child.label.configure(state="disabled")

        def worker() -> None:
            try:
                value = fn()
                ok = bool(value.get("ok", True))
                window.after(0, lambda: render(value, ok=ok))
                window.after(0, lambda: state_var.set(("完成  ·  " if ok else "受阻  ·  ") + label))
            except Exception as exc:  # noqa: BLE001
                value = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
                window.after(0, lambda: render(value, ok=False))
                window.after(0, lambda: state_var.set("异常  ·  " + label))
            finally:
                window.after(0, lambda: [child.label.configure(state="normal") for child in action_widgets])

        threading.Thread(target=worker, daemon=True).start()

    def with_profile(fn: Action) -> Callable[[], dict[str, Any]]:
        return lambda: fn(Path(home_var.get()), profile_var.get())

    def add_button(label: str, command: Callable[[], None], *, primary: bool = False) -> None:
        widget = GoldButton(actions, label, command, fonts=fonts, kind="solid" if primary else "ghost", px=14, py=8)
        widget.pack(side="left", padx=(0, 8))
        action_widgets.append(widget)

    add_button("预览变更", lambda: run("预览", with_profile(preview)))
    add_button("一键部署", lambda: run("部署", with_profile(deploy)), primary=True)
    add_button("验证部署", lambda: run("验证", lambda: verify(Path(home_var.get()))))
    add_button("完整复原", lambda: run("恢复", lambda: restore(Path(home_var.get()))))
    add_button("导出模板", lambda: run("导出", lambda: export_template(Path(home_var.get()) / "coldbrew-export", profile_var.get())))
    add_button("社区入口", lambda: render({"action": "community", "ok": True, **community}))

    tk.Label(root, text="Ctrl+P 预览   ·   Ctrl+D 部署   ·   Ctrl+V 验证   ·   Ctrl+R 复原", bg=VOID, fg=MUTE, font=(fonts["mono"], 8)).grid(row=5, column=0, sticky="w", pady=(10, 0))
    window.bind("<Control-p>", lambda _event: run("预览", with_profile(preview)))
    window.bind("<Control-d>", lambda _event: run("部署", with_profile(deploy)))
    window.bind("<Control-v>", lambda _event: run("验证", lambda: verify(Path(home_var.get()))))
    window.bind("<Control-r>", lambda _event: run("恢复", lambda: restore(Path(home_var.get()))))
    home_entry.focus_set()
    window.mainloop()
    return 0
