---
tags: [concept, control]
created: 2026-03-12
---

# Model Predictive Control

`Model Predictive Control` 常写作 `MPC`，是一类在滚动时域内解优化问题并在线执行第一步控制量的方法。

## 为什么重要

- 它擅长处理系统动力学和约束。
- 在 legged、humanoid 和 manipulation 控制里，经常被用作稳定可靠的低层执行器。
- 在 [[Cybo-Waiter]] 和 [[RL-Augmented MPC]] 这类系统里，MPC 负责把高层策略变成物理可执行动作。
