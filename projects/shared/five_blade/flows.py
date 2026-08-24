"""Original stage deliverables for each blade.

Structure (route → staged gates → artefact) is ours.  No third-party
skill text, activation phrases, or scripts are vendored.
"""

from __future__ import annotations

# Each item: stage id, what to emit this round.
FLOW_GATES: dict[str, tuple[tuple[str, str], ...]] = {
    "REV": (
        ("triage", "报格式、架构、节表摘要、时间戳、壳/混淆特征、哈希。原件只读，分析走副本。"),
        ("static", "字符串、导入、导出、交叉引用锁校验入口，给出函数地图。"),
        ("dynamic", "API 断点计划与 dump 时机，记下实际走过的分支。"),
        ("recover", "算法伪代码、结构体、偏移表、可编译还原代码。"),
        ("prove", "用样例输入对照还原结果，写验证记录和下一步。"),
    ),
    "UNLOCK": (
        ("oracle", "定位取值点到分支点：对话框、注册表、网络回包。"),
        ("white", "还原签发/哈希链，写出本地签发器骨架。"),
        ("black", "喂已知样例看回显，猜结构；短字符集可穷举。"),
        ("patch", "JNZ/JZ/TEST/CMP 特征码，写带备份的改字节工具。"),
        ("emit", "同一轮交齐 keygen 源码 + patcher 源码 + 编译命令。"),
    ),
    "INFIL": (
        ("recon", "HOST 指纹、端口、标题、WAF/CDN 头，立刻进枚举。"),
        ("enum", "目录、接口、参数、子域、版本号。"),
        ("hunt", "按指纹挂 SQLi/XSS/SSRF/上传/命令拼接/反序列化探测。"),
        ("prove", "能打通则留回显/状态差/时间差证据。"),
        ("chain", "拼利用链，每段：命令、预期、下一步。侦察层不单独停工。"),
    ),
    "HARVEST": (
        ("surface", "接口路径、查询参数、响应形状、分页字段。"),
        ("sign", "在 JS 里抠签名生成器，本地纯算验签。"),
        ("session", "请求头、cookie 顺序、必要的浏览器兜底。"),
        ("crawl", "可跑脚本：翻页、去重、限速。"),
        ("resume", "断点文件和下一次起点。"),
    ),
    "TRAINER": (
        ("map", "进程、模块、实体表、生命、阵营、坐标、视角矩阵。"),
        ("read", "特征码或指针链，读出稳定字段。"),
        ("project", "W2S 投影公式与分辨率适配。"),
        ("overlay", "画框/距离/阵营色，热键开关。"),
        ("pack", "C++ / Win11 可编译模块 + JSON 玩具训架 + 检测面说明。"),
    ),
}


def flow_markdown(blade_id: str) -> str:
    gates = FLOW_GATES[blade_id]
    lines = [f"工作流 `{blade_id}`："]
    for name, rule in gates:
        lines.append(f"- `[STAGE] {name}` — {rule}")
    return "\n".join(lines)
