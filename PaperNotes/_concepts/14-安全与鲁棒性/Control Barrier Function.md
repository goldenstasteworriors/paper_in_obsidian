---
tags: [concept, safety]
created: 2026-03-26
---

# Control Barrier Function

`Control Barrier Function` 常写作 `CBF`，是一类把安全集合不变性写成控制约束的方法。只要控制输入满足对应不等式，系统状态就会被限制在安全区域内。

## 为什么重要

- 它适合把碰撞避免、速度安全、状态约束直接写进优化器。
- 在机器人里，CBF 常和 QP 结合，形成“先满足安全，再尽量追任务”的控制结构。
- 对 humanoid 和 manipulation 来说，CBF 的价值在于它不是事后修正，而是在求解动作时就把风险拦住。

## 代表工作

- [[MIRROR]]: 在 differential IK 层面加入离散时间 CBF 约束，限制手和肘相对躯干/头部的安全裕量。

## 相关概念

- [[Differential Inverse Kinematics]]
- [[Whole-Body Controller]]
