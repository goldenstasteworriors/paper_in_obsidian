---
title: "JAX"
type: concept
tags: [deep-learning-framework, distributed-training]
created: 2026-04-29
---

# JAX

JAX 是 Google 推出的高性能数值计算和自动微分框架，常用于 TPU 上的大规模模型训练。

## 在论文中的作用

- [[PaliGemma]] 在 `big_vision` codebase 中使用 JAX 训练。
- 训练结合 [[GSPMD]] 做分布式 sharding。

## 代表工作

- [[PaliGemma]]: 使用 JAX 在 Cloud TPU 上训练 VLM。
