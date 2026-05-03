---
title: "GSPMD"
type: concept
tags: [distributed-training, sharding]
created: 2026-04-29
---

# GSPMD

GSPMD 是 XLA/JAX 生态中的通用 SPMD 分布式切分机制，用于把数组和模型计算映射到多设备。

## 在论文中的作用

- [[PaliGemma]] 使用 [[JAX]] + GSPMD 对数据、模型参数和优化器状态做跨设备分片。
- 这支持在 TPUv5e-256 上训练 3B 级 VLM。

## 代表工作

- [[PaliGemma]]: 使用 GSPMD 实现大规模 VLM 训练 sharding。
