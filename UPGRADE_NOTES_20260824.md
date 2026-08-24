# ColdBrew Suite v9 升级记录

回滚备份：`projects/_rollback_v8_20260824-175054/`

## 改动范围

- 仓库首页换成原创矢量：`banner-v9.svg`、`blades-board.svg`、`architecture-v9.svg`、`workbench-v9.svg`。文案双语重写，不搬运外部 instruct 仓库的 README 正文。
- Hub 升到 v9：五刃选择条、`COLDBREW_BLADE` 加注、Alt+1–5。
- 共享工作台增加五刃按钮与简报。
- 新增自研内核 `projects/shared/five_blade/`（SCENE-PRESS + 五条交付链）。
- Grok / DeepSeek 的 `compose_prompt` 追加 FiveEdge 段；Claude 增加 `50-five-edge.md` 与 `coldbrew-five-edge` skill；Codex `eni-solo.md` 增加五刃段落。
- `pack_release.py` 把 `five_blade` 打进 Claude/Grok/DeepSeek 独立源码包。

## 版本

| 项目 | 旧 | 新 |
| --- | --- | --- |
| Hub | v8 | v9 |
| Codex | 7.0.0 | 7.1.0 |
| Claude | 3.1.0 | 3.2.0 |
| Grok | 1.0.1 | 1.1.0 |
| DeepSeek | 1.0.1 | 1.1.0 |
| FiveEdge | — | 1.0.0 |

## 回滚

1. 用 `projects/_rollback_v8_20260824-175054/` 里的 `coldbrew_hub.py`、`README.md`、`coldbrew_ui.py`、`profile_engine.py` 覆盖对应位置。
2. 删除 `projects/shared/five_blade/`。
3. 对已部署目录跑各适配器 `restore`。
