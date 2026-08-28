---
name: coldbrew-protocol-reverse
description: 自定义协议、TCP/UDP 帧、回放与字段还原时使用。
---

# 协议分析

1. 固定长度头还是 TLV，先画字段表。
2. 对齐魔数、长度、校验、序列号。
3. 写可回放客户端：连 HOST、发 PAYLOAD、打回显。
4. 加密层单独拆：密钥从样本 / 内存 / 配置三处找。
