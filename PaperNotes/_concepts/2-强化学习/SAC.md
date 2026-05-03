---
tags: [concept, rl]
created: 2026-03-12
---

# SAC

`SAC` 指 `Soft Actor-Critic`，是一种带熵正则项的 off-policy 强化学习算法。

## 为什么常见

- 采样效率通常比 on-policy 方法更高。
- 适合连续控制和机器人动作优化。
- 在 legged control、manipulation 和 residual policy refinement 里经常被当作强 baseline。
