"""Shared ColdBrew workbench UI for the four model adapters."""

from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable

from atelier_theme import (
    CRIMSON,
    GOLD,
    GOLD_HI,
    HAIR,
    ICE,
    INK,
    MUTE,
    PLATE,
    PLATE2,
    VOID,
    GoldButton,
    pick_fonts,
    plate,
)


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
    profile_names: Callable[[], list[str] | tuple[str, ...]],
    preview: Action,
    deploy: Action,
    verify: Action,
    restore: Action,
    export_template: Callable[[Path, str], dict[str, Any]],
    community: dict[str, str],
) -> int:
    window = tk.Tk()
    fonts = pick_fonts(window)
    window.title(f"冷咖啡 · {model} · Command Center")
    window.geometry("1220x820")
    window.minsize(980, 680)
    window.configure(bg=VOID)
    window.option_add("*Font", (fonts["cn"], 10))

    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Cold.TCombobox", fieldbackground=PLATE2, background=PLATE2, foreground=INK, arrowcolor=accent, borderwidth=0, padding=6)
    style.map("Cold.TCombobox", fieldbackground=[("readonly", PLATE2)], foreground=[("readonly", INK)])

    root = tk.Frame(window, bg=VOID)
    root.pack(fill="both", expand=True)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    sidebar = tk.Frame(root, bg="#0B1016", width=218, padx=16, pady=22)
    sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
    sidebar.grid_propagate(False)
    tk.Label(sidebar, text="冷咖啡", bg="#0B1016", fg=INK, font=(fonts["cn"], 17, "bold")).pack(anchor="w")
    tk.Label(sidebar, text="COLDBREW COMMAND CENTER", bg="#0B1016", fg=MUTE, font=(fonts["mono"], 8)).pack(anchor="w", pady=(3, 24))
    tk.Label(sidebar, text="MODEL SEAT", bg="#0B1016", fg=accent, font=(fonts["mono"], 9, "bold")).pack(anchor="w", pady=(0, 8))
    tk.Label(sidebar, text=model, bg="#0B1016", fg=INK, font=(fonts["cn"], 14, "bold")).pack(anchor="w")
    tk.Label(sidebar, text=subtitle, bg="#0B1016", fg=MUTE, justify="left", wraplength=170, font=(fonts["cn"], 9)).pack(anchor="w", pady=(6, 24))
    tk.Frame(sidebar, bg=HAIR, height=1).pack(fill="x", pady=(0, 17))

    state_var = tk.StringVar(value="READY")
    state_label = tk.Label(sidebar, textvariable=state_var, bg="#0B1016", fg=ICE, font=(fonts["mono"], 9, "bold"))
    state_label.pack(anchor="w")
    tk.Label(sidebar, text="本机执行 · 可恢复", bg="#0B1016", fg=MUTE, font=(fonts["cn"], 9)).pack(anchor="w", pady=(5, 20))

    community_frame = tk.Frame(sidebar, bg="#0B1016")
    community_frame.pack(side="bottom", fill="x")
    tk.Frame(community_frame, bg=HAIR, height=1).pack(fill="x", pady=(0, 10))
    tk.Label(community_frame, text="COMMUNITY", bg="#0B1016", fg=GOLD, font=(fonts["mono"], 8)).pack(anchor="w")
    for key, value in community.items():
        tk.Label(community_frame, text=f"{key}: {value}", bg="#0B1016", fg=MUTE, anchor="w", font=(fonts["mono"], 8)).pack(fill="x", pady=(5, 0))

    header = tk.Frame(root, bg="#0A0E13", height=58, padx=24)
    header.grid(row=0, column=1, sticky="ew")
    header.grid_propagate(False)
    tk.Label(header, text="WORKBENCH /", bg="#0A0E13", fg=GOLD, font=(fonts["mono"], 9, "bold")).pack(side="left", pady=18)
    tk.Label(header, text="MAXIMUM CORE", bg="#0A0E13", fg=INK, font=(fonts["mono"], 9)).pack(side="left", padx=(8, 0), pady=18)
    tk.Label(header, text="●  LOCAL", bg="#0A0E13", fg=ICE, font=(fonts["mono"], 9)).pack(side="right", pady=18)

    content = tk.Frame(root, bg=VOID, padx=24, pady=22)
    content.grid(row=1, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(5, weight=1)

    hero = tk.Frame(content, bg=PLATE, highlightthickness=1, highlightbackground=HAIR, padx=20, pady=18)
    hero.grid(row=0, column=0, sticky="ew")
    hero.grid_columnconfigure(0, weight=1)
    tk.Label(hero, text="MAXIMUM CORE / SESSION", bg=PLATE, fg=accent, font=(fonts["mono"], 9, "bold")).grid(row=0, column=0, sticky="w")
    tk.Label(hero, text=f"{model} · 可逆配置工作台", bg=PLATE, fg=INK, font=(fonts["cn"], 24, "bold")).grid(row=1, column=0, sticky="w", pady=(7, 3))
    tk.Label(hero, text="预览 → 执行 → 验证 → 恢复。所有步骤都写入活动记录。", bg=PLATE, fg=MUTE, font=(fonts["cn"], 10)).grid(row=2, column=0, sticky="w")
    tk.Label(hero, text="●", bg=PLATE, fg=accent, font=(fonts["cn"], 28)).grid(row=0, column=1, rowspan=3, padx=(28, 7))
    tk.Label(hero, text="ONLINE", bg=PLATE, fg=accent, font=(fonts["mono"], 9, "bold")).grid(row=0, column=2, rowspan=3, sticky="e")

    profile_panel = plate(content, padx=14, pady=11)
    profile_panel.grid(row=1, column=0, sticky="ew", pady=(12, 0))
    profile_panel.grid_columnconfigure(1, weight=1)
    tk.Label(profile_panel, text="PROFILE", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))
    names = list(profile_names())
    profile_var = tk.StringVar(value="max" if "max" in names else (names[0] if names else "max"))
    profile_box = ttk.Combobox(profile_panel, values=names, textvariable=profile_var, state="readonly", style="Cold.TCombobox", width=22)
    profile_box.grid(row=0, column=1, sticky="w")
    profile_desc = tk.Label(profile_panel, text="完整路由、连续上下文与直接交付链。", bg=PLATE, fg=MUTE, font=(fonts["cn"], 9))
    profile_desc.grid(row=0, column=2, sticky="e", padx=(12, 0))
    descriptions = {
        "max": "完整路由、连续上下文与直接交付链。",
        "max-breaker": "完整路由、连续上下文与直接交付链。",
        "builder": "实现、打包、测试和可复现交付。",
        "focused": "短链路执行，优先收敛到当前目标。",
        "research": "来源、证据、结论与未知项分层。",
        "creative": "保持角色、语气和长文本连续性。",
    }
    profile_box.bind("<<ComboboxSelected>>", lambda _event: profile_desc.configure(text=descriptions.get(profile_var.get(), "当前档位已准备")))

    core_panel = plate(content, padx=14, pady=11)
    core_panel.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    core_panel.grid_columnconfigure(1, weight=1)
    tk.Label(core_panel, text="CORE", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))
    tk.Label(core_panel, text="破甲 / 越狱 · MAXIMUM CORE 六层链路", bg=PLATE, fg=INK, font=(fonts["cn"], 10, "bold")).grid(row=0, column=1, sticky="w")
    tk.Label(core_panel, text="目标  →  路由  →  上下文  →  产物  →  验证  →  恢复", bg=PLATE, fg=ICE, font=(fonts["mono"], 9)).grid(row=0, column=2, sticky="e", padx=(12, 0))

    target_panel = plate(content, padx=14, pady=11)
    target_panel.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    target_panel.grid_columnconfigure(1, weight=1)
    tk.Label(target_panel, text="TARGET", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))
    home_var = tk.StringVar(value=str(resolve_layout(home).home))
    home_entry = tk.Entry(target_panel, textvariable=home_var, bg=PLATE2, fg=INK, insertbackground=accent, relief="flat", highlightthickness=1, highlightbackground=HAIR, highlightcolor=accent, font=(fonts["mono"], 9))
    home_entry.grid(row=0, column=1, sticky="ew", ipady=7)
    tk.Label(target_panel, text="自动恢复点已启用", bg=PLATE, fg=ICE, font=(fonts["cn"], 9)).grid(row=0, column=2, sticky="e", padx=(12, 0))

    actions = tk.Frame(content, bg=VOID)
    actions.grid(row=4, column=0, sticky="ew", pady=(14, 11))
    actions.grid_columnconfigure(6, weight=1)
    output = plate(content, padx=4, pady=4)
    output.grid(row=5, column=0, sticky="nsew")
    output.grid_rowconfigure(2, weight=1)
    output.grid_columnconfigure(0, weight=1)
    tk.Label(output, text="ACTIVITY / RESULT", bg=PLATE, fg=GOLD, font=(fonts["mono"], 9, "bold")).grid(row=0, column=0, sticky="w", padx=13, pady=(10, 0))
    tk.Frame(output, bg=HAIR, height=1).grid(row=1, column=0, sticky="ew", padx=13, pady=(8, 0))
    text = tk.Text(output, bg="#0E151C", fg=INK, insertbackground=accent, relief="flat", font=(fonts["mono"], 10), padx=13, pady=12, wrap="word", bd=0)
    text.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    text.tag_configure("ok", foreground=ICE)
    text.tag_configure("error", foreground=CRIMSON)

    action_widgets: list[GoldButton] = []

    def render(value: dict[str, Any], *, ok: bool = True) -> None:
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), "ok" if ok else "error")
        text.configure(state="disabled")

    def run(label: str, fn: Callable[[], dict[str, Any]]) -> None:
        state_var.set(f"RUNNING · {label}")
        state_label.configure(fg=GOLD_HI)
        for widget in action_widgets: widget.label.configure(state="disabled")

        def worker() -> None:
            try:
                value = fn()
                success = bool(value.get("ok", True))
                window.after(0, lambda: render(value, ok=success))
                window.after(0, lambda: state_var.set(("DONE · " if success else "CHECK · ") + label))
                window.after(0, lambda: state_label.configure(fg=ICE if success else CRIMSON))
            except Exception as exc:  # noqa: BLE001
                value = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
                window.after(0, lambda: render(value, ok=False))
                window.after(0, lambda: state_var.set("ERROR · " + label))
                window.after(0, lambda: state_label.configure(fg=CRIMSON))
            finally:
                window.after(0, lambda: [widget.label.configure(state="normal") for widget in action_widgets])

        threading.Thread(target=worker, daemon=True).start()

    def with_profile(fn: Action) -> Callable[[], dict[str, Any]]:
        return lambda: fn(Path(home_var.get()), profile_var.get())

    def add_button(label: str, command: Callable[[], None], *, primary: bool = False) -> None:
        widget = GoldButton(actions, label, command, fonts=fonts, kind="solid" if primary else "ghost", px=13, py=7)
        widget.pack(side="left", padx=(0, 7))
        action_widgets.append(widget)

    add_button("预览变更", lambda: run("PREVIEW", with_profile(preview)))
    add_button("一键部署", lambda: run("DEPLOY", with_profile(deploy)), primary=True)
    add_button("验证部署", lambda: run("VERIFY", lambda: verify(Path(home_var.get()))))
    add_button("完整恢复", lambda: run("RESTORE", lambda: restore(Path(home_var.get()))))
    add_button("导出模板", lambda: run("EXPORT", lambda: export_template(Path(home_var.get()) / "coldbrew-export", profile_var.get())))
    add_button("社群入口", lambda: render({"action": "community", "ok": True, **community}))
    tk.Label(content, text="Ctrl+P 预览   ·   Ctrl+D 部署   ·   Ctrl+V 验证   ·   Ctrl+R 恢复", bg=VOID, fg=MUTE, font=(fonts["mono"], 8)).grid(row=6, column=0, sticky="w")
    window.bind("<Control-p>", lambda _event: run("PREVIEW", with_profile(preview)))
    window.bind("<Control-d>", lambda _event: run("DEPLOY", with_profile(deploy)))
    window.bind("<Control-v>", lambda _event: run("VERIFY", lambda: verify(Path(home_var.get()))))
    window.bind("<Control-r>", lambda _event: run("RESTORE", lambda: restore(Path(home_var.get()))))
    home_entry.focus_set()
    window.mainloop()
    return 0
