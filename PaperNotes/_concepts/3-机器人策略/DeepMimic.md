---
tags: [concept, robotics]
created: 2026-03-16
---

# DeepMimic

`DeepMimic` 是早期把参考动作轨迹和强化学习结合起来做角色控制与模仿的代表性方法。

## 为什么重要

- 它证明了参考动作驱动的策略学习可以产生自然的全身运动。
- 很多 humanoid motion imitation、tracking 和 sim-to-real 工作都会把它当作历史基线。
- 在 [[PhysMoDPO]] 这类论文里，它代表的是“先生成再想办法执行”的老路线。
