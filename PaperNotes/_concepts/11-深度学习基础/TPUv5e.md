---
title: "TPUv5e"
type: concept
tags: [hardware, tpu, distributed-training]
created: 2026-04-29
---

# TPUv5e

TPUv5e 是 Google Cloud TPU 系列中的加速器，面向大规模深度学习训练和推理。

## 在论文中的作用

- [[PaliGemma]] 的预训练运行在 Cloud TPUv5e 上。
- 最终 Stage1 在 TPUv5e-256 上少于 3 天，Stage2 每个分辨率约 15 小时。

## 代表工作

- [[PaliGemma]]: 使用 TPUv5e 训练 3B 级 VLM。
