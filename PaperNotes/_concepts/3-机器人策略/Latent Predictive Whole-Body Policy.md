---
type: concept
aliases: [潜在预测全身策略, 未来视觉辅助全身动作策略]
---

# Latent Predictive Whole-Body Policy

## 定义

用未来视觉特征的辅助预测任务约束全身动作表示，再以连续控制器 latent 驱动机器人。它可以帮助策略理解任务进展，但不自动具备候选动作干预下的反事实预测或规划能力。

## 数学形式

$$
\mathcal L=\mathcal L_{action}+\lambda\|\hat y_{future}-E(o_{future})\|_2^2
$$

其中动作损失监督可执行动作，E 是未来观测编码器，预测特征作为动作头的条件，λ 控制辅助监督权重。

## 核心要点

1. 不要求解码像素视频；但是否保留内部未来查询取决于具体部署架构。
2. 低层控制器的可跟踪性与物体交互的正确性需要分别评估。
3. 未来预测 MSE 与闭环任务成功率可能不一致。
4. 等参数、等控制器、等实时动作分块条件下的时序干预实验，才能较好隔离未来监督本身的收益。

## 代表工作

- [[Omega0]]：全身动作 VLM、SONIC 回放、未来 Wan latent 监督、动作 DiT 与 RTC；原文 https://arxiv.org/html/2608.06375v2 。

## 相关概念

- [[World Action Model]]
- [[Latent Action]]
- [[Real-Time Chunking]]
