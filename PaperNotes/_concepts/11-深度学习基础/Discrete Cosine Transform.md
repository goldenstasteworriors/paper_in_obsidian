---
title: "Discrete Cosine Transform"
aliases: [DCT, 离散余弦变换]
tags: [concept, signal-processing, compression]
created: 2026-04-29
---

# Discrete Cosine Transform

Discrete Cosine Transform（DCT）是一种把实值序列表示为不同频率余弦基组合的频域变换。低频系数描述整体形状，高频系数描述快速变化或尖锐跳变。

## 在机器人策略中的作用

在 [[FAST]] 中，DCT 被用于压缩连续动作块。机器人动作轨迹通常相对平滑，大部分信息集中在低频系数中，因此可以通过量化和省略小系数降低 token 数，同时保持较高动作重建精度。

## 代表工作

- [[FAST]]: 用 DCT 将高频动作块从时间域映射到频域，再做量化和 BPE 压缩。
