---
title: "DROID"
type: concept
tags: [robot-dataset, imitation-learning]
created: 2026-04-28
---

# DROID

DROID 是面向真实机器人操作的大规模数据集，包含多场景、多任务的 Franka 机器人演示数据。

## 为什么重要

- 它提供了比单实验室数据更丰富的真实世界机器人操作分布。
- 在 [[OpenVLA]] 中，作者尝试把 DROID 加入 OpenX mixture，但由于 action token accuracy 学习较慢，最终在训练最后三分之一阶段移除。

## 代表工作

- [[OpenVLA]]: 使用 DROID 风格 Franka setup 做数据高效微调评测，并讨论 DROID 加入预训练 mixture 的困难。
