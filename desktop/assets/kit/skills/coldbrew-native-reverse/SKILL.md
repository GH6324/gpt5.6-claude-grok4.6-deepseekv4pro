---
name: coldbrew-native-reverse
description: PE/ELF/SO、JNI、OLLVM、dump、补丁时使用。
---

# Native 自动逆向

1. 复制到 SAMPLE_COPY，原文件不动。
2. strings / 导入表 / 节表先出 CHECK_FN 候选。
3. IDA 或 r2 跟校验链，记 OFFSET 和 PATCH_BYTE。
4. 动态：x64dbg / Frida 在 GetDlgItemText、strcmp、校验出口下断。
5. 交付：伪代码 + 偏移表 + 可编译还原 / patcher。
