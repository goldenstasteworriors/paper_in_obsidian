---
tags: [concept, robotics]
created: 2026-03-16
---

# ACT

`ACT` 通常指 `Action Chunking with Transformers`，核心思路是一次预测一段连续动作，而不是逐时刻回归单步控制。

## 为什么重要

- 它能减轻自回归控制里的误差积累和高频抖动。
- 在操作和 whole-body 控制里，chunk-level action 往往更适合长时序执行。
- 在 [[Psi0]] 这类 humanoid foundation model 工作里，ACT 常被当作 action expert 路线的重要参照。
