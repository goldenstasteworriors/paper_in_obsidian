---
tags: [concept, rl]
created: 2026-03-10
---

# PPO

`PPO` 是 `Proximal Policy Optimization`，一种常用于机器人控制和运动模仿学习的 on-policy 强化学习算法。

## 为什么常见

- 工程上比很多 policy gradient 方法更稳。
- 对 continuous control 比较友好。
- 在 humanoid locomotion、whole-body control、[[HOI]] 里出现频率很高。
