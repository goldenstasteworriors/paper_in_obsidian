---
type: concept
aliases: [cross-embodiment, 跨本体, 跨机器人本体学习]
---

# X-Embodiment

## 定义
X-Embodiment 指跨不同机器人身体结构、传感器、执行器、控制接口和数据分布进行策略学习或迁移。

## 数学形式

$$
\pi_\theta(a \mid o, l, e),\quad e \in \mathcal{E}
$$

## 核心要点
1. 不同 embodiment 的观测空间、动作空间、控制频率和任务分布可能不同。
2. 学习目标是让策略从多个 embodiment 的数据中获得正迁移。
3. 难点包括动作语义对齐、负迁移、数据不均衡和 unseen embodiment 泛化。

## 代表工作
- [[RT-X]]: 直接在多机器人真实数据上训练跨本体策略。

## 相关概念
- [[Open X-Embodiment]]
- [[RT-X]]
- [[Imitation Learning]]
