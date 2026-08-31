# 冷咖啡 · Command Center

Electron 桌面工作台，产品主线是 **破甲 / 越狱 / MAXIMUM CORE**。它把 GPT-5.6、Claude Code、Grok 4.6 和 DeepSeek v4 Pro 四个适配器放进同一窗口，统一提供预览、部署、验证和恢复。

## 新版工作台

- 指挥台：当前状态、MAX 启动和验收入口
- 越狱档位：MAX、FOCUS、BUILDER、RESEARCH、CREATIVE
- 模型席位：四个适配器的独立状态与动作
- 执行中心：目标目录、配置层、恢复点和环境检查
- 活动流：实时日志、结果复制和可继续的阶段记录
- 社群入口：QQ 群号复制、Telegram 群/频道直达

界面文案和布局围绕“破甲 / 越狱”重做，原有社群宣传、二维码文件和适配器接口继续保留。

## 启动

```bash
npm install
npm start
```

Windows 双击 `start.bat`；macOS/Linux 使用 `start.sh`。需要 Node.js 和 Python 3.10+。

## 打包

```bash
npm run pack:win
npm run pack:mac
npm run pack:linux
```

## 目录

```text
src/main.js          主进程、IPC、窗口生命周期
src/preload.js       受限渲染桥
src/renderer/        Command Center 页面
src/splash/          MAXIMUM CORE 启动页
src/lib/             适配器、目录发现、恢复与环境模块
../projects/         四个模型适配器与共享 Tk 工作台
```

## 社群

- QQ 交流群：`1057540028`
- QQ 专题群：`1077074552`
- Telegram 群：`@chachachacha99999`
- Telegram 频道：`@chachachacha99999999`
