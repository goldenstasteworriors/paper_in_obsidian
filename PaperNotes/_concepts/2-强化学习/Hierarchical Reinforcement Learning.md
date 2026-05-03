---
type: concept
aliases: [HRL, 层级强化学习]
---

# Hierarchical Reinforcement Learning

## 定义

把决策过程拆成高层子目标 / option 选择和低层动作执行两级或多级结构的 [[Reinforcement Learning]] 方法。

## 数学形式

$$
\pi(a_t \mid s_t)=\sum_{o_t} \pi_{\text{low}}(a_t \mid s_t,o_t)\,\pi_{\text{high}}(o_t \mid s_t)
$$

## 核心要点

1. 高层负责更稀疏、更长时间尺度的决策。
2. 低层负责更短时间尺度的动作控制或技能执行。
3. 适合长时程任务、稀疏奖励和技能复用场景。

## 代表工作

- [[BAT]]: 用高层切换策略在不同 whole-body controller 之间做在线选择。
- [[Motion Primitive]]: 很多层级控制方法都会把 motion primitive 视作低层 option。

## 相关概念

- [[Reinforcement Learning]]
- [[PPO]]
- [[Motion Primitive]]
