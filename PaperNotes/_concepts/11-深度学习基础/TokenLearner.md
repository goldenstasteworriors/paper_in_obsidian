---
title: "TokenLearner"
type: concept
tags: [token-compression, attention]
created: 2026-04-28
---

# TokenLearner

TokenLearner 是一种自适应 token 压缩模块，通过学习注意力权重从大量视觉 token 中选择或组合少量信息量更高的 token。

## 在 RT-1 中

[[RT-1]] 将每帧 81 个视觉-语言 token 压缩到 8 个 token，显著降低后续 [[Transformer]] 的计算量，使 35M 参数策略能以 3 Hz 在真实机器人上闭环运行。

## 代表工作

- [[RT-1]]: 用 TokenLearner 平衡 Transformer 容量和实时控制延迟。
