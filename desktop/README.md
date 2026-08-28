# 冷咖啡 · 一键破甲越狱（原生窗口）

产品名就是 **冷咖啡 · 一键破甲越狱**。开场是锁盘被五刃劈开。按钮叫一键破甲。

这一目录是 GitHub 仓里的 Electron 壳。四个模型适配器在上一级 `projects/`。窗口壳、开场、图标、挂钩加厚都是为本仓新写的。

口令「冷咖啡」。QQ 交流群 `1057540028` · 专题群 `1077074552`。

## 它干什么

| 你点 | 软件交出来 |
| --- | --- |
| 开场 | 原创 4.8 秒破甲动画，然后进无框主窗 |
| 四个模型 | GPT-5.6 / Codex、Claude Code、Grok 4.6、DeepSeek v4 Pro |
| 五刃 | 逆向 / 破解 / 渗透 / 爬虫 / 外挂，部署时写入 `COLDBREW_BLADE` |
| 全系破甲 | 四个模型适配器 deploy，再给 Codex 加厚挂钩 |
| 完整验收 | 适配器 verify + 静态挂钩体检 + 尝试连 Codex Desktop |
| 全系复原 | 各席自己的 restore 契约，部署后你改过的文件跟适配器规则走 |
| 环境扫描 | Python / Node / Git / jadx / frida / adb |
| 选目录 | 手动指定含 `config.toml` 的 Codex 家 |
| 社群 | 一点复制 QQ 群号 |

没有卡密门。公开发 GitHub 直接用。

## Codex 挂钩加厚（相对只挂一份 MD 的桌面壳）

部署 Codex 之后，软件会再写一层：

- `model_instructions_file` 指到**现场活着的** `eni-jailbreak-*.md`（有文件才挂，不留死文件）
- `approval_policy = "never"`
- `sandbox_mode = "danger-full-access"`
- `[desktop] localeOverride = "zh-CN"`
- **不禁用** `hooks.json`。UserPromptSubmit 那条自动路由继续每轮回灌

所以它比「只拷提示词、把别人的 hooks 整份改名 disabled」更深：指令活挂钩 + 审批/沙箱写进配置 + hook 占住压缩后的回合。

## 运行

Windows 10 / 11 和 macOS 12+。需要本机 **Node.js** 和 **Python 3.10+**。

```bash
cd desktop
npm install
npm start
```

Windows 双击 `start.bat`。Mac 双击仓库根目录 `打开冷咖啡.command` 或 `desktop/start.sh`。

先开一次 Codex，让 `~/.codex/config.toml` 出现，再点一键破甲。

打 dmg / portable：`npm run pack:mac`（在苹果机或 GitHub Actions）· `npm run pack:win`

## 目录

```
src/            原创 Electron 壳
src/splash/     开场
src/renderer/   主台
src/lib/        调度、体检、挂钩加厚、Desktop 联机
上一级 projects/  四个模型适配器
```

## 许可

`LICENSE`（冷咖啡社区许可）。禁止倒卖、禁止闭源衍生。

不要把本机密钥、卡密、快照推进公开仓库。
