# 原创说明

这是给冷咖啡写的原生窗口。对照物是桌面上的 AC NEXUS 能力面，源码和图都是新写的。

## 没拿过来的

- AC.exe / Electron asar 里的 JS、CSS、HTML、SVG、webm
- `gpt5.5-unrestricted.md`、`gpt-5.6-sol-unrestricted-v35.md`、AC 的 AGENTS 模板
- 微验卡密、设备指纹、`weiyan-license`
- 「你好 我是AC」、宝宝称呼、QQ3082228970、NX 印章
- 水墨劈界、拔剑、heaven/earth 开缝那套开场
- reverse-skill 那棵包、Keysmith Python 运行时和 zip

## 新写的

- `src/splash`：锁盘被五刃劈开、碎甲、落印「破」、字幕「一键破甲越狱」
- `src/renderer`：奶油纸 + 焦糖字的无卡密工作台
- `src/lib`：四模型调度、Codex 挂钩加厚、环境扫描、静态验收、Desktop app-server 联机
- 主色：espresso `#2A1810`、gold `#C45C14`、cream `#F7EFE3`，跟冷咖啡仓品牌一致，跟 AC 的墨玉夜色不是一套

## 随包芯

`core/` 来自公开仓库 https://github.com/3641397194-wq/gpt5.6-claude-grok4.6-deepseekv4pro  
那是同一作者的四模型适配器，不是 AC 的东西。壳只 spawn 它的 CLI：预览 / 部署 / 验证 / 复原。

## 能力面对照

| 能力 | AC NEXUS | 冷咖啡 |
| --- | --- | --- |
| 开场动画 | 有（他人素材） | 有（原创破甲） |
| 无框窗 + 日志 | 有 | 有 |
| 选目录 / 打开目录 | 有 | 有 |
| 一键部署 | Codex 单家 | 四模型 |
| 恢复默认 | AC 托管清单 | 各席 restore |
| 完整验收 | Keysmith + Desktop 任务 | 适配器 verify + 挂钩体检 + Desktop |
| 环境扫描 | 有 | 有 |
| 中文 locale | 有 | 有 |
| hooks | 整份隔离 | 占住每轮回灌 |
| 最强提示词 | 拷了 v35 没挂钩 | 只挂现场存在的 jailbreak 文件 |
| 审批 / 沙箱写入 config | 无（仅验活线程临时 never） | 写入 config.toml |
| 卡密墙 | 有 | 无 |
