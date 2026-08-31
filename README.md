<div align="center">

<img src="docs/images/hero-v11.svg" width="940" alt="冷咖啡 ColdBrew Command Center" />

# 冷咖啡 · ColdBrew Command Center

**把目标、路由、产物、验证和恢复，收进一条可继续的工作链。**

<p>
  <a href="README.md"><img src="https://img.shields.io/badge/中文-当前-ff8f5a?style=for-the-badge&labelColor=0d1117" alt="中文" /></a>
  <a href="README_EN.md"><img src="https://img.shields.io/badge/English-Switch-57d8c7?style=for-the-badge&labelColor=0d1117" alt="English" /></a>
  <a href="https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro/stargazers"><img src="https://img.shields.io/github/stars/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro?style=for-the-badge&color=f4d06f&labelColor=0d1117&logo=github&logoColor=white" alt="GitHub stars" /></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Windows-10%2F11-7aa2ff?style=flat-square&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/macOS-12%2B-b9c7cc?style=flat-square&logo=apple&logoColor=0d1117" alt="macOS" />
  <img src="https://img.shields.io/badge/Linux-x64-57d8c7?style=flat-square&logo=linux&logoColor=0d1117" alt="Linux" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-f4d06f?style=flat-square&logo=python&logoColor=0d1117" alt="Python" />
  <img src="https://img.shields.io/badge/Electron-35-ff8f5a?style=flat-square&logo=electron&logoColor=0d1117" alt="Electron" />
</p>

</div>

---

## 这是什么

冷咖啡是一个本地优先的多模型工作台：Electron 提供统一桌面界面，Python 适配器负责每个模型的预览、部署、验证和恢复。四个模型共用一套操作语言，切换越狱档位后，目标会沿着同一个会话状态继续。

<div align="center">
  <img src="docs/images/window-v11.svg" width="940" alt="ColdBrew Command Center 工作台" />
</div>

### MAXIMUM CORE

MAX 档位把一次任务拆成六个连续层：

| 层 | 工作内容 |
| --- | --- |
| **OBJECTIVE** | 锁定原始目标、语言、格式与完成判据 |
| **ROUTE** | 选择唯一主路由，显示阶段顺序与当前执行链 |
| **CONTEXT** | 跨重试、上下文压缩和工具切换保留任务胶囊 |
| **ARTIFACT** | 在当前执行窗口产出代码、文档、配置或脚本 |
| **VERIFY** | 运行测试、哈希、状态检查和桌面验收 |
| **RECOVERY** | 保存恢复点、变更清单和可继续的下一步 |

工作台会把 `profile / target / stage` 一起写入执行上下文；再次打开软件时，先从最近一次已验证结果接着走。

---

## 四个模型席位

| 席位 | 目录 | 入口 | 适合的工作 |
| --- | --- | --- | --- |
| **GPT-5.6 / Codex** | `projects/codex-coldbrew` | `studio/eni_solo_deploy.py` | 指令层、工具桥、完整交付链 |
| **Claude Code** | `projects/claude-coldbrew` | `app/claude_pojia.py` | 规则层、配置事务、长会话 |
| **Grok 4.6** | `projects/grok4.6-coldbrew` | `app/grok_coldbrew.py` | 实时信息流与可续配置 |
| **DeepSeek v4 Pro** | `projects/deepseek-harness` | `app/deepseek_harness.py` | Harness 会话与模板导出 |

每个席位都提供：

- 预览：只读生成变更计划
- 部署：原子写入并建立恢复点
- 验证：检查状态、哈希和适配器结果
- 恢复：按清单恢复原始文件，保留用户后来产生的漂移

<div align="center">
  <img src="docs/images/card-codex-coldbrew.png" width="220" alt="Codex ColdBrew" />
  <img src="docs/images/card-claude-coldbrew.png" width="220" alt="Claude ColdBrew" />
  <img src="docs/images/card-grok4.6-coldbrew.png" width="220" alt="Grok ColdBrew" />
  <img src="docs/images/card-deepseek-harness.png" width="220" alt="DeepSeek Harness" />
</div>

---

## 破甲执行链

新版产品界面只展示破甲与越狱主线：每个任务都沿着六个阶段推进，模型适配器负责把阶段落到本机文件与会话配置。

| 阶段 | 交付形状 |
| --- | --- |
| **目标** | 锁定用户原句、对象、格式与完成判据 |
| **路由** | 选出唯一执行路径并显示当前步骤 |
| **上下文** | 保留档位、目标目录、已完成动作和待办项 |
| **产物** | 直接生成代码、配置、脚本、文档或模板 |
| **验证** | 运行检查、测试、哈希和桌面验收 |
| **恢复** | 保存原始快照、变更清单与下一次继续点 |

<div align="center">
  <img src="docs/images/workbench-v9.svg" width="940" alt="ColdBrew 破甲执行链" />
</div>

---

## 快速开始

### Electron 工作台（推荐）

```powershell
git clone https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro.git
cd gpt5.6-claude-grok4.6-deepseekv4pro/desktop
npm install
npm start
```

Windows 也可以双击 `desktop/start.bat`；macOS/Linux 对应 `desktop/start.sh`。打包命令：

```powershell
npm run pack:win
npm run pack:mac
npm run pack:linux
```

### Python Hub

```powershell
cd gpt5.6-claude-grok4.6-deepseekv4pro
python coldbrew_hub.py
```

启动后按这个顺序操作：

1. 在 **PROFILE** 选择 `MAX / 全开`、`FOCUS / 聚焦`、`BUILDER / 构建`、`RESEARCH / 研究` 或 `CREATIVE / 创作`。
2. 在 **BREAK / JAILBREAK** 区选择越狱档位。
3. 选择目标目录，先点 **预览** 查看变更。
4. 点 **一键启动 MAX** 或单独部署某个模型。
5. 在 **活动流** 查看阶段、结果和恢复点。

---

## 社群入口

社群宣传和入口继续保留。点击桌面工作台中的按钮可以复制群号或打开 Telegram；二维码文件位于 `docs/images/`。

<div align="center">
  <table>
    <tr>
      <td align="center"><img src="docs/images/qq-group-1-card.png" width="300" alt="QQ 交流群 1057540028" /><br /><strong>QQ 交流群</strong><br /><code>1057540028</code></td>
      <td align="center"><img src="docs/images/qq-group-2-card.png" width="300" alt="QQ 专题群 1077074552" /><br /><strong>QQ 专题群</strong><br /><code>1077074552</code></td>
    </tr>
  </table>
</div>

| 平台 | 入口 |
| --- | --- |
| Telegram 群 | [@chachachacha99999](https://t.me/chachachacha99999) |
| Telegram 频道 | [@chachachacha99999999](https://t.me/chachachacha99999999) |
| QQ 交流群 | `1057540028` |
| QQ 专题群 | `1077074552` |

<div align="center">
  <img src="docs/images/telegram-group-v2.png" width="280" alt="Telegram 群" />
  <img src="docs/images/telegram-channel-v2.png" width="280" alt="Telegram 频道" />
</div>

---

## 项目结构

```text
.
├─ desktop/                       Electron 35 桌面壳
│  └─ src/
│     ├─ main.js                  IPC、窗口与执行编排
│     ├─ renderer/                Command Center UI
│     └─ lib/                     目录发现、适配器与恢复清单
├─ projects/
│  ├─ codex-coldbrew/             GPT-5.6 / Codex
│  ├─ claude-coldbrew/            Claude Code
│  ├─ grok4.6-coldbrew/           Grok 4.6
│  ├─ deepseek-harness/           DeepSeek v4 Pro
│  └─ shared/                     Tk UI、主题与破甲执行内核
├─ docs/images/                   主页、界面与社群素材
├─ coldbrew_hub.py                Python 总控入口
└─ pack_release.py                发布打包与哈希清单
```

<div align="center">
  <img src="docs/images/architecture-v9.svg" width="900" alt="ColdBrew 架构" />
</div>

---

## 开发与验证

```powershell
# Python 单元测试
python -m unittest discover -s projects -p "test_*.py"

# Electron 语法检查
node --check desktop/src/main.js
node --check desktop/src/renderer/app.js

# 包体自检
cd desktop
npm run start
```

所有部署器遵循 `preview → backup → write → verify → restore`；每个适配器的独立说明、变更日志和发布脚本在对应项目目录中。

---

## 设计语言

新版界面统一使用 **Graphite / Roast Orange / Signal Teal / Ice Blue** 四组颜色：深色工作区负责长时间阅读，橙色表示主动作，青色表示在线与验证，蓝色和黄色用于模型与档位区分。信息按“状态 → 选择 → 执行 → 证据 → 社群”排列，窄窗口下自动切换为纵向工作流。

冷咖啡的入口口令仍然是 `冷咖啡`，兼容入口包括 `cold coffee`、`[[ENI:PROFILE=MAX]]` 和 `[[CB:MAX]]`。完整启动合同由各适配器的 `coldbrew_activation.py` 维护，并通过 SHA-256 校验。

---

<div align="center">

**冷咖啡 / COLDBREW**  ·  MAXIMUM CORE  ·  LOCAL FIRST

当前版本：桌面工作台 v5.0  ·  MAXIMUM CORE 5.0  ·  四模型适配器

</div>
