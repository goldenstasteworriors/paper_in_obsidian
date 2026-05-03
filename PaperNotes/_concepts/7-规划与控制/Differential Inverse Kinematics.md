---
tags: [concept, control]
created: 2026-03-26
---

# Differential Inverse Kinematics

`Differential Inverse Kinematics` 常写作 `differential IK`，指在当前位形附近用一阶线性化，把 task-space 误差转成一次小的关节增量求解问题。

## 为什么重要

- 它比 global IK 快得多，适合高频控制和 teleoperation。
- 它通常被写成带约束的 QP，很容易和关节限位、速度限位、自碰撞约束拼在一起。
- 缺点也很明显: 它是局部方法，容易被奇异位形、关节极限和 active constraint 困在坏 basin 里。

## 代表工作

- [[MIRROR]]: 用并行 continuation 把 differential IK 从单实例局部更新，扩成可逃离坏 basin 的实时 teleoperation 求解器。

## 相关概念

- [[Control Barrier Function]]
- [[Whole-Body Controller]]
