---
type: concept
aliases: [IL, 模仿学习]
---

# Imitation Learning

## 定义

通过模仿专家示范来学习策略，而不是直接从环境奖励中探索的机器学习范式。

## 数学形式

$$
\min_{\theta} \sum_{(o_t, a_t) \in \mathcal{D}} \|\pi_\theta(o_t) - a_t\|^2
$$

## 核心要点

1. 训练稳定、样本效率高，但容易受 compounding error 影响。
2. 常见形式包括 behavior cloning、DAgger 和 inverse RL 等。
3. 适合机器人示教、遥操作数据学习和 human-to-robot transfer。

## 代表工作

- [[LIDEA]]: 利用 human video 辅助机器人模仿学习。
- [[OmniUMI]]: 用多模态示教信号训练 contact-rich manipulation 策略。

## 相关概念

- [[DAgger]]
- [[Teleoperation]]

