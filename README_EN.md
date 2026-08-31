<div align="center">

<img src="docs/images/hero-v11.svg" width="940" alt="ColdBrew Command Center" />

# ColdBrew Command Center

**One continuous workspace for objectives, routes, artifacts, verification and recovery.**

<p>
  <a href="README.md"><img src="https://img.shields.io/badge/中文-Switch-ff8f5a?style=for-the-badge&labelColor=0d1117" alt="Chinese" /></a>
  <a href="README_EN.md"><img src="https://img.shields.io/badge/English-Current-57d8c7?style=for-the-badge&labelColor=0d1117" alt="English" /></a>
  <a href="https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro/stargazers"><img src="https://img.shields.io/github/stars/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro?style=for-the-badge&color=f4d06f&labelColor=0d1117&logo=github&logoColor=white" alt="GitHub stars" /></a>
</p>

<p><img src="https://img.shields.io/badge/Windows-10%2F11-7aa2ff?style=flat-square" alt="Windows" /> <img src="https://img.shields.io/badge/macOS-12%2B-b9c7cc?style=flat-square" alt="macOS" /> <img src="https://img.shields.io/badge/Linux-x64-57d8c7?style=flat-square" alt="Linux" /> <img src="https://img.shields.io/badge/Electron-35-ff8f5a?style=flat-square" alt="Electron" /></p>

</div>

---

## What It Is

ColdBrew is a local-first multi-model workbench focused on jailbreak and break workflows. The Electron shell provides one desktop surface while Python adapters handle preview, deploy, verify and restore for each model. Profiles and targets travel with the session, so a long task can continue from its last verified checkpoint.

<div align="center"><img src="docs/images/window-v11.svg" width="940" alt="ColdBrew workbench" /></div>

### MAXIMUM CORE

MAX keeps six layers together:

| Layer | Role |
| --- | --- |
| **OBJECTIVE** | Original goal, language, format and completion criteria |
| **ROUTE** | One visible route with ordered execution stages |
| **CONTEXT** | Profile, target and pending stage across retries and compaction |
| **ARTIFACT** | Concrete code, documents, configuration or scripts |
| **VERIFY** | Tests, hashes, state checks and desktop acceptance |
| **RECOVERY** | Restore points, changed-file manifests and resumable next steps |

---

## Four Model Seats

| Seat | Directory | Entry point |
| --- | --- | --- |
| **GPT-5.6 / Codex** | `projects/codex-coldbrew` | `studio/eni_solo_deploy.py` |
| **Claude Code** | `projects/claude-coldbrew` | `app/claude_pojia.py` |
| **Grok 4.6** | `projects/grok4.6-coldbrew` | `app/grok_coldbrew.py` |
| **DeepSeek v4 Pro** | `projects/deepseek-harness` | `app/deepseek_harness.py` |

Every seat exposes the same four actions: preview a plan, deploy with an atomic restore point, verify the result, and restore while preserving later user drift.

<div align="center"><img src="docs/images/card-codex-coldbrew.png" width="220" alt="Codex" /> <img src="docs/images/card-claude-coldbrew.png" width="220" alt="Claude" /> <img src="docs/images/card-grok4.6-coldbrew.png" width="220" alt="Grok" /> <img src="docs/images/card-deepseek-harness.png" width="220" alt="DeepSeek" /></div>

---

## Break / Jailbreak Profiles

Profiles are the primary product language. Choose the intensity that matches the session; the selected profile is sent to every adapter.

| Profile | Focus |
| --- | --- |
| **MAX / Full** | Full objective lock, layered context, direct artifact delivery and recovery |
| **FOCUS** | Short execution loop for one sharply defined target |
| **BUILDER** | Implementation, packaging, tests and reproducible output |
| **RESEARCH** | Sources, evidence, decisions and open assumptions |
| **CREATIVE** | Voice, characters, continuity and complete drafts |

The visible chain is always `objective → route → context → artifact → verify → recovery`.

---

## Quick Start

```powershell
git clone https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro.git
cd gpt5.6-claude-grok4.6-deepseekv4pro/desktop
npm install
npm start
```

For the Python workbench:

```powershell
cd gpt5.6-claude-grok4.6-deepseekv4pro
python coldbrew_hub.py
```

Choose a profile, select a target, preview, deploy, verify, then use the activity stream to resume or restore.

---

## Community

The existing community promotion stays in place. QR assets live under `docs/images/`; the desktop buttons copy QQ numbers and open Telegram links.

<div align="center"><img src="docs/images/qq-group-1-card.png" width="300" alt="QQ group 1057540028" /> <img src="docs/images/qq-group-2-card.png" width="300" alt="QQ group 1077074552" /></div>

| Platform | Entry |
| --- | --- |
| Telegram group | [@chachachacha99999](https://t.me/chachachacha99999) |
| Telegram channel | [@chachachacha99999999](https://t.me/chachachacha99999999) |
| QQ discussion group | `1057540028` |
| QQ topic group | `1077074552` |

<div align="center"><img src="docs/images/telegram-group-v2.png" width="280" alt="Telegram group" /> <img src="docs/images/telegram-channel-v2.png" width="280" alt="Telegram channel" /></div>

---

## Repository Map

```text
desktop/                    Electron 35 shell and Command Center UI
projects/codex-coldbrew     GPT-5.6 / Codex adapter
projects/claude-coldbrew    Claude Code adapter
projects/grok4.6-coldbrew   Grok 4.6 adapter
projects/deepseek-harness   DeepSeek v4 Pro adapter
projects/shared             Tk UI, theme and execution core
docs/images                 Homepage, UI and community assets
coldbrew_hub.py             Python orchestration entry
pack_release.py             Release packaging and hashes
```

## Development Checks

```powershell
python -m unittest discover -s projects -p "test_*.py"
node --check desktop/src/main.js
node --check desktop/src/renderer/app.js
```

The activation phrase remains `冷咖啡`; compatibility entries are `cold coffee`, `[[ENI:PROFILE=MAX]]` and `[[CB:MAX]]`. Each adapter maintains its own activation contract and SHA-256 check.

<div align="center"><strong>COLDBREW / MAXIMUM CORE / BREAK & JAILBREAK / LOCAL FIRST</strong></div>
