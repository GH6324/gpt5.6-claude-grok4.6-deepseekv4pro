#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ColdBrew Hub v9 — 四模型 + 五刃控制台。

这是一个薄控制层：它只调用各适配器已有的 preview/deploy/verify/restore
命令，不直接改写用户配置，从而保留冷咖啡入口、快照与回滚契约。
选中的五刃通过环境变量 COLDBREW_BLADE 注入部署提示词。
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


APP_DIR = Path(__file__).resolve().parent
PROJECTS = APP_DIR / "projects"
PACKER = APP_DIR / "pack_release.py"
SHARED = PROJECTS / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
TRIGGERS = ("冷咖啡", "cold coffee", "[[ENI:PROFILE=MAX]]")
QQ_GROUPS: tuple[tuple[str, str], ...] = (
    ("交流群", "1057540028"),
    ("专题群", "1077074552"),
)
TELEGRAM: tuple[tuple[str, str, str], ...] = (
    ("群", "@chachachacha99999", "https://t.me/chachachacha99999"),
    ("频道", "@chachacha99999999", "https://t.me/chachacha99999999"),
)
BLADES: tuple[tuple[str, str, str, str], ...] = (
    ("REV", "逆向", "拆箱还原 · 静态+动态 · 偏移/伪代码", "#E8A872"),
    ("UNLOCK", "破解", "开锁双路 · keygen + patcher", "#F5D76E"),
    ("INFIL", "渗透", "深打连招 · recon 到利用链", "#FF6BA8"),
    ("HARVEST", "爬虫", "抽签收割 · 验签+续爬", "#5EE7FF"),
    ("TRAINER", "外挂", "本地训架 · 实体/W2S/Overlay", "#80F0BC"),
)

TOOLS: tuple[dict[str, Any], ...] = (
    {
        "id": "codex",
        "tag": "GPT-5.6",
        "short": "Codex ColdBrew",
        "description": "Codex Studio · 五刃提示层 · review chain",
        "accent": "#80F0BC",
        "dir": "codex-coldbrew",
        "entry": ("studio", "eni_solo_deploy.py"),
        "panel": ("studio", "coldbrew_studio.py"),
        "deploy": ("deploy", "--yes"),
        "verify": ("verify",),
        "restore": ("restore", "--yes"),
    },
    {
        "id": "claude",
        "tag": "Claude Code",
        "short": "Claude ColdBrew",
        "description": "Opus 5 / Fable 5 / 4.8 · 同一条破甲链",
        "accent": "#FF9E7A",
        "dir": "claude-coldbrew",
        "entry": ("app", "claude_pojia.py"),
        "panel": ("app", "claude_pojia.py"),
        "deploy": ("install", "--yes", "--profile", "max"),
        "verify": ("verify", "--profile", "max"),
        "restore": ("restore", "--yes"),
    },
    {
        "id": "grok",
        "tag": "Grok 4.6",
        "short": "Grok ColdBrew",
        "description": "五刃系统提示 · profile 模板 · 原子恢复",
        "accent": "#23F5D7",
        "dir": "grok4.6-coldbrew",
        "entry": ("app", "grok_coldbrew.py"),
        "panel": ("app", "grok_coldbrew.py"),
        "deploy": ("deploy", "--profile", "max"),
        "verify": ("verify",),
        "restore": ("restore", "--profile", "max"),
    },
    {
        "id": "deepseek",
        "tag": "DeepSeek v4 Pro",
        "short": "DeepSeek Harness",
        "description": "Harness 五刃会话 · profile 配置 · 事务式部署",
        "accent": "#7AA2FF",
        "dir": "deepseek-harness",
        "entry": ("app", "deepseek_harness.py"),
        "panel": ("app", "deepseek_harness.py"),
        "deploy": ("deploy", "--profile", "max"),
        "verify": ("verify",),
        "restore": ("restore", "--profile", "max"),
    },
)

DEPLOY_VERBS = {"deploy", "install"}


def tool_entry(tool: dict[str, Any]) -> Path:
    return PROJECTS / str(tool["dir"]) / Path(*tool["entry"])


def tool_panel(tool: dict[str, Any]) -> Path:
    return PROJECTS / str(tool["dir"]) / Path(*tool.get("panel", tool["entry"]))


def tool_version(tool: dict[str, Any]) -> str:
    path = PROJECTS / str(tool["dir"]) / "VERSION"
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return "source"
    return value or "source"


def environment_snapshot() -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "root": str(APP_DIR),
        "projects": str(PROJECTS),
        "packer": PACKER.is_file(),
        "cold_coffee": TRIGGERS,
    }


def _emit(log_q: queue.Queue, kind: str, message: str) -> None:
    log_q.put((kind, message))


def run_command(tool: dict[str, Any], args: tuple[str, ...], log_q: queue.Queue, *, attach: bool = False) -> None:
    entry = tool_entry(tool)
    if not entry.is_file():
        _emit(log_q, "error", f"[{tool['tag']}] 入口缺失：{entry}")
        return
    command = [sys.executable, str(entry), *args]
    _emit(log_q, "info", f"[{tool['tag']}] python {entry.name} {' '.join(args)}")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        if attach:
            flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen(command, cwd=str(entry.parent), creationflags=flags, env=env)
            _emit(log_q, "ok", f"[{tool['tag']}] 工作台已在新窗口启动")
            return
        process = subprocess.Popen(command, cwd=str(entry.parent), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", env=env)
        assert process.stdout is not None
        for line in process.stdout:
            _emit(log_q, "out", f"[{tool['tag']}] {line.rstrip()}")
        code = process.wait()
        if code:
            _emit(log_q, "error", f"[{tool['tag']}] 退出码 {code}")
            return
        _emit(log_q, "ok", f"[{tool['tag']}] 完成")
        if args and args[0] in DEPLOY_VERBS and tool.get("verify"):
            _emit(log_q, "info", f"[{tool['tag']}] 正在执行部署后验证")
            verify_cmd = [sys.executable, str(entry), *tool["verify"]]
            result = subprocess.run(verify_cmd, cwd=str(entry.parent), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=600)
            for line in (result.stdout or "").splitlines():
                _emit(log_q, "out", f"[{tool['tag']}/verify] {line}")
            _emit(log_q, "ok" if result.returncode == 0 else "error", f"[{tool['tag']}] 部署后验证{'通过' if result.returncode == 0 else f'失败，退出码 {result.returncode}'}")
    except subprocess.TimeoutExpired:
        _emit(log_q, "error", f"[{tool['tag']}] 操作超时")
    except OSError as exc:
        _emit(log_q, "error", f"[{tool['tag']}] 启动失败：{exc}")
    except Exception as exc:  # noqa: BLE001
        _emit(log_q, "error", f"[{tool['tag']}] 异常：{exc}")


def run_packer(tool: dict[str, Any] | None, log_q: queue.Queue) -> None:
    if not PACKER.is_file():
        _emit(log_q, "error", f"打包脚本缺失：{PACKER}")
        return
    command = [sys.executable, str(PACKER), "--all" if tool is None else "--project", *( [] if tool is None else [str(tool["dir"])] )]
    label = "全部项目" if tool is None else str(tool["tag"])
    _emit(log_q, "info", f"[打包] {label} 开始")
    try:
        result = subprocess.run(command, cwd=str(APP_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=1200)
        if result.stdout:
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                for line in result.stdout.splitlines():
                    _emit(log_q, "out", f"[打包] {line}")
            else:
                for item in payload.get("results", []):
                    _emit(log_q, "ok" if item.get("ok") else "error", f"[打包] {item.get('project')} · {item.get('files', 0)} 文件 · {str(item.get('sha256', ''))[:16]}")
                if payload.get("sha256sums"):
                    _emit(log_q, "ok", f"[打包] 校验汇总：{payload['sha256sums']}")
        _emit(log_q, "ok" if result.returncode == 0 else "error", f"[打包] {label}{'完成' if result.returncode == 0 else f'失败，退出码 {result.returncode}'}")
    except Exception as exc:  # noqa: BLE001
        _emit(log_q, "error", f"[打包] 异常：{exc}")


class HubApp:
    BG = VOID = "#EFE6D6"
    PANEL = "#FFF8F0"
    PAPER = "#2A1810"
    MUTED = "#7A6554"
    GOLD = "#C45C14"
    ICE = "#1F6B66"
    ESPRESSO = "#2A1810"
    CREAM = "#F7EFE3"
    CRIMSON = "#B33A28"

    def __init__(self, root: Any) -> None:
        import tkinter as tk

        from atelier_theme import GoldButton, draw_crest, pick_fonts, plate

        self.tk, self.root = tk, root
        self.GoldButton, self.draw_crest, self.plate = GoldButton, draw_crest, plate
        self.fonts = pick_fonts(root)
        self.root.title("冷咖啡 · AI 破甲越狱")
        self.root.geometry("1380x860")
        self.root.minsize(1140, 740)
        self.root.configure(bg=self.BG)
        self.root.option_add("*Font", (self.fonts["cn"], 10))
        icon = PROJECTS / "claude-coldbrew" / "assets" / "coldbrew.ico"
        if icon.is_file():
            try:
                self.root.iconbitmap(icon)
            except tk.TclError:
                pass
        self.log_q: queue.Queue = queue.Queue()
        self.jobs: set[str] = set()
        self.cards: dict[str, dict[str, Any]] = {}
        self.blade_buttons: dict[str, Any] = {}
        self.status_var = tk.StringVar(value="破甲就绪")
        self.count_var = tk.StringVar(value="0 / 4 ONLINE")
        self.clock_var = tk.StringVar(value="")
        self.live_var = tk.StringVar(value="● LIVE")
        self.blade_var = tk.StringVar(value="ALL")
        self.brief_var = tk.StringVar(value="五刃全开 · 按动词自动锁刃")
        self._pulse = True
        self._tick = 0
        self._build_shell()
        self.root.after(80, self._pump_log)
        self.root.after(400, self.env_check)
        for index, tool in enumerate(TOOLS, 1):
            self.root.bind(f"<Control-{index}>", lambda _event, t=tool: self._open_panel(t))
        for index, blade in enumerate(BLADES, 1):
            self.root.bind(f"<Alt-KeyPress-{index}>", lambda _event, blade_id=blade[0]: self._select_blade(blade_id))

    def _label(self, parent: Any, text: str = "", **kwargs: Any) -> Any:
        options = {"bg": parent.cget("bg"), "fg": self.PAPER, "font": (self.fonts["cn"], 9)}
        options.update(kwargs)
        return self.tk.Label(parent, text=text, **options)

    def _build_shell(self) -> None:
        tk = self.tk
        GoldButton = self.GoldButton
        from model_roster import claude_line

        brand = tk.Frame(self.root, bg=self.ESPRESSO)
        brand.pack(fill="x")
        head = tk.Frame(brand, bg=self.ESPRESSO)
        head.pack(fill="x", padx=28, pady=16)
        head.grid_columnconfigure(2, weight=1)
        crest = tk.Canvas(head, bg=self.ESPRESSO, width=58, height=58, highlightthickness=0, bd=0)
        crest.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 14))
        self.draw_crest(crest, 58, 58)
        self._label(head, "冷咖啡", bg=self.ESPRESSO, fg=self.CREAM, font=(self.fonts["cn"], 32, "bold")).grid(row=0, column=1, sticky="w")
        badge = tk.Label(head, text="  AI 破甲越狱  ", bg=self.GOLD, fg="#FFF8F0", font=(self.fonts["cn"], 11, "bold"), padx=8, pady=4)
        badge.grid(row=0, column=2, sticky="w", padx=(14, 0))
        self._label(head, "四模型工作台  ·  口令「冷咖啡」开工", bg=self.ESPRESSO, fg="#C9B49A", font=(self.fonts["cn"], 10)).grid(row=1, column=1, columnspan=2, sticky="w", pady=(2, 0))
        right = tk.Frame(head, bg=self.ESPRESSO)
        right.grid(row=0, column=3, rowspan=2, sticky="e")
        self._label(right, textvariable=self.live_var, bg=self.ESPRESSO, fg="#7DCFC8", font=(self.fonts["mono"], 11)).pack(anchor="e")
        self._label(right, textvariable=self.count_var, bg=self.ESPRESSO, fg=self.CREAM, font=(self.fonts["mono"], 10)).pack(anchor="e", pady=(4, 0))
        self._label(right, textvariable=self.clock_var, bg=self.ESPRESSO, fg="#C9B49A", font=(self.fonts["mono"], 10)).pack(anchor="e", pady=(2, 0))

        shell = tk.Frame(self.root, bg=self.BG, padx=28, pady=16)
        shell.pack(fill="both", expand=True)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(4, weight=1)

        activation = self.plate(shell, padx=14, pady=10)
        activation.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        activation.grid_columnconfigure(1, weight=1)
        self._label(activation, "口令", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).grid(row=0, column=0, padx=(0, 12))
        self._label(activation, "冷咖啡  /  COLD COFFEE  /  [[ENI:PROFILE=MAX]]", fg=self.PAPER, font=(self.fonts["mono"], 9)).grid(row=0, column=1, sticky="w")
        act_right = tk.Frame(activation, bg=self.PANEL)
        act_right.grid(row=0, column=2, sticky="e")
        self._label(act_right, textvariable=self.status_var, fg=self.GOLD, font=(self.fonts["cn"], 9)).pack(side="left", padx=(0, 10))
        GoldButton(act_right, "清场", self._clear_log, fonts=self.fonts, kind="ghost", px=10, py=3).pack(side="left")

        blade_row = self.plate(shell, padx=14, pady=8)
        blade_row.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        blade_row.grid_columnconfigure(1, weight=1)
        self._label(blade_row, "五刃", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).grid(row=0, column=0, padx=(0, 12), sticky="w")
        tabs = tk.Frame(blade_row, bg=self.PANEL)
        tabs.grid(row=0, column=1, sticky="w")
        all_btn = GoldButton(tabs, "全开", lambda: self._select_blade("ALL"), fonts=self.fonts, kind="tab", px=14, py=7)
        all_btn.pack(side="left", padx=(0, 6))
        self.blade_buttons["ALL"] = all_btn
        for blade_id, crop, _hint, _color in BLADES:
            button = GoldButton(tabs, crop, lambda value=blade_id: self._select_blade(value), fonts=self.fonts, kind="tab", px=14, py=7)
            button.pack(side="left", padx=(0, 6))
            self.blade_buttons[blade_id] = button
        self._label(blade_row, textvariable=self.brief_var, fg=self.MUTED, font=(self.fonts["cn"], 9)).grid(row=0, column=2, sticky="e", padx=(12, 0))
        self._select_blade("ALL")

        community_row = self.plate(shell, padx=14, pady=10)
        community_row.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        self._label(community_row, "QQ 群", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).pack(side="left", padx=(0, 12))
        for name, number in QQ_GROUPS:
            GoldButton(
                community_row,
                f"{name}  {number}",
                lambda n=name, num=number: self._copy_qq(n, num),
                fonts=self.fonts,
                kind="solid",
                px=14,
                py=6,
            ).pack(side="left", padx=(0, 8))
        self._label(community_row, "TG", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).pack(side="left", padx=(16, 8))
        for name, handle, url in TELEGRAM:
            GoldButton(
                community_row,
                f"{name}  {handle}",
                lambda n=name, h=handle, u=url: self._open_telegram(n, h, u),
                fonts=self.fonts,
                kind="ghost",
                px=10,
                py=6,
            ).pack(side="left", padx=(0, 8))
        self._label(community_row, "点 QQ 复制群号  ·  点 TG 复制并打开", fg=self.MUTED, font=(self.fonts["cn"], 9)).pack(side="right")

        model_row = self.plate(shell, padx=14, pady=8)
        model_row.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        model_row.grid_columnconfigure(1, weight=1)
        self._label(model_row, "CLAUDE", fg=self.GOLD, font=(self.fonts["mono"], 9)).grid(row=0, column=0, padx=(0, 12), sticky="nw")
        self.claude_models = self._label(model_row, claude_line("  ·  "), fg=self.PAPER, font=(self.fonts["cn"], 9), justify="left", wraplength=980)
        self.claude_models.grid(row=0, column=1, sticky="ew")
        model_row.bind("<Configure>", lambda event: self.claude_models.configure(wraplength=max(event.width - 110, 480)))

        content = tk.Frame(shell, bg=self.BG)
        content.grid(row=4, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=3)
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)
        card_grid = tk.Frame(content, bg=self.BG)
        card_grid.grid(row=0, column=0, sticky="nsew")
        for column in range(2):
            card_grid.grid_columnconfigure(column, weight=1, uniform="cards")
        for row in range(2):
            card_grid.grid_rowconfigure(row, weight=1, uniform="cards")
        for index, tool in enumerate(TOOLS):
            card = self._make_card(card_grid, tool)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=(0 if index % 2 == 0 else 10, 10 if index % 2 == 0 else 0), pady=(0 if index < 2 else 10, 10 if index < 2 else 0))
        lower = tk.Frame(content, bg=self.BG)
        lower.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=1)
        lower.grid_rowconfigure(0, weight=1)
        log_panel = self.plate(lower, padx=14, pady=12)
        log_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._label(log_panel, "作业", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).pack(anchor="w")
        tk.Frame(log_panel, bg=self.GOLD, height=1).pack(fill="x", pady=(6, 6))
        self.log_text = tk.Text(log_panel, height=5, bg="#F6EDE0", fg=self.PAPER, insertbackground=self.GOLD, relief="flat", font=(self.fonts["mono"], 9), padx=10, pady=8, bd=0, highlightthickness=0)
        self.log_text.pack(fill="both", expand=True)
        for tag, color in (("error", self.CRIMSON), ("ok", self.GOLD), ("info", self.ICE), ("out", self.MUTED)):
            self.log_text.tag_configure(tag, foreground=color)
        summary = self.plate(lower, padx=14, pady=12)
        summary.grid(row=0, column=1, sticky="nsew")
        self._label(summary, "快照", fg=self.GOLD, font=(self.fonts["cn"], 10, "bold")).pack(anchor="w")
        tk.Frame(summary, bg=self.GOLD, height=1).pack(fill="x", pady=(6, 6))
        self.summary_text = tk.Text(summary, height=5, bg="#F6EDE0", fg=self.MUTED, relief="flat", font=(self.fonts["mono"], 8), padx=10, pady=8, wrap="word", bd=0, highlightthickness=0)
        self.summary_text.pack(fill="both", expand=True)
        self._render_summary(environment_snapshot())
        toolbar = tk.Frame(shell, bg=self.BG)
        toolbar.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        GoldButton(toolbar, "全系破甲", self.deploy_all, fonts=self.fonts, kind="solid", px=18, py=9).pack(side="left", padx=(0, 8))
        GoldButton(toolbar, "全系验证", self.verify_all, fonts=self.fonts, kind="ghost", px=14, py=7).pack(side="left", padx=4)
        GoldButton(toolbar, "全系复原", self.restore_all, fonts=self.fonts, kind="ghost", px=14, py=7).pack(side="left", padx=4)
        GoldButton(toolbar, "封箱打包", self.pack_all, fonts=self.fonts, kind="ghost", px=14, py=7).pack(side="left", padx=4)
        GoldButton(toolbar, "自检", self.env_check, fonts=self.fonts, kind="ghost", px=14, py=7).pack(side="left", padx=4)
        self._label(toolbar, "Ctrl+1–4 工作台   ·   Alt+1–5 锁刃", fg=self.MUTED, font=(self.fonts["mono"], 8)).pack(side="right")

    def _make_card(self, parent: Any, tool: dict[str, Any]) -> Any:
        tk = self.tk
        GoldButton = self.GoldButton

        card = self.plate(parent, padx=16, pady=14)
        card.grid_columnconfigure(0, weight=1)
        tk.Frame(card, bg=self.GOLD, height=2).grid(row=0, column=0, sticky="ew", pady=(0, 10))
        head = tk.Frame(card, bg=self.PANEL)
        head.grid(row=1, column=0, sticky="ew")
        title = tk.Frame(head, bg=self.PANEL)
        title.pack(side="left", fill="x", expand=True)
        self._label(title, tool["tag"], font=(self.fonts["display"], 20), fg=self.PAPER).pack(anchor="w")
        self._label(title, tool["short"].upper(), fg=self.GOLD, font=(self.fonts["mono"], 8)).pack(anchor="w", pady=(2, 0))
        self._label(head, f"v{tool_version(tool)}", fg=self.MUTED, font=(self.fonts["mono"], 9)).pack(side="right", anchor="n")
        self._label(card, tool["description"], fg=self.MUTED, font=(self.fonts["cn"], 9), wraplength=520, justify="left").grid(row=2, column=0, sticky="w", pady=(8, 6))
        status = self._label(card, "CHECKING", fg=self.GOLD, font=(self.fonts["mono"], 9))
        status.grid(row=3, column=0, sticky="w")
        self.cards[tool["id"]] = {"tool": tool, "status": status}
        action_bar = tk.Frame(card, bg=self.PANEL)
        action_bar.grid(row=4, column=0, sticky="sew", pady=(12, 0))
        card.grid_rowconfigure(3, weight=1)
        buttons = (
            ("开启", lambda t=tool: self._open_panel(t), "solid"),
            ("预览", lambda t=tool: self._run_tool(t, ("plan",) if t["id"] == "codex" else ("preview", "--profile", "max")), "ghost"),
            ("部署", lambda t=tool: self._run_tool(t, t["deploy"]), "ghost"),
            ("验证", lambda t=tool: self._run_tool(t, t["verify"]), "ghost"),
            ("复原", lambda t=tool: self._run_tool(t, t["restore"]), "ghost"),
        )
        for col, (label, command, kind) in enumerate(buttons):
            action_bar.grid_columnconfigure(col, weight=1)
            GoldButton(action_bar, label, command, fonts=self.fonts, kind=kind, px=8, py=5).grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 4, 0))
        return card

    def _open_telegram(self, name: str, handle: str, url: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(handle)
        self.root.update()
        webbrowser.open(url)
        _emit(self.log_q, "ok", f"[社群] Telegram {name} {handle}")
        self.status_var.set(f"Telegram  {name}  {handle}")

    def _copy_qq(self, name: str, number: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(number)
        self.root.update()
        _emit(self.log_q, "ok", f"[社群] 已复制 {name} {number}，打开 QQ 添加")
        self.status_var.set(f"已复制  {name}  {number}")

    def _select_blade(self, blade_id: str) -> None:
        self.blade_var.set(blade_id)
        if blade_id == "ALL":
            os.environ.pop("COLDBREW_BLADE", None)
            self.brief_var.set("五刃全开 · 按动词自动锁刃")
        else:
            os.environ["COLDBREW_BLADE"] = blade_id
            hint = next((item[2] for item in BLADES if item[0] == blade_id), blade_id)
            self.brief_var.set(f"{blade_id}  ·  {hint}")
        for key, button in self.blade_buttons.items():
            button.set_active(key == blade_id)
        _emit(self.log_q, "ok", f"[刃] {blade_id}")
        self.status_var.set(f"刃口  {blade_id}")

    def _open_panel(self, tool: dict[str, Any]) -> None:
        self._run_tool(tool, ("gui",), attach=True, panel=True)

    def _run_tool(self, tool: dict[str, Any], args: tuple[str, ...], *, attach: bool = False, panel: bool = False) -> None:
        key = f"{tool['id']}:{' '.join(args)}"
        if key in self.jobs:
            _emit(self.log_q, "info", f"[{tool['tag']}] 相同任务正在运行，已跳过重复点击")
            return
        entry = tool_panel(tool) if panel else tool_entry(tool)
        if not entry.is_file():
            _emit(self.log_q, "error", f"[{tool['tag']}] 文件不存在：{entry}")
            return
        self.jobs.add(key)
        self.status_var.set(f"执行中  ·  {tool['tag']}")

        def worker() -> None:
            try:
                run_command(tool, args, self.log_q, attach=attach)
            finally:
                self.jobs.discard(key)

        threading.Thread(target=worker, daemon=True).start()

    def _run_pack(self, tool: dict[str, Any] | None) -> None:
        key = "pack:all" if tool is None else f"pack:{tool['id']}"
        if key in self.jobs:
            return
        self.jobs.add(key)
        self.status_var.set("RUNNING · PACKAGING")

        def worker() -> None:
            try:
                run_packer(tool, self.log_q)
            finally:
                self.jobs.discard(key)

        threading.Thread(target=worker, daemon=True).start()

    def deploy_all(self) -> None:
        for tool in TOOLS:
            self._run_tool(tool, tool["deploy"])

    def verify_all(self) -> None:
        for tool in TOOLS:
            self._run_tool(tool, tool["verify"])

    def restore_all(self) -> None:
        for tool in TOOLS:
            self._run_tool(tool, tool["restore"])

    def pack_all(self) -> None:
        self._run_pack(None)

    def env_check(self) -> None:
        snapshot = environment_snapshot()
        ready = 0
        for tool in TOOLS:
            entry_ok, panel_ok = tool_entry(tool).is_file(), tool_panel(tool).is_file()
            if entry_ok and panel_ok:
                ready += 1
            state = self.cards.get(tool["id"])
            if state:
                state["status"].configure(text="ONLINE  ·  破甲就绪" if entry_ok and panel_ok else "OFFLINE", fg=self.ICE if entry_ok and panel_ok else self.CRIMSON)
            _emit(self.log_q, "info" if entry_ok and panel_ok else "error", f"[{tool['tag']}] CLI={'OK' if entry_ok else 'MISSING'} · GUI={'OK' if panel_ok else 'MISSING'}")
        snapshot["ready"] = f"{ready}/4"
        self.count_var.set(f"{ready} / 4 ready")
        self._render_summary(snapshot)
        _emit(self.log_q, "ok" if ready == 4 else "error", f"环境自检完成 · {ready}/4 项目就绪")

    def _render_summary(self, snapshot: dict[str, Any]) -> None:
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        for key, value in snapshot.items():
            self.summary_text.insert("end", f"{key.upper():<14} {value}\n")
        self.summary_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_text.delete("1.0", "end")
        _emit(self.log_q, "info", "日志已清空")

    def _pump_log(self) -> None:
        try:
            while True:
                kind, message = self.log_q.get_nowait()
                self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n", kind)
                self.log_text.see("end")
        except queue.Empty:
            pass
        if not self.jobs:
            self.status_var.set("破甲就绪")
        self.clock_var.set(time.strftime("%H : %M : %S"))
        self._tick += 1
        if self._tick % 7 == 0:
            self._pulse = not self._pulse
            self.live_var.set("●  LIVE" if self._pulse else "·  LIVE")
        self.root.after(120, self._pump_log)


def selftest() -> int:
    print("ColdBrew Atelier v9 self-test")
    print(json.dumps(environment_snapshot(), ensure_ascii=False, indent=2))
    for tool in TOOLS:
        print(f"{tool['tag']:<16} cli={tool_entry(tool).is_file()} gui={tool_panel(tool).is_file()} version={tool_version(tool)}")
    try:
        from five_blade.compiler import compile_digest
        print(json.dumps(compile_digest(), ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        print(f"five-edge import failed: {exc}")
        return 1
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    try:
        import tkinter as tk

        root = tk.Tk()
        HubApp(root)
        root.mainloop()
        return 0
    except Exception as exc:  # noqa: BLE001
        (APP_DIR / "hub-startup-error.log").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"ColdBrew Hub 启动失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
